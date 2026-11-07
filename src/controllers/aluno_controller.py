"""Páginas do aluno."""

from flask import request

from src.controllers.controller import Controller
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.resposta import Resposta


class AlunoController(Controller):
    """Questões e resultados do aluno."""

    TIPO_USUARIO = "aluno"

    def registrar_rotas(self):
        """Registra as rotas do aluno."""
        self.adicionar_rota("/aluno", "aluno_painel", self.painel)
        self.adicionar_rota("/aluno/questoes", "aluno_questoes", self.questoes)
        self.adicionar_rota(
            "/aluno/questoes/<int:questao_id>",
            "aluno_responder",
            self.responder,
            ("GET", "POST"),
        )
        self.adicionar_rota("/aluno/resultados", "aluno_resultados", self.resultados)

    def painel(self):
        """Mostra o painel com a saudação ao aluno."""
        return self.renderizar("aluno/painel.html", aluno=self.usuario)

    def questoes(self):
        """Lista as questões, aplicando os filtros de disciplina, banca e tipo."""
        filtros = {
            "disciplina": request.args.get("disciplina", ""),
            "banca": request.args.get("banca", ""),
            "tipo": request.args.get("tipo", ""),
        }

        questoes = Questao.buscar(filtros["disciplina"], filtros["banca"], filtros["tipo"])

        return self.renderizar(
            "aluno/questoes.html",
            questoes=questoes,
            filtros=filtros,
            disciplinas=Questao.listar_disciplinas(),
            bancas=Questao.listar_bancas(),
        )

    def responder(self, questao_id):
        """Mostra a questão e, no envio, registra a resposta e mostra o resultado."""
        questao = Questao.buscar_por_id(questao_id)
        if questao is None:
            return self.redirecionar("/aluno/questoes", "Questão não encontrada.", "erro")

        if request.method == "POST":
            try:
                resposta = Resposta.registrar(
                    self.usuario.id, questao, request.form.get("resposta", "")
                )
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                return self.renderizar("aluno/feedback.html", questao=questao, resposta=resposta)

        return self.renderizar("aluno/responder.html", questao=questao)

    def resultados(self):
        """Mostra o desempenho do aluno e o histórico de respostas."""
        return self.renderizar(
            "aluno/resultados.html",
            desempenho=Desempenho.do_aluno(self.usuario),
            respostas=Resposta.listar_por_aluno(self.usuario.id),
        )
