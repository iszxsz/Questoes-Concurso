"""Testes da redação e da correção pelo professor."""

from src.models.correcao_redacao import CorrecaoRedacao
from src.models.desempenho import Desempenho
from src.models.questao import Questao
from src.models.redacao import Redacao
from src.models.resposta import Resposta
from tests.apoio import TEXTO_REDACAO, criar_cenario, criar_redacao, deve_recusar


def testar_redacao_e_uma_questao():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)

    assert isinstance(redacao, Questao)
    assert not redacao.CORRECAO_AUTOMATICA
    assert multipla.CORRECAO_AUTOMATICA

    salva = Questao.buscar_por_id(redacao.id)
    assert isinstance(salva, Redacao)
    assert salva.enunciado == "Desafios para a formação de leitores no Brasil"
    assert len(Questao.buscar(tipo=Redacao.TIPO)) == 1


def testar_texto_curto_recusado():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)

    mensagem = deve_recusar(Resposta.registrar, aluno.id, redacao, "Texto curto demais.")
    assert mensagem == "A redação deve ter pelo menos 300 caracteres."
    deve_recusar(Resposta.registrar, aluno.id, redacao, "")
    assert Resposta.listar_por_aluno(aluno.id) == []


def testar_redacao_fica_pendente():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)

    resposta = Resposta.registrar(aluno.id, redacao, "  " + TEXTO_REDACAO + "  ")
    assert resposta.pendente
    assert not resposta.acertou
    assert resposta.nota is None
    assert resposta.resposta == TEXTO_REDACAO
    assert resposta.rotulo_situacao == "Aguardando correção"
    assert len(Resposta.listar_pendentes()) == 1


def testar_correcao_valida():
    correcao = CorrecaoRedacao([200, 160, "120", 160, 80], "  Bom texto, revise a conclusão. ")
    assert correcao.nota == 720
    assert correcao.comentario == "Bom texto, revise a conclusão."
    assert str(correcao) == "720 de 1000"
    assert correcao.itens()[0] == (Redacao.COMPETENCIAS[0], 200)


def testar_correcao_invalida():
    mensagem = deve_recusar(CorrecaoRedacao, [200, 160, 120, 160], "Comentário")
    assert mensagem == "Dê nota às cinco competências."

    mensagem = deve_recusar(CorrecaoRedacao, [200, 160, 120, 160, 150], "Comentário")
    assert mensagem == "Cada competência vale 0, 40, 80, 120, 160 ou 200."

    deve_recusar(CorrecaoRedacao, [200, 160, 120, 160, 240], "Comentário")
    deve_recusar(CorrecaoRedacao, [200, 160, 120, 160, ""], "Comentário")

    mensagem = deve_recusar(CorrecaoRedacao, [200, 160, 120, 160, 80], "   ")
    assert mensagem == "Escreva um comentário para o aluno."


def testar_correcao_do_formulario():
    dados = {
        "competencia_1": "40",
        "competencia_2": "80",
        "competencia_3": "120",
        "competencia_4": "160",
        "competencia_5": "200",
        "comentario": "Ótima proposta de intervenção.",
    }
    assert CorrecaoRedacao.de_formulario(dados).nota == 600


def testar_professor_corrige():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)
    resposta = Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)

    resposta.registrar_correcao(CorrecaoRedacao([160, 160, 120, 120, 80], "Faltou repertório."))
    assert resposta.corrigida
    assert resposta.corrigida_em is not None

    salva = Resposta.buscar_por_id(resposta.id)
    assert salva.corrigida
    assert salva.nota == 640
    assert salva.correcao.comentario == "Faltou repertório."
    assert salva.rotulo_situacao == "Corrigida"
    assert Resposta.listar_pendentes() == []


def testar_nao_corrige_duas_vezes_nem_objetiva():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)
    resposta = Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)
    correcao = CorrecaoRedacao([200, 200, 200, 200, 200], "Nota máxima.")
    resposta.registrar_correcao(correcao)

    mensagem = deve_recusar(resposta.registrar_correcao, correcao)
    assert mensagem == "Esta redação já foi corrigida."

    objetiva = Resposta.registrar(aluno.id, multipla, "B")
    mensagem = deve_recusar(objetiva.registrar_correcao, correcao)
    assert mensagem == "Só redações são corrigidas pelo professor."


def testar_desempenho_com_redacao():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)

    Resposta.registrar(aluno.id, multipla, "B")
    primeira = Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)
    segunda = Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)
    Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)

    primeira.registrar_correcao(CorrecaoRedacao([200, 200, 160, 160, 120], "Muito bom."))
    segunda.registrar_correcao(CorrecaoRedacao([120, 120, 80, 80, 80], "Precisa melhorar."))

    desempenho = Desempenho.do_aluno(aluno)
    assert desempenho.geral.total == 1
    assert desempenho.geral.percentual == 100.0
    assert desempenho.redacoes.quantidade == 2
    assert desempenho.redacoes.pendentes == 1
    assert desempenho.redacoes.media == 660.0


def deve_ser_so_leitura(objeto, atributo, valor):
    """Falha o teste se for possível trocar o atributo direto."""
    try:
        setattr(objeto, atributo, valor)
    except AttributeError:
        return
    raise AssertionError(f"{atributo} deveria ser só leitura")


def testar_encapsulamento():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)
    resposta = Resposta.registrar(aluno.id, redacao, TEXTO_REDACAO)

    # sem registrar_correcao não tem como marcar como corrigida
    deve_ser_so_leitura(resposta, "situacao", "corrigida")
    deve_ser_so_leitura(resposta, "correcao", None)
    deve_ser_so_leitura(multipla, "gabarito", "A")

    correcao = CorrecaoRedacao([200, 200, 200, 200, 200], "Nota máxima.")
    deve_ser_so_leitura(correcao, "comentario", "")
    deve_ser_so_leitura(correcao, "nota", 0)
    try:
        correcao.competencias[0] = 0
    except TypeError:
        pass
    else:
        raise AssertionError("as notas da correção deveriam ser imutáveis")

    desempenho = Desempenho.do_aluno(aluno)
    deve_ser_so_leitura(desempenho.redacoes, "pendentes", 0)
    deve_ser_so_leitura(desempenho.geral, "total", 10)
    deve_ser_so_leitura(desempenho, "redacoes", None)

    mensagem = deve_recusar(Resposta, aluno.id, multipla.id, "B", "qualquer")
    assert mensagem == "Situação de resposta inválida: qualquer."

    # privado (__) não aparece de fora com o nome que tem dentro da classe
    assert not hasattr(correcao, "__competencias")
    assert not hasattr(resposta, "__situacao")
    # protegido (_) continua lá porque a subclasse precisa
    assert hasattr(desempenho, "_geral")


if __name__ == "__main__":
    testar_redacao_e_uma_questao()
    testar_texto_curto_recusado()
    testar_redacao_fica_pendente()
    testar_correcao_valida()
    testar_correcao_invalida()
    testar_correcao_do_formulario()
    testar_professor_corrige()
    testar_nao_corrige_duas_vezes_nem_objetiva()
    testar_desempenho_com_redacao()
    testar_encapsulamento()
    print("Todos os testes de redação passaram.")
