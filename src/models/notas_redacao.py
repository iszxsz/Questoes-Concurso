"""Média das notas de redação."""


class NotasRedacao:
    """Junta as notas das redações corrigidas e conta as que faltam corrigir.

    Faz para a redação o papel que Aproveitamento faz para as objetivas.
    Os contadores são internos: só mudam por registrar() e
    registrar_pendente(), e são lidos pelas propriedades.
    """

    def __init__(self):
        """Começa sem nenhuma nota e sem pendentes."""
        self.__quantidade = 0
        self.__soma = 0
        self.__pendentes = 0

    def __str__(self):
        """Resumo no formato "Redações: média X em N corrigidas"."""
        return f"Redações: média {self.media} em {self.quantidade} corrigidas"

    def registrar(self, nota):
        """Soma a nota de uma redação corrigida.

        Raises:
            ValueError: se a nota for negativa.
        """
        if nota < 0:
            raise ValueError("A nota da redação não pode ser negativa.")
        self.__quantidade += 1
        self.__soma += nota

    def registrar_pendente(self):
        """Conta uma redação que ainda não foi corrigida."""
        self.__pendentes += 1

    @property
    def quantidade(self):
        """Quantidade de redações corrigidas."""
        return self.__quantidade

    @property
    def pendentes(self):
        """Quantidade de redações esperando correção."""
        return self.__pendentes

    @property
    def media(self):
        """Média das notas com uma casa decimal; 0.0 sem redações corrigidas."""
        if self.__quantidade == 0:
            return 0.0
        return round(self.__soma / self.__quantidade, 1)
