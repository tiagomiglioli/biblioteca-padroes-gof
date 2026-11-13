"""Regra herdada: responsável explícito e pessoas distintas em cada transação."""
import uuid
from datetime import timedelta

import pytest

from dominio.erros import ErroDominio
from tests.apoio import ANA, HOJE, emprestar, livro_no_banco, sistema_pronto
from tests.test_fluxo_web import app, cliente, cadastrar_basico, circular


@pytest.mark.parametrize("operacao", ["reservar", "emprestar", "devolver"])
@pytest.mark.parametrize("atendente", [None, "", "INEXISTENTE", "MESMA"])
def test_atendente_invalido_recusa_sem_mudar_livro(fabrica, operacao, atendente):
    sistema = sistema_pronto(fabrica)
    sistema.atendente.inserir({"id": "MESMA", "cpf": ANA["cpf"]})
    if operacao != "reservar":
        sistema.fachada.reservar("E1", "L1", atendente_id="A1")
    if operacao == "devolver":
        sistema.fachada.emprestar("E1", "L1", atendente_id="A1")
    antes = livro_no_banco(fabrica)
    with pytest.raises(ErroDominio, match="[Aa]tendente|pessoas diferentes"):
        if operacao == "devolver":
            sistema.fachada.devolver("L1", HOJE, atendente_id=atendente)
        else:
            getattr(sistema.fachada, operacao)("E1", "L1", atendente_id=atendente)
    depois = livro_no_banco(fabrica)
    assert (depois.nome_estado, depois.vencimento) == (antes.nome_estado, antes.vencimento)
    assert sistema.indicadores.devolucoes == 0
    assert sistema.multa.listar() == ()


def test_omitir_atendente_nao_cria_reserva(fabrica):
    sistema = sistema_pronto(fabrica)
    with pytest.raises(ErroDominio, match="[Aa]tendente"):
        sistema.fachada.reservar("E1", "L1")
    assert livro_no_banco(fabrica).nome_estado == "LIVRE"


def test_responsavel_de_cada_operacao_nao_sobrescreve_o_anterior(fabrica):
    sistema = sistema_pronto(fabrica)
    sistema.pessoa.inserir({"cpf": "12345678901", "nome": "Carla", "sobrenome": "Teste", "email": "carla@example.test"})
    sistema.atendente.inserir({"id": "A2", "cpf": "12345678901"})
    reserva = sistema.emprestimo.solicitar_reserva("E1", "L1", "operador", atendente_id="A1")
    with fabrica.criar_unidade_trabalho() as uow:
        assert fabrica.criar_movimentacao(uow).consultar_reserva("L1", "E1").atendente_id == "A1"
    emprestimo = sistema.emprestimo.realizar_emprestimo("E1", "L1", atendente_id="A2")
    with fabrica.criar_unidade_trabalho() as uow:
        registro = fabrica.criar_movimentacao(uow).consultar_emprestimo("L1")
        assert registro.atendente_id == "A2"
    devolucao = sistema.devolucao.registrar_devolucao("L1", HOJE + timedelta(days=35), atendente_id="A1")
    assert (reserva.atendente_id, emprestimo.atendente_id, devolucao.atendente_id) == ("A1", "A2", "A1")
    assert sistema.multa.listar()[0].dias_atraso == 5
    with pytest.raises(ErroDominio):
        sistema.atendente.excluir("A2")


def test_reserva_sem_atendente_faz_rollback_do_command_e_permite_corrigir(fabrica):
    sistema = sistema_pronto(fabrica)
    identificador = str(uuid.uuid4())
    with pytest.raises(ErroDominio):
        sistema.emprestimo.solicitar_reserva("E1", "L1", "operador", identificador)
    comprovante = sistema.emprestimo.solicitar_reserva("E1", "L1", "operador", identificador, atendente_id="A1")
    repetido = sistema.emprestimo.solicitar_reserva("E1", "L1", "operador", identificador, atendente_id="A1")
    assert comprovante == repetido
    assert comprovante.atendente_id == "A1"


def test_web_exige_atendente_e_mostra_responsavel(cliente, app, fabrica):
    cadastrar_basico(cliente)
    pagina = circular(cliente, "reservar", atendente_id="")
    assert "atendente" in pagina.lower()
    assert livro_no_banco(fabrica).nome_estado == "LIVRE"
    pagina = circular(cliente, "reservar", atendente_id="A1")
    assert "Reserva registrada" in pagina and "Atendente: A1" in pagina
    assert "Atendente responsável" in pagina
