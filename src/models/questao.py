import json
from abc import ABC, abstractmethod

from src import database


class Questao(ABC):
    """Base de todos os tipos de questão objetiva."""

    TIPO = None
    NOME_TIPO = None
    ANO_MINIMO = 1990
    ANO_MAXIMO = 2100

    def __init__(self, enunciado, disciplina, banca, ano, professor_id, gabarito, id=None):
        self.id = id
        self.enunciado = enunciado.strip()
        self.disciplina = disciplina.strip()
        self.banca = banca.strip()
        self.professor_id = professor_id

        if self.enunciado == "" or self.disciplina == "" or self.banca == "":
            raise ValueError("Preencha enunciado, disciplina e banca.")

        try:
            self.ano = int(ano)
        except (TypeError, ValueError):
            raise ValueError("Informe um ano válido.")
        if self.ano < self.ANO_MINIMO or self.ano > self.ANO_MAXIMO:
            raise ValueError("Informe um ano válido.")

        self.gabarito = str(gabarito).strip().upper()
        if self.gabarito not in self.valores_validos:
            raise ValueError("O gabarito deve ser um destes: " + ", ".join(self.valores_validos) + ".")

    def __str__(self):
        return f"{self.disciplina} · {self.banca} · {self.ano}"

    @abstractmethod
    def opcoes(self):
        """Lista de pares (valor, texto) das opções da questão."""

    def para_formulario(self):
        """Campos comuns da questão no formato do formulário, para editar."""
        return {
            "enunciado": self.enunciado,
            "disciplina": self.disciplina,
            "banca": self.banca,
            "ano": str(self.ano),
            "gabarito": self.gabarito,
        }

    def alternativas_em_texto(self):
        """Alternativas no formato gravado no banco; None para tipos sem alternativas."""
        return None

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

    def validar_resposta(self, resposta):
        """Devolve a resposta limpa, ou lança ValueError se não for uma das opções."""
        resposta = str(resposta or "").strip().upper()
        if resposta not in self.valores_validos:
            raise ValueError("Marque uma das opções.")
        return resposta

    def corrigir(self, resposta):
        """Devolve "correta" ou "errada" comparando a resposta com o gabarito."""
        if self.validar_resposta(resposta) == self.gabarito:
            return "correta"
        return "errada"

    def salvar(self):
        """Insere a questão no banco e preenche o id."""
        conexao = database.conectar()
        cursor = conexao.execute(
            "INSERT INTO questao (tipo, enunciado, disciplina, banca, ano, "
            "professor_id, alternativas, gabarito) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.TIPO,
                self.enunciado,
                self.disciplina,
                self.banca,
                self.ano,
                self.professor_id,
                self.alternativas_em_texto(),
                self.gabarito,
            ),
        )
        conexao.commit()
        self.id = cursor.lastrowid
        conexao.close()

    def atualizar(self):
        """Grava no banco os dados atuais de uma questão que já existe."""
        conexao = database.conectar()
        conexao.execute(
            "UPDATE questao SET enunciado = ?, disciplina = ?, banca = ?, ano = ?, "
            "alternativas = ?, gabarito = ? WHERE id = ?",
            (
                self.enunciado,
                self.disciplina,
                self.banca,
                self.ano,
                self.alternativas_em_texto(),
                self.gabarito,
                self.id,
            ),
        )
        conexao.commit()
        conexao.close()

    def tem_respostas(self):
        """True se algum aluno já respondeu esta questão."""
        conexao = database.conectar()
        linha = conexao.execute(
            "SELECT COUNT(*) AS total FROM resposta WHERE questao_id = ?", (self.id,)
        ).fetchone()
        conexao.close()
        return linha["total"] > 0

    def excluir(self):
        """Apaga a questão e a tira dos simulados em que estiver.

        Raises:
            ValueError: se a questão já tiver respostas.
        """
        if self.tem_respostas():
            raise ValueError("Esta questão já tem respostas e não pode ser excluída.")

        conexao = database.conectar()
        conexao.execute("DELETE FROM simulado_questao WHERE questao_id = ?", (self.id,))
        conexao.execute("DELETE FROM questao WHERE id = ?", (self.id,))
        conexao.commit()
        conexao.close()

    @staticmethod
    def de_linha(linha):
        """Cria o objeto do tipo certo a partir de uma linha da tabela questao."""
        # import aqui dentro pra não dar importação circular
        from src.models.questao_certo_errado import QuestaoCertoErrado
        from src.models.questao_multipla import QuestaoMultipla

        if linha["tipo"] == QuestaoMultipla.TIPO:
            return QuestaoMultipla(
                linha["enunciado"],
                linha["disciplina"],
                linha["banca"],
                linha["ano"],
                linha["professor_id"],
                json.loads(linha["alternativas"]),
                linha["gabarito"],
                linha["id"],
            )
        return QuestaoCertoErrado(
            linha["enunciado"],
            linha["disciplina"],
            linha["banca"],
            linha["ano"],
            linha["professor_id"],
            linha["gabarito"],
            linha["id"],
        )

    @staticmethod
    def buscar_por_id(questao_id):
        """Busca uma questão pelo id, ou devolve None."""
        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM questao WHERE id = ?", (questao_id,)).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Questao.de_linha(linha)

    @staticmethod
    def buscar(disciplina=None, banca=None, tipo=None):
        """Busca questões com filtros opcionais, ordenadas por disciplina e id."""
        sql = "SELECT * FROM questao WHERE 1 = 1"
        parametros = []
        if disciplina:
            sql += " AND disciplina = ?"
            parametros.append(disciplina)
        if banca:
            sql += " AND banca = ?"
            parametros.append(banca)
        if tipo:
            sql += " AND tipo = ?"
            parametros.append(tipo)
        sql += " ORDER BY disciplina, id"

        conexao = database.conectar()
        linhas = conexao.execute(sql, parametros).fetchall()
        conexao.close()

        questoes = []
        for linha in linhas:
            questoes.append(Questao.de_linha(linha))
        return questoes

    @staticmethod
    def listar_disciplinas():
        """Disciplinas cadastradas, em ordem alfabética."""
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT DISTINCT disciplina FROM questao ORDER BY disciplina"
        ).fetchall()
        conexao.close()

        disciplinas = []
        for linha in linhas:
            disciplinas.append(linha["disciplina"])
        return disciplinas

    @staticmethod
    def listar_bancas():
        """Bancas cadastradas, em ordem alfabética."""
        conexao = database.conectar()
        linhas = conexao.execute("SELECT DISTINCT banca FROM questao ORDER BY banca").fetchall()
        conexao.close()

        bancas = []
        for linha in linhas:
            bancas.append(linha["banca"])
        return bancas
