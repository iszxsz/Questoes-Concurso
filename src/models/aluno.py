from src import database
from src.models.usuario import Usuario


class Aluno(Usuario):

    TIPO = "aluno"
    NOME_TIPO = "Aluno"

    @classmethod
    def cadastrar(cls, nome, email, senha, confirmar_senha):
        return super().cadastrar(nome, email, senha, confirmar_senha)

    @staticmethod
    def buscar_por_id(usuario_id):
        usuario = Usuario.buscar_por_id(usuario_id)
        if isinstance(usuario, Aluno):
            return usuario
        return None

    @staticmethod
    def listar():
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT * FROM usuario WHERE tipo = ? ORDER BY nome COLLATE NOCASE, id",
            (Aluno.TIPO,),
        ).fetchall()
        conexao.close()

        alunos = []
        for linha in linhas:
            alunos.append(Usuario.de_linha(linha))
        return alunos