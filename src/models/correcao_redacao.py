"""Correção de uma redação feita pelo professor."""

import json

from src.models.redacao import Redacao


class CorrecaoRedacao:
    """Notas das cinco competências e o comentário do professor.

    Depois de criada a correção não muda: as notas e o comentário ficam em
    atributos internos e só podem ser lidos pelas propriedades. A nota final
    não é guardada, é sempre a soma das competências.

    Attributes:
        NIVEIS (tuple): notas aceitas em cada competência, como no ENEM.
    """

    NIVEIS = (0, 40, 80, 120, 160, 200)

    def __init__(self, competencias, comentario):
        """Valida as notas e o comentário.

        Args:
            competencias (list): uma nota para cada competência, na ordem.
            comentario (str): comentário do professor para o aluno.

        Raises:
            ValueError: se faltar nota, alguma nota não for um dos NIVEIS ou
                o comentário estiver vazio.
        """
        if len(competencias) != len(Redacao.COMPETENCIAS):
            raise ValueError("Dê nota às cinco competências.")

        notas = []
        for nota in competencias:
            notas.append(self.__validar_nota(nota))
        # tupla pra ninguém conseguir trocar uma nota depois
        self.__competencias = tuple(notas)
        self.__comentario = self.__validar_comentario(comentario)

    def __str__(self):
        """Nota final no formato "nota de 1000"."""
        return f"{self.nota} de {self.nota_maxima()}"

    def __validar_nota(self, nota):
        """Devolve a nota como inteiro, ou lança ValueError se não for um dos níveis."""
        try:
            nota = int(nota)
        except (TypeError, ValueError):
            raise ValueError("Dê nota às cinco competências.")
        if nota not in self.NIVEIS:
            raise ValueError(f"Cada competência vale {self.niveis_em_texto()}.")
        return nota

    def __validar_comentario(self, comentario):
        """Devolve o comentário limpo, ou lança ValueError se estiver vazio."""
        comentario = str(comentario or "").strip()
        if comentario == "":
            raise ValueError("Escreva um comentário para o aluno.")
        return comentario

    @property
    def competencias(self):
        """Notas das competências, na ordem do ENEM (só leitura)."""
        return self.__competencias

    @property
    def comentario(self):
        """Comentário do professor (só leitura)."""
        return self.__comentario

    @property
    def nota(self):
        """Soma das notas das competências, de 0 a 1000."""
        return sum(self.__competencias)

    @classmethod
    def nota_maxima(cls):
        """Maior nota possível: nível máximo vezes o número de competências."""
        return max(cls.NIVEIS) * len(Redacao.COMPETENCIAS)

    @classmethod
    def niveis_em_texto(cls):
        """Níveis no formato "0, 40, 80, 120, 160 ou 200"."""
        textos = []
        for nivel in cls.NIVEIS:
            textos.append(str(nivel))
        return ", ".join(textos[:-1]) + " ou " + textos[-1]

    def itens(self):
        """Pares (nome da competência, nota), na ordem do ENEM."""
        itens = []
        for posicao, nome in enumerate(Redacao.COMPETENCIAS):
            itens.append((nome, self.__competencias[posicao]))
        return itens

    def competencias_em_texto(self):
        """Notas em JSON, como ficam gravadas no banco."""
        return json.dumps(list(self.__competencias))

    @classmethod
    def de_formulario(cls, dados):
        """Cria a correção lendo os campos competencia_1 a competencia_5 e comentario."""
        competencias = []
        for numero in range(1, len(Redacao.COMPETENCIAS) + 1):
            competencias.append(dados.get(f"competencia_{numero}", ""))
        return cls(competencias, dados.get("comentario", ""))

    @classmethod
    def de_texto(cls, competencias, comentario):
        """Cria a correção a partir das colunas competencias (JSON) e comentario."""
        return cls(json.loads(competencias), comentario)
