from src import database
from src.models.usuario import Usuario


class Aluno(Usuario):

    TIPO = "aluno"

    @classmethod
    def cadastrar(cls, nome, email, senha, confirmar_senha):
        nome = Usuario.validar_nome(nome)
        email = Usuario.validar_email(email)

        if Usuario.buscar_por_email(email) is not None:
            raise ValueError("E-mail já cadastrado.")

        senha = senha or ""
        if len(senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        if senha != confirmar_senha:
            raise ValueError("As senhas não conferem.")

        aluno = cls(nome, email, Usuario.gerar_hash(senha))
        aluno.salvar()
        return aluno

    @classmethod
    def listar(cls):
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT * FROM usuario WHERE tipo = ? ORDER BY nome", (cls.TIPO,)
        ).fetchall()
        conexao.close()

        alunos = []
        for linha in linhas:
            alunos.append(Usuario.de_linha(linha))
        return alunos