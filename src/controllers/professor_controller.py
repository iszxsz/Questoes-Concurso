"""Páginas do professor."""

from flask import request

from src.controllers.controller import Controller
from src.models.aluno import Aluno
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.questao_certo_errado import QuestaoCertoErrado
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta


class ProfessorController(Controller):
    """Cadastro de questões e acompanhamento dos alunos."""

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

            alternativas = []
            for letra in QuestaoMultipla.LETRAS:
                alternativas.append(dados.get("alternativa_" + letra.lower(), ""))

            try:
                questao = QuestaoMultipla(
                    dados.get("enunciado", ""),
                    dados.get("disciplina", ""),
                    dados.get("banca", ""),
                    dados.get("ano", ""),
                    self.usuario.id,
                    alternativas,
                    dados.get("gabarito", ""),
                )
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
                questao = QuestaoCertoErrado(
                    dados.get("enunciado", ""),
                    dados.get("disciplina", ""),
                    dados.get("banca", ""),
                    dados.get("ano", ""),
                    self.usuario.id,
                    dados.get("gabarito", ""),
                )
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
