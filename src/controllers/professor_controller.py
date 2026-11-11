"""Páginas do professor."""

from flask import request

from src.controllers.controller import Controller
from src.models.aluno import Aluno
from src.models.correcao_redacao import CorrecaoRedacao
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.questao_verdadeiro_falso import QuestaoVerdadeiroFalso
from src.models.questao_multipla import QuestaoMultipla
from src.models.redacao import Redacao
from src.models.resposta import Resposta
from src.models.simulado import Simulado


class ProfessorController(Controller):
    """Cadastro de questões e simulados, correção de redações e acompanhamento dos alunos.

    Attributes:
        FORMULARIOS (dict): página do formulário de cada tipo de questão.
    """

    TIPO_USUARIO = "professor"
    FORMULARIOS = {
        QuestaoMultipla.TIPO: "professor/nova_multipla.html",
        QuestaoVerdadeiroFalso.TIPO: "professor/nova_verdadeiro_falso.html",
        Redacao.TIPO: "professor/nova_redacao.html",
    }

    def _registrar_rotas(self):
        """Registra as rotas do professor."""
        self._adicionar_rota("/professor", "professor_painel", self.painel)
        self._adicionar_rota("/professor/questoes", "professor_questoes", self.questoes)
        self._adicionar_rota(
            "/professor/questoes/nova-multipla",
            "professor_nova_multipla",
            self.nova_multipla,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/professor/questoes/nova-verdadeiro-falso",
            "professor_nova_verdadeiro_falso",
            self.nova_verdadeiro_falso,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/professor/questoes/nova-redacao",
            "professor_nova_redacao",
            self.nova_redacao,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/professor/questoes/<int:questao_id>/editar",
            "professor_editar_questao",
            self.editar_questao,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/professor/questoes/<int:questao_id>/excluir",
            "professor_excluir_questao",
            self.excluir_questao,
            ("POST",),
        )
        self._adicionar_rota("/professor/simulados", "professor_simulados", self.simulados)
        self._adicionar_rota(
            "/professor/simulados/novo",
            "professor_novo_simulado",
            self.novo_simulado,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/professor/simulados/<int:simulado_id>",
            "professor_simulado_detalhe",
            self.simulado_detalhe,
        )
        self._adicionar_rota("/professor/redacoes", "professor_redacoes", self.redacoes)
        self._adicionar_rota(
            "/professor/redacoes/<int:resposta_id>",
            "professor_corrigir_redacao",
            self.corrigir_redacao,
            ("GET", "POST"),
        )
        self._adicionar_rota("/professor/alunos", "professor_alunos", self.alunos)
        self._adicionar_rota(
            "/professor/alunos/<int:aluno_id>", "professor_aluno_detalhe", self.aluno_detalhe
        )

    def painel(self):
        """Mostra o painel com o total de questões, de alunos e de redações pendentes."""
        return self._renderizar(
            "professor/painel.html",
            professor=self.usuario,
            total_questoes=len(Questao.buscar()),
            total_alunos=len(Aluno.listar_todos()),
            total_pendentes=len(Resposta.listar_pendentes()),
        )

    def questoes(self):
        """Lista todas as questões cadastradas."""
        return self._renderizar("professor/questoes.html", questoes=Questao.buscar())

    def nova_multipla(self):
        """Mostra o formulário e cadastra uma questão de múltipla escolha."""
        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                questao = QuestaoMultipla.de_formulario(dados, self.usuario.id)
                questao.salvar()
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} cadastrada."
                )

        return self._renderizar(
            "professor/nova_multipla.html", dados=dados, letras=QuestaoMultipla.LETRAS
        )

    def nova_verdadeiro_falso(self):
        """Mostra o formulário e cadastra uma questão de verdadeiro ou falso."""
        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                questao = QuestaoVerdadeiroFalso.de_formulario(dados, self.usuario.id)
                questao.salvar()
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} cadastrada."
                )

        return self._renderizar(
            "professor/nova_verdadeiro_falso.html", dados=dados, opcoes=QuestaoVerdadeiroFalso.OPCOES
        )

    def nova_redacao(self):
        """Mostra o formulário e cadastra uma proposta de redação."""
        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                questao = Redacao.de_formulario(dados, self.usuario.id)
                questao.salvar()
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    "/professor/questoes", f"Redação nº {questao.id} cadastrada."
                )

        return self._renderizar(
            "professor/nova_redacao.html", dados=dados, competencias=Redacao.COMPETENCIAS
        )

    def editar_questao(self, questao_id):
        """Mostra o formulário já preenchido e grava as alterações da questão."""
        questao = Questao.buscar_por_id(questao_id)
        if questao is None:
            return self._redirecionar("/professor/questoes", "Questão não encontrada.", "erro")

        dados = questao.para_formulario()

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                editada = questao.de_formulario(dados, questao.professor_id, questao.id)
                editada.atualizar()
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    "/professor/questoes", f"Questão nº {questao.id} atualizada."
                )

        return self._renderizar(
            self.FORMULARIOS[questao.TIPO],
            dados=dados,
            questao=questao,
            letras=QuestaoMultipla.LETRAS,
            opcoes=QuestaoVerdadeiroFalso.OPCOES,
            competencias=Redacao.COMPETENCIAS,
        )

    def excluir_questao(self, questao_id):
        """Exclui a questão, se ela ainda não tiver respostas."""
        questao = Questao.buscar_por_id(questao_id)
        if questao is None:
            return self._redirecionar("/professor/questoes", "Questão não encontrada.", "erro")

        try:
            questao.excluir()
        except ValueError as erro:
            return self._redirecionar("/professor/questoes", str(erro), "erro")

        return self._redirecionar("/professor/questoes", f"Questão nº {questao.id} excluída.")

    def simulados(self):
        """Lista os simulados cadastrados."""
        return self._renderizar("professor/simulados.html", simulados=Simulado.listar_todos())

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
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    f"/professor/simulados/{simulado.id}",
                    f"Simulado criado com {len(simulado)} questões.",
                )

        return self._renderizar(
            "professor/novo_simulado.html",
            titulo=titulo,
            escolhidas=escolhidas,
            questoes=Questao.buscar(),
        )

    def simulado_detalhe(self, simulado_id):
        """Mostra as questões do simulado e o resultado de cada aluno que o fez."""
        simulado = Simulado.buscar_por_id(simulado_id)
        if simulado is None:
            return self._redirecionar("/professor/simulados", "Simulado não encontrado.", "erro")

        return self._renderizar(
            "professor/simulado_detalhe.html",
            simulado=simulado,
            resultados=simulado.resultados(),
        )

    def redacoes(self):
        """Lista as redações que esperam correção, da mais antiga para a mais nova."""
        return self._renderizar("professor/redacoes.html", pendentes=Resposta.listar_pendentes())

    def corrigir_redacao(self, resposta_id):
        """Mostra o texto do aluno e grava as notas das competências e o comentário."""
        resposta = Resposta.buscar_por_id(resposta_id)
        if resposta is None or not (resposta.pendente or resposta.corrigida):
            return self._redirecionar("/professor/redacoes", "Redação não encontrada.", "erro")

        dados = {}

        if request.method == "POST":
            dados = request.form.to_dict()
            try:
                resposta.registrar_correcao(CorrecaoRedacao.de_formulario(dados))
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    "/professor/redacoes",
                    f"Redação de {resposta.aluno().nome} corrigida: {resposta.correcao}.",
                )

        return self._renderizar(
            "professor/corrigir_redacao.html",
            resposta=resposta,
            questao=resposta.questao(),
            aluno=resposta.aluno(),
            dados=dados,
            competencias=Redacao.COMPETENCIAS,
            niveis=CorrecaoRedacao.NIVEIS,
        )

    def alunos(self):
        """Lista os alunos com o desempenho geral de cada um."""
        desempenhos = []
        for aluno in Aluno.listar_todos():
            desempenhos.append(Desempenho.do_aluno(aluno))

        return self._renderizar("professor/alunos.html", desempenhos=desempenhos)

    def aluno_detalhe(self, aluno_id):
        """Mostra o desempenho e o histórico de um aluno."""
        aluno = Aluno.buscar_por_id(aluno_id)
        if aluno is None:
            return self._redirecionar("/professor/alunos", "Aluno não encontrado.", "erro")

        return self._renderizar(
            "professor/aluno_detalhe.html",
            desempenho=Desempenho.do_aluno(aluno),
            respostas=Resposta.listar_por_aluno(aluno.id),
        )
