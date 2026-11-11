"""Testes da questão de verdadeiro ou falso."""

from src.models.questao import Questao
from src.models.questao_verdadeiro_falso import QuestaoVerdadeiroFalso
from tests.apoio import deve_recusar


def criar(gabarito="F"):
    return QuestaoVerdadeiroFalso("Afirmação", "Português", "Cebraspe", 2023, 1, gabarito)


def testar_gabarito_minusculo_aceito():
    assert criar("f").gabarito == "F"


def testar_tipo_e_nome():
    questao = criar()
    assert questao.TIPO == "verdadeiro_falso"
    assert questao.NOME_TIPO == "Verdadeiro ou falso"


def testar_e_uma_questao():
    assert isinstance(criar(), Questao)


def testar_gabarito_invalido_recusado():
    assert deve_recusar(criar, "A") == "O gabarito deve ser um destes: V, F."
    deve_recusar(criar, "")


def testar_opcoes_e_textos():
    questao = criar()
    assert questao.opcoes() == [("V", "Verdadeiro"), ("F", "Falso")]
    assert questao.texto_da_opcao("V") == "Verdadeiro"
    assert questao.texto_da_opcao("F") == "Falso"


def testar_correcao_e_validacao():
    questao = criar("F")
    assert questao.corrigir("F") == "correta"
    assert questao.corrigir(" v ") == "errada"
    assert questao.validar_resposta("f") == "F"
    deve_recusar(questao.validar_resposta, "A")
    deve_recusar(questao.validar_resposta, "")


if __name__ == "__main__":
    testar_gabarito_minusculo_aceito()
    testar_tipo_e_nome()
    testar_e_uma_questao()
    testar_gabarito_invalido_recusado()
    testar_opcoes_e_textos()
    testar_correcao_e_validacao()
    print("Todos os testes de questão de verdadeiro ou falso passaram.")
