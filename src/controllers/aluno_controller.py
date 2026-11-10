"""Páginas do aluno."""

from flask import request

from src.controllers.controller import Controller
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.resposta import Resposta
from src.models.simulado import Simulado


class AlunoController(Controller):
    """Questões e resultados do aluno."""

    TIPO_USUARIO = "aluno"

    def _registrar_rotas(self):
        """Registra as rotas do aluno."""
        self._adicionar_rota("/aluno", "aluno_painel", self.painel)
        self._adicionar_rota("/aluno/questoes", "aluno_questoes", self.questoes)
        self._adicionar_rota(
            "/aluno/questoes/<int:questao_id>",
            "aluno_responder",
            self.responder,
            ("GET", "POST"),
        )
        self._adicionar_rota("/aluno/resultados", "aluno_resultados", self.resultados)
        self._adicionar_rota("/aluno/simulados", "aluno_simulados", self.simulados)
        self._adicionar_rota(
            "/aluno/simulados/<int:simulado_id>",
            "aluno_fazer_simulado",
            self.fazer_simulado,
            ("GET", "POST"),
        )
        self._adicionar_rota(
            "/aluno/simulados/<int:simulado_id>/resultado",
            "aluno_resultado_simulado",
            self.resultado_simulado,
        )
        self._adicionar_rota(
            "/aluno/redacoes/<int:resposta_id>", "aluno_redacao", self.redacao
        )

    def painel(self):
        """Mostra o painel com a saudação ao aluno."""
        return self._renderizar("aluno/painel.html", aluno=self.usuario)

    def questoes(self):
        """Lista as questões, aplicando os filtros de disciplina, banca e tipo."""
        filtros = {
            "disciplina": request.args.get("disciplina", ""),
            "banca": request.args.get("banca", ""),
            "tipo": request.args.get("tipo", ""),
        }

        questoes = Questao.buscar(filtros["disciplina"], filtros["banca"], filtros["tipo"])

        return self._renderizar(
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
            return self._redirecionar("/aluno/questoes", "Questão não encontrada.", "erro")

        if request.method == "POST":
            try:
                resposta = Resposta.registrar(
                    self.usuario.id, questao, request.form.get("resposta", "")
                )
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._renderizar("aluno/feedback.html", questao=questao, resposta=resposta)

        return self._renderizar("aluno/responder.html", questao=questao)

    def resultados(self):
        """Mostra o desempenho do aluno e o histórico de respostas."""
        return self._renderizar(
            "aluno/resultados.html",
            desempenho=Desempenho.do_aluno(self.usuario),
            respostas=Resposta.listar_por_aluno(self.usuario.id),
        )

    def simulados(self):
        """Lista os simulados com o resultado do aluno em cada um."""
        resultados = []
        for simulado in Simulado.listar_todos():
            resultados.append(simulado.resultado_de(self.usuario))

        return self._renderizar("aluno/simulados.html", resultados=resultados)

    def fazer_simulado(self, simulado_id):
        """Mostra todas as questões do simulado e envia as respostas de uma vez."""
        simulado = Simulado.buscar_por_id(simulado_id)
        if simulado is None:
            return self._redirecionar("/aluno/simulados", "Simulado não encontrado.", "erro")

        if simulado.ja_feito_por(self.usuario):
            return self._redirecionar(
                f"/aluno/simulados/{simulado.id}/resultado", "Você já fez este simulado.", "erro"
            )

        marcadas = {}

        if request.method == "POST":
            for questao in simulado.questoes:
                marcadas[questao.id] = request.form.get(f"questao_{questao.id}", "")
            try:
                simulado.responder(self.usuario, marcadas)
            except ValueError as erro:
                self._avisar_erro(str(erro))
            else:
                return self._redirecionar(
                    f"/aluno/simulados/{simulado.id}/resultado", "Simulado enviado."
                )

        return self._renderizar("aluno/fazer_simulado.html", simulado=simulado, marcadas=marcadas)

    def resultado_simulado(self, simulado_id):
        """Mostra o resultado do aluno no simulado, questão por questão."""
        simulado = Simulado.buscar_por_id(simulado_id)
        if simulado is None:
            return self._redirecionar("/aluno/simulados", "Simulado não encontrado.", "erro")

        resultado = simulado.resultado_de(self.usuario)
        if not resultado.feito:
            return self._redirecionar(f"/aluno/simulados/{simulado.id}")

        return self._renderizar("aluno/resultado_simulado.html", resultado=resultado)

    def redacao(self, resposta_id):
        """Mostra a redação enviada pelo aluno e, se já corrigida, a nota e o comentário."""
        resposta = Resposta.buscar_por_id(resposta_id)
        # o aluno só pode ver a própria redação
        if resposta is None or resposta.aluno_id != self.usuario.id:
            return self._redirecionar("/aluno/resultados", "Redação não encontrada.", "erro")
        if not (resposta.pendente or resposta.corrigida):
            return self._redirecionar("/aluno/resultados", "Redação não encontrada.", "erro")

        return self._renderizar(
            "aluno/redacao.html", resposta=resposta, questao=resposta.questao()
        )
