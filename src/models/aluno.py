"""Aluno: usuário que se cadastra sozinho e responde questões."""

from src import database
from src.models.usuario import Usuario


class Aluno(Usuario):
    """Usuário do tipo aluno.

    Attributes:
        TAMANHO_MINIMO_SENHA (int): menor tamanho de senha aceito no cadastro.
    """

    TIPO = "aluno"
    TAMANHO_MINIMO_SENHA = 6

    @classmethod
    def validar_senha(cls, senha, confirmar_senha):
        """Devolve a senha, ou lança ValueError se for curta ou diferente da confirmação."""
        senha = senha or ""
        if len(senha) < cls.TAMANHO_MINIMO_SENHA:
            raise ValueError(
                f"A senha deve ter pelo menos {cls.TAMANHO_MINIMO_SENHA} caracteres."
            )
        if senha != confirmar_senha:
            raise ValueError("As senhas não conferem.")
        return senha

    @classmethod
    def cadastrar(cls, nome, email, senha, confirmar_senha):
        """Valida os dados, cria e salva um novo aluno e devolve o objeto.

        Raises:
            ValueError: com a mensagem da primeira regra que falhar.
        """
        nome = cls.validar_nome(nome)
        email = cls.validar_email(email)
        senha = cls.validar_senha(senha, confirmar_senha)

        aluno = cls(nome, email, cls.gerar_hash(senha))
        aluno.salvar()
        return aluno

    @staticmethod
    def listar_todos():
        """Devolve todos os alunos em ordem de nome."""
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT * FROM usuario WHERE tipo = ? ORDER BY nome", (Aluno.TIPO,)
        ).fetchall()
        conexao.close()

        alunos = []
        for linha in linhas:
            alunos.append(Usuario.de_linha(linha))
        return alunos
