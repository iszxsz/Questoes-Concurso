"""Classe base dos controllers."""

from flask import flash, g, redirect, render_template, session

from src.models.usuario import Usuario


class Controller:
    """Base de todos os controllers: rotas, controle de acesso e respostas comuns.

    Attributes:
        TIPO_USUARIO (str | None): None (aberto a todos), "aluno" ou "professor".
    """

    TIPO_USUARIO = None

    def __init__(self, app):
        """Guarda a aplicação e registra as rotas."""
        self.app = app
        self.registrar_rotas()

    def registrar_rotas(self):
        """Vazio na base; cada subclasse redefine."""

    def adicionar_rota(self, endereco, nome, metodo, metodos=("GET",)):
        """Registra a rota no Flask passando antes pelo controle de acesso."""

        def pagina(**parametros):
            # o mesmo controller atende todo mundo, por isso o usuário fica no g e não no self
            g.usuario = self.usuario_logado()

            if self.TIPO_USUARIO is not None:
                if g.usuario is None or g.usuario.tipo != self.TIPO_USUARIO:
                    return self.redirecionar("/login", "Faça login para continuar.", "erro")

            return metodo(**parametros)

        self.app.add_url_rule(endereco, nome, pagina, methods=list(metodos))

    @property
    def usuario(self):
        """Usuário da requisição atual, ou None."""
        return g.get("usuario")

    def usuario_logado(self):
        """Busca o usuário cujo id está na sessão, ou devolve None."""
        usuario_id = session.get("usuario_id")
        if usuario_id is None:
            return None
        return Usuario.buscar_por_id(usuario_id)

    def renderizar(self, template, **dados):
        """Monta a página a partir do template."""
        return render_template(template, **dados)

    def redirecionar(self, endereco, mensagem=None, categoria="sucesso"):
        """Redireciona, com mensagem opcional para a próxima página."""
        if mensagem is not None:
            flash(mensagem, categoria)
        return redirect(endereco)

    def avisar_erro(self, mensagem):
        """Guarda uma mensagem de erro para a próxima página."""
        flash(mensagem, "erro")
