"""Configurações gerais do quiz."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent

# PIN de acesso à área administrativa. O padrão '1234' é só para uso local: em produção defina o PIN real
# na variável de ambiente QUIZ_PIN_ADMIN (no Vercel), para que ele não fique público no GitHub.
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


# Banco PostgreSQL (ex.: Neon). Quando definido, é usado no lugar do SQLite.
URL_BANCO = _url_do_banco()

# Arquivo do banco SQLite, usado quando URL_BANCO não está definido (criado automaticamente na primeira execução).
# No Vercel o sistema de arquivos é somente leitura, exceto /tmp (que é temporário).
_BANCO_PADRAO = Path('/tmp/quiz.db') if os.environ.get('VERCEL') else RAIZ / 'quiz.db'
CAMINHO_BANCO = Path(os.environ.get('QUIZ_BANCO', _BANCO_PADRAO))

# Problemas de configuração no Vercel, mostrados como alerta na área administrativa:
# - sem PostgreSQL, cada instância do Vercel tem o seu próprio SQLite temporário e os dados "somem";
# - sem QUIZ_SECRET_KEY, cada instância gera uma chave diferente e as sessões (jogo e login) se perdem.
NO_VERCEL = bool(os.environ.get('VERCEL'))
BANCO_TEMPORARIO = NO_VERCEL and not URL_BANCO
SEM_CHAVE_SESSAO = NO_VERCEL and not os.environ.get('QUIZ_SECRET_KEY')

# Fuso horário usado para gravar e exibir datas (os servidores do Vercel rodam em UTC).
FUSO = ZoneInfo(os.environ.get('QUIZ_FUSO', 'America/Sao_Paulo'))

LETRAS = ['A', 'B', 'C', 'D', 'E']
QTD_ALTERNATIVAS = 5

# Quantas perguntas são sorteadas do banco a cada jornada (se houver menos cadastradas, usa todas).
PERGUNTAS_POR_JORNADA = 5

# Avaliação do quiz exibida ao final da jornada (validação): notas de 1 a NOTA_MAXIMA e um campo de sugestão.
# A chave é a coluna da tabela "avaliacoes" (não mude); os textos podem ser alterados à vontade:
# pergunta (tela do jogador), titulo (gráficos), curto (selos e colunas do PDF), minimo/maximo (extremos da escala).
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
