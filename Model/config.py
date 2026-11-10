"""Configurações gerais do quiz."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent

# PIN de acesso à área administrativa. O padrão '1234' é só para uso local: em produção defina o PIN real
# na variável de ambiente QUIZ_PIN_ADMIN (no Vercel), para que ele não fique público no GitHub.
PIN_ADMIN = os.environ.get('QUIZ_PIN_ADMIN', '1234')

# Banco PostgreSQL (ex.: Neon). Quando definido, é usado no lugar do SQLite.
# A integração Neon do Vercel cria DATABASE_URL automaticamente; POSTGRES_URL é aceito como alternativa.
URL_BANCO = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

# Arquivo do banco SQLite, usado quando URL_BANCO não está definido (criado automaticamente na primeira execução).
# No Vercel o sistema de arquivos é somente leitura, exceto /tmp (que é temporário).
_BANCO_PADRAO = Path('/tmp/quiz.db') if os.environ.get('VERCEL') else RAIZ / 'quiz.db'
CAMINHO_BANCO = Path(os.environ.get('QUIZ_BANCO', _BANCO_PADRAO))

# Fuso horário usado para gravar e exibir datas (os servidores do Vercel rodam em UTC).
FUSO = ZoneInfo(os.environ.get('QUIZ_FUSO', 'America/Sao_Paulo'))

LETRAS = ['A', 'B', 'C', 'D', 'E']
QTD_ALTERNATIVAS = 5

# Tamanho máximo do nome do participante (vale para o campo do menu e para o que é gravado no banco).
TAMANHO_MAXIMO_NOME = 40
