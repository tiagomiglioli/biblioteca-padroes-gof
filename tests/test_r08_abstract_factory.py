"""R08 — Abstract Factory: famílias compatíveis de acesso aos dados."""
import pytest

from dominio.entidades import Livro
from dominio.erros import ErroDominio
from dominio.persistencia_factory import FabricaMemoria, FabricaMySQL, criar_fabrica
from persistencia import memoria, mysql
from persistencia.unidade_trabalho import UnidadeTrabalhoMemoria, UnidadeTrabalhoMySQL


def produtos(fabrica, uow):
    return [fabrica.criar_acervo(uow), fabrica.criar_movimentacao(uow),
            fabrica.criar_relacionamento(uow), fabrica.criar_financeiro(uow)]


def test_r08_perfil_de_teste_fornece_apenas_objetos_em_memoria(monkeypatch):
    def sem_sql(*args, **kwargs):
        raise AssertionError("a família em memória não pode abrir conexão SQL")
    monkeypatch.setattr("mysql.connector.connect", sem_sql)

    fabrica = criar_fabrica("memoria")

    assert isinstance(fabrica, FabricaMemoria)
    with fabrica.criar_unidade_trabalho() as uow:
        assert isinstance(uow, UnidadeTrabalhoMemoria)
        for produto in produtos(fabrica, uow):
            assert type(produto).__module__ == memoria.__name__
        fabrica.criar_acervo(uow).inserir(Livro("L1", "Livro"))


def test_r08_perfil_de_producao_fornece_repositorios_mysql_na_mesma_unidade_de_trabalho(fabrica_mysql):
    assert isinstance(fabrica_mysql, FabricaMySQL)
    with fabrica_mysql.criar_unidade_trabalho() as uow:
        assert isinstance(uow, UnidadeTrabalhoMySQL)
        repositorios = produtos(fabrica_mysql, uow)
        for repositorio in repositorios:
            assert type(repositorio).__module__ == mysql.__name__
        # Mesma conexão = mesma transação: é isso que permite o rollback integral.
        assert {id(repositorio.conexao) for repositorio in repositorios} == {id(uow.conexao)}


def test_r08_perfil_mysql_e_criado_pela_configuracao_sem_conectar():
    fabrica = criar_fabrica("mysql", {"host": "x", "user": "u", "password": "p", "database": "d"})
    assert isinstance(fabrica, FabricaMySQL)


def test_r08_perfil_desconhecido_e_recusado():
    with pytest.raises(ErroDominio):
        criar_fabrica("oracle")       # o Oracle é réplica: a aplicação não escreve nele


def test_r08_repositorio_mysql_recusa_unidade_de_trabalho_em_memoria():
    with FabricaMemoria().criar_unidade_trabalho() as uow_memoria:
        with pytest.raises(TypeError):
            mysql.AcervoMySQL(uow_memoria)


def test_r08_repositorio_em_memoria_recusa_unidade_de_trabalho_mysql():
    uow_mysql = UnidadeTrabalhoMySQL({})      # nem chega a conectar
    with pytest.raises(TypeError):
        memoria.AcervoMemoria(uow_mysql)


def test_r08_unidade_de_trabalho_desfaz_tudo_quando_ha_erro(fabrica):
    with pytest.raises(RuntimeError):
        with fabrica.criar_unidade_trabalho() as uow:
            fabrica.criar_acervo(uow).inserir(Livro("L1", "Livro"))
            raise RuntimeError("falha no meio da operação")

    with fabrica.criar_unidade_trabalho() as uow:
        assert fabrica.criar_acervo(uow).obter("L1") is None


def test_r08_estado_do_livro_e_gravado_e_reconstituido(fabrica):
    from datetime import date
    livro = Livro("L1", "Livro")
    livro.reservar()
    livro.emprestar(date(2026, 11, 1))
    livro.renovar()
    with fabrica.criar_unidade_trabalho() as uow:
        fabrica.criar_acervo(uow).inserir(livro)

    with fabrica.criar_unidade_trabalho() as uow:
        lido = fabrica.criar_acervo(uow).obter("L1")

    assert (lido.nome_estado, lido.num_renovacoes, lido.vencimento) == ("RENOVADO", 1, date(2026, 12, 31))
    assert lido is not livro
