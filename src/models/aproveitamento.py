"""Contagem de acertos de um conjunto de questões."""


class Aproveitamento:
    """Guarda quantas questões foram respondidas e quantas foram acertadas."""

    def __init__(self, nome):
        """Guarda o nome e começa total e acertos em zero."""
        self.nome = nome
        self.total = 0
        self.acertos = 0

    def __str__(self):
        """Resumo no formato "nome: acertos de total (percentual%)"."""
        return f"{self.nome}: {self.acertos} de {self.total} ({self.percentual}%)"

    def registrar(self, acertou):
        """Conta uma questão respondida e, se acertou for verdadeiro, um acerto."""
        self.total += 1
        if acertou:
            self.acertos += 1

    @property
    def erros(self):
        """Questões respondidas menos acertos."""
        return self.total - self.acertos

    @property
    def percentual(self):
        """Acertos sobre total vezes 100, com uma casa decimal; 0.0 sem respostas."""
        if self.total == 0:
            return 0.0
        return round(self.acertos / self.total * 100, 1)
