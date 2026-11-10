"""Área administrativa: estatísticas por pergunta, registro de jornadas, avaliações do quiz (com relatórios em PDF)
e cadastro de perguntas."""
import hmac
from io import BytesIO

from flask import Blueprint, abort, redirect, render_template, request, send_file, session, url_for

from Controller import relatorio_pdf
from Controller.graficos import fatias_pizza
from Model import repositorio
from Model.config import BANCO_TEMPORARIO, LETRAS, NOTA_MAXIMA, PIN_ADMIN, QTD_ALTERNATIVAS, SEM_CHAVE_SESSAO
from Model.perguntas_iniciais import PERGUNTAS_INICIAIS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Globais (e não context processor) para ficarem visíveis também dentro de macros importadas, como _graficos.html.
admin_bp.add_app_template_global(fatias_pizza)
admin_bp.add_app_template_global(repositorio.percentual_acerto)


@admin_bp.context_processor
def alertas_de_configuracao():
    """Problemas de configuração do Vercel que fazem dados ou sessões se perderem (exibidos no topo do admin)."""
    alertas = []
    if BANCO_TEMPORARIO:
        alertas.append('Banco de dados temporário: o site está no Vercel sem PostgreSQL (variável DATABASE_URL). '
                       'Cada servidor do Vercel usa um banco próprio, que é apagado sozinho, então as jornadas, '
                       'avaliações e perguntas cadastradas se perdem. Conecte um banco Neon ao projeto em '
                       'Storage e faça um Redeploy.')
    if SEM_CHAVE_SESSAO:
        alertas.append('Variável QUIZ_SECRET_KEY não definida: jogadores podem perder a jornada no meio e o login do '
                       'admin pode cair. Defina-a em Settings → Environment Variables e faça um Redeploy.')
    return {'alertas_configuracao': alertas}


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
            return redirect(url_for('admin.estatisticas'))
        erro = True
    return render_template('admin_login.html', erro=erro)


@admin_bp.get('/sair')
def sair():
    session.pop('admin', None)
    return redirect(url_for('menu.inicio'))


@admin_bp.get('/')
def inicio():
    return redirect(url_for('admin.estatisticas'))


# ---------- Estatísticas por pergunta ----------

def _estatisticas_selecionadas():
    """Estatísticas das perguntas marcadas na tela (parâmetro ?p=<id>, repetido); sem marcação, todas."""
    estatisticas = repositorio.estatisticas_por_pergunta()
    marcadas = set(request.args.getlist('p', type=int))
    selecionadas = [e for e in estatisticas if e['id'] in marcadas]
    return estatisticas, marcadas, selecionadas or estatisticas


@admin_bp.get('/estatisticas')
def estatisticas():
    estatisticas, marcadas, selecionadas = _estatisticas_selecionadas()
    return render_template(
        'admin_estatisticas.html',
        resumo=repositorio.resumo_partidas(),
        estatisticas=estatisticas,
        marcadas=marcadas,
        graficos=selecionadas if request.args.get('graficos') else None,
    )


@admin_bp.get('/estatisticas/pdf')
def estatisticas_pdf():
    _, marcadas, selecionadas = _estatisticas_selecionadas()
    pdf = relatorio_pdf.relatorio_estatisticas(repositorio.resumo_partidas(), selecionadas, filtrado=bool(marcadas))
    return _baixar_pdf(pdf, 'estatisticas')


# ---------- Registro de jornadas (cada conclusão do questionário) ----------

@admin_bp.get('/jornadas')
def jornadas():
    partidas = repositorio.listar_partidas()
    taxas = [p['taxa'] for p in partidas if p['taxa'] is not None]
    return render_template(
        'admin_jornadas.html',
        partidas=partidas,
        media=repositorio.percentual_acerto(sum(taxas), len(taxas) * 100),
        melhor=max(taxas) if taxas else None,
        participantes=repositorio.medias_por_participante(partidas),
        letras=LETRAS,
    )


@admin_bp.get('/jornadas/pdf')
def jornadas_pdf():
    partidas = repositorio.listar_partidas()
    pdf = relatorio_pdf.relatorio_jornadas(
        repositorio.resumo_partidas(), partidas, repositorio.medias_por_participante(partidas)
    )
    return _baixar_pdf(pdf, 'jornadas')


@admin_bp.post('/jornadas/limpar')
def limpar_jornadas():
    repositorio.limpar_partidas()
    return redirect(url_for('admin.jornadas'))


# ---------- Avaliações do quiz (validação: notas de 1 a 10 e sugestões) ----------

def _dados_avaliacoes():
    avaliacoes = repositorio.listar_avaliacoes()
    jornadas = repositorio.resumo_partidas()['partidas']
    return {
        'avaliacoes': avaliacoes,
        'criterios': repositorio.resumo_avaliacoes(avaliacoes),
        'jornadas': jornadas,
        # Quantas jornadas concluídas foram avaliadas (taxa de resposta da validação).
        'taxa_resposta': repositorio.percentual_acerto(len(avaliacoes), jornadas),
        'com_comentario': sum(1 for a in avaliacoes if a['comentario']),
    }


@admin_bp.get('/avaliacoes')
def avaliacoes():
    dados = _dados_avaliacoes()
    so_comentarios = bool(request.args.get('comentarios'))
    lista = [a for a in dados['avaliacoes'] if a['comentario']] if so_comentarios else dados['avaliacoes']
    return render_template('admin_avaliacoes.html', **dados, lista=lista, so_comentarios=so_comentarios,
                           nota_maxima=NOTA_MAXIMA)


@admin_bp.get('/avaliacoes/pdf')
def avaliacoes_pdf():
    return _baixar_pdf(relatorio_pdf.relatorio_avaliacoes(**_dados_avaliacoes()), 'avaliacoes')


def _baixar_pdf(conteudo, nome):
    return send_file(
        BytesIO(conteudo),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'guardiao-{nome}-{repositorio.agora():%Y-%m-%d}.pdf',
    )


# ---------- Perguntas ----------

@admin_bp.get('/perguntas')
def perguntas():
    return render_template(
        'admin_perguntas.html',
        perguntas=repositorio.listar_perguntas(),
        letras=LETRAS,
        total_padrao=len(PERGUNTAS_INICIAIS),
        adicionadas=request.args.get('adicionadas', type=int),
    )


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


@admin_bp.post('/perguntas/adicionar-padrao')
def adicionar_perguntas_padrao():
    """Adiciona as provações padrão que ainda não estão no banco, sem apagar nem alterar as existentes."""
    return redirect(url_for('admin.perguntas', adicionadas=repositorio.adicionar_perguntas_faltantes()))


@admin_bp.post('/perguntas/restaurar')
def restaurar_perguntas():
    repositorio.restaurar_perguntas_iniciais()
    return redirect(url_for('admin.perguntas'))
