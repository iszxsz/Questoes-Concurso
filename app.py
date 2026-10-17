"""Ponto de entrada: cria o servidor Flask e registra as rotas."""

import os

from flask import Flask

from src.controllers.aluno_controller import AlunoController
from src.controllers.auth_controller import AuthController
from src.controllers.professor_controller import ProfessorController

CONTROLLERS = (AuthController, AlunoController, ProfessorController)


def criar_app():
    """Cria a aplicação Flask com todos os controllers registrados."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")

    for classe_controller in CONTROLLERS:
        classe_controller(app)

    return app


if __name__ == "__main__":
    criar_app().run(debug=True)
