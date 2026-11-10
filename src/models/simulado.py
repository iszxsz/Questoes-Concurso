"""Simulado: conjunto de questões que o aluno faz de uma vez."""

from src import database
from src.models.aluno import Aluno
from src.models.questao import Questao
from src.models.resposta import Resposta
from src.models.resultado_simulado import ResultadoSimulado


class Simulado:
    """Simulado montado por um professor, formado por objetos Questao.

    Attributes:
        MINIMO_QUESTOES (int): menor número de questões para salvar um simulado.
    """

    MINIMO_QUESTOES = 2

    def __init__(self, titulo, professor_id, questoes, id=None):
        """Guarda os dados e valida o título."""
        self.id = id
        self.titulo = str(titulo or "").strip()
        self.professor_id = professor_id
        self.questoes = list(questoes)

        if self.titulo == "":
            raise ValueError("Informe o título do simulado.")

    def __str__(self):
        """Título e quantidade de questões."""
        return f"{self.titulo} ({len(self)} questões)"

    def __len__(self):
        """Quantidade de questões do simulado."""
        return len(self.questoes)

    def salvar(self):
        """Insere o simulado e suas questões, na ordem da lista, e preenche o id.

        Raises:
            ValueError: se o simulado tiver menos questões que o mínimo.
        """
        if len(self) < self.MINIMO_QUESTOES:
            raise ValueError(f"Escolha pelo menos {self.MINIMO_QUESTOES} questões.")

        conexao = database.conectar()
        cursor = conexao.execute(
            "INSERT INTO simulado (titulo, professor_id) VALUES (?, ?)",
            (self.titulo, self.professor_id),
        )
        self.id = cursor.lastrowid

        for posicao, questao in enumerate(self.questoes, start=1):
            conexao.execute(
                "INSERT INTO simulado_questao (simulado_id, questao_id, posicao) VALUES (?, ?, ?)",
                (self.id, questao.id, posicao),
            )
        conexao.commit()
        conexao.close()

    @classmethod
    def montar(cls, titulo, professor_id, questao_ids):
        """Busca as questões escolhidas, cria o simulado, salva e devolve."""
        questoes = []
        for questao_id in questao_ids:
            questao = Questao.buscar_por_id(questao_id)
            if questao is not None:
                questoes.append(questao)

        simulado = cls(titulo, professor_id, questoes)
        simulado.salvar()
        return simulado

    def ja_feito_por(self, aluno):
        """True se o aluno já respondeu este simulado."""
        return len(Resposta.listar_por_simulado(self.id, aluno.id)) > 0

    def resultado_de(self, aluno):
        """Resultado do aluno neste simulado."""
        return ResultadoSimulado.do_simulado(aluno, self)

    def resultados(self):
        """Resultados dos alunos que já fizeram o simulado, em ordem de nome."""
        resultados = []
        for aluno in Aluno.listar_todos():
            resultado = self.resultado_de(aluno)
            if resultado.feito:
                resultados.append(resultado)
        return resultados

    def responder(self, aluno, respostas):
        """Registra as respostas do aluno e devolve o resultado.

        Args:
            aluno (Aluno): aluno que está fazendo o simulado.
            respostas (dict): valor marcado em cada questão, pelo id da questão.

        Raises:
            ValueError: se o aluno já fez o simulado ou deixou alguma questão
                sem resposta válida. Nesse caso nada é salvo.
        """
        if self.ja_feito_por(aluno):
            raise ValueError("Você já fez este simulado.")

        # valida tudo antes de salvar a primeira, pra não ficar simulado pela metade
        respostas_limpas = self.__validar_respostas(respostas)
        for questao in self.questoes:
            Resposta.registrar(aluno.id, questao, respostas_limpas[questao.id], self.id)

        return self.resultado_de(aluno)

    def __validar_respostas(self, respostas):
        """Devolve as respostas limpas pelo id da questão, ou lança ValueError
        dizendo o número da primeira questão com problema."""
        respostas_limpas = {}
        for numero, questao in enumerate(self.questoes, start=1):
            enviada = str(respostas.get(questao.id) or "").strip()
            if enviada == "":
                raise ValueError(f"Responda a questão {numero} antes de enviar.")
            try:
                respostas_limpas[questao.id] = questao.validar_resposta(enviada)
            except ValueError as erro:
                raise ValueError(f"Questão {numero}: {erro}")
        return respostas_limpas

    @staticmethod
    def buscar_questoes(simulado_id):
        """Questões de um simulado, na ordem em que foram escolhidas."""
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT questao.* FROM questao "
            "JOIN simulado_questao ON simulado_questao.questao_id = questao.id "
            "WHERE simulado_questao.simulado_id = ? ORDER BY simulado_questao.posicao",
            (simulado_id,),
        ).fetchall()
        conexao.close()

        questoes = []
        for linha in linhas:
            questoes.append(Questao.de_linha(linha))
        return questoes

    @staticmethod
    def de_linha(linha):
        """Cria o simulado a partir de uma linha da tabela, já com as questões."""
        return Simulado(
            linha["titulo"],
            linha["professor_id"],
            Simulado.buscar_questoes(linha["id"]),
            linha["id"],
        )

    @staticmethod
    def buscar_por_id(simulado_id):
        """Busca um simulado pelo id, ou devolve None."""
        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM simulado WHERE id = ?", (simulado_id,)).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Simulado.de_linha(linha)

    @staticmethod
    def listar_todos():
        """Todos os simulados, do mais novo para o mais antigo."""
        conexao = database.conectar()
        linhas = conexao.execute("SELECT * FROM simulado ORDER BY id DESC").fetchall()
        conexao.close()

        simulados = []
        for linha in linhas:
            simulados.append(Simulado.de_linha(linha))
        return simulados
