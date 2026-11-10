"""Redação no modelo do ENEM."""

from src.models.questao import Questao


class Redacao(Questao):
    """Proposta de redação que o aluno responde com um texto.

    Não tem opções nem gabarito: o enunciado é o tema e a correção é feita
    pelo professor, nas cinco competências do ENEM. Por isso corrigir()
    sempre devolve "pendente".

    Attributes:
        COMPETENCIAS (tuple): nome de cada uma das cinco competências.
        MINIMO_CARACTERES (int): menor tamanho de texto aceito.
    """

    TIPO = "redacao"
    NOME_TIPO = "Redação"
    CORRECAO_AUTOMATICA = False
    MINIMO_CARACTERES = 300
    COMPETENCIAS = (
        "Domínio da modalidade escrita formal da língua portuguesa",
        "Compreensão da proposta e desenvolvimento do tema dentro do texto dissertativo-argumentativo",
        "Seleção, organização e interpretação de informações e argumentos",
        "Conhecimento dos mecanismos linguísticos necessários para a argumentação",
        "Proposta de intervenção que respeite os direitos humanos",
    )

    def validar_resposta(self, resposta):
        """Devolve o texto sem espaços nas pontas, ou lança ValueError se for curto."""
        texto = str(resposta or "").strip()
        if len(texto) < self.MINIMO_CARACTERES:
            raise ValueError(
                f"A redação deve ter pelo menos {self.MINIMO_CARACTERES} caracteres."
            )
        return texto

    def corrigir(self, resposta):
        """Só valida o texto: quem corrige a redação é o professor."""
        self.validar_resposta(resposta)
        return "pendente"

    @classmethod
    def de_formulario(cls, dados, professor_id, id=None):
        """Cria a redação a partir dos campos do formulário."""
        return cls(
            dados.get("enunciado", ""),
            dados.get("disciplina", ""),
            dados.get("banca", ""),
            dados.get("ano", ""),
            professor_id,
            id,
        )

    @classmethod
    def _montar_de_linha(cls, linha):
        """Cria a redação a partir de uma linha da tabela questao."""
        return cls(
            linha["enunciado"],
            linha["disciplina"],
            linha["banca"],
            linha["ano"],
            linha["professor_id"],
            linha["id"],
        )
