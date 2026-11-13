"""Regressões da auditoria: vínculos preservados e banco de testes protegido."""
import pytest
import mysql.connector

from dominio.erros import ErroDominio
from tests.apoio import ANA, BIA, HOJE, emprestar, sistema_pronto
from tests import conftest


@pytest.mark.parametrize("pessoa", [ANA, BIA])
def test_pessoa_vinculada_nao_pode_ser_excluida(fabrica, pessoa):
    sistema = sistema_pronto(fabrica)
    if pessoa == BIA:
        sistema.estudante.excluir("E2")  # Bia permanece vinculada somente como atendente.
    with pytest.raises(ErroDominio):
        sistema.pessoa.excluir(pessoa["cpf"])
    assert sistema.pessoa.consultar(pessoa["cpf"]) is not None


@pytest.mark.parametrize("fase", ["reserva", "emprestimo", "historico"])
def test_estudante_com_movimentacao_nao_pode_ser_excluido(fabrica, fase):
    sistema = sistema_pronto(fabrica)
    sistema.fachada.reservar("E1", "L1", atendente_id="A1")
    if fase != "reserva":
        sistema.fachada.emprestar("E1", "L1", atendente_id="A1")
    if fase == "historico":
        sistema.fachada.devolver("L1", HOJE, atendente_id="A1")
    with pytest.raises(ErroDominio):
        sistema.estudante.excluir("E1")
    assert sistema.estudante.consultar("E1") is not None


def test_livro_livre_com_historico_nao_pode_ser_excluido(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    sistema.fachada.devolver("L1", HOJE, atendente_id="A1")
    sistema.fachada.inspecionar("L1", True)
    with pytest.raises(ErroDominio):
        sistema.acervo.excluir("L1")
    assert sistema.acervo.consultar("L1").nome_estado == "LIVRE"


def test_exclusao_sem_vinculos_continua_permitida(fabrica):
    sistema = sistema_pronto(fabrica)
    sistema.estudante.excluir("E1")
    sistema.pessoa.excluir(ANA["cpf"])
    sistema.acervo.excluir("L1")
    assert sistema.pessoa.consultar(ANA["cpf"]) is None
    assert sistema.acervo.consultar("L1") is None


def test_base_teste_nao_pode_ser_base_da_aplicacao(monkeypatch):
    monkeypatch.setenv("MYSQL_DATABASE", "biblioteca_producao")
    monkeypatch.setenv("MYSQL_TEST_DATABASE", "biblioteca_producao")
    with pytest.raises(ValueError, match="MYSQL_TEST_DATABASE"):
        conftest.parametros_mysql_teste()


def test_erro_sql_de_bootstrap_nao_vira_skip(monkeypatch):
    def falhar(*args, **kwargs):
        raise mysql.connector.ProgrammingError("SQL inválido", errno=1064)
    monkeypatch.setattr(conftest, "executar_arquivo_sql", falhar)
    with pytest.raises(mysql.connector.ProgrammingError):
        try:
            conftest.mysql_preparado.__wrapped__()
        except pytest.skip.Exception:
            pytest.fail("Erro SQL não pode ser tratado como MySQL indisponível")
