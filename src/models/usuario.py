import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from src import database


class Usuario:

    TIPO = None

    def __init__(self, nome, email, senha_hash, matricula=None, id=None):
        self.id = id
        self.nome = Usuario.validar_nome(nome)
        self.email = Usuario.validar_email(email)
        self.senha_hash = senha_hash
        self.matricula = matricula

    def __str__(self):
        return f"{self.nome} ({self.email})"

    @property
    def primeiro_nome(self):
        return self.nome.split()[0]

    @staticmethod
    def validar_nome(nome):
        nome = str(nome or "").strip()
        if nome == "":
            raise ValueError("Informe o nome.")
        return nome

    @staticmethod
    def validar_email(email):
        email = str(email or "").strip().lower()
        antes, arroba, depois = email.partition("@")
        if arroba == "" or antes == "" or depois == "":
            raise ValueError("Informe um e-mail válido.")
        return email

    @staticmethod
    def gerar_hash(senha):
        return generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def salvar(self):
        if self.TIPO is None:
            raise ValueError("Use Aluno ou Professor para salvar um usuário.")

        conexao = database.conectar()
        try:
            cursor = conexao.execute(
                "INSERT INTO usuario (nome, email, senha_hash, tipo, matricula) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.nome, self.email, self.senha_hash, self.TIPO, self.matricula),
            )
            conexao.commit()
        except sqlite3.IntegrityError:
            raise ValueError("E-mail já cadastrado.")
        finally:
            conexao.close()

        self.id = cursor.lastrowid

    @staticmethod
    def de_linha(linha):
        from src.models.aluno import Aluno
        from src.models.professor import Professor

        if linha["tipo"] == Professor.TIPO:
            classe = Professor
        else:
            classe = Aluno
        return classe(
            linha["nome"],
            linha["email"],
            linha["senha_hash"],
            linha["matricula"],
            linha["id"],
        )

    @classmethod
    def buscar_por_id(cls, usuario_id):
        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
        conexao.close()

        if linha is None:
            return None

        usuario = Usuario.de_linha(linha)
        if not isinstance(usuario, cls):
            return None
        return usuario

    @staticmethod
    def buscar_por_email(email):
        email = str(email or "").strip().lower()

        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM usuario WHERE email = ?", (email,)).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Usuario.de_linha(linha)

    @staticmethod
    def autenticar(email, senha):
        usuario = Usuario.buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            return None
        return usuario