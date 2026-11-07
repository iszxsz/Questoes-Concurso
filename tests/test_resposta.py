"""Testes do registro e da listagem de respostas."""

from src.models.questao_certo_errado import QuestaoCertoErrado
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta
from tests.apoio import criar_cenario, deve_recusar


def testar_registro_correto():
    aluno, multipla, certo_errado = criar_cenario()

    resposta = Resposta.registrar(aluno.id, multipla, " b ")
    assert resposta.id is not None
    assert resposta.resposta == "B"
    assert resposta.acertou
    assert resposta.rotulo_situacao == "Correta"
    assert resposta.respondida_em is not None
    assert len(resposta.data_formatada) == len("dd/mm/aaaa hh:mm")


def testar_registro_errado():
    aluno, multipla, certo_errado = criar_cenario()

    resposta = Resposta.registrar(aluno.id, certo_errado, "e")
    assert not resposta.acertou
    assert resposta.rotulo_situacao == "Errada"


def testar_resposta_invalida_nao_salva():
    aluno, multipla, certo_errado = criar_cenario()

    deve_recusar(Resposta.registrar, aluno.id, multipla, "")
    deve_recusar(Resposta.registrar, aluno.id, multipla, "D")
    deve_recusar(Resposta.registrar, aluno.id, certo_errado, "A")
    assert Resposta.listar_por_aluno(aluno.id) == []


def testar_listagem_da_mais_recente():
    aluno, multipla, certo_errado = criar_cenario()

    primeira = Resposta.registrar(aluno.id, multipla, "A")
    segunda = Resposta.registrar(aluno.id, certo_errado, "C")

    respostas = Resposta.listar_por_aluno(aluno.id)
    assert len(respostas) == 2
    assert respostas[0].id == segunda.id
    assert respostas[1].id == primeira.id
    assert isinstance(respostas[0].questao(), QuestaoCertoErrado)
    assert isinstance(respostas[1].questao(), QuestaoMultipla)


def testar_aluno_sem_respostas():
    aluno, multipla, certo_errado = criar_cenario()
    assert Resposta.listar_por_aluno(aluno.id) == []


if __name__ == "__main__":
    testar_registro_correto()
    testar_registro_errado()
    testar_resposta_invalida_nao_salva()
    testar_listagem_da_mais_recente()
    testar_aluno_sem_respostas()
    print("Todos os testes de resposta passaram.")
