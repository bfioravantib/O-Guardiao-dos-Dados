"""Tela inicial com o botão para começar o questionário."""
from flask import Blueprint, render_template

from Model import repositorio
from Model.config import PERGUNTAS_POR_JORNADA

menu_bp = Blueprint('menu', __name__)


@menu_bp.get('/')
def inicio():
    return render_template(
        'menuprincipal.html',
        total_perguntas=repositorio.contar_perguntas(),
        perguntas_por_jornada=PERGUNTAS_POR_JORNADA,
    )
