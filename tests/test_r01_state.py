"""R01 — State: ciclo de vida do Livro (transições T1–T11 do Trabalho 02)."""
from datetime import date, timedelta

import pytest

from dominio.entidades import Livro
from dominio.erros import TransicaoInvalida
from dominio.estados import ESTADOS, estado_por_nome

HOJE = date(2026, 11, 1)


def livro_emprestado():
    livro = Livro("L1", "Padrões de Projeto")
    livro.reservar()
    livro.emprestar(HOJE)
    return livro


def test_r01_ha_uma_classe_para_cada_um_dos_sete_estados():
    nomes = {"LIVRE", "RESERVADO", "EMPRESTADO", "RENOVADO", "DEVOLVIDO", "REPARANDO", "INCINERADO"}
    assert set(ESTADOS) == nomes
    assert len({type(estado) for estado in ESTADOS.values()}) == 7


def test_r01_terceira_renovacao_recusada_sem_alterar_vencimento():
    livro = livro_emprestado()
    livro.renovar()
    livro.renovar()
    vencimento_antes = livro.vencimento
    assert vencimento_antes == HOJE + timedelta(days=90)

    with pytest.raises(TransicaoInvalida):
        livro.renovar()

    assert livro.vencimento == vencimento_antes
    assert livro.num_renovacoes == 2
    assert livro.nome_estado == "RENOVADO"


def test_r01_devolvido_nao_inspecionado_nao_pode_ser_reservado():
    livro = livro_emprestado()
    livro.devolver()

    with pytest.raises(TransicaoInvalida):
        livro.reservar()

    assert livro.nome_estado == "DEVOLVIDO"


def test_r01_laudo_irrecuperavel_leva_reparando_a_incinerado():
    livro = Livro("L1", "Livro")
    livro.enviar_para_reparo()
    assert livro.nome_estado == "REPARANDO"

    livro.registrar_laudo_irrecuperavel()

    assert livro.nome_estado == "INCINERADO"


def test_r01_ciclo_completo_segue_a_maquina_de_estados():
    livro = Livro("L1", "Livro")
    assert livro.nome_estado == "LIVRE"                       # T1
    livro.reservar()
    assert livro.nome_estado == "RESERVADO"                   # T2
    livro.emprestar(HOJE)
    assert livro.nome_estado == "EMPRESTADO"                  # T3
    assert livro.vencimento == HOJE + timedelta(days=30)
    livro.renovar()
    assert livro.nome_estado == "RENOVADO"                    # T4
    livro.renovar()
    assert livro.nome_estado == "RENOVADO"                    # T5
    livro.devolver()
    assert livro.nome_estado == "DEVOLVIDO"                   # T6
    livro.inspecionar(bom_estado=False)
    assert livro.nome_estado == "REPARANDO"                   # T8
    livro.retornar_do_reparo()
    assert livro.nome_estado == "LIVRE"                       # T10


def test_r01_inspecao_em_bom_estado_libera_o_livro():
    livro = livro_emprestado()
    livro.devolver()
    livro.inspecionar(bom_estado=True)                        # T7
    assert livro.nome_estado == "LIVRE"


EVENTOS = {
    "reservar": lambda livro: livro.reservar(),
    "emprestar": lambda livro: livro.emprestar(HOJE),
    "renovar": lambda livro: livro.renovar(),
    "devolver": lambda livro: livro.devolver(),
    "inspecionar": lambda livro: livro.inspecionar(bom_estado=True),
    "enviar_para_reparo": lambda livro: livro.enviar_para_reparo(),
    "retornar_do_reparo": lambda livro: livro.retornar_do_reparo(),
    "registrar_laudo_irrecuperavel": lambda livro: livro.registrar_laudo_irrecuperavel(),
    "excluir": lambda livro: livro.excluir(),
}

# Eventos que cada estado aceita; todo o resto deve ser recusado sem mexer no livro.
ACEITOS = {
    "LIVRE": {"reservar", "enviar_para_reparo", "excluir"},
    "RESERVADO": {"emprestar"},
    "EMPRESTADO": {"renovar", "devolver"},
    "RENOVADO": {"renovar", "devolver"},
    "DEVOLVIDO": {"inspecionar"},
    "REPARANDO": {"retornar_do_reparo", "registrar_laudo_irrecuperavel"},
    "INCINERADO": set(),
}

RECUSAS = [(estado, evento) for estado in ACEITOS for evento in EVENTOS if evento not in ACEITOS[estado]]


@pytest.mark.parametrize("estado,evento", RECUSAS)
def test_r01_evento_invalido_e_recusado_sem_alterar_o_livro(estado, evento):
    livro = Livro("L1", "Livro", estado=estado_por_nome(estado), num_renovacoes=1, vencimento=HOJE)

    with pytest.raises(TransicaoInvalida):
        EVENTOS[evento](livro)

    assert (livro.nome_estado, livro.num_renovacoes, livro.vencimento) == (estado, 1, HOJE)


def test_r01_estado_e_reconstituido_pelo_nome_gravado():
    livro = livro_emprestado()
    nome_gravado = livro.nome_estado            # é isto que vai para a coluna livro.estado

    recarregado = Livro("L1", "Livro", estado=estado_por_nome(nome_gravado),
                        num_renovacoes=livro.num_renovacoes, vencimento=livro.vencimento)
    recarregado.renovar()

    assert recarregado.nome_estado == "RENOVADO"
