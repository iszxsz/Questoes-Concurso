"""Questão de certo ou errado."""

from src.models.questao import Questao


class QuestaoCertoErrado(Questao):
    """Afirmação que o aluno julga como certa ou errada, no estilo das provas do Cebraspe."""
