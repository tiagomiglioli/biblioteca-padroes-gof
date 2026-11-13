"""Responsáveis e vínculos preservados nos produtos das duas famílias."""
from datetime import date

import pytest

from dominio.entidades import Atendente, Estudante, Livro, Pessoa, Comprovante
from dominio.erros import ErroDominio


@pytest.fixture
def dados(fabrica):
    with fabrica.criar_unidade_trabalho() as uow:
        rel = fabrica.criar_relacionamento(uow)
        for n in range(1, 5):
            rel.inserir_pessoa(Pessoa(str(n) * 11, "Pessoa", str(n), "p@exemplo.com"))
        rel.inserir_estudante(Estudante("E", "1" * 11))
        for n in range(2, 5):
            rel.inserir_atendente(Atendente(f"A{n}", str(n) * 11))
        fabrica.criar_acervo(uow).inserir(Livro("L", "Livro"))
    return fabrica


def test_responsaveis_distintos_persistem_e_reserva_vira_historico(dados):
    with dados.criar_unidade_trabalho() as uow:
        mov = dados.criar_movimentacao(uow)
        reserva = mov.inserir_reserva("L", "E", date(2026, 11, 1), "A2")
        assert mov.consultar_reserva("L", "E").atendente_id == "A2"
        mov.remover_reserva(reserva.id)
        assert mov.consultar_reserva("L", "E") is None
        emp = mov.inserir_emprestimo("L", "E", date(2026, 11, 1), "A3")
        assert mov.consultar_emprestimo("L").atendente_id == "A3"
        mov.registrar_devolucao(emp.id, date(2026, 11, 2), "A4")
    with dados.criar_unidade_trabalho() as uow:
        rel = dados.criar_relacionamento(uow)
        for id in ("A2", "A3", "A4"):
            with pytest.raises(ErroDominio):
                rel.excluir_atendente(id)
        assert rel.obter_atendente("A4", para_atualizar=True) is not None
        assert rel.obter_estudante("E", para_atualizar=True) is not None
        if hasattr(uow, "conexao"):
            cursor = uow.conexao.cursor()
            try:
                cursor.execute("SELECT atendente_id, atendente_devolucao_id FROM emprestimo WHERE id = %s", (emp.id,))
                assert cursor.fetchone() == ("A3", "A4")
                cursor.execute("SELECT atendente_id, ativa FROM reserva WHERE id = %s", (reserva.id,))
                assert cursor.fetchone() == ("A2", 0)
            finally:
                cursor.close()
        else:
            historico = uow.banco.tabelas["emprestimos"][emp.id]
            assert (historico.atendente_id, historico.atendente_devolucao_id) == ("A3", "A4")
            historico_reserva = uow.banco.tabelas["reservas"][reserva.id]
            assert (historico_reserva.atendente_id, historico_reserva.ativa) == ("A2", False)


def test_rollback_preserva_reserva_e_responsavel(dados):
    with dados.criar_unidade_trabalho() as uow:
        reserva = dados.criar_movimentacao(uow).inserir_reserva("L", "E", date(2026, 11, 1), "A2")
    with pytest.raises(RuntimeError):
        with dados.criar_unidade_trabalho() as uow:
            mov = dados.criar_movimentacao(uow)
            mov.remover_reserva(reserva.id)
            mov.inserir_emprestimo("L", "E", date(2026, 11, 1), "A3")
            raise RuntimeError("falha após registrar empréstimo")
    with dados.criar_unidade_trabalho() as uow:
        mov = dados.criar_movimentacao(uow)
        assert mov.consultar_reserva("L", "E").atendente_id == "A2"
        assert mov.consultar_emprestimo("L") is None


@pytest.mark.parametrize("papel", ["estudante", "atendente"])
@pytest.mark.parametrize("fase", ["reserva", "emprestimo", "devolucao"])
def test_papel_usado_nao_pode_trocar_pessoa(dados, papel, fase):
    with dados.criar_unidade_trabalho() as uow:
        mov = dados.criar_movimentacao(uow)
        if fase == "reserva":
            mov.inserir_reserva("L", "E", date(2026, 11, 1), "A2")
        else:
            emp = mov.inserir_emprestimo("L", "E", date(2026, 11, 1), "A2" if fase == "emprestimo" else "A4")
            if fase == "devolucao":
                mov.registrar_devolucao(emp.id, date(2026, 11, 2), "A2")
    with pytest.raises(ErroDominio):
        with dados.criar_unidade_trabalho() as uow:
            rel = dados.criar_relacionamento(uow)
            if papel == "estudante":
                rel.atualizar_estudante(Estudante("E", "4" * 11))
            else:
                rel.atualizar_atendente(Atendente("A2", "4" * 11))
    with dados.criar_unidade_trabalho() as uow:
        rel = dados.criar_relacionamento(uow)
        assert rel.obter_estudante("E").cpf == "1" * 11
        assert rel.obter_atendente("A2").cpf == "2" * 11
        rel.atualizar_atendente(Atendente("A2", "2" * 11))
        rel.atualizar_atendente(Atendente("A3", "4" * 11))
        assert rel.obter_atendente("A3").cpf == "4" * 11


def test_comprovante_antigo_permanece_legivel():
    texto = '{"operacao":"reserva","livro_id":"L","estudante_id":"E","estado":"RESERVADO","vencimento":null,"mensagem":"ok"}'
    assert Comprovante.de_texto(texto).atendente_id is None
