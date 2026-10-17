"""Páginas do professor."""

from src.controllers.controller import Controller


class ProfessorController(Controller):
    """Cadastro de questões e acompanhamento dos alunos."""

    TIPO_USUARIO = "professor"
