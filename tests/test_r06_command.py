"""R06 — Command: solicitações de circulação como objetos, executadas uma única vez."""
import threading
import uuid
from datetime import datetime, timedelta

import pytest

from dominio.circulacao_command import ComandoRenovacao, ComandoReserva
from dominio.erros import ErroDominio
from tests.apoio import HOJE, emprestar, livro_no_banco, sistema_pronto


def renovacao(sistema, id=None):
    return ComandoRenovacao(sistema.fachada, "E1", "L1", autor="ana", id=id)


def test_r06_solicitacao_tem_identificador_autor_instante_e_execucao(fabrica):
    sistema = sistema_pronto(fabrica)
    comando = ComandoReserva(sistema.fachada, "E1", "L1", autor="ana", atendente_id="A1")

    assert uuid.UUID(comando.id)
    assert comando.autor == "ana"
    assert isinstance(comando.criado_em, datetime)
    assert callable(comando.executar)


def test_r06_renovacao_executada_duas_vezes_com_o_mesmo_identificador_acrescenta_apenas_30_dias(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    id_solicitacao = str(uuid.uuid4())

    primeiro = sistema.executor.executar(renovacao(sistema, id_solicitacao))
    segundo = sistema.executor.executar(renovacao(sistema, id_solicitacao))

    livro = livro_no_banco(fabrica)
    assert livro.vencimento == HOJE + timedelta(days=60)      # 30 do empréstimo + 30, uma vez só
    assert livro.num_renovacoes == 1
    assert segundo == primeiro                                # resposta consistente na repetição


def test_r06_solicitacoes_diferentes_continuam_sujeitas_ao_limite_de_duas_renovacoes(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    sistema.executor.executar(renovacao(sistema))
    sistema.executor.executar(renovacao(sistema))

    with pytest.raises(ErroDominio):
        sistema.executor.executar(renovacao(sistema))

    livro = livro_no_banco(fabrica)
    assert (livro.num_renovacoes, livro.vencimento) == (2, HOJE + timedelta(days=90))


def test_r06_submissoes_simultaneas_do_mesmo_identificador_executam_uma_unica_vez(fabrica):
    sistema = sistema_pronto(fabrica)
    emprestar(sistema)
    id_solicitacao = str(uuid.uuid4())
    largada = threading.Barrier(8)
    comprovantes, erros = [], []

    def submeter():
        largada.wait()
        try:
            comprovantes.append(sistema.executor.executar(renovacao(sistema, id_solicitacao)))
        except Exception as erro:               # qualquer erro reprova o teste abaixo
            erros.append(erro)

    threads = [threading.Thread(target=submeter) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert erros == []
    assert len(comprovantes) == 8 and len(set(comprovantes)) == 1
    livro = livro_no_banco(fabrica)
    assert (livro.num_renovacoes, livro.vencimento) == (1, HOJE + timedelta(days=60))


def test_r06_reserva_repetida_com_o_mesmo_identificador_nao_e_refeita(fabrica):
    sistema = sistema_pronto(fabrica)
    comando = ComandoReserva(sistema.fachada, "E1", "L1", autor="ana", atendente_id="A1")

    primeiro = sistema.executor.executar(comando)
    segundo = sistema.executor.executar(comando)       # sem idempotência, o State recusaria

    assert segundo == primeiro
    assert livro_no_banco(fabrica).nome_estado == "RESERVADO"


def test_r06_identificador_que_nao_e_uuid_e_recusado(fabrica):
    sistema = sistema_pronto(fabrica)
    with pytest.raises(ErroDominio):
        ComandoReserva(sistema.fachada, "E1", "L1", autor="ana", id="'; DROP TABLE livro; --", atendente_id="A1")


def test_r06_solicitacao_recusada_nao_fica_registrada_como_executada(fabrica):
    sistema = sistema_pronto(fabrica)
    comando = renovacao(sistema)                        # livro ainda LIVRE: será recusada
    with pytest.raises(ErroDominio):
        sistema.executor.executar(comando)

    emprestar(sistema)
    assert sistema.executor.executar(comando).estado == "RENOVADO"
