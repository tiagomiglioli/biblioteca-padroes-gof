"""Fixtures compartilhadas.

`fabrica` roda cada teste nas DUAS famílias de persistência (memória e MySQL).
Sem MySQL acessível, a variante MySQL aparece como "skipped" — nunca como aprovada.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from dominio.configuracao_singleton import ConfiguracaoSistema
from dominio.persistencia_factory import FabricaMemoria, FabricaMySQL
from persistencia.mysql import executar_arquivo_sql

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
TABELAS = ["comando_executado", "quitacao", "multa", "emprestimo", "reserva", "livro",
           "grupo_acervo", "estudante", "atendente", "pessoa", "usuario"]


def parametros_mysql_teste():
    """Banco SEPARADO do de demonstração: os testes apagam todas as tabelas dele."""
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", ""),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_TEST_DATABASE", "biblioteca_gof_teste"),
    }


@pytest.fixture(scope="session")
def mysql_preparado():
    """Cria o banco de teste e aplica sql/schema.sql; pula se o MySQL não responder."""
    import mysql.connector
    parametros = parametros_mysql_teste()
    try:
        executar_arquivo_sql({**parametros, "connection_timeout": 3}, RAIZ / "sql" / "schema.sql")
    except mysql.connector.Error as erro:
        pytest.skip(f"MySQL indisponível para testes de integração: {erro.msg}")
    return parametros


@pytest.fixture
def fabrica_mysql(mysql_preparado):
    import mysql.connector
    conexao = mysql.connector.connect(**mysql_preparado)
    cursor = conexao.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tabela in TABELAS:
        cursor.execute(f"TRUNCATE TABLE {tabela}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conexao.commit()
    conexao.close()
    return FabricaMySQL(mysql_preparado)


@pytest.fixture(params=["memoria", "mysql"])
def fabrica(request):
    if request.param == "memoria":
        return FabricaMemoria()
    return request.getfixturevalue("fabrica_mysql")


@pytest.fixture(autouse=True)
def configuracao(monkeypatch):
    """Cada teste recebe um Singleton novo, com valores conhecidos."""
    monkeypatch.setenv("PERSISTENCE_PROFILE", "memoria")
    monkeypatch.setenv("POLITICA_MULTA", "original")
    monkeypatch.setenv("BANCO_COBRANCA", "A")
    ConfiguracaoSistema.reiniciar_para_testes()
    yield ConfiguracaoSistema.obter_instancia()
    ConfiguracaoSistema.reiniciar_para_testes()
