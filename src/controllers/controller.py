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
        self._app = app
        self._registrar_rotas()

    def _registrar_rotas(self):
        """Vazio na base; cada subclasse redefine."""

    def _adicionar_rota(self, endereco, nome, metodo, metodos=("GET",)):
        """Registra a rota no Flask passando antes pelo controle de acesso."""

        def pagina(**parametros):
            # o mesmo controller atende todo mundo, por isso o usuário fica no g e não no self
            g.usuario = self.__usuario_logado()

            if g.usuario is None:
                session.pop("usuario_id", None)
                session.pop("tipo", None)
                session.pop("nome", None)

            if self.TIPO_USUARIO is not None:
                if g.usuario is None or g.usuario.TIPO != self.TIPO_USUARIO:
                    return self._redirecionar("/login", "Faça login para continuar.", "erro")

            return metodo(**parametros)

        self._app.add_url_rule(endereco, nome, pagina, methods=list(metodos))

    @property
    def usuario(self):
        """Usuário da requisição atual, ou None."""
        return g.get("usuario")

    def __usuario_logado(self):
        """Busca o usuário cujo id está na sessão, ou devolve None."""
        usuario_id = session.get("usuario_id")
        if usuario_id is None:
            return None
        return Usuario.buscar_por_id(usuario_id)

    def _renderizar(self, template, **dados):
        """Monta a página a partir do template."""
        return render_template(template, **dados)

    def _redirecionar(self, endereco, mensagem=None, categoria="sucesso"):
        """Redireciona, com mensagem opcional para a próxima página."""
        if mensagem is not None:
            flash(mensagem, categoria)
        return redirect(endereco)

    def _avisar_erro(self, mensagem):
        """Guarda uma mensagem de erro para a próxima página."""
        flash(mensagem, "erro")
