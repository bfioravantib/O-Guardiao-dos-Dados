"""Configurações gerais do quiz."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# PIN de acesso à área administrativa (pode ser definido pela variável de ambiente QUIZ_PIN_ADMIN).
PIN_ADMIN = os.environ.get('QUIZ_PIN_ADMIN', '1234')

# Arquivo do banco SQLite (criado automaticamente na primeira execução).
CAMINHO_BANCO = Path(os.environ.get('QUIZ_BANCO', RAIZ / 'quiz.db'))

LETRAS = ['A', 'B', 'C', 'D', 'E']
QTD_ALTERNATIVAS = 5
