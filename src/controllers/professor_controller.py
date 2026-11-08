"""Páginas do professor."""

from flask import request

from src.controllers.controller import Controller
from src.models.aluno import Aluno
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.questao_certo_errado import QuestaoCertoErrado
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta
from src.models.simulado import Simulado


class ProfessorController(Controller):
    """Cadastro de questões e simulados e acompanhamento dos alunos."""

    TIPO_USUARIO = "professor"

    def registrar_rotas(self):
        """Registra as rotas do professor."""
        self.adicionar_rota("/professor", "professor_painel", self.painel)
        self.adicionar_rota("/professor/questoes", "professor_questoes", self.questoes)
        self.adicionar_rota(
            "/professor/questoes/nova-multipla",
            "professor_nova_multipla",
            self.nova_multipla,
            ("GET", "POST"),
        )
        self.adicionar_rota(
            "/professor/questoes/nova-certo-errado",
            "professor_nova_certo_errado",
            self.nova_certo_errado,
            ("GET", "POST"),
        )
        self.adicionar_rota(
            "/professor/questoes/<int:questao_id>/editar",
            "professor_editar_questao",
            self.editar_questao,
            ("GET", "POST"),
        )
        self.adicionar_rota(
            "/professor/questoes/<int:questao_id>/excluir",
            "professor_excluir_questao",
            self.excluir_questao,
            ("POST",),
        )
        self.adicionar_rota("/professor/simulados", "professor_simulados", self.simulados)
        self.adicionar_rota(
            "/professor/simulados/novo",
            "professor_novo_simulado",
            self.novo_simulado,
            ("GET", "POST"),
        )
        self.adicionar_rota(
            "/professor/simulados/<int:simulado_id>",
            "professor_simulado_detalhe",
            self.simulado_detalhe,
        )
        self.adicionar_rota("/professor/alunos", "professor_alunos", self.alunos)
        self.adicionar_rota(
            "/professor/alunos/<int:aluno_id>", "professor_aluno_detalhe", self.aluno_detalhe
        )

    def painel(self):
        """Mostra o painel com o total de questões e de alunos."""
        return self.renderizar(
            "professor/painel.html",
            professor=self.usuario,
            total_questoes=len(Questao.buscar()),
            total_alunos=len(Aluno.listar_todos()),
        )

    def questoes(self):
        """Lista todas as questões cadastradas."""
        return self.renderizar("professor/questoes.html", questoes=Questao.buscar())

    def nova_multipla(self):
        """Mostra o formulário e cadastra uma questão de múltipla escolha."""
        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                questao = QuestaoMultipla.de_formulario(dados, self.usuario.id)
                questao.salvar()
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                return self.redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} cadastrada."
                )

        return self.renderizar(
            "professor/nova_multipla.html", dados=dados, letras=QuestaoMultipla.LETRAS
        )

    def nova_certo_errado(self):
        """Mostra o formulário e cadastra uma questão de certo ou errado."""
        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                questao = QuestaoCertoErrado.de_formulario(dados, self.usuario.id)
                questao.salvar()
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                return self.redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} cadastrada."
                )

        return self.renderizar(
            "professor/nova_certo_errado.html", dados=dados, opcoes=QuestaoCertoErrado.OPCOES
        )

    def editar_questao(self, questao_id):
        """Mostra o formulário já preenchido e grava as alterações da questão."""
        questao = Questao.buscar_por_id(questao_id)
        if questao is None:
            return self.redirecionar("/professor/questoes", "Questão não encontrada.", "erro")

        dados = questao.para_formulario()

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                editada = questao.de_formulario(dados, questao.professor_id, questao.id)
                editada.atualizar()
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                return self.redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} atualizada."
                )

        if questao.TIPO == QuestaoMultipla.TIPO:
            pagina = "professor/nova_multipla.html"
        else:
            pagina = "professor/nova_certo_errado.html"

        return self.renderizar(
            pagina,
            dados=dados,
            questao=questao,
            letras=QuestaoMultipla.LETRAS,
            opcoes=QuestaoCertoErrado.OPCOES,
        )

    def excluir_questao(self, questao_id):
        """Exclui a questão, se ela ainda não tiver respostas."""
        questao = Questao.buscar_por_id(questao_id)
        if questao is None:
            return self.redirecionar("/professor/questoes", "Questão não encontrada.", "erro")

        try:
            questao.excluir()
        except ValueError as erro:
            return self.redirecionar("/professor/questoes", str(erro), "erro")

        return self.redirecionar("/professor/questoes", f"Questão nº {questao.id} excluída.")

    def simulados(self):
        """Lista os simulados cadastrados."""
        return self.renderizar("professor/simulados.html", simulados=Simulado.listar_todos())

    def novo_simulado(self):
        """Mostra as questões para escolher e cria o simulado."""
        titulo = ""
        escolhidas = []

        if request.method == "POST":
            titulo = request.form.get("titulo", "")
            escolhidas = request.form.getlist("questoes")
            try:
                simulado = Simulado.montar(titulo, self.usuario.id, escolhidas)
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                return self.redirecionar(
                    f"/professor/simulados/{simulado.id}",
                    f"Simulado criado com {len(simulado)} questões.",
                )

        return self.renderizar(
            "professor/novo_simulado.html",
            titulo=titulo,
            escolhidas=escolhidas,
            questoes=Questao.buscar(),
        )

    def simulado_detalhe(self, simulado_id):
        """Mostra as questões do simulado e o resultado de cada aluno que o fez."""
        simulado = Simulado.buscar_por_id(simulado_id)
        if simulado is None:
            return self.redirecionar("/professor/simulados", "Simulado não encontrado.", "erro")

        return self.renderizar(
            "professor/simulado_detalhe.html",
            simulado=simulado,
            resultados=simulado.resultados(),
        )

    def alunos(self):
        """Lista os alunos com o desempenho geral de cada um."""
        desempenhos = []
        for aluno in Aluno.listar_todos():
            desempenhos.append(Desempenho.do_aluno(aluno))

        return self.renderizar("professor/alunos.html", desempenhos=desempenhos)

    def aluno_detalhe(self, aluno_id):
        """Mostra o desempenho e o histórico de um aluno."""
        aluno = Aluno.buscar_por_id(aluno_id)
        if aluno is None:
            return self.redirecionar("/professor/alunos", "Aluno não encontrado.", "erro")

        return self.renderizar(
            "professor/aluno_detalhe.html",
            desempenho=Desempenho.do_aluno(aluno),
            respostas=Resposta.listar_por_aluno(aluno.id),
        )
