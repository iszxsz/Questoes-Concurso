"""Desempenho de um aluno."""

from src.models.aproveitamento import Aproveitamento
from src.models.notas_redacao import NotasRedacao
from src.models.resposta import Resposta


class Desempenho:
    """Resume as respostas de um aluno: aproveitamento geral, por disciplina
    e média das redações.

    Tudo fica em atributos internos. De fora só dá para ler pelas
    propriedades e somar respostas com registrar().
    """

    def __init__(self, aluno):
        """Guarda o aluno, o aproveitamento geral, o dicionário por disciplina
        e as notas de redação."""
        # protegidos (um _ só) porque ResultadoSimulado herda e usa
        self._aluno = aluno
        self._geral = Aproveitamento("Geral")
        self._redacoes = NotasRedacao()
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

    @property
    def aluno(self):
        """Aluno dono do desempenho."""
        return self._aluno

    @property
    def geral(self):
        """Aproveitamento de todas as questões objetivas."""
        return self._geral

    @property
    def redacoes(self):
        """Notas das redações (média e pendentes)."""
        return self._redacoes

    def registrar(self, resposta):
        """Soma a resposta no lugar certo, conforme a situação dela.

        Redação não entra no percentual de acertos: corrigida soma na média
        das redações e pendente só é contada.
        """
        if resposta.pendente:
            self._redacoes.registrar_pendente()
        elif resposta.corrigida:
            self._redacoes.registrar(resposta.nota)
        else:
            self.__registrar_objetiva(resposta)

    def __registrar_objetiva(self, resposta):
        """Soma a resposta objetiva no geral e na disciplina da questão."""
        disciplina = resposta.questao().disciplina
        self._geral.registrar(resposta.acertou)
        self.__aproveitamento_da_disciplina(disciplina).registrar(resposta.acertou)

    def __aproveitamento_da_disciplina(self, disciplina):
        """Aproveitamento da disciplina, criado na primeira vez que aparece."""
        if disciplina not in self._disciplinas:
            self._disciplinas[disciplina] = Aproveitamento(disciplina)
        return self._disciplinas[disciplina]

    def por_disciplina(self):
        """Lista dos aproveitamentos por disciplina, em ordem alfabética."""
        lista = []
        for nome in sorted(self._disciplinas):
            lista.append(self._disciplinas[nome])
        return lista
