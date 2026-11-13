"""R02 — Strategy: políticas de cálculo de multa."""
from datetime import timedelta
from decimal import Decimal

import pytest

from dominio.multas_strategy import (POLITICAS, MultaComTeto, MultaComTolerancia, MultaOriginal,
                                      PoliticaMulta)
from tests.apoio import HOJE, emprestar, sistema_pronto


def test_r02_cinco_dias_de_atraso_custam_5_na_original_e_3_na_tolerancia():
    assert MultaOriginal().calcular(5) == Decimal("5.00")
    assert MultaComTolerancia().calcular(5) == Decimal("3.00")


@pytest.mark.parametrize("politica", [MultaOriginal(), MultaComTeto(), MultaComTolerancia()])
def test_r02_sem_atraso_o_valor_e_zero(politica):
    assert politica.calcular(0) == Decimal("0.00")


def test_r02_politica_com_teto_para_em_20_reais():
    assert MultaComTeto().calcular(19) == Decimal("19.00")
    assert MultaComTeto().calcular(20) == Decimal("20.00")
    assert MultaComTeto().calcular(45) == Decimal("20.00")


def test_r02_tolerancia_nao_cobra_os_dois_primeiros_dias():
    assert MultaComTolerancia().calcular(1) == Decimal("0.00")
    assert MultaComTolerancia().calcular(2) == Decimal("0.00")
    assert MultaComTolerancia().calcular(3) == Decimal("1.00")


@pytest.mark.parametrize("politica", list(POLITICAS.values()))
def test_r02_valores_monetarios_sao_decimal(politica):
    assert isinstance(politica, PoliticaMulta)
    assert isinstance(politica.calcular(7), Decimal)


def devolver_com_atraso(sistema, dias, livro_id="L1"):
    """Empresta hoje e devolve `dias` depois do vencimento (data injetada, sem mexer no relógio)."""
    emprestar(sistema, livro_id=livro_id)
    sistema.fachada.devolver(livro_id, HOJE + timedelta(days=30 + dias), atendente_id="A1")
    return sistema.multa.listar()[-1]


def test_r02_dias_de_atraso_saem_das_datas_de_vencimento_e_devolucao(fabrica):
    multa = devolver_com_atraso(sistema_pronto(fabrica), 5)
    assert (multa.dias_atraso, multa.valor, multa.politica) == (5, Decimal("5.00"), "original")


def test_r02_politica_vigente_vem_da_configuracao_administrativa(fabrica, configuracao):
    sistema = sistema_pronto(fabrica)
    sistema.multa.definir_politica("tolerancia")

    multa = devolver_com_atraso(sistema, 5)

    assert configuracao.politica_multa == "tolerancia"
    assert (multa.valor, multa.politica) == (Decimal("3.00"), "tolerancia")


def test_r02_trocar_a_politica_nao_recalcula_multa_ja_emitida(fabrica):
    sistema = sistema_pronto(fabrica, livros=("L1", "L2"))
    antiga = devolver_com_atraso(sistema, 5, "L1")

    sistema.multa.definir_politica("tolerancia")
    nova = devolver_com_atraso(sistema, 5, "L2")

    relida = next(multa for multa in sistema.multa.listar() if multa.id == antiga.id)
    assert (relida.valor, relida.politica) == (Decimal("5.00"), "original")
    assert (nova.valor, nova.politica) == (Decimal("3.00"), "tolerancia")


def test_r02_nova_politica_entra_sem_alterar_o_servico_de_multas(fabrica, monkeypatch):
    class MultaEmDobro(PoliticaMulta):
        nome = "dobro"

        def calcular(self, dias_atraso):
            return Decimal(2 * dias_atraso).quantize(Decimal("0.01"))

    monkeypatch.setitem(POLITICAS, "dobro", MultaEmDobro())
    sistema = sistema_pronto(fabrica)
    sistema.multa.definir_politica("dobro")

    assert devolver_com_atraso(sistema, 5).valor == Decimal("10.00")


def test_r02_politica_desconhecida_e_recusada(fabrica, configuracao):
    from dominio.erros import ErroDominio
    with pytest.raises(ErroDominio):
        sistema_pronto(fabrica).multa.definir_politica("inexistente")
    assert configuracao.politica_multa == "original"


def test_r02_emissao_do_boleto_e_a_mesma_em_qualquer_politica(fabrica):
    sistema = sistema_pronto(fabrica, livros=("L1", "L2"))
    primeira = devolver_com_atraso(sistema, 5, "L1")
    sistema.multa.definir_politica("teto")
    segunda = devolver_com_atraso(sistema, 5, "L2")

    assert primeira.banco == segunda.banco == "A"
    assert primeira.id_boleto and segunda.id_boleto and primeira.id_boleto != segunda.id_boleto
