"""R04 — Facade: entrada única e transacional para a circulação."""
from datetime import timedelta

import pytest

from dominio.entidades import Comprovante
from dominio.erros import ErroDominio
from tests.apoio import HOJE, emprestar, livro_no_banco, sistema_pronto


def reserva_ativa(fabrica, estudante_id="E1", livro_id="L1"):
    with fabrica.criar_unidade_trabalho() as uow:
        return fabrica.criar_movimentacao(uow).consultar_reserva(livro_id, estudante_id)


def emprestimo_aberto(fabrica, livro_id="L1"):
    with fabrica.criar_unidade_trabalho() as uow:
        return fabrica.criar_movimentacao(uow).consultar_emprestimo(livro_id)


def test_r04_emprestimo_valida_reserva_remove_reserva_cria_emprestimo_e_atualiza_livro(fabrica):
    sistema = sistema_pronto(fabrica)
    sistema.fachada.reservar("E1", "L1", atendente_id="A1")
    assert reserva_ativa(fabrica) is not None

    comprovante = sistema.fachada.emprestar("E1", "L1", atendente_id="A1")

    assert reserva_ativa(fabrica) is None
    assert emprestimo_aberto(fabrica).estudante_id == "E1"
    assert livro_no_banco(fabrica).nome_estado == "EMPRESTADO"
    assert comprovante == Comprovante("emprestimo", "L1", "E1", "EMPRESTADO",
                                      HOJE + timedelta(days=30), comprovante.mensagem, atendente_id="A1")


def test_r04_fachada_devolve_comprovantes_e_nao_colecoes(fabrica):
    sistema = sistema_pronto(fabrica)
    resultados = [sistema.fachada.reservar("E1", "L1", atendente_id="A1"), sistema.fachada.consultar_reserva("E1", "L1"),
                  sistema.fachada.emprestar("E1", "L1", atendente_id="A1"), sistema.fachada.renovar("E1", "L1"),
                  sistema.fachada.devolver("L1", HOJE, atendente_id="A1"), sistema.fachada.inspecionar("L1", True)]

    for resultado in resultados:
        assert isinstance(resultado, Comprovante)
        for valor in vars(resultado).values():
            assert not isinstance(valor, (list, dict, set, tuple))


def test_r04_emprestimo_exige_reserva_do_mesmo_estudante(fabrica):
    sistema = sistema_pronto(fabrica)
    sistema.fachada.reservar("E1", "L1", atendente_id="A1")

    with pytest.raises(ErroDominio):
        sistema.fachada.emprestar("E2", "L1", atendente_id="A1")

    assert reserva_ativa(fabrica) is not None
    assert livro_no_banco(fabrica).nome_estado == "RESERVADO"


class _MovimentacaoQueFalha:
    def __init__(self, real):
        self._real = real

    def __getattr__(self, nome):
        return getattr(self._real, nome)

    def inserir_emprestimo(self, *argumentos):
        raise RuntimeError("falha injetada depois de remover a reserva")


class _FabricaComFalha:
    """Família real, exceto por um passo do meio do empréstimo que quebra."""

    def __init__(self, real):
        self._real = real

    def __getattr__(self, nome):
        return getattr(self._real, nome)

    def criar_movimentacao(self, uow):
        return _MovimentacaoQueFalha(self._real.criar_movimentacao(uow))


def test_r04_falha_no_meio_do_emprestimo_desfaz_tudo(fabrica):
    sistema_pronto(fabrica).fachada.reservar("E1", "L1", atendente_id="A1")
    sistema_com_falha = sistema_pronto(_FabricaComFalha(fabrica))

    with pytest.raises(RuntimeError):
        sistema_com_falha.fachada.emprestar("E1", "L1", atendente_id="A1")

    assert reserva_ativa(fabrica) is not None            # a reserva removida voltou
    assert emprestimo_aberto(fabrica) is None
    assert livro_no_banco(fabrica).nome_estado == "RESERVADO"


def test_r04_reserva_exige_livro_e_estudante_cadastrados(fabrica):
    sistema = sistema_pronto(fabrica)
    with pytest.raises(ErroDominio):
        sistema.fachada.reservar("E1", "NAO-EXISTE", atendente_id="A1")
    with pytest.raises(ErroDominio):
        sistema.fachada.reservar("NAO-EXISTE", "L1", atendente_id="A1")
    assert livro_no_banco(fabrica).nome_estado == "LIVRE"


def test_r04_renovacao_exige_emprestimo_do_mesmo_estudante(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)

    with pytest.raises(ErroDominio):
        sistema.fachada.renovar("E2", "L1")

    assert livro_no_banco(fabrica).vencimento == HOJE + timedelta(days=30)


def test_r04_tratadores_delegam_a_fachada(fabrica):
    sistema = sistema_pronto(fabrica)

    sistema.emprestimo.solicitar_reserva("E1", "L1", autor="ana", atendente_id="A1")
    assert sistema.emprestimo.consultar_reserva("E1", "L1").estado == "RESERVADO"
    assert sistema.emprestimo.realizar_emprestimo("E1", "L1", atendente_id="A1").estado == "EMPRESTADO"
    assert sistema.emprestimo.renovar_emprestimo("E1", "L1", autor="ana").estado == "RENOVADO"
    assert sistema.devolucao.registrar_devolucao("L1", HOJE, atendente_id="A1").estado == "DEVOLVIDO"
    assert sistema.devolucao.inspecionar("L1", bom_estado=False).estado == "REPARANDO"
    assert sistema.devolucao.registrar_laudo_irrecuperavel("L1").estado == "INCINERADO"
