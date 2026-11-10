"""Tela inicial: nome do participante e botão para começar o questionário."""
from flask import Blueprint, render_template

from Model import repositorio
from Model.config import TAMANHO_MAXIMO_NOME

menu_bp = Blueprint('menu', __name__)


@menu_bp.get('/')
def inicio():
    return render_template(
        'menuprincipal.html',
        total_perguntas=repositorio.contar_perguntas(),
        tamanho_maximo_nome=TAMANHO_MAXIMO_NOME,
    )
