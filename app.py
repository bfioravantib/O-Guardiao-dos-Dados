"""Ponto de entrada do quiz. Execute: python app.py  e acesse http://127.0.0.1:5000"""
import os
import secrets

from flask import Flask

from Controller.admin import admin_bp
from Controller.jogo import jogo_bp
from Controller.menu import menu_bp
from Model import banco
from Model.config import RAIZ


def criar_app():
    app = Flask(
        __name__,
        template_folder=str(RAIZ / 'View' / 'Página'),
        static_folder=str(RAIZ / 'View' / 'Estilo'),
        static_url_path='/estilo',
    )
    # Sem QUIZ_SECRET_KEY definida, uma chave aleatória é gerada a cada início (sessões abertas se perdem ao reiniciar).
    app.config['SECRET_KEY'] = os.environ.get('QUIZ_SECRET_KEY') or secrets.token_hex(32)

    banco.inicializar()
    app.teardown_appcontext(banco.fechar)

    app.register_blueprint(menu_bp)
    app.register_blueprint(jogo_bp)
    app.register_blueprint(admin_bp)
    return app


# Instância no nível do módulo: usada pelo Vercel (e por servidores WSGI como gunicorn).
app = criar_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
