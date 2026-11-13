"""R10 — Composite: organização hierárquica do acervo."""
import pytest

from dominio.acervo_composite import ComponenteAcervo, GrupoAcervo, ItemLivro, mover
from dominio.entidades import Livro
from dominio.erros import ErroDominio
from tests.apoio import emprestar, livro_no_banco, sistema_pronto


def unidade_com_duas_secoes():
    unidade, exatas, humanas = GrupoAcervo("Unidade Centro"), GrupoAcervo("Exatas"), GrupoAcervo("Humanas")
    unidade.adicionar(exatas)
    unidade.adicionar(humanas)
    for livro_id in ("L1", "L2", "L3"):
        exatas.adicionar(ItemLivro(livro_id))
    for livro_id in ("L4", "L5"):
        humanas.adicionar(ItemLivro(livro_id))
    return unidade, exatas, humanas


def test_r10_unidade_com_secoes_de_tres_e_dois_livros_informa_cinco():
    unidade, exatas, humanas = unidade_com_duas_secoes()

    assert (exatas.contar_livros(), humanas.contar_livros()) == (3, 2)
    assert unidade.contar_livros() == 5
    assert unidade.listar_livros() == ["L1", "L2", "L3", "L4", "L5"]


def test_r10_grupos_e_itens_respondem_as_mesmas_operacoes():
    item = ItemLivro("L1")
    for componente in (item, GrupoAcervo("Seção")):
        assert isinstance(componente, ComponenteAcervo)
    assert (item.contar_livros(), item.listar_livros()) == (1, ["L1"])
    assert (GrupoAcervo("Vazia").contar_livros(), GrupoAcervo("Vazia").listar_livros()) == (0, [])


def test_r10_arvore_tem_profundidade_variavel():
    unidade, exatas, _ = unidade_com_duas_secoes()
    subsecao, prateleira = GrupoAcervo("Computação"), GrupoAcervo("Prateleira 3")
    exatas.adicionar(subsecao)
    subsecao.adicionar(prateleira)
    prateleira.adicionar(ItemLivro("L6"))

    assert unidade.contar_livros() == 6
    assert exatas.contar_livros() == 4


def test_r10_grupo_recusa_ciclos():
    unidade, exatas, _ = unidade_com_duas_secoes()
    subsecao = GrupoAcervo("Computação")
    exatas.adicionar(subsecao)

    with pytest.raises(ErroDominio):
        exatas.adicionar(exatas)              # grupo dentro de si mesmo
    with pytest.raises(ErroDominio):
        subsecao.adicionar(unidade)           # ancestral dentro do descendente
    with pytest.raises(ErroDominio):
        mover(exatas, subsecao)               # mover para dentro de si mesmo

    assert unidade.contar_livros() == 5
    assert exatas.pai is unidade


def test_r10_grupo_recusa_livro_que_ja_pertence_a_outro_grupo():
    unidade, exatas, humanas = unidade_com_duas_secoes()
    item_l1 = exatas.filhos[0]

    with pytest.raises(ErroDominio):
        humanas.adicionar(ItemLivro("L1"))    # mesmo livro, outro item
    with pytest.raises(ErroDominio):
        humanas.adicionar(item_l1)            # mesmo item, sem sair do grupo atual

    assert unidade.contar_livros() == 5
    assert humanas.listar_livros() == ["L4", "L5"]


def test_r10_item_referencia_o_livro_apenas_pelo_identificador():
    item = ItemLivro("L1")
    assert not any(isinstance(valor, Livro) for valor in vars(item).values())
    assert item.livro_id == "L1"


def test_r10_mover_entre_secoes_muda_so_a_arvore():
    unidade, exatas, humanas = unidade_com_duas_secoes()
    item = exatas.filhos[0]

    mover(item, humanas)

    assert (exatas.contar_livros(), humanas.contar_livros(), unidade.contar_livros()) == (2, 3, 5)
    assert item.livro_id == "L1" and item.pai is humanas


def test_r10_mover_livro_nao_altera_id_estado_nem_emprestimo(fabrica):
    sistema = sistema_pronto(fabrica)
    unidade = sistema.acervo.criar_grupo("Unidade Centro", None)
    exatas = sistema.acervo.criar_grupo("Exatas", unidade)
    humanas = sistema.acervo.criar_grupo("Humanas", unidade)
    sistema.acervo.mover_livro("L1", exatas)
    emprestar(sistema)
    antes = livro_no_banco(fabrica)

    sistema.acervo.mover_livro("L1", humanas)

    depois = livro_no_banco(fabrica)
    assert (depois.id, depois.nome_estado, depois.vencimento, depois.num_renovacoes) == \
        (antes.id, "EMPRESTADO", antes.vencimento, antes.num_renovacoes)
    with fabrica.criar_unidade_trabalho() as uow:
        assert fabrica.criar_movimentacao(uow).consultar_emprestimo("L1").estudante_id == "E1"
    arvore = sistema.acervo.arvore()
    assert arvore.contar_livros() == 1
    assert [grupo.contar_livros() for grupo in arvore.filhos[0].filhos] == [0, 1]


def test_r10_arvore_persistida_conta_recursivamente(fabrica):
    sistema = sistema_pronto(fabrica, livros=("L1", "L2", "L3", "L4", "L5"))
    unidade = sistema.acervo.criar_grupo("Unidade Centro", None)
    exatas = sistema.acervo.criar_grupo("Exatas", unidade)
    humanas = sistema.acervo.criar_grupo("Humanas", unidade)
    for livro_id in ("L1", "L2", "L3"):
        sistema.acervo.mover_livro(livro_id, exatas)
    for livro_id in ("L4", "L5"):
        sistema.acervo.mover_livro(livro_id, humanas)

    assert sistema.acervo.arvore().contar_livros() == 5


def test_r10_tratador_recusa_livro_ou_grupo_inexistente(fabrica):
    sistema = sistema_pronto(fabrica)
    grupo = sistema.acervo.criar_grupo("Unidade", None)
    with pytest.raises(ErroDominio):
        sistema.acervo.mover_livro("NAO-EXISTE", grupo)
    with pytest.raises(ErroDominio):
        sistema.acervo.mover_livro("L1", 9999)
    with pytest.raises(ErroDominio):
        sistema.acervo.criar_grupo("Seção órfã", 9999)
