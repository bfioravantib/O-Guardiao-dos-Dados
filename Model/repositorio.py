"""Acesso aos dados: perguntas, jogadores e histórico de partidas."""
import json
import secrets
from datetime import datetime, timezone

from Model.banco import USA_POSTGRES, inserir_perguntas_iniciais, obter
from Model.config import CRITERIOS_AVALIACAO, FUSO, NOTA_MAXIMA
from Model.perguntas_iniciais import PERGUNTAS_INICIAIS


def agora():
    """Data e hora atuais no fuso configurado (horário de Brasília por padrão)."""
    return datetime.now(FUSO)


def _ler_data(texto):
    """Converte a data gravada para o fuso configurado.

    Datas novas são gravadas com o fuso (ex.: 2026-11-10T11:18:00-03:00). As antigas, sem fuso, foram gravadas
    no horário do servidor: UTC no Vercel (PostgreSQL) ou o horário do computador (SQLite local).
    """
    data = datetime.fromisoformat(texto)
    if data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc) if USA_POSTGRES else data.astimezone()
    return data.astimezone(FUSO)


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
    """Apaga todas as perguntas e grava as de Model/perguntas_iniciais.py."""
    conexao = obter()
    conexao.execute('DELETE FROM perguntas')
    inserir_perguntas_iniciais(conexao)
    conexao.commit()


def adicionar_perguntas_faltantes():
    """Grava as perguntas de Model/perguntas_iniciais.py que ainda não estão no banco (compara pelo enunciado).

    Não apaga nem altera nenhuma pergunta existente. Retorna quantas foram adicionadas.
    """
    conexao = obter()
    existentes = {linha['enunciado'] for linha in conexao.execute('SELECT enunciado FROM perguntas').fetchall()}
    novas = [p for p in PERGUNTAS_INICIAIS if p['enunciado'] not in existentes]
    if novas:
        inserir_perguntas_iniciais(conexao, novas)
        conexao.commit()
    return len(novas)


def novo_jogador():
    """Próximo número de jogador (1, 2, 3...), um por jornada concluída.

    O número é o id gerado pelo banco na tabela "jogadores", então nunca se repete, mesmo com várias jornadas
    terminando ao mesmo tempo. O código aleatório só preenche a coluna (não identifica ninguém).
    """
    conexao = obter()
    numero = conexao.execute('INSERT INTO jogadores (codigo) VALUES (?) RETURNING id',
                             (secrets.token_hex(16),)).fetchone()['id']
    conexao.commit()
    return numero


def rotulo_jogador(numero):
    return f'Jogador {numero}'


def registrar_partida(respostas, participante=None):
    """Grava uma partida. Cada resposta: {pergunta_id, enunciado, escolhida, correta}. Retorna o id da partida."""
    conexao = obter()
    acertos = sum(1 for r in respostas if r['escolhida'] == r['correta'])
    partida_id = conexao.execute(
        'INSERT INTO partidas (data, total, acertos, participante) VALUES (?, ?, ?, ?) RETURNING id',
        (agora().isoformat(timespec='seconds'), len(respostas), acertos, participante or None),
    ).fetchone()['id']
    conexao.executemany(
        'INSERT INTO respostas (partida_id, pergunta_id, enunciado, escolhida, correta) VALUES (?, ?, ?, ?, ?)',
        [(partida_id, r['pergunta_id'], r['enunciado'], r['escolhida'], r['correta']) for r in respostas],
    )
    conexao.commit()
    return partida_id


def percentual_acerto(acertos, total):
    """Percentual de acerto inteiro (0,5 arredonda para cima), ou None quando não há respostas.

    Usado na tela, nos gráficos e no PDF, para que todos mostrem exatamente o mesmo número.
    """
    return (acertos * 200 + total) // (total * 2) if total else None


def _montar_resposta(linha):
    return {
        'pergunta_id': linha['pergunta_id'],
        'enunciado': linha['enunciado'],
        'escolhida': linha['escolhida'],
        'correta': linha['correta'],
        'acertou': linha['escolhida'] == linha['correta'],
    }


