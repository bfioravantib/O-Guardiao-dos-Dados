from flask import Blueprint, render_template

from Model import repositorio

menu_bp = Blueprint('menu', __name__)


@menu_bp.get('/')
def inicio():
    return render_template('menuprincipal.html', total_perguntas=repositorio.contar_perguntas())
