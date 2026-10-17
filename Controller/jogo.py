"""Fluxo do jogo. O andamento da partida fica na sessão; ela só é gravada no banco ao terminar."""
from flask import Blueprint, redirect, render_template, request, session, url_for

from Model import repositorio
from Model.config import LETRAS

jogo_bp = Blueprint('jogo', __name__, url_prefix='/jogo')


def _pergunta_atual(jogo):
    """Pergunta da posição atual, pulando as que foram excluídas durante a partida."""
    while jogo['indice'] < len(jogo['perguntas']):
        pergunta = repositorio.obter_pergunta(jogo['perguntas'][jogo['indice']])
        if pergunta:
            return pergunta
        jogo['perguntas'].pop(jogo['indice'])
        session.modified = True
    return None


def _finalizar(jogo):
    session.pop('jogo', None)
    if not jogo['respostas']:
        return redirect(url_for('menu.inicio'))
    session['ultima_partida'] = repositorio.registrar_partida(jogo['respostas'])
    return redirect(url_for('jogo.resultado'))


@jogo_bp.get('/')
def iniciar():
    ids = [p['id'] for p in repositorio.listar_perguntas()]
    if not ids:
        return render_template('sem_perguntas.html')
    session['jogo'] = {'perguntas': ids, 'indice': 0, 'respostas': []}
    return redirect(url_for('jogo.pergunta'))


@jogo_bp.get('/pergunta')
def pergunta():
    jogo = session.get('jogo')
    if not jogo:
        return redirect(url_for('jogo.iniciar'))

    pergunta = _pergunta_atual(jogo)
    if pergunta is None:
        return _finalizar(jogo)

    respondida = len(jogo['respostas']) > jogo['indice']
    resposta = jogo['respostas'][jogo['indice']] if respondida else None
    total = len(jogo['perguntas'])
    return render_template(
        'jogo.html',
        pergunta=pergunta,
        resposta=resposta,
        numero=jogo['indice'] + 1,
        total=total,
        ultima=jogo['indice'] == total - 1,
        letras=LETRAS,
    )


@jogo_bp.post('/responder')
def responder():
    jogo = session.get('jogo')
    if not jogo:
        return redirect(url_for('jogo.iniciar'))

    pergunta = _pergunta_atual(jogo)
    ja_respondida = len(jogo['respostas']) > jogo['indice']
    escolhida = request.form.get('alternativa', type=int)

    if pergunta and not ja_respondida and escolhida is not None and 0 <= escolhida < len(pergunta['alternativas']):
        jogo['respostas'].append({
            'pergunta_id': pergunta['id'],
            'enunciado': pergunta['enunciado'],
            'escolhida': escolhida,
            'correta': pergunta['correta'],
        })
        session.modified = True
    return redirect(url_for('jogo.pergunta'))


@jogo_bp.post('/proxima')
def proxima():
    jogo = session.get('jogo')
    if not jogo:
        return redirect(url_for('jogo.iniciar'))

    if len(jogo['respostas']) > jogo['indice']:
        jogo['indice'] += 1
        session.modified = True
    if jogo['indice'] >= len(jogo['perguntas']):
        return _finalizar(jogo)
    return redirect(url_for('jogo.pergunta'))


@jogo_bp.get('/resultado')
def resultado():
    partida_id = session.get('ultima_partida')
    partida = repositorio.obter_partida(partida_id) if partida_id else None
    if partida is None:
        return redirect(url_for('menu.inicio'))

    percentual = round(partida['acertos'] / partida['total'] * 100)
    if percentual == 100:
        mensagem = 'Perfeito! Você acertou todas.'
    elif percentual >= 70:
        mensagem = 'Muito bem!'
    elif percentual >= 40:
        mensagem = 'Bom resultado!'
    else:
        mensagem = 'Continue praticando!'
    return render_template('resultado.html', partida=partida, percentual=percentual, mensagem=mensagem)
