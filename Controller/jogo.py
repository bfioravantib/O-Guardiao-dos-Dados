"""Fluxo do jogo. O andamento da partida fica na sessão; ela só é gravada no banco ao terminar."""
import random

from flask import Blueprint, redirect, render_template, request, session, url_for

from Model import repositorio
from Model.config import (CRITERIOS_AVALIACAO, LETRAS, NOTA_MAXIMA, PERGUNTAS_POR_JORNADA,
                          TAMANHO_MAXIMO_COMENTARIO)

jogo_bp = Blueprint('jogo', __name__, url_prefix='/jogo')


def _numero_jogador():
    """Número anônimo do jogador deste navegador; na primeira jornada concluída ele recebe o próximo número."""
    codigo = session.get('jogador')
    numero = repositorio.numero_jogador(codigo) if codigo else None
    if numero is None:
        numero, session['jogador'] = repositorio.novo_jogador()
    return numero


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
    participante = repositorio.rotulo_jogador(_numero_jogador())
    session['ultima_partida'] = repositorio.registrar_partida(jogo['respostas'], participante)
    return redirect(url_for('jogo.resultado'))


@jogo_bp.get('/')
def iniciar():
    ids = [p['id'] for p in repositorio.listar_perguntas()]
    if not ids:
        return render_template('sem_perguntas.html')
    # Sorteia as perguntas da jornada (ordem aleatória, sem repetir).
    sorteadas = random.sample(ids, min(PERGUNTAS_POR_JORNADA, len(ids)))
    session['jogo'] = {'perguntas': sorteadas, 'indice': 0, 'respostas': []}
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


def _ultima_partida():
    partida_id = session.get('ultima_partida')
    return repositorio.obter_partida(partida_id) if partida_id else None


@jogo_bp.get('/resultado')
def resultado():
    partida = _ultima_partida()
    if partida is None:
        return redirect(url_for('menu.inicio'))
    return _tela_resultado(partida)


def _tela_resultado(partida, erro=None, preenchido=None):
    """Tela final: placar, título conquistado e o formulário de avaliação (ou o agradecimento, se já avaliou)."""
    percentual = partida['taxa']  # mesmo arredondamento do registro de jornadas
    if percentual == 100:
        mensagem = 'Perfeito! Você acertou todas.'
    elif percentual >= 70:
        mensagem = 'Muito bem!'
    elif percentual >= 40:
        mensagem = 'Bom resultado!'
    else:
        mensagem = 'Continue praticando!'
    return render_template(
        'resultado.html',
        partida=partida,
        percentual=percentual,
        mensagem=mensagem,
        avaliacao=repositorio.obter_avaliacao(partida['id']),
        criterios=CRITERIOS_AVALIACAO,
        nota_maxima=NOTA_MAXIMA,
        tamanho_maximo_comentario=TAMANHO_MAXIMO_COMENTARIO,
        erro=erro,
        preenchido=preenchido or {},
    )


@jogo_bp.post('/avaliar')
def avaliar():
    """Recebe a avaliação do quiz (notas de 1 a NOTA_MAXIMA e sugestão opcional) da última jornada concluída."""
    partida = _ultima_partida()
    if partida is None:
        return redirect(url_for('menu.inicio'))

    notas = {c['chave']: request.form.get(c['chave'], type=int) for c in CRITERIOS_AVALIACAO}
    comentario = (request.form.get('comentario') or '').strip()[:TAMANHO_MAXIMO_COMENTARIO]
    if not all(nota is not None and 1 <= nota <= NOTA_MAXIMA for nota in notas.values()):
        # Devolve a tela com o que já foi preenchido, para a pessoa não perder o comentário.
        return _tela_resultado(partida, 'Escolha uma nota de 1 a %d em cada pergunta.' % NOTA_MAXIMA,
                               {**notas, 'comentario': comentario}), 400
    repositorio.registrar_avaliacao(partida['id'], notas, comentario)
    return redirect(url_for('jogo.resultado') + '#avaliacao')
