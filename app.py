"""Ponto de entrada do quiz. Execute: python app.py  e acesse http://127.0.0.1:5000"""
import os
import secrets

from flask import Flask

from Controller.admin import admin_bp
from Controller.graficos import estilo_percentual
from Controller.jogo import jogo_bp
from Controller.menu import menu_bp
from Model import banco
from Model.config import RAIZ


def _paginas_sem_cache(resposta):
    """Páginas HTML nunca ficam guardadas no navegador: depois de um deploy, o celular sempre recebe a versão nova
    (sem isso, navegadores como Brave/Chrome podem reabrir uma cópia antiga da página ao voltar ou restaurar a aba).
    O CSS continua usando o ?v= de base.html para se atualizar."""
    if resposta.mimetype == 'text/html':
        resposta.headers['Cache-Control'] = 'no-store'
    return resposta


def criar_app():
    app = Flask(
        __name__,
        template_folder=str(RAIZ / 'View' / 'Página'),
        static_folder=str(RAIZ / 'View' / 'Estilo'),
        static_url_path='/estilo',
    )
    app.config['SECRET_KEY'] = os.environ.get('QUIZ_SECRET_KEY') or secrets.token_hex(32)

    banco.inicializar()
    app.teardown_appcontext(banco.fechar)
    app.after_request(_paginas_sem_cache)
    app.add_template_global(estilo_percentual)

    app.register_blueprint(menu_bp)
    app.register_blueprint(jogo_bp)
    app.register_blueprint(admin_bp)
    return app


app = criar_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
