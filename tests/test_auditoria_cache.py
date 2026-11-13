"""Metadados acompanham alterações confirmadas no acervo."""
from dominio.consulta_decorator import ConsultaBase, ConsultaComCache, ConsultaComMedicao
from dominio.tratadores import TratadorDeAcervo
from tests.apoio import sistema_pronto


def test_cache_atualiza_titulo_depois_da_edicao(fabrica):
    sistema = sistema_pronto(fabrica)
    assert sistema.acervo.consultar_metadados("L1").titulo == "Livro L1"
    assert sistema.acervo.atualizar({"id": "L1", "titulo": "Título corrigido"}) is True
    assert sistema.acervo.consultar_metadados("L1").titulo == "Título corrigido"
    assert sistema.medicao.total_consultas == 2


def test_cache_remove_livro_depois_da_exclusao(fabrica):
    sistema = sistema_pronto(fabrica)
    assert sistema.acervo.consultar_metadados("L1") is not None
    assert sistema.acervo.excluir("L1") is True
    assert sistema.acervo.consultar_metadados("L1") is None


def test_falha_na_invalidacao_nao_impede_mutacao_confirmada(fabrica):
    sistema = sistema_pronto(fabrica)
    titulos_confirmados = []

    class CacheComFalha(dict):
        def pop(self, chave, padrao=None):
            # Uma nova transação já deve enxergar a alteração ao invalidar.
            titulos_confirmados.append(sistema.acervo.consultar("L1").titulo)
            raise ConnectionError("cache indisponível para remoção")

    consulta = ConsultaComMedicao(ConsultaComCache(ConsultaBase(fabrica), CacheComFalha()))
    tratador = TratadorDeAcervo(fabrica, consulta)
    assert tratador.consultar_metadados("L1").titulo == "Livro L1"
    assert tratador.atualizar({"id": "L1", "titulo": "Título corrigido"}) is True
    assert sistema.acervo.consultar("L1").titulo == "Título corrigido"
    assert titulos_confirmados == ["Título corrigido"]
    assert tratador.consultar_metadados("L1").titulo == "Título corrigido"
