"""Regressões da auditoria: reentrega não duplica efeitos já confirmados."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from dominio.devolucao_observer import OuvinteDevolucao
from tests.apoio import HOJE, emprestar, sistema_pronto


def test_reentrega_concorrente_nao_duplica_ouvintes(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    eventos = []

    class Coletor(OuvinteDevolucao):
        def notificar(self, evento):
            eventos.append(evento)

    sistema.publicador.registrar(Coletor())
    sistema.fachada.devolver("L1", HOJE + timedelta(days=35), atendente_id="A1")
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(sistema.publicador.publicar, [eventos[0]] * 8))
    assert sistema.inspecao.pendentes == ["L1"]
    assert sistema.indicadores.devolucoes == 1
    assert sistema.indicadores.dias_de_atraso == 5
    assert len(sistema.multa.listar()) == 1
    assert len(sistema.email.caixa_de_saida) == 2
    assert len(eventos) == 1


def test_reentrega_tenta_novamente_apenas_ouvinte_que_falhou(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    eventos = []

    class Instavel(OuvinteDevolucao):
        def notificar(self, evento):
            eventos.append(evento)
            if len(eventos) == 1:
                raise ConnectionError("falha transitória antes do efeito")

    sistema.publicador.registrar(Instavel())
    sistema.fachada.devolver("L1", HOJE + timedelta(days=30), atendente_id="A1")
    sistema.publicador.publicar(eventos[0])
    sistema.publicador.publicar(eventos[0])
    assert len(eventos) == 2
    assert sistema.indicadores.devolucoes == 1
    assert len(sistema.email.caixa_de_saida) == 1