def _montar_partida(linha, respostas):
    return {
        'id': linha['id'],
        'data': _ler_data(linha['data']),
        'participante': linha['participante'],
        'total': linha['total'],
        'acertos': linha['acertos'],
        'erros': linha['total'] - linha['acertos'],
        'taxa': percentual_acerto(linha['acertos'], linha['total']),
        'respostas': respostas,
    }


def obter_partida(partida_id):
    linha = obter().execute('SELECT * FROM partidas WHERE id = ?', (partida_id,)).fetchone()
    if not linha:
        return None
    respostas = obter().execute(
        'SELECT pergunta_id, enunciado, escolhida, correta FROM respostas WHERE partida_id = ? ORDER BY id',
        (partida_id,),
    ).fetchall()
    return _montar_partida(linha, [_montar_resposta(r) for r in respostas])


def listar_partidas():
    """Registro de cada conclusão do questionário, mais recentes primeiro.

    Cada partida recebe 'numero' (1 = a mais antiga). Duas consultas no total, em vez de uma por partida.
    """
    linhas = obter().execute('SELECT * FROM partidas ORDER BY id DESC').fetchall()
    respostas = {}
    for r in obter().execute(
        'SELECT partida_id, pergunta_id, enunciado, escolhida, correta FROM respostas ORDER BY id'
    ).fetchall():
        respostas.setdefault(r['partida_id'], []).append(_montar_resposta(r))
    partidas = [_montar_partida(linha, respostas.get(linha['id'], [])) for linha in linhas]
    for i, partida in enumerate(partidas):
        partida['numero'] = len(partidas) - i
    return partidas


def medias_por_participante(partidas):
    """Média de aproveitamento de cada participante, a partir da lista de listar_partidas().

    Nomes iguais com maiúsculas/minúsculas diferentes contam como a mesma pessoa (vale a grafia mais recente).
    Jornadas sem nome (anteriores ao campo) formam o grupo "anônimo", sempre por último.
    A média é a das porcentagens de cada jornada, como a "Média de Aproveitamento" do registro.
    """
    grupos = {}
    for partida in sorted(partidas, key=lambda p: p['id']):
        nome = partida['participante']
        grupo = grupos.setdefault(nome.casefold() if nome else None,
                                  {'nome': nome, 'anonimo': not nome, 'jornadas': 0, 'soma_taxas': 0, 'acertos': 0})
        if nome:
            grupo['nome'] = nome
        grupo['jornadas'] += 1
        grupo['soma_taxas'] += partida['taxa'] or 0
        grupo['acertos'] += partida['acertos']

    participantes = []
    for grupo in grupos.values():
        participantes.append({
            'nome': grupo['nome'],
            'anonimo': grupo['anonimo'],
            'jornadas': grupo['jornadas'],
            'media': percentual_acerto(grupo['soma_taxas'], grupo['jornadas'] * 100),
            'media_acertos': grupo['acertos'] / grupo['jornadas'],
        })
    participantes.sort(key=lambda p: (p['anonimo'], -p['media'], (p['nome'] or '').casefold()))
    return participantes


def resumo_partidas():
    linha = obter().execute(
        'SELECT COUNT(*) AS partidas, COALESCE(SUM(total), 0) AS respostas, COALESCE(SUM(acertos), 0) AS acertos FROM partidas'
    ).fetchone()
    resumo = {chave: int(linha[chave]) for chave in ('partidas', 'respostas', 'acertos')}
    resumo['erros'] = resumo['respostas'] - resumo['acertos']
    resumo['taxa'] = percentual_acerto(resumo['acertos'], resumo['respostas'])
    return resumo


