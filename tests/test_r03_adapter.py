"""R03 — Adapter: bancos A e B com APIs incompatíveis atrás de um contrato único."""
import inspect
from datetime import timedelta
from decimal import Decimal

import pytest

from dominio import multas_strategy
from dominio.bancos_adapter import (AdaptadorBancoA, AdaptadorBancoB, BancoA, BancoB,
                                     CobrancaInstitucional, SolicitacaoCobranca, criar_cobranca)
from tests.apoio import ANA, HOJE, emprestar, sistema_pronto

SETE_REAIS = SolicitacaoCobranca(referencia="multa-1", cpf=ANA["cpf"], valor=Decimal("7.00"))


def test_r03_a_mesma_solicitacao_de_7_reais_vira_700_centavos_no_banco_a_e_7_00_no_banco_b():
    banco_a, banco_b = BancoA(), BancoB()

    AdaptadorBancoA(banco_a).emitir_boleto(SETE_REAIS)
    AdaptadorBancoB(banco_b).emitir_boleto(SETE_REAIS)

    assert banco_a.recebido["valor_centavos"] == 700
    assert isinstance(banco_a.recebido["valor_centavos"], int)
    assert banco_b.recebido["amount"] == Decimal("7.00")


def test_r03_adaptadores_convertem_o_documento_para_o_formato_de_cada_banco():
    banco_a, banco_b = BancoA(), BancoB()
    AdaptadorBancoA(banco_a).emitir_boleto(SETE_REAIS)
    AdaptadorBancoB(banco_b).emitir_boleto(SETE_REAIS)

    assert banco_a.recebido["cpf"] == "11122233344"
    assert banco_b.recebido["document"] == "111.222.333-44"


@pytest.mark.parametrize("adaptador", [AdaptadorBancoA(BancoA()), AdaptadorBancoB(BancoB())])
def test_r03_identificador_e_situacao_voltam_no_formato_institucional(adaptador):
    assert isinstance(adaptador, CobrancaInstitucional)

    boleto = adaptador.emitir_boleto(SETE_REAIS)

    assert isinstance(boleto.id_boleto, str) and boleto.id_boleto
    assert boleto.banco == adaptador.nome_banco
    assert boleto.situacao == "EMITIDO"


@pytest.mark.parametrize("adaptador", [AdaptadorBancoA(BancoA()), AdaptadorBancoB(BancoB())])
def test_r03_notificacao_de_pagamento_e_traduzida_pelo_adaptador(adaptador):
    boleto = adaptador.emitir_boleto(SETE_REAIS)
    notificacao_do_banco = adaptador.simular_pagamento(boleto.id_boleto)

    pagamento = adaptador.traduzir_notificacao(notificacao_do_banco)

    assert pagamento.id_boleto == boleto.id_boleto
    assert isinstance(pagamento.id_notificacao, str) and pagamento.id_notificacao
    assert pagamento.pago is True


def test_r03_situacao_que_nao_e_pagamento_nao_vira_pago():
    assert AdaptadorBancoA(BancoA()).traduzir_notificacao(
        {"evento": "e1", "codigo": "A-1", "situacao": "REGISTRADO"}).pago is False
    assert AdaptadorBancoB(BancoB()).traduzir_notificacao(
        {"notification_uuid": "n1", "titulo_id": 1, "status": 1}).pago is False


def test_r03_servico_de_multas_nao_tem_condicionais_por_banco():
    fonte = inspect.getsource(multas_strategy)
    for proibido in ("BancoA", "BancoB", "AdaptadorBanco", "banco ==", "banco_cobranca"):
        assert proibido not in fonte


def test_r03_banco_da_instalacao_e_escolhido_pela_configuracao():
    assert isinstance(criar_cobranca("A"), AdaptadorBancoA)
    assert isinstance(criar_cobranca("B"), AdaptadorBancoB)


def multa_atrasada(sistema):
    emprestar(sistema)
    sistema.fachada.devolver("L1", HOJE + timedelta(days=37), atendente_id="A1")
    return sistema.multa.listar()[-1]


@pytest.mark.parametrize("banco", ["A", "B"])
def test_r03_o_mesmo_servico_funciona_com_qualquer_banco(fabrica, configuracao, banco):
    configuracao.banco_cobranca = banco
    sistema = sistema_pronto(fabrica)
    multa = multa_atrasada(sistema)
    assert (multa.valor, multa.banco, multa.quitada) == (Decimal("7.00"), banco, False)

    assert sistema.multa.simular_pagamento(multa.id) is True

    assert sistema.multa.listar()[-1].quitada is True


def test_r03_notificacao_repetida_nao_gera_segunda_quitacao(fabrica):
    sistema = sistema_pronto(fabrica)
    multa = multa_atrasada(sistema)
    notificacao = sistema.cobranca.simular_pagamento(multa.id_boleto)

    assert sistema.servico_multa.registrar_pagamento(notificacao) is True
    assert sistema.servico_multa.registrar_pagamento(notificacao) is False       # mesma notificação
    outra = sistema.cobranca.simular_pagamento(multa.id_boleto)
    assert sistema.servico_multa.registrar_pagamento(outra) is False             # outra, mesma multa

    with fabrica.criar_unidade_trabalho() as uow:
        assert fabrica.criar_financeiro(uow).obter_multa(multa.id).quitada is True


def test_r03_notificacao_de_boleto_desconhecido_e_ignorada(fabrica):
    sistema = sistema_pronto(fabrica)
    assert sistema.servico_multa.registrar_pagamento(
        {"evento": "e9", "codigo": "A-nao-existe", "situacao": "LIQUIDADO"}) is False
