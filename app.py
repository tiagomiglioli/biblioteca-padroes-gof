"""Inicia e configura o Flask. Aqui as peças são ligadas uma única vez."""
import logging
from datetime import date
from getpass import getpass
from pathlib import Path

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect

from config import configuracao_flask, parametros_mysql
from dominio.configuracao_singleton import ConfiguracaoSistema
from dominio.persistencia_factory import criar_fabrica
from dominio.tratadores import montar_sistema
from persistencia.mysql import executar_arquivo_sql
from persistencia.migracoes import migrar_atendentes
from web.autenticacao import configurar_login
from web.rotas import paginas

RAIZ = Path(__file__).resolve().parent


def criar_app(config_extra=None, fabrica=None, relogio=date.today):
    """Monta a aplicação. `fabrica` e `relogio` existem para os testes injetarem os seus."""
    app = Flask(__name__)
    app.config.update(configuracao_flask())
    app.config.update(config_extra or {})
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Defina SECRET_KEY no arquivo .env (veja .env.example).")

    configuracao = ConfiguracaoSistema.obter_instancia()                 # Singleton (R11)
    # Abstract Factory (R08): a família de persistência é escolhida aqui, uma única vez.
    fabrica = fabrica or criar_fabrica(configuracao.perfil_persistencia, parametros_mysql())
    app.sistema = montar_sistema(fabrica, configuracao, relogio)

    CSRFProtect(app)                      # todo POST precisa do token do formulário
    configurar_login(app)
    app.register_blueprint(paginas)
    app.jinja_env.filters["reais"] = lambda valor: f"R$ {valor:.2f}".replace(".", ",")
    app.jinja_env.filters["data_br"] = lambda data: data.strftime("%d/%m/%Y") if data else "—"

    @app.errorhandler(CSRFError)
    def token_invalido(erro):
        return render_template("erro.html", mensagem="Formulário expirado. Volte e tente de novo."), 400

    @app.errorhandler(500)
    def erro_interno(erro):
        # O detalhe vai para o log do servidor; o usuário não vê SQL nem traceback.
        logging.getLogger("biblioteca").exception("Erro interno")
        return render_template("erro.html", mensagem="Erro interno. Tente novamente."), 500

    registrar_comandos(app)
    return app


create_app = criar_app       # nome que o comando `flask --app app ...` procura


def registrar_comandos(app):
    """Comandos de preparação: flask --app app init-db | seed-demo | criar-usuario."""

    @app.cli.command("init-db")
    def init_db():
        """Cria o banco (se faltar) e as tabelas de sql/schema.sql."""
        executar_arquivo_sql(parametros_mysql(), RAIZ / "sql" / "schema.sql")
        migrar_atendentes(parametros_mysql())
        click.echo("Banco e tabelas prontos.")

    @app.cli.command("migrar-db")
    def migrar_db():
        """Atualiza uma base existente sem apagar ou atribuir responsáveis ao histórico."""
        migrar_atendentes(parametros_mysql())
        click.echo("Migração de responsáveis concluída; histórico preservado.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Carrega os dados fictícios de sql/seed_demo.sql."""
        executar_arquivo_sql(parametros_mysql(), RAIZ / "sql" / "seed_demo.sql")
        click.echo("Dados de demonstração carregados.")

    @app.cli.command("criar-usuario")
    @click.argument("login")
    def criar_usuario(login):
        """Cria (ou troca a senha de) um usuário de login. A senha é pedida no terminal."""
        app.sistema.acesso.criar_usuario(login, getpass("Senha (mínimo 8 caracteres): "))
        click.echo(f"Usuário {login} gravado (somente o hash da senha).")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    criar_app().run()
