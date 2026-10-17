"""Conexão com o banco SQLite e criação do esquema."""
import json
import sqlite3
from contextlib import closing

from flask import g

from Model.config import CAMINHO_BANCO
from Model.perguntas_iniciais import PERGUNTAS_INICIAIS

# respostas.pergunta_id não tem chave estrangeira de propósito: o histórico continua
# agrupável mesmo depois que a pergunta é excluída (o enunciado fica copiado na resposta).
ESQUEMA = """
CREATE TABLE perguntas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    enunciado    TEXT    NOT NULL,
    alternativas TEXT    NOT NULL,  -- lista JSON com as 5 alternativas
    correta      INTEGER NOT NULL,
    comentario   TEXT    NOT NULL
);

CREATE TABLE partidas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    data    TEXT    NOT NULL,
    total   INTEGER NOT NULL,
    acertos INTEGER NOT NULL
);

CREATE TABLE respostas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id  INTEGER NOT NULL REFERENCES partidas(id) ON DELETE CASCADE,
    pergunta_id INTEGER NOT NULL,
    enunciado   TEXT    NOT NULL,
    escolhida   INTEGER NOT NULL,
    correta     INTEGER NOT NULL
);
"""


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


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


def inicializar():
    """Cria as tabelas e cadastra as perguntas de exemplo apenas quando o banco ainda não existe."""
    with closing(conectar()) as conexao:
        existe = conexao.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'perguntas'"
        ).fetchone()
        if not existe:
            conexao.executescript(ESQUEMA)
            inserir_perguntas_iniciais(conexao)
            conexao.commit()
