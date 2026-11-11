"""Funções de apoio usadas pelos testes."""

import os

from src import database
from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.questao_verdadeiro_falso import QuestaoVerdadeiroFalso
from src.models.questao_multipla import QuestaoMultipla
from src.models.redacao import Redacao
from src.models.usuario import Usuario

CAMINHO_BANCO_TESTE = "teste.db"
SENHA_TESTE = "123456"

# uns 300 e poucos caracteres, passa do mínimo da redação
TEXTO_REDACAO = "A leitura forma cidadãos mais críticos e participativos. " * 5 + "Fim do texto do aluno."


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
        tuple: (aluno, multipla, verdadeiro_falso).
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

    verdadeiro_falso = QuestaoVerdadeiroFalso(
        "Todo o poder emana do povo.",
        "Direito Constitucional",
        "Cebraspe",
        2022,
        professor.id,
        "V",
    )
    verdadeiro_falso.salvar()

    return aluno, multipla, verdadeiro_falso


def criar_redacao(professor_id):
    """Cria e salva uma redação no estilo ENEM.

    Args:
        professor_id (int): id do professor autor.

    Returns:
        Redacao: a redação já com id.
    """
    redacao = Redacao(
        "Desafios para a formação de leitores no Brasil",
        "Redação",
        "INEP",
        2023,
        professor_id,
    )
    redacao.salvar()
    return redacao
