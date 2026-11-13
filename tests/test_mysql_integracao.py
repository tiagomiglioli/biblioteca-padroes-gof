"""Integração com MySQL REAL. Sem MySQL acessível, estes testes são pulados (skipped)."""
import uuid
from datetime import timedelta
from decimal import Decimal

import mysql.connector
import pytest

from app import criar_app
from dominio.circulacao_command import ComandoRenovacao
from dominio.erros import ErroDominio
from dominio.persistencia_factory import FabricaMySQL
from tests.apoio import ANA, HOJE, emprestar, livro_no_banco, sistema_pronto
from tests.test_autenticacao import CONFIG_TESTE, SENHA


def consultar(parametros, sql, valores=()):
    conexao = mysql.connector.connect(**parametros)
    try:
        cursor = conexao.cursor()
        cursor.execute(sql, valores)
        return cursor.fetchall()
    finally:
        conexao.close()


def test_mysql_dados_continuam_la_depois_de_fechar_e_reabrir(fabrica_mysql, mysql_preparado):
    sistema = sistema_pronto(fabrica_mysql)
    emprestar(sistema)
    sistema.fachada.renovar("E1", "L1")
    sistema.fachada.devolver("L1", HOJE + timedelta(days=65))
    del sistema, fabrica_mysql                         # nada do processo "antigo" sobra

    nova_fabrica = FabricaMySQL(mysql_preparado)       # como se a aplicação tivesse reiniciado
    novo_sistema = sistema_pronto(nova_fabrica)

    livro = livro_no_banco(nova_fabrica)
    assert (livro.nome_estado, livro.num_renovacoes, livro.vencimento) == ("DEVOLVIDO", 1, HOJE + timedelta(days=60))
    multa = novo_sistema.multa.listar()[0]
    assert (multa.dias_atraso, multa.valor, multa.politica) == (5, Decimal("5.00"), "original")
    assert novo_sistema.pessoa.consultar(ANA["cpf"]).nome == "Ana"


def test_mysql_reinicio_da_aplicacao_web_mantem_login_e_dados(fabrica_mysql, mysql_preparado):
    primeira = criar_app(CONFIG_TESTE, fabrica=fabrica_mysql, relogio=lambda: HOJE)
    primeira.sistema.acesso.criar_usuario("admin", SENHA)
    cliente = primeira.test_client()
    cliente.post("/login", data={"login": "admin", "senha": SENHA})
    cliente.post("/cadastros/livro", data={"acao": "inserir", "id": "L9", "titulo": "Persistente"})

    segunda = criar_app(CONFIG_TESTE, fabrica=FabricaMySQL(mysql_preparado), relogio=lambda: HOJE)
    cliente = segunda.test_client()

    assert cliente.post("/login", data={"login": "admin", "senha": SENHA}).status_code == 302
    assert "Persistente" in cliente.get("/acervo").get_data(as_text=True)


def test_mysql_tabelas_sao_innodb_com_chaves_estrangeiras_e_unicas(mysql_preparado):
    banco = mysql_preparado["database"]
    motores = consultar(mysql_preparado, "SELECT table_name, engine FROM information_schema.tables"
                                         " WHERE table_schema = %s", (banco,))
    assert len(motores) == 11 and {motor for _, motor in motores} == {"InnoDB"}

    restricoes = {(tabela, tipo) for tabela, tipo in consultar(
        mysql_preparado, "SELECT table_name, constraint_type FROM information_schema.table_constraints"
                         " WHERE table_schema = %s", (banco,))}
    for esperado in [("estudante", "FOREIGN KEY"), ("emprestimo", "FOREIGN KEY"), ("multa", "UNIQUE"),
                     ("quitacao", "UNIQUE"), ("comando_executado", "PRIMARY KEY"), ("pessoa", "PRIMARY KEY")]:
        assert esperado in restricoes


def test_mysql_restricao_do_banco_barra_comando_e_quitacao_repetidos(fabrica_mysql, mysql_preparado):
    sistema = sistema_pronto(fabrica_mysql)
    emprestar(sistema)
    comando = ComandoRenovacao(sistema.fachada, "E1", "L1", autor="ana")
    sistema.executor.executar(comando)
    sistema.fachada.devolver("L1", HOJE + timedelta(days=70))
    multa = sistema.multa.listar()[0]
    sistema.multa.simular_pagamento(multa.id)

    with pytest.raises(mysql.connector.IntegrityError):     # direto no banco, sem passar pelo Python
        consultar(mysql_preparado, "INSERT INTO comando_executado (id, tipo, autor, criado_em)"
                                   " VALUES (%s, 'renovacao', 'x', NOW())", (comando.id,))
    with pytest.raises(mysql.connector.IntegrityError):
        consultar(mysql_preparado, "INSERT INTO quitacao (id_notificacao, multa_id) VALUES (%s, %s)",
                  (str(uuid.uuid4()), multa.id))


def test_mysql_exclusao_com_vinculo_vira_erro_de_dominio_e_nada_e_apagado(fabrica_mysql):
    sistema = sistema_pronto(fabrica_mysql)
    with pytest.raises(ErroDominio):
        sistema.pessoa.excluir(ANA["cpf"])              # Ana tem um estudante vinculado
    assert sistema.pessoa.consultar(ANA["cpf"]) is not None


def test_mysql_texto_malicioso_e_guardado_como_texto(fabrica_mysql, mysql_preparado):
    sistema = sistema_pronto(fabrica_mysql)
    ataque = "x'; DROP TABLE livro;--"
    sistema.acervo.inserir({"id": "INJ", "titulo": ataque})

    assert sistema.acervo.consultar("INJ").titulo == ataque
    assert sistema.acervo.consultar("' OR '1'='1") is None
    assert len(sistema.acervo.listar()) == 2            # L1 e INJ: a tabela continua inteira


def test_mysql_cada_operacao_fecha_a_propria_conexao(fabrica_mysql):
    with fabrica_mysql.criar_unidade_trabalho() as uow:
        conexao = uow.conexao
        assert conexao.is_connected()
    assert not conexao.is_connected()                   # nada de conexão global reaproveitada


def test_mysql_comandos_de_preparacao_criam_banco_dados_e_usuario(fabrica_mysql, mysql_preparado, monkeypatch):
    monkeypatch.setenv("MYSQL_DATABASE", mysql_preparado["database"])
    monkeypatch.setenv("PERSISTENCE_PROFILE", "mysql")
    from dominio.configuracao_singleton import ConfiguracaoSistema
    ConfiguracaoSistema.reiniciar_para_testes()
    monkeypatch.setattr("app.getpass", lambda texto: SENHA)
    app = criar_app(CONFIG_TESTE)                       # sem fábrica injetada: escolhida pelo perfil
    executor = app.test_cli_runner()

    for comando in (["init-db"], ["seed-demo"], ["seed-demo"], ["criar-usuario", "admin"]):
        resultado = executor.invoke(args=comando)
        assert resultado.exit_code == 0, resultado.output

    assert len(app.sistema.acervo.listar()) == 5
    assert app.sistema.acervo.arvore().contar_livros() == 5
    assert app.test_client().post("/login", data={"login": "admin", "senha": SENHA}).status_code == 302
