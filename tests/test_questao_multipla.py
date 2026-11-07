"""Testes da questão de múltipla escolha e da classe abstrata Questao."""

from src.models.questao import Questao
from src.models.questao_multipla import QuestaoMultipla
from tests.apoio import deve_recusar

ALTERNATIVAS = ["excessão", "exceção", "excesão"]


def criar(alternativas=ALTERNATIVAS, gabarito="B", ano=2023, enunciado="Qual está certa?"):
    return QuestaoMultipla(enunciado, "Português", "FGV", ano, 1, alternativas, gabarito)


def testar_correcao_com_espacos_e_minusculas():
    questao = criar(gabarito=" b ")
    assert questao.gabarito == "B"
    assert questao.corrigir(" b ") == "correta"
    assert questao.corrigir("a") == "errada"


def testar_resposta_valida():
    questao = criar()
    assert questao.validar_resposta(" c ") == "C"


def testar_resposta_invalida():
    questao = criar()
    assert deve_recusar(questao.validar_resposta, "") == "Marque uma das opções."
    deve_recusar(questao.validar_resposta, "D")
    deve_recusar(questao.validar_resposta, "AB")


def testar_questao_invalida():
    mensagem = deve_recusar(criar, ["só uma"])
    assert mensagem == "A questão deve ter de 2 a 5 alternativas."

    mensagem = deve_recusar(criar, ["a", "", "c"])
    assert mensagem == "Preencha as alternativas em ordem, sem pular letras."

    mensagem = deve_recusar(criar, ALTERNATIVAS, "D")
    assert mensagem == "O gabarito deve ser um destes: A, B, C."

    deve_recusar(criar, ALTERNATIVAS, "")

    assert deve_recusar(criar, ALTERNATIVAS, "B", "abc") == "Informe um ano válido."
    assert deve_recusar(criar, ALTERNATIVAS, "B", 1500) == "Informe um ano válido."

    mensagem = deve_recusar(criar, ALTERNATIVAS, "B", 2023, "   ")
    assert mensagem == "Preencha enunciado, disciplina e banca."


def testar_alternativas_vazias_no_final_ignoradas():
    questao = criar(["a", "b", "c", "", ""])
    assert questao.alternativas == ["a", "b", "c"]


def testar_opcoes_e_textos():
    questao = criar()
    assert questao.opcoes() == [("A", "excessão"), ("B", "exceção"), ("C", "excesão")]
    assert questao.valores_validos == ["A", "B", "C"]
    assert questao.texto_da_opcao("B") == "exceção"
    assert str(questao) == "Português · FGV · 2023"


def testar_questao_nao_pode_ser_criada():
    try:
        Questao("Enunciado", "Português", "FGV", 2023, 1, "A")
    except TypeError:
        return
    raise AssertionError("Questao é abstrata e não deveria ser criada")


if __name__ == "__main__":
    testar_correcao_com_espacos_e_minusculas()
    testar_resposta_valida()
    testar_resposta_invalida()
    testar_questao_invalida()
    testar_alternativas_vazias_no_final_ignoradas()
    testar_opcoes_e_textos()
    testar_questao_nao_pode_ser_criada()
    print("Todos os testes de questão de múltipla escolha passaram.")
