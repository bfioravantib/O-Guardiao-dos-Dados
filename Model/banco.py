"""Conexão com o banco e criação do esquema.

Dois bancos são suportados, com o mesmo código de consultas:
- PostgreSQL (ex.: Neon), quando a variável de ambiente DATABASE_URL (ou POSTGRES_URL) está definida.
  É o modo usado em produção no Vercel, onde os dados precisam persistir.
- SQLite local (arquivo quiz.db), quando nenhuma dessas variáveis existe. Prático para desenvolver.

As consultas são escritas com o marcador "?" do SQLite; a classe Conexao o converte para "%s" no PostgreSQL.
"""
import json
import sqlite3
from contextlib import closing

from flask import g

from Model.config import CAMINHO_BANCO, URL_BANCO
from Model.perguntas_iniciais import PERGUNTAS_INICIAIS

USA_POSTGRES = bool(URL_BANCO)

# respostas.pergunta_id não tem chave estrangeira de propósito: o histórico continua
# agrupável mesmo depois que a pergunta é excluída (o enunciado fica copiado na resposta).
# {ID} vira a coluna de chave primária autoincrementada de cada banco.
ESQUEMA = """
CREATE TABLE IF NOT EXISTS perguntas (
    id           {ID},
    enunciado    TEXT    NOT NULL,
    alternativas TEXT    NOT NULL,  -- lista JSON com as 5 alternativas
    correta      INTEGER NOT NULL,
    comentario   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS partidas (
    id      {ID},
    data    TEXT    NOT NULL,
    total   INTEGER NOT NULL,
    acertos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS respostas (
    id          {ID},
    partida_id  INTEGER NOT NULL REFERENCES partidas(id) ON DELETE CASCADE,
    pergunta_id INTEGER NOT NULL,
    enunciado   TEXT    NOT NULL,
    escolhida   INTEGER NOT NULL,
    correta     INTEGER NOT NULL
);
"""
COLUNA_ID = 'SERIAL PRIMARY KEY' if USA_POSTGRES else 'INTEGER PRIMARY KEY AUTOINCREMENT'


class Conexao:
    """Envolve a conexão do SQLite ou do PostgreSQL com a mesma interface (execute, executemany, commit, close)."""

    def __init__(self, bruta):
        self._bruta = bruta

    def _sql(self, sql):
        return sql.replace('?', '%s') if USA_POSTGRES else sql

    def execute(self, sql, parametros=()):
        if USA_POSTGRES:
            cursor = self._bruta.cursor()
            cursor.execute(self._sql(sql), parametros)
            return cursor
        return self._bruta.execute(sql, parametros)

    def executemany(self, sql, lista_parametros):
        if USA_POSTGRES:
            with self._bruta.cursor() as cursor:
                cursor.executemany(self._sql(sql), lista_parametros)
        else:
            self._bruta.executemany(sql, lista_parametros)

    def commit(self):
        self._bruta.commit()

    def close(self):
        self._bruta.close()


def conectar():
    if USA_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row

        # prepare_threshold=None: sem "prepared statements", que não combinam com o pool de conexões do Neon.
        bruta = psycopg.connect(URL_BANCO, row_factory=dict_row, prepare_threshold=None)
    else:
        bruta = sqlite3.connect(CAMINHO_BANCO)
        bruta.row_factory = sqlite3.Row
        bruta.execute('PRAGMA foreign_keys = ON')
    return Conexao(bruta)


def obter():
    """Conexão da requisição atual (aberta sob demanda e fechada no fim da requisição)."""
    if 'banco' not in g:
        g.banco = conectar()
    return g.banco


def fechar(_erro=None):
    conexao = g.pop('banco', None)
    if conexao is not None:
        conexao.close()


def inserir_perguntas_iniciais(conexao):
    conexao.executemany(
        'INSERT INTO perguntas (enunciado, alternativas, correta, comentario) VALUES (?, ?, ?, ?)',
        [(p['enunciado'], json.dumps(p['alternativas'], ensure_ascii=False), p['correta'], p['comentario'])
         for p in PERGUNTAS_INICIAIS],
    )


def _tabela_perguntas_existe(conexao):
    if USA_POSTGRES:
        sql = "SELECT to_regclass('perguntas') IS NOT NULL AS existe"
    else:
        sql = "SELECT COUNT(*) > 0 AS existe FROM sqlite_master WHERE type = 'table' AND name = 'perguntas'"
    return bool(conexao.execute(sql).fetchone()['existe'])


def inicializar():
    """Cria as tabelas e cadastra as perguntas de exemplo apenas quando o banco ainda não existe."""
    with closing(conectar()) as conexao:
        if USA_POSTGRES:
            # No Vercel várias instâncias podem iniciar ao mesmo tempo: a trava evita cadastrar as perguntas duas vezes.
            conexao.execute('SELECT pg_advisory_xact_lock(7240513)')
        if not _tabela_perguntas_existe(conexao):
            for comando in ESQUEMA.format(ID=COLUNA_ID).split(';'):
                if comando.strip():
                    conexao.execute(comando)
            inserir_perguntas_iniciais(conexao)
        conexao.commit()  # também libera a trava do PostgreSQL
