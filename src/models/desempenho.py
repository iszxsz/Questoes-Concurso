"""Desempenho de um aluno."""

from src.models.aproveitamento import Aproveitamento
from src.models.resposta import Resposta


class Desempenho:
    """Resume as respostas de um aluno: aproveitamento geral e por disciplina."""

    def __init__(self, aluno):
        """Guarda o aluno, o aproveitamento geral e o dicionário por disciplina."""
        self.aluno = aluno
        self.geral = Aproveitamento("Geral")
        self._disciplinas = {}

    def __str__(self):
        """Resumo com o nome do aluno e o aproveitamento geral."""
        return f"Desempenho de {self.aluno.nome}: {self.geral}"

    @classmethod
    def do_aluno(cls, aluno):
        """Cria o desempenho e registra todas as respostas do aluno."""
        desempenho = cls(aluno)
        for resposta in Resposta.listar_por_aluno(aluno.id):
            desempenho.registrar(resposta)
        return desempenho

    def registrar(self, resposta):
        """Soma a resposta ao geral e ao aproveitamento da disciplina da questão."""
        disciplina = resposta.questao().disciplina
        if disciplina not in self._disciplinas:
            self._disciplinas[disciplina] = Aproveitamento(disciplina)

        self.geral.registrar(resposta.acertou)
        self._disciplinas[disciplina].registrar(resposta.acertou)

    def por_disciplina(self):
        """Lista dos aproveitamentos por disciplina, em ordem alfabética."""
        lista = []
        for nome in sorted(self._disciplinas):
            lista.append(self._disciplinas[nome])
        return lista
