"""Resposta de um aluno a uma questão."""

from datetime import datetime, timezone

from src import database
from src.models.aluno import Aluno
from src.models.correcao_redacao import CorrecaoRedacao
from src.models.questao import Questao


class Resposta:
    """Resposta enviada por um aluno.

    Questão objetiva já sai corrigida ("correta" ou "errada"). Redação sai
    "pendente" e vira "corrigida" quando o professor registra a correção.

    Attributes:
        ROTULOS (dict): texto mostrado na tela para cada situação.
    """

    ROTULOS = {
        "correta": "Correta",
        "errada": "Errada",
        "pendente": "Aguardando correção",
        "corrigida": "Corrigida",
    }

    def __init__(
        self,
        aluno_id,
        questao_id,
        resposta,
        situacao,
        respondida_em=None,
        id=None,
        simulado_id=None,
        correcao=None,
        corrigida_em=None,
    ):
        """Guarda os dados da resposta. simulado_id fica None fora de simulado
        e correcao fica None enquanto a redação não for corrigida.

        Situação, correção e data da correção ficam em atributos internos:
        só mudam por registrar_correcao(), que confere as regras antes.

        Raises:
            ValueError: se a situação não for uma das de ROTULOS.
        """
        self.id = id
        self.aluno_id = aluno_id
        self.questao_id = questao_id
        self.resposta = resposta
        self.respondida_em = respondida_em
        self.simulado_id = simulado_id
        self.__situacao = self.__validar_situacao(situacao)
        self.__correcao = correcao
        self.__corrigida_em = corrigida_em

    def __str__(self):
        return f"Questão {self.questao_id} · {self.rotulo_situacao}"

    def __validar_situacao(self, situacao):
        """Devolve a situação, ou lança ValueError se ela não existir."""
        if situacao not in self.ROTULOS:
            raise ValueError(f"Situação de resposta inválida: {situacao}.")
        return situacao

    @property
    def situacao(self):
        """Situação da resposta: "correta", "errada", "pendente" ou "corrigida"."""
        return self.__situacao

    @property
    def correcao(self):
        """Correção do professor (CorrecaoRedacao), ou None."""
        return self.__correcao

    @property
    def corrigida_em(self):
        """Data da correção como vem do banco, ou None."""
        return self.__corrigida_em

    @property
    def acertou(self):
        """True se a resposta está correta."""
        return self.__situacao == "correta"

    @property
    def pendente(self):
        """True se é uma redação esperando a correção do professor."""
        return self.__situacao == "pendente"

    @property
    def corrigida(self):
        """True se é uma redação que o professor já corrigiu."""
        return self.__situacao == "corrigida"

    @property
    def nota(self):
        """Nota da redação corrigida, ou None."""
        if self.__correcao is None:
            return None
        return self.__correcao.nota

    @property
    def rotulo_situacao(self):
        """Situação para mostrar na tela, por exemplo "Correta" ou "Corrigida"."""
        return self.ROTULOS[self.__situacao]

    @staticmethod
    def __formatar_data(texto):
        """Converte uma data do banco (UTC) para o horário local em dd/mm/aaaa hh:mm."""
        data_utc = datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return data_utc.astimezone().strftime("%d/%m/%Y %H:%M")

    @property
    def data_formatada(self):
        """Data da resposta no horário local, no formato dd/mm/aaaa hh:mm."""
        return Resposta.__formatar_data(self.respondida_em)

    @property
    def data_correcao_formatada(self):
        """Data da correção no horário local, ou None se não foi corrigida."""
        if self.__corrigida_em is None:
            return None
        return Resposta.__formatar_data(self.__corrigida_em)

    def questao(self):
        """Busca a questão que foi respondida."""
        return Questao.buscar_por_id(self.questao_id)

    def aluno(self):
        """Busca o aluno que enviou a resposta."""
        return Aluno.buscar_por_id(self.aluno_id)

    @staticmethod
    def registrar(aluno_id, questao, resposta, simulado_id=None):
        """Valida e corrige pela própria questão, salva e devolve a resposta.

        Se a resposta for inválida, o ValueError da questão sobe e nada é salvo.
        """
        resposta_limpa = questao.validar_resposta(resposta)
        situacao = questao.corrigir(resposta_limpa)

        nova = Resposta(aluno_id, questao.id, resposta_limpa, situacao, simulado_id=simulado_id)
        nova.salvar()
        return nova

    def registrar_correcao(self, correcao):
        """Guarda a correção do professor e marca a redação como corrigida.

        Raises:
            ValueError: se a resposta não estiver esperando correção.
        """
        if self.corrigida:
            raise ValueError("Esta redação já foi corrigida.")
        if not self.pendente:
            raise ValueError("Só redações são corrigidas pelo professor.")

        self.__correcao = correcao
        self.__situacao = "corrigida"
        self.__gravar_correcao()

    def __gravar_correcao(self):
        """Grava no banco a situação e a correção atuais e lê a data da correção."""
        conexao = database.conectar()
        conexao.execute(
            "UPDATE resposta SET situacao = ?, competencias = ?, comentario = ?, "
            "corrigida_em = CURRENT_TIMESTAMP WHERE id = ?",
            (
                self.__situacao,
                self.__correcao.competencias_em_texto(),
                self.__correcao.comentario,
                self.id,
            ),
        )
        conexao.commit()

        linha = conexao.execute(
            "SELECT corrigida_em FROM resposta WHERE id = ?", (self.id,)
        ).fetchone()
        self.__corrigida_em = linha["corrigida_em"]
        conexao.close()

    def salvar(self):
        """Insere no banco e preenche o id e a data da resposta."""
        conexao = database.conectar()
        cursor = conexao.execute(
            "INSERT INTO resposta (aluno_id, questao_id, resposta, situacao, simulado_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.aluno_id, self.questao_id, self.resposta, self.situacao, self.simulado_id),
        )
        conexao.commit()
        self.id = cursor.lastrowid

        linha = conexao.execute(
            "SELECT respondida_em FROM resposta WHERE id = ?", (self.id,)
        ).fetchone()
        self.respondida_em = linha["respondida_em"]
        conexao.close()

    @staticmethod
    def de_linha(linha):
        """Cria a resposta a partir de uma linha da tabela resposta."""
        correcao = None
        if linha["competencias"] is not None:
            correcao = CorrecaoRedacao.de_texto(linha["competencias"], linha["comentario"])

        return Resposta(
            linha["aluno_id"],
            linha["questao_id"],
            linha["resposta"],
            linha["situacao"],
            linha["respondida_em"],
            linha["id"],
            linha["simulado_id"],
            correcao,
            linha["corrigida_em"],
        )

    @staticmethod
    def buscar_por_id(resposta_id):
        """Busca uma resposta pelo id, ou devolve None."""
        conexao = database.conectar()
        linha = conexao.execute("SELECT * FROM resposta WHERE id = ?", (resposta_id,)).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Resposta.de_linha(linha)

    @staticmethod
    def listar_por_aluno(aluno_id):
        """Respostas do aluno, da mais recente para a mais antiga."""
        return Resposta.__listar(
            "SELECT * FROM resposta WHERE aluno_id = ? ORDER BY respondida_em DESC, id DESC",
            (aluno_id,),
        )

    @staticmethod
    def listar_por_simulado(simulado_id, aluno_id):
        """Respostas do aluno em um simulado, na ordem em que foram salvas."""
        return Resposta.__listar(
            "SELECT * FROM resposta WHERE simulado_id = ? AND aluno_id = ? ORDER BY id",
            (simulado_id, aluno_id),
        )

    @staticmethod
    def listar_pendentes():
        """Redações esperando correção, da mais antiga para a mais nova."""
        return Resposta.__listar(
            "SELECT * FROM resposta WHERE situacao = 'pendente' ORDER BY respondida_em, id"
        )

    @staticmethod
    def __listar(sql, parametros=()):
        """Roda a consulta e monta uma Resposta para cada linha."""
        conexao = database.conectar()
        linhas = conexao.execute(sql, parametros).fetchall()
        conexao.close()

        respostas = []
        for linha in linhas:
            respostas.append(Resposta.de_linha(linha))
        return respostas
