"""R09 — Decorator: consulta ao acervo com cache e medição opcionais."""
import pytest

from dominio.consulta_decorator import (ConsultaAcervo, ConsultaBase, ConsultaComCache,
                                         ConsultaComMedicao, MetadadosLivro)
from dominio.erros import ErroDominio
from tests.apoio import livro_no_banco, sistema_pronto


class ConsultaContada(ConsultaBase):
    """A implementação original, só contando quantas vezes foi realmente ao repositório."""

    idas_ao_repositorio = 0

    def consultar(self, livro_id):
        self.idas_ao_repositorio += 1
        return super().consultar(livro_id)


def test_r09_segunda_consulta_usa_cache_e_ainda_gera_medicao(fabrica):
    sistema_pronto(fabrica)
    base = ConsultaContada(fabrica)
    medicao = ConsultaComMedicao(ConsultaComCache(base))        # medição por fora, cache por dentro

    primeira = medicao.consultar("L1")
    segunda = medicao.consultar("L1")

    assert primeira == segunda == MetadadosLivro("L1", "Livro L1")
    assert base.idas_ao_repositorio == 1                        # a segunda veio do cache
    assert medicao.total_consultas == 2                         # e mesmo assim foi medida


def test_r09_a_ordem_da_cadeia_importa(fabrica):
    sistema_pronto(fabrica)
    medicao = ConsultaComMedicao(ConsultaContada(fabrica))
    cache_por_fora = ConsultaComCache(medicao)

    cache_por_fora.consultar("L1")
    cache_por_fora.consultar("L1")

    assert medicao.total_consultas == 1          # o cache respondeu antes de chegar à medição


def test_r09_resultado_antigo_do_cache_nunca_autoriza_reserva(fabrica):
    sistema = sistema_pronto(fabrica)
    antes = sistema.acervo.consultar_metadados("L1")            # entra no cache com o livro LIVRE
    sistema.fachada.reservar("E1", "L1", atendente_id="A1")                        # o livro deixa de estar LIVRE

    assert sistema.acervo.consultar_metadados("L1") == antes    # o cache continua respondendo
    with pytest.raises(ErroDominio):
        sistema.fachada.reservar("E2", "L1", atendente_id="A1")                    # a reserva olha o estado atual

    assert livro_no_banco(fabrica).nome_estado == "RESERVADO"


def test_r09_cache_guarda_apenas_metadados():
    campos = set(MetadadosLivro.__dataclass_fields__)
    assert campos == {"id", "titulo"}                           # nada de estado ou vencimento


class CacheQuebrado:
    def __contains__(self, chave):
        raise ConnectionError("cache fora do ar")

    def __getitem__(self, chave):
        raise ConnectionError("cache fora do ar")

    def __setitem__(self, chave, valor):
        raise ConnectionError("cache fora do ar")


def test_r09_cache_com_defeito_cai_na_implementacao_original(fabrica):
    sistema_pronto(fabrica)
    consulta = ConsultaComCache(ConsultaBase(fabrica), cache=CacheQuebrado())

    assert consulta.consultar("L1") == MetadadosLivro("L1", "Livro L1")
    assert consulta.consultar("L1") == MetadadosLivro("L1", "Livro L1")


def test_r09_decoradores_e_original_obedecem_ao_mesmo_contrato(fabrica):
    base = ConsultaBase(fabrica)
    for consulta in (base, ConsultaComCache(base), ConsultaComMedicao(base)):
        assert isinstance(consulta, ConsultaAcervo)
        assert consulta.consultar("NAO-EXISTE") is None


def test_r09_cadeia_da_instalacao_mede_as_consultas_do_tratador(fabrica):
    sistema = sistema_pronto(fabrica)
    sistema.acervo.consultar_metadados("L1")
    sistema.acervo.consultar_metadados("L1")
    assert sistema.medicao.total_consultas == 2
