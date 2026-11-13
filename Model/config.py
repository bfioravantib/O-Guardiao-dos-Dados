"""Configurações gerais do quiz."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent

PIN_ADMIN = os.environ.get('QUIZ_PIN_ADMIN', '1234')

def _url_do_banco():
    """Endereço do PostgreSQL (ex.: Neon), ou None para usar o SQLite.

    A integração Neon do Vercel cria DATABASE_URL (e POSTGRES_URL). Se o banco foi conectado com um prefixo
    personalizado, as variáveis ganham esse prefixo (ex.: STORAGE_DATABASE_URL), que também é aceito.
    """
    for nome in ('DATABASE_URL', 'POSTGRES_URL'):
        if os.environ.get(nome):
            return os.environ[nome]
    for sufixo in ('_DATABASE_URL', '_POSTGRES_URL'):
        for nome, valor in sorted(os.environ.items()):
            if nome.endswith(sufixo) and valor:
                return valor
    return None


URL_BANCO = _url_do_banco()

_BANCO_PADRAO = Path('/tmp/quiz.db') if os.environ.get('VERCEL') else RAIZ / 'quiz.db'
CAMINHO_BANCO = Path(os.environ.get('QUIZ_BANCO', _BANCO_PADRAO))

NO_VERCEL = bool(os.environ.get('VERCEL'))
BANCO_TEMPORARIO = NO_VERCEL and not URL_BANCO
SEM_CHAVE_SESSAO = NO_VERCEL and not os.environ.get('QUIZ_SECRET_KEY')

FUSO = ZoneInfo(os.environ.get('QUIZ_FUSO', 'America/Sao_Paulo'))

LETRAS = ['A', 'B', 'C', 'D', 'E']
QTD_ALTERNATIVAS = 5

PERGUNTAS_POR_JORNADA = 5

NOTA_MAXIMA = 10
TAMANHO_MAXIMO_COMENTARIO = 1000
CRITERIOS_AVALIACAO = [
    {'chave': 'dificuldade', 'pergunta': 'Qual foi o nível de dificuldade das perguntas?',
     'titulo': 'Dificuldade das perguntas', 'curto': 'Dificuldade', 'minimo': 'Muito fáceis', 'maximo': 'Muito difíceis'},
    {'chave': 'facilidade', 'pergunta': 'Quão fácil foi utilizar o quiz?',
     'titulo': 'Facilidade de uso', 'curto': 'Uso', 'minimo': 'Muito difícil', 'maximo': 'Muito fácil'},
    {'chave': 'relevancia', 'pergunta': 'Quão relevantes foram as informações que você recebeu?',
     'titulo': 'Relevância das informações', 'curto': 'Relevância', 'minimo': 'Nada relevantes', 'maximo': 'Muito relevantes'},
]
