from src.models.usuario import Usuario


class Professor(Usuario):

    TIPO = "professor"

    def __init__(self, nome, email, senha_hash, matricula, id=None):
       
        matricula = str(matricula or "").strip()
        if matricula == "":
            raise ValueError("Informe a matrícula.")
        super().__init__(nome, email, senha_hash, matricula, id)

    def __str__(self):
        return f"{self.nome} (matrícula {self.matricula})"
