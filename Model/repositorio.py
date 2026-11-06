"""Acesso aos dados: perguntas e histórico de partidas."""
import json
from datetime import datetime

from Model.banco import inserir_perguntas_iniciais, obter


# ---------- Perguntas ----------

def _montar_pergunta(linha):
    return {
        'id': linha['id'],
        'enunciado': linha['enunciado'],
        'alternativas': json.loads(linha['alternativas']),
        'correta': linha['correta'],
        'comentario': linha['comentario'],
    }


def listar_perguntas():
    linhas = obter().execute('SELECT * FROM perguntas ORDER BY id').fetchall()
    return [_montar_pergunta(linha) for linha in linhas]


def obter_pergunta(pergunta_id):
    linha = obter().execute('SELECT * FROM perguntas WHERE id = ?', (pergunta_id,)).fetchone()
    return _montar_pergunta(linha) if linha else None


def contar_perguntas():
    return obter().execute('SELECT COUNT(*) AS total FROM perguntas').fetchone()['total']


def salvar_pergunta(enunciado, alternativas, correta, comentario, pergunta_id=None):
    conexao = obter()
    valores = (enunciado, json.dumps(alternativas, ensure_ascii=False), correta, comentario)
    if pergunta_id:
        conexao.execute(
            'UPDATE perguntas SET enunciado = ?, alternativas = ?, correta = ?, comentario = ? WHERE id = ?',
            (*valores, pergunta_id),
        )
    else:
        conexao.execute(
            'INSERT INTO perguntas (enunciado, alternativas, correta, comentario) VALUES (?, ?, ?, ?)',
            valores,
        )
    conexao.commit()


def excluir_pergunta(pergunta_id):
    conexao = obter()
    conexao.execute('DELETE FROM perguntas WHERE id = ?', (pergunta_id,))
    conexao.commit()


def restaurar_perguntas_iniciais():
    conexao = obter()
    conexao.execute('DELETE FROM perguntas')
    inserir_perguntas_iniciais(conexao)
    conexao.commit()


# ---------- Partidas (respostas) ----------

def registrar_partida(respostas):
    """Grava uma partida. Cada resposta: {pergunta_id, enunciado, escolhida, correta}. Retorna o id da partida."""
    conexao = obter()
    acertos = sum(1 for r in respostas if r['escolhida'] == r['correta'])
    # RETURNING id funciona no SQLite e no PostgreSQL (lastrowid só existe no SQLite).
    partida_id = conexao.execute(
        'INSERT INTO partidas (data, total, acertos) VALUES (?, ?, ?) RETURNING id',
        (datetime.now().isoformat(timespec='seconds'), len(respostas), acertos),
    ).fetchone()['id']
    conexao.executemany(
        'INSERT INTO respostas (partida_id, pergunta_id, enunciado, escolhida, correta) VALUES (?, ?, ?, ?, ?)',
        [(partida_id, r['pergunta_id'], r['enunciado'], r['escolhida'], r['correta']) for r in respostas],
    )
    conexao.commit()
    return partida_id


def _respostas_da_partida(partida_id):
    linhas = obter().execute(
        'SELECT pergunta_id, enunciado, escolhida, correta FROM respostas WHERE partida_id = ? ORDER BY id',
        (partida_id,),
    ).fetchall()
    return [{**dict(linha), 'acertou': linha['escolhida'] == linha['correta']} for linha in linhas]


def _montar_partida(linha):
    return {
        'id': linha['id'],
        'data': datetime.fromisoformat(linha['data']),
        'total': linha['total'],
        'acertos': linha['acertos'],
        'respostas': _respostas_da_partida(linha['id']),
    }


def obter_partida(partida_id):
    linha = obter().execute('SELECT * FROM partidas WHERE id = ?', (partida_id,)).fetchone()
    return _montar_partida(linha) if linha else None


def listar_partidas():
    """Partidas mais recentes primeiro."""
    linhas = obter().execute('SELECT * FROM partidas ORDER BY id DESC').fetchall()
    return [_montar_partida(linha) for linha in linhas]


def resumo_partidas():
    linha = obter().execute(
        'SELECT COUNT(*) AS partidas, COALESCE(SUM(total), 0) AS respostas, COALESCE(SUM(acertos), 0) AS acertos FROM partidas'
    ).fetchone()
    return dict(linha)


def desempenho_por_pergunta():
    """Perguntas atuais (mesmo sem respostas) + perguntas já excluídas que constam no histórico."""
    estatisticas = {
        p['id']: {'enunciado': p['enunciado'], 'vezes': 0, 'acertos': 0, 'excluida': False}
        for p in listar_perguntas()
    }
    linhas = obter().execute(
        'SELECT pergunta_id, enunciado, escolhida = correta AS acertou FROM respostas ORDER BY id'
    ).fetchall()
    for linha in linhas:
        est = estatisticas.setdefault(
            linha['pergunta_id'],
            {'enunciado': linha['enunciado'], 'vezes': 0, 'acertos': 0, 'excluida': True},
        )
        est['vezes'] += 1
        est['acertos'] += int(linha['acertou'])  # PostgreSQL devolve booleano; SQLite, 0/1
    return list(estatisticas.values())


def limpar_partidas():
    conexao = obter()
    conexao.execute('DELETE FROM partidas')  # respostas são apagadas em cascata
    conexao.commit()
