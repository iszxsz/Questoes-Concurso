"""Contagem de acertos de um conjunto de questões."""


class Aproveitamento:
    """Guarda quantas questões foram respondidas e quantas foram acertadas.

    Os contadores são internos: só mudam por registrar() e são lidos
    pelas propriedades total e acertos.
    """

    def __init__(self, nome):
        """Guarda o nome e começa total e acertos em zero."""
        self.__nome = nome
        self.__total = 0
        self.__acertos = 0

    def __str__(self):
        """Resumo no formato "nome: acertos de total (percentual%)"."""
        return f"{self.nome}: {self.acertos} de {self.total} ({self.percentual}%)"

    def registrar(self, acertou):
        """Conta uma questão respondida e, se acertou for verdadeiro, um acerto."""
        self.__total += 1
        if acertou:
            self.__acertos += 1

    @property
    def nome(self):
        """Nome do aproveitamento: "Geral" ou a disciplina."""
        return self.__nome

    @property
    def total(self):
        """Questões respondidas."""
        return self.__total

    @property
    def acertos(self):
        """Questões acertadas."""
        return self.__acertos

    @property
    def erros(self):
        """Questões respondidas menos acertos."""
        return self.__total - self.__acertos

    @property
    def percentual(self):
        """Acertos sobre total vezes 100, com uma casa decimal; 0.0 sem respostas."""
        if self.__total == 0:
            return 0.0
        return round(self.__acertos / self.__total * 100, 1)
