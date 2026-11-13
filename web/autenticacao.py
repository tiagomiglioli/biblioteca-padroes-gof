"""Login e logout com Flask-Login. A sessão é um cookie assinado pelo Flask."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

acesso = Blueprint("acesso", __name__)


class UsuarioWeb(UserMixin):
    """O que o Flask-Login guarda na sessão: apenas o login."""

    def __init__(self, login):
        self.id = login


def configurar_login(app):
    gerenciador = LoginManager(app)
    gerenciador.login_view = "acesso.login"
    gerenciador.login_message = "Faça login para continuar."
    gerenciador.session_protection = "strong"

    @gerenciador.user_loader
    def carregar(login):
        # A cada requisição confirma no banco que o usuário ainda existe.
        usuario = current_app.sistema.acesso.obter(login)
        return UsuarioWeb(usuario.login) if usuario else None

    app.register_blueprint(acesso)


@acesso.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = current_app.sistema.acesso.autenticar(request.form.get("login", ""),
                                                        request.form.get("senha", ""))
        if usuario is None:
            # Mesma mensagem para login ou senha errados: não revela quais logins existem.
            flash("Login ou senha inválidos.", "erro")
            return render_template("login.html"), 401
        session.clear()                    # sessão nova a cada login (evita fixação de sessão)
        login_user(UsuarioWeb(usuario.login))
        # Sempre para o painel: o parâmetro ?next= é ignorado para não redirecionar a sites externos.
        return redirect(url_for("paginas.painel"))
    return render_template("login.html")


@acesso.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("acesso.login"))
