"""Área administrativa: histórico de respostas e cadastro de perguntas."""
import hmac

from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from Model import repositorio
from Model.config import LETRAS, PIN_ADMIN, QTD_ALTERNATIVAS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def exigir_acesso():
    if request.endpoint != 'admin.login' and not session.get('admin'):
        return redirect(url_for('admin.login'))


# ---------- Acesso ----------

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = False
    if request.method == 'POST':
        if hmac.compare_digest(request.form.get('pin', ''), PIN_ADMIN):
            session['admin'] = True
            return redirect(url_for('admin.respostas'))
        erro = True
    return render_template('admin_login.html', erro=erro)


@admin_bp.get('/sair')
def sair():
    session.pop('admin', None)
    return redirect(url_for('menu.inicio'))


@admin_bp.get('/')
def inicio():
    return redirect(url_for('admin.respostas'))


# ---------- Respostas ----------

@admin_bp.get('/respostas')
def respostas():
    return render_template(
        'admin_respostas.html',
        resumo=repositorio.resumo_partidas(),
        desempenho=repositorio.desempenho_por_pergunta(),
        partidas=repositorio.listar_partidas(),
        letras=LETRAS,
    )


@admin_bp.post('/respostas/limpar')
def limpar_respostas():
    repositorio.limpar_partidas()
    return redirect(url_for('admin.respostas'))


# ---------- Perguntas ----------

@admin_bp.get('/perguntas')
def perguntas():
    return render_template('admin_perguntas.html', perguntas=repositorio.listar_perguntas(), letras=LETRAS)


def _ler_formulario():
    """Lê e valida o formulário de pergunta. Retorna (dados, erros)."""
    dados = {
        'enunciado': request.form.get('enunciado', '').strip(),
        'alternativas': [request.form.get(f'alternativa_{i}', '').strip() for i in range(QTD_ALTERNATIVAS)],
        'correta': request.form.get('correta', type=int),
        'comentario': request.form.get('comentario', '').strip(),
    }
    erros = []
    if not dados['enunciado']:
        erros.append('Informe o enunciado.')
    if not all(dados['alternativas']):
        erros.append(f'Preencha as {QTD_ALTERNATIVAS} alternativas.')
    if dados['correta'] is None or not 0 <= dados['correta'] < QTD_ALTERNATIVAS:
        erros.append('Marque a alternativa correta.')
    if not dados['comentario']:
        erros.append('Informe o comentário.')
    return dados, erros


def _formulario(pergunta, pergunta_id=None, erros=None):
    return render_template(
        'admin_form_pergunta.html',
        pergunta=pergunta,
        pergunta_id=pergunta_id,
        erros=erros or [],
        letras=LETRAS[:QTD_ALTERNATIVAS],
    )


@admin_bp.route('/perguntas/nova', methods=['GET', 'POST'])
def nova_pergunta():
    if request.method == 'POST':
        dados, erros = _ler_formulario()
        if not erros:
            repositorio.salvar_pergunta(**dados)
            return redirect(url_for('admin.perguntas'))
        return _formulario(dados, erros=erros)
    vazia = {'enunciado': '', 'alternativas': [''] * QTD_ALTERNATIVAS, 'correta': None, 'comentario': ''}
    return _formulario(vazia)


@admin_bp.route('/perguntas/<int:pergunta_id>/editar', methods=['GET', 'POST'])
def editar_pergunta(pergunta_id):
    pergunta = repositorio.obter_pergunta(pergunta_id)
    if pergunta is None:
        abort(404)
    if request.method == 'POST':
        dados, erros = _ler_formulario()
        if not erros:
            repositorio.salvar_pergunta(**dados, pergunta_id=pergunta_id)
            return redirect(url_for('admin.perguntas'))
        return _formulario(dados, pergunta_id, erros)
    return _formulario(pergunta, pergunta_id)


@admin_bp.post('/perguntas/<int:pergunta_id>/excluir')
def excluir_pergunta(pergunta_id):
    repositorio.excluir_pergunta(pergunta_id)
    return redirect(url_for('admin.perguntas'))


@admin_bp.post('/perguntas/restaurar')
def restaurar_perguntas():
    repositorio.restaurar_perguntas_iniciais()
    return redirect(url_for('admin.perguntas'))
