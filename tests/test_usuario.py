"""Testes de usuário, aluno e professor."""

from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.usuario import Usuario
from tests.apoio import SENHA_TESTE, criar_cenario, deve_recusar, preparar_banco


def testar_cadastro_limpa_dados():
    preparar_banco()
    aluno = Aluno.cadastrar("  Maria Silva  ", " Maria@Teste.com ", "abc123", "abc123")

    assert aluno.id is not None
    assert aluno.nome == "Maria Silva"
    assert aluno.email == "maria@teste.com"
    assert not aluno.verificar_senha("outra123")
    assert aluno.verificar_senha("abc123")


def testar_cadastro_recusado():
    criar_cenario()

    mensagem = deve_recusar(Aluno.cadastrar, "Outro", "ALUNO@teste.com", "abc123", "abc123")
    assert mensagem == "E-mail já cadastrado."

    assert deve_recusar(Aluno.cadastrar, " ", "a@b.com", "abc123", "abc123") == "Informe o nome."
    assert deve_recusar(Aluno.cadastrar, "Ana", "ab.com", "abc123", "abc123") == "Informe um e-mail válido."

    mensagem = deve_recusar(Aluno.cadastrar, "Ana", "a@b.com", "123", "123")
    assert mensagem == "A senha deve ter pelo menos 6 caracteres."

    mensagem = deve_recusar(Aluno.cadastrar, "Ana", "a@b.com", "abc123", "abc124")
    assert mensagem == "As senhas não conferem."


def testar_autenticacao():
    aluno, multipla, verdadeiro_falso = criar_cenario()

    entrou = Usuario.autenticar(" ALUNO@Teste.com ", SENHA_TESTE)
    assert isinstance(entrou, Aluno)
    assert entrou.id == aluno.id

    assert Usuario.autenticar("aluno@teste.com", "errada") is None
    assert Usuario.autenticar("ninguem@teste.com", SENHA_TESTE) is None


def testar_busca_de_professor():
    aluno, multipla, verdadeiro_falso = criar_cenario()

    professor = Usuario.buscar_por_id(multipla.professor_id)
    assert isinstance(professor, Professor)
    assert professor.nome == "Ana Souza"
    assert professor.matricula == "P0001"
    assert Aluno.buscar_por_id(professor.id) is None


def testar_listagem_de_alunos():
    criar_cenario()
    Aluno.cadastrar("Bruna Alves", "bruna@teste.com", "abc123", "abc123")

    nomes = []
    for aluno in Aluno.listar_todos():
        nomes.append(aluno.nome)
    assert nomes == ["Bruna Alves", "Carlos Lima"]


if __name__ == "__main__":
    testar_cadastro_limpa_dados()
    testar_cadastro_recusado()
    testar_autenticacao()
    testar_busca_de_professor()
    testar_listagem_de_alunos()
    print("Todos os testes de usuário passaram.")
