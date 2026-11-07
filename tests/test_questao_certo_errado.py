"""Testes da questão de certo ou errado."""

from src.models.questao import Questao
from src.models.questao_certo_errado import QuestaoCertoErrado
from tests.apoio import deve_recusar


def criar(gabarito="E"):
    return QuestaoCertoErrado("Afirmação", "Português", "Cebraspe", 2023, 1, gabarito)


def testar_gabarito_minusculo_aceito():
    assert criar("e").gabarito == "E"


def testar_tipo_e_nome():
    questao = criar()
    assert questao.TIPO == "certo_errado"
    assert questao.NOME_TIPO == "Certo ou errado"


def testar_e_uma_questao():
    assert isinstance(criar(), Questao)


def testar_gabarito_invalido_recusado():
    assert deve_recusar(criar, "A") == "O gabarito deve ser um destes: C, E."
    deve_recusar(criar, "")


def testar_opcoes_e_textos():
    questao = criar()
    assert questao.opcoes() == [("C", "Certo"), ("E", "Errado")]
    assert questao.texto_da_opcao("C") == "Certo"
    assert questao.texto_da_opcao("E") == "Errado"


def testar_correcao_e_validacao():
    questao = criar("E")
    assert questao.corrigir("E") == "correta"
    assert questao.corrigir(" c ") == "errada"
    assert questao.validar_resposta("e") == "E"
    deve_recusar(questao.validar_resposta, "A")
    deve_recusar(questao.validar_resposta, "")


if __name__ == "__main__":
    testar_gabarito_minusculo_aceito()
    testar_tipo_e_nome()
    testar_e_uma_questao()
    testar_gabarito_invalido_recusado()
    testar_opcoes_e_textos()
    testar_correcao_e_validacao()
    print("Todos os testes de questão de certo ou errado passaram.")
