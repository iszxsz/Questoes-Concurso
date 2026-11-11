"""Questão de verdadeiro ou falso."""

from src.models.questao_objetiva import QuestaoObjetiva


class QuestaoVerdadeiroFalso(QuestaoObjetiva):
    """Afirmação que o aluno julga como verdadeira ou falsa."""

    TIPO = "verdadeiro_falso"
    NOME_TIPO = "Verdadeiro ou falso"
    OPCOES = (("V", "Verdadeiro"), ("F", "Falso"))

    def __init__(self, enunciado, disciplina, banca, ano, professor_id, gabarito, id=None):
        """Usa o construtor de Questao, que limpa e valida os dados."""
        super().__init__(enunciado, disciplina, banca, ano, professor_id, gabarito, id)

    def opcoes(self):
        """Pares (valor, texto) das duas opções: V (Verdadeiro) e F (Falso)."""
        return list(self.OPCOES)

    @classmethod
    def de_formulario(cls, dados, professor_id, id=None):
        """Cria a questão a partir dos campos do formulário."""
        return cls(
            dados.get("enunciado", ""),
            dados.get("disciplina", ""),
            dados.get("banca", ""),
            dados.get("ano", ""),
            professor_id,
            dados.get("gabarito", ""),
            id,
        )

    @classmethod
    def _montar_de_linha(cls, linha):
        """Cria a questão a partir de uma linha da tabela questao."""
        return cls(
            linha["enunciado"],
            linha["disciplina"],
            linha["banca"],
            linha["ano"],
            linha["professor_id"],
            linha["gabarito"],
            linha["id"],
        )
