"""Recria o banco com dados de exemplo para teste."""

import json
import os

from werkzeug.security import generate_password_hash

from src import database

SENHA_PADRAO = "123456"

PROFESSOR = {
    "nome": "Ana Souza",
    "email": "professor@teste.com",
    "tipo": "professor",
    "matricula": "P0001",
}

ALUNO = {
    "nome": "Carlos Lima",
    "email": "aluno@teste.com",
    "tipo": "aluno",
    "matricula": None,
}

QUESTOES_MULTIPLA = [
    {
        "id": 1,
        "disciplina": "Português",
        "banca": "FGV",
        "ano": 2023,
        "enunciado": "Assinale a alternativa em que a palavra está escrita corretamente.",
        "alternativas": ["excessão", "exceção", "excesão", "eceção"],
        "gabarito": "B",
    },
    {
        "id": 2,
        "disciplina": "Português",
        "banca": "FCC",
        "ano": 2022,
        "enunciado": 'Na frase "Os alunos chegaram cedo", o sujeito é:',
        "alternativas": ["oculto", "indeterminado", "simples", "composto", "inexistente"],
        "gabarito": "C",
    },
    {
        "id": 3,
        "disciplina": "Matemática",
        "banca": "FGV",
        "ano": 2023,
        "enunciado": "Um produto custa R$ 200,00 e recebe desconto de 15%. Qual é o preço final?",
        "alternativas": ["R$ 170,00", "R$ 185,00", "R$ 175,00", "R$ 160,00"],
        "gabarito": "A",
    },
    {
        "id": 4,
        "disciplina": "Matemática",
        "banca": "Cebraspe",
        "ano": 2021,
        "enunciado": "Qual é o valor de 3² + 4²?",
        "alternativas": ["7", "14", "25", "49"],
        "gabarito": "C",
    },
    {
        "id": 5,
        "disciplina": "Direito Constitucional",
        "banca": "Cebraspe",
        "ano": 2022,
        "enunciado": (
            "Segundo a Constituição Federal de 1988, são Poderes da União, "
            "independentes e harmônicos entre si:"
        ),
        "alternativas": [
            "o Legislativo, o Executivo e o Judiciário",
            "o Executivo, o Legislativo e o Ministério Público",
            "o Legislativo, o Judiciário e o Tribunal de Contas",
            "o Executivo, o Judiciário e a Defensoria Pública",
        ],
        "gabarito": "A",
    },
    {
        "id": 6,
        "disciplina": "Direito Constitucional",
        "banca": "FCC",
        "ano": 2023,
        "enunciado": "De acordo com a Constituição Federal de 1988, a Capital Federal é:",
        "alternativas": ["Rio de Janeiro", "São Paulo", "Brasília", "Goiânia"],
        "gabarito": "C",
    },
]


def apagar_banco():
    """Remove o arquivo do banco, se ele existir."""
    if os.path.exists(database.CAMINHO_BANCO):
        os.remove(database.CAMINHO_BANCO)


def inserir_usuario(conexao, usuario):
    """Insere um usuário com a senha padrão já transformada em hash.

    Args:
        conexao (sqlite3.Connection): conexão aberta com o banco.
        usuario (dict): nome, email, tipo e matricula do usuário.

    Returns:
        int: id gerado para o usuário.
    """
    cursor = conexao.execute(
        "INSERT INTO usuario (nome, email, senha_hash, tipo, matricula) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            usuario["nome"],
            usuario["email"],
            generate_password_hash(SENHA_PADRAO),
            usuario["tipo"],
            usuario["matricula"],
        ),
    )
    return cursor.lastrowid


def inserir_questoes_multipla(conexao, professor_id):
    """Insere as questões de múltipla escolha de exemplo.

    Args:
        conexao (sqlite3.Connection): conexão aberta com o banco.
        professor_id (int): id do professor que fica como autor das questões.
    """
    for questao in QUESTOES_MULTIPLA:
        conexao.execute(
            "INSERT INTO questao (id, tipo, enunciado, disciplina, banca, ano, "
            "professor_id, alternativas, gabarito) "
            "VALUES (?, 'multipla', ?, ?, ?, ?, ?, ?, ?)",
            (
                questao["id"],
                questao["enunciado"],
                questao["disciplina"],
                questao["banca"],
                questao["ano"],
                professor_id,
                json.dumps(questao["alternativas"], ensure_ascii=False),
                questao["gabarito"],
            ),
        )


def main():
    """Apaga o banco, cria as tabelas de novo e insere os dados de teste."""
    apagar_banco()
    database.criar_tabelas()

    conexao = database.conectar()

    professor_id = inserir_usuario(conexao, PROFESSOR)
    inserir_usuario(conexao, ALUNO)

    inserir_questoes_multipla(conexao, professor_id)

    conexao.commit()
    conexao.close()
    print("Banco recriado com dados de teste.")


if __name__ == "__main__":
    main()
