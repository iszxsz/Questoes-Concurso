"""Testes de edição e exclusão de questões."""

from src.models.questao import Questao
from src.models.questao_certo_errado import QuestaoCertoErrado
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta
from src.models.simulado import Simulado
from tests.apoio import criar_cenario, deve_recusar


def testar_formulario_ida_e_volta():
    aluno, multipla, certo_errado = criar_cenario()

    dados = multipla.para_formulario()
    assert dados["alternativa_b"] == "exceção"
    assert dados["ano"] == "2023"

    copia = QuestaoMultipla.de_formulario(dados, multipla.professor_id, multipla.id)
    assert copia.alternativas == multipla.alternativas
    assert copia.gabarito == "B"

    dados = certo_errado.para_formulario()
    assert "alternativa_a" not in dados
    copia = QuestaoCertoErrado.de_formulario(dados, certo_errado.professor_id)
    assert copia.gabarito == "C"


def testar_editar_questao():
    aluno, multipla, certo_errado = criar_cenario()

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
    aluno, multipla, certo_errado = criar_cenario()

    dados = certo_errado.para_formulario()
    dados["gabarito"] = "A"
    mensagem = deve_recusar(QuestaoCertoErrado.de_formulario, dados, 1, certo_errado.id)
    assert mensagem == "O gabarito deve ser um destes: C, E."
    assert Questao.buscar_por_id(certo_errado.id).gabarito == "C"


def testar_excluir_questao_sem_respostas():
    aluno, multipla, certo_errado = criar_cenario()
    assert not multipla.tem_respostas()

    multipla.excluir()
    assert Questao.buscar_por_id(multipla.id) is None
    assert len(Questao.buscar()) == 1


def testar_excluir_questao_com_respostas_bloqueado():
    aluno, multipla, certo_errado = criar_cenario()
    Resposta.registrar(aluno.id, multipla, "A")
    assert multipla.tem_respostas()

    mensagem = deve_recusar(multipla.excluir)
    assert mensagem == "Esta questão já tem respostas e não pode ser excluída."
    assert Questao.buscar_por_id(multipla.id) is not None


def testar_excluir_questao_que_esta_em_simulado():
    aluno, multipla, certo_errado = criar_cenario()
    simulado = Simulado.montar("Simulado", multipla.professor_id, [multipla.id, certo_errado.id])

    multipla.excluir()
    assert len(Simulado.buscar_por_id(simulado.id)) == 1


if __name__ == "__main__":
    testar_formulario_ida_e_volta()
    testar_editar_questao()
    testar_edicao_invalida()
    testar_excluir_questao_sem_respostas()
    testar_excluir_questao_com_respostas_bloqueado()
    testar_excluir_questao_que_esta_em_simulado()
    print("Todos os testes de manutenção de questão passaram.")
