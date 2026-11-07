"""Testes do desempenho do aluno."""

from src.models.desempenho import Desempenho
from src.models.resposta import Resposta
from tests.apoio import criar_cenario


def testar_aluno_sem_respostas():
    aluno, multipla, certo_errado = criar_cenario()

    desempenho = Desempenho.do_aluno(aluno)
    assert desempenho.aluno is aluno
    assert desempenho.geral.total == 0
    assert desempenho.geral.acertos == 0
    assert desempenho.geral.percentual == 0.0
    assert desempenho.por_disciplina() == []


def testar_tres_respostas():
    aluno, multipla, certo_errado = criar_cenario()
    Resposta.registrar(aluno.id, multipla, "B")
    Resposta.registrar(aluno.id, multipla, "A")
    Resposta.registrar(aluno.id, certo_errado, "C")

    desempenho = Desempenho.do_aluno(aluno)
    assert desempenho.geral.total == 3
    assert desempenho.geral.acertos == 2
    assert desempenho.geral.percentual == 66.7

    disciplinas = desempenho.por_disciplina()
    assert len(disciplinas) == 2

    assert disciplinas[0].nome == "Direito Constitucional"
    assert disciplinas[0].total == 1
    assert disciplinas[0].percentual == 100.0

    assert disciplinas[1].nome == "Português"
    assert disciplinas[1].total == 2
    assert disciplinas[1].percentual == 50.0


if __name__ == "__main__":
    testar_aluno_sem_respostas()
    testar_tres_respostas()
    print("Todos os testes de desempenho passaram.")
