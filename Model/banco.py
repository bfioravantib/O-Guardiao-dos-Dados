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
    id           {ID},
    data         TEXT    NOT NULL,
    total        INTEGER NOT NULL,
    acertos      INTEGER NOT NULL,
    participante TEXT               -- rótulo anônimo, ex.: "Jogador 3" (NULL nas jornadas mais antigas)
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

# Tabelas criadas depois da primeira versão. Ficam fora do ESQUEMA porque são criadas por _atualizar_esquema(),
# tanto em bancos novos quanto nos que já existiam (o quiz.db local e o Neon).
TABELAS_ADICIONAIS = [
    # Numeração anônima dos jogadores: o id gerado pelo banco é o número do "Jogador N" (sem repetir, mesmo com
    # vários acessos simultâneos). O código aleatório fica na sessão do navegador para reconhecer o jogador nas
    # próximas jornadas, sem guardar nenhum dado pessoal.
    """CREATE TABLE IF NOT EXISTS jogadores (
    id     {ID},
    codigo TEXT NOT NULL UNIQUE
)""",
    # Avaliação do quiz respondida ao final da jornada (notas de 1 a 10 e sugestão opcional), no máximo uma por
    # jornada. Apagar a jornada ("Limpar histórico") apaga a avaliação junto.
    """CREATE TABLE IF NOT EXISTS avaliacoes (
    id          {ID},
    partida_id  INTEGER NOT NULL UNIQUE REFERENCES partidas(id) ON DELETE CASCADE,
    data        TEXT    NOT NULL,
    dificuldade INTEGER NOT NULL,
    facilidade  INTEGER NOT NULL,
    relevancia  INTEGER NOT NULL,
    comentario  TEXT
)""",
]


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


def inserir_perguntas_iniciais(conexao, perguntas=PERGUNTAS_INICIAIS):
    """Grava perguntas no formato de Model/perguntas_iniciais.py (por padrão, todas as de lá)."""
    conexao.executemany(
        'INSERT INTO perguntas (enunciado, alternativas, correta, comentario) VALUES (?, ?, ?, ?)',
        [(p['enunciado'], json.dumps(p['alternativas'], ensure_ascii=False), p['correta'], p['comentario'])
         for p in perguntas],
    )


def _tabela_perguntas_existe(conexao):
    if USA_POSTGRES:
        sql = "SELECT to_regclass('perguntas') IS NOT NULL AS existe"
    else:
        sql = "SELECT COUNT(*) > 0 AS existe FROM sqlite_master WHERE type = 'table' AND name = 'perguntas'"
    return bool(conexao.execute(sql).fetchone()['existe'])


def _coluna_existe(conexao, tabela, coluna):
    if USA_POSTGRES:
        sql = ('SELECT COUNT(*) > 0 AS existe FROM information_schema.columns '
               'WHERE table_schema = current_schema() AND table_name = ? AND column_name = ?')
        return bool(conexao.execute(sql, (tabela, coluna)).fetchone()['existe'])
    return any(linha['name'] == coluna for linha in conexao.execute(f'PRAGMA table_info({tabela})').fetchall())


def _atualizar_esquema(conexao):
    """Ajustes em bancos criados por versões anteriores do app (o SQLite local e o Neon já em uso)."""
    if not _coluna_existe(conexao, 'partidas', 'participante'):
        conexao.execute('ALTER TABLE partidas ADD COLUMN participante TEXT')
    for tabela in TABELAS_ADICIONAIS:
        conexao.execute(tabela.format(ID=COLUNA_ID))


def inicializar():
    """Cria as tabelas (com as perguntas padrão) quando o banco ainda não existe e atualiza bancos antigos."""
    with closing(conectar()) as conexao:
        if USA_POSTGRES:
            # No Vercel várias instâncias podem iniciar ao mesmo tempo: a trava evita cadastrar as perguntas duas vezes.
            conexao.execute('SELECT pg_advisory_xact_lock(7240513)')
        if not _tabela_perguntas_existe(conexao):
            for comando in ESQUEMA.format(ID=COLUNA_ID).split(';'):
                if comando.strip():
                    conexao.execute(comando)
            inserir_perguntas_iniciais(conexao)
        _atualizar_esquema(conexao)
        conexao.commit()  # também libera a trava do PostgreSQL
