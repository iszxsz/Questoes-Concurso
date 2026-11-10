"""Base das questões objetivas, que têm opções e gabarito."""

from abc import abstractmethod

from src.models.questao import Questao


class QuestaoObjetiva(Questao):
    """Questão com opções fixas e gabarito, corrigida automaticamente.

    Fica entre Questao e os tipos objetivos. Assim a redação, que não tem
    opções nem gabarito, também pode ser uma Questao.
    """

    CORRECAO_AUTOMATICA = True

    def __init__(self, enunciado, disciplina, banca, ano, professor_id, gabarito, id=None):
        """Valida os dados comuns na base e depois o gabarito pelas opções."""
        super().__init__(enunciado, disciplina, banca, ano, professor_id, id)
        self._gabarito = self.__validar_gabarito(gabarito)

    def __validar_gabarito(self, gabarito):
        """Devolve o gabarito limpo, ou lança ValueError se não for uma das opções."""
        gabarito = str(gabarito).strip().upper()
        if gabarito not in self.valores_validos:
            raise ValueError("O gabarito deve ser um destes: " + ", ".join(self.valores_validos) + ".")
        return gabarito

    @property
    def gabarito(self):
        """Valor da opção correta (só leitura; para mudar, edite a questão)."""
        return self._gabarito

    @abstractmethod
    def opcoes(self):
        """Lista de pares (valor, texto) das opções da questão."""

    @property
    def valores_validos(self):
        """Valores das opções, por exemplo ["A", "B", "C"]."""
        valores = []
        for valor, texto in self.opcoes():
            valores.append(valor)
        return valores

    def texto_da_opcao(self, valor):
        """Texto da opção com esse valor, ou o próprio valor se ela não existir."""
        for valor_opcao, texto in self.opcoes():
            if valor_opcao == valor:
                return texto
        return valor

    def para_formulario(self):
        """Campos comuns mais o gabarito."""
        dados = super().para_formulario()
        dados["gabarito"] = self._gabarito
        return dados

    def _gabarito_em_texto(self):
        """Gabarito como fica gravado no banco."""
        return self._gabarito

    def validar_resposta(self, resposta):
        """Devolve a resposta limpa, ou lança ValueError se não for uma das opções."""
        resposta = str(resposta or "").strip().upper()
        if resposta not in self.valores_validos:
            raise ValueError("Marque uma das opções.")
        return resposta

    def corrigir(self, resposta):
        """Devolve "correta" ou "errada" comparando a resposta com o gabarito."""
        if self.validar_resposta(resposta) == self._gabarito:
            return "correta"
        return "errada"
