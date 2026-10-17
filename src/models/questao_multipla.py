"""Questão de múltipla escolha."""

from src.models.questao import Questao


class QuestaoMultipla(Questao):
    """Questão com alternativas identificadas pelas letras A a E."""

    TIPO = "multipla"
    NOME_TIPO = "Múltipla escolha"
    LETRAS = "ABCDE"

    def __init__(self, enunciado, disciplina, banca, ano, professor_id, alternativas, gabarito, id=None):
        """Limpa e valida as alternativas antes de chamar a base."""
        limpas = []
        for texto in alternativas:
            limpas.append(texto.strip())

        while len(limpas) > 0 and limpas[-1] == "":
            limpas.pop()

        if "" in limpas:
            raise ValueError("Preencha as alternativas em ordem, sem pular letras.")
        if len(limpas) < 2 or len(limpas) > len(self.LETRAS):
            raise ValueError("A questão deve ter de 2 a 5 alternativas.")

        self.alternativas = limpas
        super().__init__(enunciado, disciplina, banca, ano, professor_id, gabarito, id)

    def opcoes(self):
        """Pares (letra, texto) de cada alternativa."""
        pares = []
        for posicao, texto in enumerate(self.alternativas):
            pares.append((self.LETRAS[posicao], texto))
        return pares
