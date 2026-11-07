"""Testes da contagem de aproveitamento."""

from src.models.aproveitamento import Aproveitamento


def testar_comeca_zerado():
    aproveitamento = Aproveitamento("Português")
    assert aproveitamento.nome == "Português"
    assert aproveitamento.total == 0
    assert aproveitamento.acertos == 0
    assert aproveitamento.erros == 0
    assert aproveitamento.percentual == 0.0


def testar_acertos_e_erros():
    aproveitamento = Aproveitamento("Português")
    aproveitamento.registrar(True)
    aproveitamento.registrar(False)
    aproveitamento.registrar(True)

    assert aproveitamento.total == 3
    assert aproveitamento.acertos == 2
    assert aproveitamento.erros == 1
    assert aproveitamento.percentual == 66.7


def testar_tudo_certo():
    aproveitamento = Aproveitamento("Matemática")
    aproveitamento.registrar(True)
    aproveitamento.registrar(True)
    assert aproveitamento.percentual == 100.0


if __name__ == "__main__":
    testar_comeca_zerado()
    testar_acertos_e_erros()
    testar_tudo_certo()
    print("Todos os testes de aproveitamento passaram.")
