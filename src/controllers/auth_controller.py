"""Entrada e saída do sistema."""

from flask import request, session

from src.controllers.controller import Controller
from src.models.aluno import Aluno
from src.models.usuario import Usuario


class AuthController(Controller):
    """Login, cadastro de aluno, logout e página inicial. Aberto a todos."""

    TIPO_USUARIO = None

    def registrar_rotas(self):
        """Registra as rotas de entrada e saída."""
        self.adicionar_rota("/", "inicio", self.inicio)
        self.adicionar_rota("/login", "login", self.login, ("GET", "POST"))
        self.adicionar_rota("/cadastro", "cadastro", self.cadastro, ("GET", "POST"))
        self.adicionar_rota("/logout", "logout", self.logout)

    def iniciar_sessao(self, usuario):
        """Limpa a sessão e guarda os dados do usuário que entrou."""
        session.clear()
        session["usuario_id"] = usuario.id
        session["tipo"] = usuario.TIPO
        session["nome"] = usuario.primeiro_nome

    def inicio(self):
        """Manda para o login ou para o painel do perfil do usuário."""
        if self.usuario is None:
            return self.redirecionar("/login")
        return self.redirecionar("/" + self.usuario.TIPO)

    def login(self):
        """Mostra o formulário de login e autentica o usuário."""
        email = ""

        if request.method == "POST":
            email = request.form.get("email", "")
            senha = request.form.get("senha", "")

            usuario = Usuario.autenticar(email, senha)
            if usuario is None:
                self.avisar_erro("E-mail ou senha incorretos.")
            else:
                self.iniciar_sessao(usuario)
                return self.redirecionar("/")

        return self.renderizar("login.html", email=email)

    def cadastro(self):
        """Mostra o formulário de cadastro e cria a conta do aluno."""
        nome = ""
        email = ""

        if request.method == "POST":
            nome = request.form.get("nome", "")
            email = request.form.get("email", "")
            senha = request.form.get("senha", "")
            confirmar_senha = request.form.get("confirmar_senha", "")

            try:
                aluno = Aluno.cadastrar(nome, email, senha, confirmar_senha)
            except ValueError as erro:
                self.avisar_erro(str(erro))
            else:
                self.iniciar_sessao(aluno)
                return self.redirecionar("/", "Conta criada com sucesso.")

        return self.renderizar("cadastro.html", nome=nome, email=email)

    def logout(self):
        """Limpa a sessão e volta para o login."""
        session.clear()
        return self.redirecionar("/login", "Você saiu do sistema.")
