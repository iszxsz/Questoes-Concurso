from src.models.questao import Questao


class QuestaoCertoErrado(Questao):

    TIPO = "certo_errado"
    NOME_TIPO = "Certo ou errado"
    OPCOES = (("C", "Certo"), ("E", "Errado"))

    def opcoes(self):
        return list(self.OPCOES)
