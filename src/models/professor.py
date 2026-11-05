"""Professor: usuário que cadastra questões e acompanha os alunos."""

from src.models.usuario import Usuario


class Professor(Usuario):
    """Usuário do tipo professor, que além dos dados comuns tem matrícula."""

    TIPO = "professor"

    def __init__(self, nome, email, senha_hash, matricula, id=None):
        """Chama o construtor de Usuario e guarda a matrícula, que é obrigatória."""
        super().__init__(nome, email, senha_hash, id)

        self.matricula = str(matricula or "").strip()
        if self.matricula == "":
            raise ValueError("Informe a matrícula.")

    def __str__(self):
        """Representa o professor pelo nome e pela matrícula."""
        return f"{self.nome} (matrícula {self.matricula})"
