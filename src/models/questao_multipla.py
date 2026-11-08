"""Questão de múltipla escolha."""

import json

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

    @classmethod
    def de_formulario(cls, dados, professor_id, id=None):
        """Cria a questão lendo as alternativas dos campos alternativa_a a alternativa_e."""
        alternativas = []
        for letra in cls.LETRAS:
            alternativas.append(dados.get("alternativa_" + letra.lower(), ""))

        return cls(
            dados.get("enunciado", ""),
            dados.get("disciplina", ""),
            dados.get("banca", ""),
            dados.get("ano", ""),
            professor_id,
            alternativas,
            dados.get("gabarito", ""),
            id,
        )

    def para_formulario(self):
        """Campos comuns mais um campo para cada alternativa."""
        dados = super().para_formulario()
        for letra, texto in self.opcoes():
            dados["alternativa_" + letra.lower()] = texto
        return dados

    def alternativas_em_texto(self):
        """Alternativas em JSON, como ficam gravadas no banco."""
        return json.dumps(self.alternativas, ensure_ascii=False)
