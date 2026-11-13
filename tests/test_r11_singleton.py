"""R11 — Singleton (pedido pelo professor): ConfiguracaoSistema."""
import threading

import pytest

from dominio.configuracao_singleton import ConfiguracaoSistema


def test_r11_obter_instancia_devolve_sempre_o_mesmo_objeto():
    primeiro = ConfiguracaoSistema.obter_instancia()
    segundo = ConfiguracaoSistema.obter_instancia()
    assert primeiro is segundo


def test_r11_construtor_direto_e_proibido():
    with pytest.raises(TypeError):
        ConfiguracaoSistema()


def test_r11_threads_simultaneas_recebem_a_mesma_instancia():
    ConfiguracaoSistema.reiniciar_para_testes()
    recebidas = []
    largada = threading.Barrier(20)

    def pegar():
        largada.wait()
        recebidas.append(ConfiguracaoSistema.obter_instancia())

    threads = [threading.Thread(target=pegar) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(recebidas) == 20
    assert len({id(instancia) for instancia in recebidas}) == 1


def test_r11_ambiente_e_lido_uma_unica_vez_na_criacao(monkeypatch):
    configuracao = ConfiguracaoSistema.obter_instancia()
    assert configuracao.politica_multa == "original"

    monkeypatch.setenv("POLITICA_MULTA", "teto")       # não reconfigura em silêncio

    assert ConfiguracaoSistema.obter_instancia().politica_multa == "original"


def test_r11_mudanca_explicita_vale_para_todos_os_pontos_de_acesso():
    ConfiguracaoSistema.obter_instancia().politica_multa = "tolerancia"
    assert ConfiguracaoSistema.obter_instancia().politica_multa == "tolerancia"
