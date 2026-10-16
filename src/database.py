"""Conexão com o banco SQLite e criação das tabelas."""

import sqlite3

CAMINHO_BANCO = "questoes.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('aluno', 'professor')),
    matricula TEXT
);

CREATE TABLE IF NOT EXISTS questao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('multipla', 'certo_errado')),
    enunciado TEXT NOT NULL,
    disciplina TEXT NOT NULL,
    banca TEXT NOT NULL,
    ano INTEGER NOT NULL,
    professor_id INTEGER NOT NULL REFERENCES usuario (id),
    alternativas TEXT,
    gabarito TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resposta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL REFERENCES usuario (id),
    questao_id INTEGER NOT NULL REFERENCES questao (id),
    resposta TEXT NOT NULL,
    situacao TEXT NOT NULL CHECK (situacao IN ('correta', 'errada')),
    respondida_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def conectar():
    """Abre uma conexão com o banco de dados.

    Lê CAMINHO_BANCO a cada chamada, assim os testes conseguem trocar o
    arquivo do banco antes de conectar.

    Returns:
        sqlite3.Connection: conexão que permite acessar as colunas pelo nome
        e com as chaves estrangeiras ativadas.
    """
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    """Cria as tabelas do sistema caso ainda não existam."""
    conexao = conectar()
    conexao.executescript(ESQUEMA)
    conexao.close()


def listar_tabelas():
    """Busca os nomes das tabelas que existem no banco.

    Returns:
        list[str]: nomes das tabelas em ordem alfabética.
    """
    conexao = conectar()
    linhas = conexao.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    conexao.close()

    nomes = []
    for linha in linhas:
        nomes.append(linha["name"])
    return nomes


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas:", listar_tabelas())
