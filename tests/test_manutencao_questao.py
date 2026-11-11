"""Testes de edição e exclusão de questões."""

from src.models.questao import Questao
from src.models.questao_verdadeiro_falso import QuestaoVerdadeiroFalso
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta
from src.models.simulado import Simulado
from tests.apoio import criar_cenario, criar_redacao, deve_recusar


def testar_editar_redacao():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    redacao = criar_redacao(multipla.professor_id)

    dados = redacao.para_formulario()
    assert "gabarito" not in dados
    dados["enunciado"] = "O lixo eletrônico no Brasil"
    editada = redacao.de_formulario(dados, redacao.professor_id, redacao.id)
    editada.atualizar()

    salva = Questao.buscar_por_id(redacao.id)
    assert salva.enunciado == "O lixo eletrônico no Brasil"
    assert salva.NOME_TIPO == "Redação"


def testar_formulario_ida_e_volta():
    aluno, multipla, verdadeiro_falso = criar_cenario()

    dados = multipla.para_formulario()
    assert dados["alternativa_b"] == "exceção"
    assert dados["ano"] == "2023"

    copia = QuestaoMultipla.de_formulario(dados, multipla.professor_id, multipla.id)
    assert copia.alternativas == multipla.alternativas
    assert copia.gabarito == "B"

    dados = verdadeiro_falso.para_formulario()
    assert "alternativa_a" not in dados
    copia = QuestaoVerdadeiroFalso.de_formulario(dados, verdadeiro_falso.professor_id)
    assert copia.gabarito == "V"


def testar_editar_questao():
    aluno, multipla, verdadeiro_falso = criar_cenario()

    dados = multipla.para_formulario()
    dados["enunciado"] = "Enunciado novo"
    dados["alternativa_d"] = "excesção"
    dados["gabarito"] = "D"
    editada = QuestaoMultipla.de_formulario(dados, multipla.professor_id, multipla.id)
    editada.atualizar()

    salva = Questao.buscar_por_id(multipla.id)
    assert salva.enunciado == "Enunciado novo"
    assert len(salva.alternativas) == 4
    assert salva.gabarito == "D"


def testar_edicao_invalida():
    aluno, multipla, verdadeiro_falso = criar_cenario()

    dados = verdadeiro_falso.para_formulario()
    dados["gabarito"] = "A"
    mensagem = deve_recusar(QuestaoVerdadeiroFalso.de_formulario, dados, 1, verdadeiro_falso.id)
    assert mensagem == "O gabarito deve ser um destes: V, F."
    assert Questao.buscar_por_id(verdadeiro_falso.id).gabarito == "V"


def testar_excluir_questao_sem_respostas():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    assert not multipla.tem_respostas()

    multipla.excluir()
    assert Questao.buscar_por_id(multipla.id) is None
    assert len(Questao.buscar()) == 1


def testar_excluir_questao_com_respostas_bloqueado():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    Resposta.registrar(aluno.id, multipla, "A")
    assert multipla.tem_respostas()

    mensagem = deve_recusar(multipla.excluir)
    assert mensagem == "Esta questão já tem respostas e não pode ser excluída."
    assert Questao.buscar_por_id(multipla.id) is not None


def testar_excluir_questao_que_esta_em_simulado():
    aluno, multipla, verdadeiro_falso = criar_cenario()
    simulado = Simulado.montar("Simulado", multipla.professor_id, [multipla.id, verdadeiro_falso.id])

    multipla.excluir()
    assert len(Simulado.buscar_por_id(simulado.id)) == 1


if __name__ == "__main__":
    testar_formulario_ida_e_volta()
    testar_editar_questao()
    testar_edicao_invalida()
    testar_excluir_questao_sem_respostas()
    testar_excluir_questao_com_respostas_bloqueado()
    testar_excluir_questao_que_esta_em_simulado()
    testar_editar_redacao()
    print("Todos os testes de manutenção de questão passaram.")
