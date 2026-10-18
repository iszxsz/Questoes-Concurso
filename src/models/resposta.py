"""Resposta de um aluno a uma questão."""

from src import database
from src.models.questao import Questao


class Resposta:
    """Resposta enviada por um aluno, já corrigida."""

    def __init__(self, aluno_id, questao_id, resposta, situacao, respondida_em=None, id=None):
        """Guarda os dados da resposta."""
        self.id = id
        self.aluno_id = aluno_id
        self.questao_id = questao_id
        self.resposta = resposta
        self.situacao = situacao
        self.respondida_em = respondida_em

    def __str__(self):
        return f"Questão {self.questao_id} · {self.resposta} · {self.rotulo_situacao}"

    @property
    def acertou(self):
        """True se a resposta está correta."""
        return self.situacao == "correta"

    @property
    def rotulo_situacao(self):
        """Situação para mostrar na tela: "Correta" ou "Errada"."""
        if self.acertou:
            return "Correta"
        return "Errada"

    def questao(self):
        """Busca a questão que foi respondida."""
        return Questao.buscar_por_id(self.questao_id)

    @staticmethod
    def registrar(aluno_id, questao, resposta):
        """Valida e corrige pela própria questão, salva e devolve a resposta.

        Se a resposta for inválida, o ValueError da questão sobe e nada é salvo.
        """
        resposta_limpa = questao.validar_resposta(resposta)
        situacao = questao.corrigir(resposta_limpa)

        nova = Resposta(aluno_id, questao.id, resposta_limpa, situacao)
        nova.salvar()
        return nova

    def salvar(self):
        """Insere no banco e preenche o id e a data da resposta."""
        conexao = database.conectar()
        cursor = conexao.execute(
            "INSERT INTO resposta (aluno_id, questao_id, resposta, situacao) VALUES (?, ?, ?, ?)",
            (self.aluno_id, self.questao_id, self.resposta, self.situacao),
        )
        conexao.commit()
        self.id = cursor.lastrowid

        # o CURRENT_TIMESTAMP do SQLite salva em UTC, fica 3h na frente do horário de Brasília... precisa tratar isso quando for mostrar a data na tela (T06)
        linha = conexao.execute(
            "SELECT respondida_em FROM resposta WHERE id = ?", (self.id,)
        ).fetchone()
        self.respondida_em = linha["respondida_em"]
        conexao.close()

    @staticmethod
    def de_linha(linha):
        """Cria a resposta a partir de uma linha da tabela resposta."""
        return Resposta(
            linha["aluno_id"],
            linha["questao_id"],
            linha["resposta"],
            linha["situacao"],
            linha["respondida_em"],
            linha["id"],
        )

    @staticmethod
    def listar_por_aluno(aluno_id):
        """Respostas do aluno, da mais recente para a mais antiga."""
        conexao = database.conectar()
        linhas = conexao.execute(
            "SELECT * FROM resposta WHERE aluno_id = ? ORDER BY respondida_em DESC, id DESC",
            (aluno_id,),
        ).fetchall()
        conexao.close()

        respostas = []
        for linha in linhas:
            respostas.append(Resposta.de_linha(linha))
        return respostas
