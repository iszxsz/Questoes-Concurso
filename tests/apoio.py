"""Funções de apoio usadas pelos testes."""

import os

from src import database
from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.questao_certo_errado import QuestaoCertoErrado
from src.models.questao_multipla import QuestaoMultipla
from src.models.usuario import Usuario

CAMINHO_BANCO_TESTE = "teste.db"
SENHA_TESTE = "123456"


def deve_recusar(funcao, *argumentos):
    """Chama a função e falha o teste se ela não lançar ValueError.

    Args:
        funcao: função ou classe que deve recusar os argumentos.
        *argumentos: valores passados para a função.

    Returns:
        str: mensagem do ValueError, para o teste poder conferir.
    """
    try:
        funcao(*argumentos)
    except ValueError as erro:
        return str(erro)
    raise AssertionError(f"{funcao.__name__} deveria lançar ValueError com {argumentos}")


def preparar_banco():
    """Troca o banco para teste.db, apaga o arquivo se existir e cria as tabelas."""
    database.CAMINHO_BANCO = CAMINHO_BANCO_TESTE
    if os.path.exists(CAMINHO_BANCO_TESTE):
        os.remove(CAMINHO_BANCO_TESTE)
    database.criar_tabelas()


def criar_cenario():
    """Prepara o banco e cria um professor, um aluno e uma questão de cada tipo.

    Returns:
        tuple: (aluno, multipla, certo_errado).
    """
    preparar_banco()

    professor = Professor(
        "Ana Souza", "professor@teste.com", Usuario.gerar_hash(SENHA_TESTE), "P0001"
    )
    professor.salvar()

    aluno = Aluno.cadastrar("Carlos Lima", "aluno@teste.com", SENHA_TESTE, SENHA_TESTE)

    multipla = QuestaoMultipla(
        "Qual palavra está escrita corretamente?",
        "Português",
        "FGV",
        2023,
        professor.id,
        ["excessão", "exceção", "excesão"],
        "B",
    )
    multipla.salvar()

    certo_errado = QuestaoCertoErrado(
        "Todo o poder emana do povo.",
        "Direito Constitucional",
        "Cebraspe",
        2022,
        professor.id,
        "C",
    )
    certo_errado.salvar()

    return aluno, multipla, certo_errado
