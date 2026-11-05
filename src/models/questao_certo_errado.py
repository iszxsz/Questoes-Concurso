"""Questão de certo ou errado."""

from src.models.questao import Questao


class QuestaoCertoErrado(Questao):
    """Afirmação que o aluno julga como certa ou errada, no estilo Cebraspe."""

    TIPO = "certo_errado"
    NOME_TIPO = "Certo ou errado"
    OPCOES = (("C", "Certo"), ("E", "Errado"))

    def __init__(self, enunciado, disciplina, banca, ano, professor_id, gabarito, id=None):
        """Usa o construtor de Questao, que limpa e valida os dados."""
        super().__init__(enunciado, disciplina, banca, ano, professor_id, gabarito, id)

    def opcoes(self):
        """Pares (valor, texto) das duas opções: C (Certo) e E (Errado)."""
        return list(self.OPCOES)
