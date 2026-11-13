"""Autenticação e segurança da interface web (Flask-Login, hash de senha, CSRF, sessão)."""
import re

import pytest

from app import criar_app
from tests.apoio import HOJE

SENHA = "senha-de-teste"
CONFIG_TESTE = {"TESTING": True, "SECRET_KEY": "chave-so-para-testes", "WTF_CSRF_ENABLED": False}

ROTAS_PROTEGIDAS = ["/", "/cadastros", "/acervo", "/circulacao", "/multas"]
POSTS_PROTEGIDOS = ["/cadastros/pessoa", "/acervo/grupo", "/acervo/mover", "/circulacao",
                    "/multas/politica", "/multas/1/pagar", "/multas/1/boleto", "/logout"]


@pytest.fixture
def app(fabrica):
    app = criar_app(CONFIG_TESTE, fabrica=fabrica, relogio=lambda: HOJE)
    app.sistema.acesso.criar_usuario("admin", SENHA)
    return app


@pytest.fixture
def cliente(app):
    return app.test_client()


def entrar(cliente, login="admin", senha=SENHA):
    return cliente.post("/login", data={"login": login, "senha": senha})


def test_login_valido_da_acesso_ao_painel(cliente):
    resposta = entrar(cliente)
    assert resposta.status_code == 302 and resposta.headers["Location"] == "/"
    assert cliente.get("/").status_code == 200


@pytest.mark.parametrize("login,senha", [("admin", "senha-errada"), ("nao-existe", SENHA), ("", "")])
def test_login_invalido_nao_da_acesso_e_nao_revela_qual_campo_errou(cliente, login, senha):
    resposta = entrar(cliente, login, senha)
    assert resposta.status_code == 401
    assert "Login ou senha inválidos." in resposta.get_data(as_text=True)
    assert cliente.get("/").status_code == 302


def test_logout_encerra_a_sessao(cliente):
    entrar(cliente)
    assert cliente.post("/logout").status_code == 302
    assert cliente.get("/").headers["Location"].startswith("/login")


def test_logout_nao_aceita_get(cliente):
    entrar(cliente)
    assert cliente.get("/logout").status_code == 405


@pytest.mark.parametrize("rota", ROTAS_PROTEGIDAS)
def test_paginas_exigem_login(cliente, rota):
    resposta = cliente.get(rota)
    assert resposta.status_code == 302 and resposta.headers["Location"].startswith("/login")


@pytest.mark.parametrize("rota", POSTS_PROTEGIDOS)
def test_operacoes_exigem_login_no_backend(cliente, app, rota):
    resposta = cliente.post(rota, data={"cpf": "11122233344", "nome": "X", "sobrenome": "Y", "email": "x@y"})
    assert resposta.status_code == 302 and resposta.headers["Location"].startswith("/login")
    assert app.sistema.pessoa.listar() == ()


def test_senha_e_guardada_apenas_como_hash(app):
    usuario = app.sistema.acesso.obter("admin")
    assert SENHA not in usuario.senha_hash
    assert usuario.senha_hash.startswith(("scrypt:", "pbkdf2:"))


def test_senha_curta_e_recusada(app):
    from dominio.erros import ErroDominio
    with pytest.raises(ErroDominio):
        app.sistema.acesso.criar_usuario("outro", "1234")


def test_tentativa_de_injecao_de_sql_no_login_nao_autentica(cliente, app):
    for ataque in ("' OR '1'='1", "admin' -- ", "admin'; DROP TABLE usuario; -- "):
        assert entrar(cliente, ataque, ataque).status_code == 401
    assert app.sistema.acesso.obter("admin") is not None       # a tabela continua lá
    assert entrar(cliente).status_code == 302


def test_login_nao_redireciona_para_site_externo(cliente):
    resposta = cliente.post("/login?next=https://site-malicioso.example", data={"login": "admin", "senha": SENHA})
    assert resposta.headers["Location"] == "/"


def test_cookie_de_sessao_e_httponly_e_samesite(cliente):
    cookie = entrar(cliente).headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_secret_key_e_obrigatoria(fabrica, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        criar_app({"TESTING": True}, fabrica=fabrica)


def test_post_sem_token_csrf_e_recusado(fabrica):
    app = criar_app({**CONFIG_TESTE, "WTF_CSRF_ENABLED": True}, fabrica=fabrica)
    app.sistema.acesso.criar_usuario("admin", SENHA)
    cliente = app.test_client()

    assert cliente.post("/login", data={"login": "admin", "senha": SENHA}).status_code == 400

    pagina = cliente.get("/login").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', pagina).group(1)
    resposta = cliente.post("/login", data={"login": "admin", "senha": SENHA, "csrf_token": token})
    assert resposta.status_code == 302


def test_erro_interno_nao_mostra_detalhes_ao_usuario(app, cliente):
    app.config["PROPAGATE_EXCEPTIONS"] = False
    entrar(cliente)

    def quebrar():
        raise RuntimeError("SELECT senha FROM usuario -- detalhe interno")
    app.sistema.acervo.listar = quebrar

    resposta = cliente.get("/acervo")
    assert resposta.status_code == 500
    assert "detalhe interno" not in resposta.get_data(as_text=True)
