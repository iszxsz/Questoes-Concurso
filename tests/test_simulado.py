"""Testes de simulado e do resultado do aluno no simulado."""

from src.models.desempenho import Desempenho
from src.models.questao_multipla import QuestaoMultipla
from src.models.resposta import Resposta
from src.models.resultado_simulado import ResultadoSimulado
from src.models.simulado import Simulado
from tests.apoio import criar_cenario, deve_recusar


def montar_simulado():
    aluno, multipla, certo_errado = criar_cenario()
    simulado = Simulado.montar(
        "Simulado 1", multipla.professor_id, [str(certo_errado.id), str(multipla.id)]
    )
    return aluno, multipla, certo_errado, simulado


def testar_montar_e_buscar():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    assert simulado.id is not None
    assert len(simulado) == 2

    salvo = Simulado.buscar_por_id(simulado.id)
    assert salvo.titulo == "Simulado 1"
    assert salvo.questoes[0].id == certo_errado.id
    assert salvo.questoes[1].id == multipla.id
    assert isinstance(salvo.questoes[1], QuestaoMultipla)
    assert str(salvo) == "Simulado 1 (2 questões)"
    assert len(Simulado.listar_todos()) == 1


def testar_simulado_invalido():
    aluno, multipla, certo_errado = criar_cenario()
    professor_id = multipla.professor_id

    mensagem = deve_recusar(Simulado.montar, "  ", professor_id, [multipla.id, certo_errado.id])
    assert mensagem == "Informe o título do simulado."

    mensagem = deve_recusar(Simulado.montar, "Simulado", professor_id, [multipla.id])
    assert mensagem == "Escolha pelo menos 2 questões."

    mensagem = deve_recusar(Simulado.montar, "Simulado", professor_id, [multipla.id, 999])
    assert mensagem == "Escolha pelo menos 2 questões."
    assert Simulado.listar_todos() == []


def testar_responder():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    assert not simulado.ja_feito_por(aluno)

    resultado = simulado.responder(aluno, {multipla.id: " b ", certo_errado.id: "E"})

    assert isinstance(resultado, ResultadoSimulado)
    assert isinstance(resultado, Desempenho)
    assert resultado.feito
    assert resultado.geral.total == 2
    assert resultado.geral.acertos == 1
    assert resultado.geral.percentual == 50.0
    assert simulado.ja_feito_por(aluno)

    respostas = Resposta.listar_por_simulado(simulado.id, aluno.id)
    assert len(respostas) == 2
    assert respostas[0].simulado_id == simulado.id


def testar_simulado_feito_uma_vez():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    simulado.responder(aluno, {multipla.id: "B", certo_errado.id: "C"})

    mensagem = deve_recusar(simulado.responder, aluno, {multipla.id: "B", certo_errado.id: "C"})
    assert mensagem == "Você já fez este simulado."
    assert len(Resposta.listar_por_aluno(aluno.id)) == 2


def testar_resposta_faltando_nao_salva_nada():
    aluno, multipla, certo_errado, simulado = montar_simulado()

    mensagem = deve_recusar(simulado.responder, aluno, {certo_errado.id: "C"})
    assert mensagem == "Responda a questão 2 antes de enviar."

    deve_recusar(simulado.responder, aluno, {certo_errado.id: "C", multipla.id: "Z"})
    assert Resposta.listar_por_aluno(aluno.id) == []
    assert not simulado.ja_feito_por(aluno)


def testar_resultado_questao_por_questao():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    simulado.responder(aluno, {multipla.id: "A", certo_errado.id: "C"})

    resultado = simulado.resultado_de(aluno)
    itens = resultado.itens()
    assert itens[0][0].id == certo_errado.id
    assert itens[0][1].acertou
    assert itens[1][0].id == multipla.id
    assert not itens[1][1].acertou

    disciplinas = resultado.por_disciplina()
    assert disciplinas[0].nome == "Direito Constitucional"
    assert disciplinas[1].nome == "Português"


def testar_resultado_conta_so_o_simulado():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    Resposta.registrar(aluno.id, multipla, "A")
    simulado.responder(aluno, {multipla.id: "B", certo_errado.id: "C"})

    assert simulado.resultado_de(aluno).geral.total == 2
    assert Desempenho.do_aluno(aluno).geral.total == 3


def testar_resultados_dos_alunos():
    aluno, multipla, certo_errado, simulado = montar_simulado()
    assert simulado.resultados() == []

    simulado.responder(aluno, {multipla.id: "B", certo_errado.id: "C"})
    resultados = simulado.resultados()
    assert len(resultados) == 1
    assert resultados[0].aluno.id == aluno.id
    assert resultados[0].geral.percentual == 100.0


if __name__ == "__main__":
    testar_montar_e_buscar()
    testar_simulado_invalido()
    testar_responder()
    testar_simulado_feito_uma_vez()
    testar_resposta_faltando_nao_salva_nada()
    testar_resultado_questao_por_questao()
    testar_resultado_conta_so_o_simulado()
    testar_resultados_dos_alunos()
    print("Todos os testes de simulado passaram.")
