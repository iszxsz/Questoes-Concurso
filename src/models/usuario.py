"""Classe base dos usuários e acesso à tabela usuario."""

import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from src import database


class Usuario:
    """Base de Aluno e Professor, com o que é comum aos dois.

    Attributes:
        TIPO (str | None): valor gravado na coluna tipo; cada subclasse define o seu.
    """

    TIPO = None

    def __init__(self, nome, email, senha_hash, id=None):
        """Guarda os atributos, validando nome e e-mail."""
        self.id = id
        self.nome = Usuario.validar_nome(nome)
        self.email = Usuario.validar_email(email)
        self._senha_hash = senha_hash

    def __str__(self):
        """Representa o usuário pelo nome."""
        return self.nome

    @property
    def primeiro_nome(self):
        """Primeira palavra do nome."""
        return self.nome.split()[0]

    @staticmethod
    def validar_nome(nome):
        """Devolve o nome sem espaços nas pontas, ou lança ValueError se estiver vazio."""
        nome = str(nome or "").strip()
        if nome == "":
            raise ValueError("Informe o nome.")
        return nome

    @staticmethod
    def validar_email(email):
        """Devolve o e-mail limpo e em minúsculas, ou lança ValueError se for inválido."""
        email = str(email or "").strip().lower()
        antes, arroba, depois = email.partition("@")
        if arroba == "" or antes == "" or depois == "":
            raise ValueError("Informe um e-mail válido.")
        return email

    @staticmethod
    def gerar_hash(senha):
        """Gera o hash de uma senha para guardar no banco."""
        return generate_password_hash(senha)

    def verificar_senha(self, senha):
        """True se a senha informada confere com o hash guardado."""
        return check_password_hash(self._senha_hash, senha)

    def salvar(self):
        """Insere o usuário com o TIPO da subclasse e preenche o id.

        Raises:
            ValueError: se for chamado em Usuario ou se o e-mail já existir.
        """
        if self.TIPO is None:
            raise ValueError("Use Aluno ou Professor para salvar um usuário.")

        matricula = getattr(self, "matricula", None)

        conexao = database.conectar()
        try:
            cursor = conexao.execute(
                "INSERT INTO usuario (nome, email, senha_hash, tipo, matricula) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.nome, self.email, self._senha_hash, self.TIPO, matricula),
            )
            conexao.commit()
            self.id = cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("E-mail já cadastrado.")
        finally:
            conexao.close()

    @staticmethod
    def de_linha(linha):
        """Cria um Aluno ou um Professor conforme a coluna tipo da linha."""
        # import aqui dentro pra não dar importação circular
        from src.models.aluno import Aluno
        from src.models.professor import Professor

        if linha["tipo"] == Professor.TIPO:
            return Professor(
                linha["nome"],
                linha["email"],
                linha["senha_hash"],
                linha["matricula"],
                linha["id"],
            )
        return Aluno(linha["nome"], linha["email"], linha["senha_hash"], linha["id"])

    @classmethod
    def buscar_por_id(cls, usuario_id):
        """Busca um usuário pelo id, ou devolve None.

        Chamado por uma subclasse, como Aluno.buscar_por_id, só devolve
        o usuário se ele for daquele tipo.
        """
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
        """Busca um usuário pelo e-mail, ignorando espaços e maiúsculas, ou devolve None."""
        email = str(email or "").strip().lower()

        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM usuario WHERE email = ?", (email,)).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Usuario.de_linha(linha)

    @staticmethod
    def autenticar(email, senha):
        """Devolve o usuário se o e-mail existir e a senha conferir; senão None."""
        usuario = Usuario.buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            return None
        return usuario
