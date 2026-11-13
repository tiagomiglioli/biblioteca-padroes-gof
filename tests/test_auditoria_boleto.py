"""Regressão: segunda via concorrente não pode criar duas cobranças."""
import threading
from datetime import timedelta

import pytest

from tests.apoio import HOJE, emprestar, sistema_pronto


@pytest.mark.parametrize("banco", ["A", "B"])
def test_boleto_concorrente_emite_uma_cobranca_e_aceita_seu_pagamento(fabrica, configuracao, monkeypatch, banco):
    configuracao.banco_cobranca = banco
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    emitir_real = sistema.cobranca.emitir_boleto

    def banco_indisponivel(pedido):
        raise ConnectionError("falha temporária do banco")

    monkeypatch.setattr(sistema.cobranca, "emitir_boleto", banco_indisponivel)
    sistema.fachada.devolver("L1", HOJE + timedelta(days=34), atendente_id="A1")
    multa = sistema.multa.listar()[0]
    assert multa.id_boleto is None
    emails_antes = len(sistema.email.caixa_de_saida)
    encontro_no_banco = threading.Barrier(2)
    largada = threading.Barrier(2)
    emitidos, resultados, erros = [], [], []

    def banco_lento(pedido):
        # Sem exclusão, ambas as chamadas chegam ao banco antes de gravar.
        # Com exclusão, só uma chega; o prazo libera a resposta sem deadlock.
        try:
            encontro_no_banco.wait(timeout=1)
        except threading.BrokenBarrierError:
            pass
        boleto = emitir_real(pedido)
        emitidos.append(boleto.id_boleto)
        return boleto

    monkeypatch.setattr(sistema.cobranca, "emitir_boleto", banco_lento)

    def emitir():
        try:
            largada.wait(timeout=5)
            resultados.append(sistema.servico_multa.emitir_boleto(multa.id).id_boleto)
        except Exception as erro:
            erros.append(erro)

    threads = [threading.Thread(target=emitir, daemon=True) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not any(thread.is_alive() for thread in threads)
    assert erros == []
    assert len(emitidos) == 1
    assert resultados == [emitidos[0], emitidos[0]]
    assert sistema.multa.listar()[0].id_boleto == emitidos[0]
    assert len(sistema.email.caixa_de_saida) == emails_antes + 1
    notificacao = sistema.cobranca.simular_pagamento(emitidos[0])
    assert sistema.servico_multa.registrar_pagamento(notificacao) is True
    assert sistema.servico_multa.registrar_pagamento(notificacao) is False
