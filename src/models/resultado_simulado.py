"""Resultado de um aluno em um simulado."""

from src.models.desempenho import Desempenho
from src.models.resposta import Resposta


class ResultadoSimulado(Desempenho):
    """Desempenho de um aluno contando só as respostas de um simulado.

    Herda de Desempenho o aproveitamento geral e por disciplina, e
    acrescenta o simulado e a lista de respostas dadas nele.
    """

    def __init__(self, aluno, simulado):
        """Começa o desempenho do aluno e guarda o simulado."""
        super().__init__(aluno)
        self.__simulado = simulado
        self.__respostas = []

    def __str__(self):
        """Resumo com o aluno, o simulado e o aproveitamento."""
        return f"{self.aluno.nome} em {self.simulado.titulo}: {self.geral}"

    @classmethod
    def do_simulado(cls, aluno, simulado):
        """Cria o resultado e registra as respostas do aluno nesse simulado."""
        resultado = cls(aluno, simulado)
        for resposta in Resposta.listar_por_simulado(simulado.id, aluno.id):
            resultado.registrar(resposta)
        return resultado

    def registrar(self, resposta):
        """Soma a resposta ao desempenho e guarda na lista de respostas."""
        super().registrar(resposta)
        self.__respostas.append(resposta)

    @property
    def simulado(self):
        """Simulado deste resultado."""
        return self.__simulado

    @property
    def respostas(self):
        """Cópia da lista de respostas, pra quem usa não mexer na original."""
        return list(self.__respostas)

    @property
    def feito(self):
        """True se o aluno já fez o simulado."""
        # não dá pra usar geral.total: num simulado só de redação ele fica 0
        return len(self.__respostas) > 0

    def itens(self):
        """Pares (questão, resposta) na ordem do simulado; resposta None se faltar."""
        resposta_da_questao = self.__respostas_por_questao()

        itens = []
        for questao in self.__simulado.questoes:
            itens.append((questao, resposta_da_questao.get(questao.id)))
        return itens

    def __respostas_por_questao(self):
        """Dicionário com a resposta dada em cada questão, pelo id da questão."""
        respostas = {}
        for resposta in self.__respostas:
            respostas[resposta.questao_id] = resposta
        return respostas
