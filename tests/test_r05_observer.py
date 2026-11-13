"""R05 — Observer: reações independentes à devolução."""
import dataclasses
from datetime import timedelta
from decimal import Decimal

import pytest

from dominio.devolucao_observer import EventoDevolucao, OuvinteDevolucao
from tests.apoio import ANA, HOJE, emprestar, livro_no_banco, sistema_pronto

VENCIMENTO = HOJE + timedelta(days=30)


def test_r05_devolucao_atrasada_alimenta_inspecao_multa_e_indicadores(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)

    sistema.fachada.devolver("L1", VENCIMENTO + timedelta(days=4))

    assert sistema.inspecao.pendentes == ["L1"]
    assert [multa.valor for multa in sistema.multa.listar()] == [Decimal("4.00")]
    assert (sistema.indicadores.devolucoes, sistema.indicadores.atrasadas) == (1, 1)
    assert sistema.indicadores.dias_de_atraso == 4


def test_r05_devolucao_no_prazo_nao_gera_multa(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)

    sistema.fachada.devolver("L1", VENCIMENTO)

    assert sistema.multa.listar() == ()
    assert (sistema.indicadores.devolucoes, sistema.indicadores.atrasadas) == (1, 0)
    assert sistema.inspecao.pendentes == ["L1"]


def test_r05_livro_permanece_devolvido_ate_a_decisao_da_inspecao(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    sistema.fachada.devolver("L1", VENCIMENTO)

    assert livro_no_banco(fabrica).nome_estado == "DEVOLVIDO"     # avisar a inspeção não muda o estado

    sistema.fachada.inspecionar("L1", bom_estado=True)
    assert livro_no_banco(fabrica).nome_estado == "LIVRE"


def test_r05_falha_do_email_nao_afeta_os_demais_nem_desfaz_a_devolucao(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)

    def servidor_fora_do_ar(*argumentos):
        raise ConnectionError("servidor de e-mail fora do ar")
    sistema.email.enviar = servidor_fora_do_ar

    comprovante = sistema.fachada.devolver("L1", VENCIMENTO + timedelta(days=4))

    assert comprovante.estado == "DEVOLVIDO"
    assert livro_no_banco(fabrica).nome_estado == "DEVOLVIDO"
    assert sistema.inspecao.pendentes == ["L1"]
    assert len(sistema.multa.listar()) == 1
    assert sistema.indicadores.devolucoes == 1
    assert len(sistema.publicador.falhas) >= 1


def test_r05_publicacao_ocorre_depois_da_confirmacao_da_devolucao(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    visto = {}

    class OuvinteQueConfereOBanco(OuvinteDevolucao):
        def notificar(self, evento):
            # Outra transação só enxerga a devolução se ela já foi confirmada (commit).
            visto["estado"] = livro_no_banco(fabrica).nome_estado

    sistema.publicador.registrar(OuvinteQueConfereOBanco())     # novo ouvinte, tratador intocado
    sistema.devolucao.registrar_devolucao("L1", VENCIMENTO)

    assert visto == {"estado": "DEVOLVIDO"}


def test_r05_evento_leva_os_dados_necessarios_e_e_imutavel(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    recebidos = []

    class Coletor(OuvinteDevolucao):
        def notificar(self, evento):
            recebidos.append(evento)

    sistema.publicador.registrar(Coletor())
    sistema.fachada.devolver("L1", VENCIMENTO + timedelta(days=2))

    evento = recebidos[0]
    assert isinstance(evento, EventoDevolucao)
    assert (evento.estudante_id, evento.cpf, evento.email) == ("E1", ANA["cpf"], ANA["email"])
    assert (evento.livro_id, evento.vencimento, evento.data_devolucao) == \
        ("L1", VENCIMENTO, VENCIMENTO + timedelta(days=2))
    assert evento.dias_atraso == 2
    with pytest.raises(dataclasses.FrozenInstanceError):
        evento.vencimento = HOJE


def test_r05_email_de_devolucao_vai_para_a_caixa_de_saida_simulada(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    sistema.fachada.devolver("L1", VENCIMENTO)
    assert sistema.email.caixa_de_saida[-1][0] == ANA["email"]