def estatisticas_por_pergunta():
    """Acertos e erros de cada pergunta, somados a partir das respostas gravadas.

    Inclui as perguntas atuais (mesmo sem respostas) e as já excluídas que constam no histórico.
    Cada item recebe 'numero' (posição na lista, usada na tela e no PDF).
    """
    estatisticas = {
        p['id']: {'id': p['id'], 'enunciado': p['enunciado'], 'respostas': 0, 'acertos': 0, 'excluida': False}
        for p in listar_perguntas()
    }
    linhas = obter().execute(
        'SELECT pergunta_id, MAX(enunciado) AS enunciado, COUNT(*) AS respostas, '
        'SUM(CASE WHEN escolhida = correta THEN 1 ELSE 0 END) AS acertos '
        'FROM respostas GROUP BY pergunta_id ORDER BY pergunta_id'
    ).fetchall()
    for linha in linhas:
        est = estatisticas.setdefault(
            linha['pergunta_id'],
            {'id': linha['pergunta_id'], 'enunciado': linha['enunciado'], 'excluida': True},
        )
        est['respostas'] = int(linha['respostas'])
        est['acertos'] = int(linha['acertos'])
    lista = list(estatisticas.values())
    for numero, est in enumerate(lista, 1):
        est['numero'] = numero
        est['erros'] = est['respostas'] - est['acertos']
        est['taxa'] = percentual_acerto(est['acertos'], est['respostas'])
    return lista


CHAVES_AVALIACAO = [c['chave'] for c in CRITERIOS_AVALIACAO]


def registrar_avaliacao(partida_id, notas, comentario):
    """Grava a avaliação de uma jornada. 'notas' tem uma nota (1 a NOTA_MAXIMA) para cada critério.

    Se a jornada já foi avaliada, não grava de novo (vale a primeira avaliação).
    """
    conexao = obter()
    conexao.execute(
        'INSERT INTO avaliacoes (partida_id, data, dificuldade, facilidade, relevancia, comentario) '
        'VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (partida_id) DO NOTHING',
        (partida_id, agora().isoformat(timespec='seconds'), *(notas[c] for c in CHAVES_AVALIACAO), comentario or None),
    )
    conexao.commit()


def _montar_avaliacao(linha):
    avaliacao = {chave: linha[chave] for chave in ('id', 'partida_id', 'comentario', *CHAVES_AVALIACAO)}
    avaliacao['data'] = _ler_data(linha['data'])
    avaliacao['participante'] = linha['participante']
    return avaliacao


def obter_avaliacao(partida_id):
    linha = obter().execute(
        'SELECT a.*, p.participante FROM avaliacoes a JOIN partidas p ON p.id = a.partida_id WHERE a.partida_id = ?',
        (partida_id,),
    ).fetchone()
    return _montar_avaliacao(linha) if linha else None


def listar_avaliacoes():
    """Todas as avaliações, mais recentes primeiro, com o jogador da jornada avaliada."""
    linhas = obter().execute(
        'SELECT a.*, p.participante FROM avaliacoes a JOIN partidas p ON p.id = a.partida_id ORDER BY a.id DESC'
    ).fetchall()
    return [_montar_avaliacao(linha) for linha in linhas]


def resumo_avaliacoes(avaliacoes):
    """Para cada critério: média (uma casa decimal) e distribuição (quantas avaliações deram cada nota)."""
    resumo = []
    for criterio in CRITERIOS_AVALIACAO:
        notas = [a[criterio['chave']] for a in avaliacoes]
        distribuicao = [notas.count(nota) for nota in range(1, NOTA_MAXIMA + 1)]
        resumo.append({
            **criterio,
            'media': round(sum(notas) / len(notas), 1) if notas else None,
            'distribuicao': distribuicao,
            'maior_contagem': max(distribuicao),
        })
    return resumo


def limpar_partidas():
    """Apaga o histórico (jornadas, respostas e avaliações) e recomeça a numeração do "Jogador 1"."""
    conexao = obter()
    conexao.execute('DELETE FROM partidas')
    if USA_POSTGRES:
        conexao.execute('TRUNCATE jogadores RESTART IDENTITY')
    else:
        conexao.execute('DELETE FROM jogadores')
        conexao.execute("DELETE FROM sqlite_sequence WHERE name = 'jogadores'")
    conexao.commit()
