"""Configurações lidas do ambiente (.env). Nenhuma senha ou chave fica no código."""
import os

from dotenv import load_dotenv

load_dotenv()


def parametros_mysql():
    """Parâmetros de conexão do MySQL, vindos do ambiente."""
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", ""),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "biblioteca_gof"),
    }


def configuracao_flask():
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),          # sem valor padrão: obrigatória
        "SESSION_COOKIE_HTTPONLY": True,                     # JavaScript não lê o cookie de sessão
        "SESSION_COOKIE_SAMESITE": "Lax",
        # Em produção com HTTPS, defina SESSION_COOKIE_SECURE=1 no ambiente.
        "SESSION_COOKIE_SECURE": os.environ.get("SESSION_COOKIE_SECURE") == "1",
    }
