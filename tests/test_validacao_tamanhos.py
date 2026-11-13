"""Limites persistidos são validados no servidor, não apenas no HTML."""
import pytest

from dominio.erros import ErroDominio
from tests.apoio import ANA, sistema_pronto


@pytest.mark.parametrize("tipo,campo,limite", [
    ("pessoa", "nome", 80), ("pessoa", "sobrenome", 80), ("pessoa", "email", 120),
    ("acervo", "id", 20), ("acervo", "titulo", 200),
    ("estudante", "id", 20), ("atendente", "id", 20),
])
def test_cadastro_recusa_campo_acima_do_limite_sem_gravar(fabrica, tipo, campo, limite):
    sistema = sistema_pronto(fabrica)
    dados = {**ANA, "cpf": "12345678901", "id": "NOVO", "titulo": "Título"}
    sistema.pessoa.inserir({**ANA, "cpf": "99988877766"})
    if tipo in ("estudante", "atendente"):
        dados["cpf"] = "99988877766"
    dados[campo] = "x" * (limite + 1)
    if campo == "email":
        dados[campo] = "x" * (limite - 1) + "@x"
    tratador = getattr(sistema, tipo)
    antes = tratador.listar()
    with pytest.raises(ErroDominio, match="máximo"):
        tratador.inserir(dados)
    depois = tratador.listar()
    if tipo == "acervo":
        assert [(livro.id, livro.titulo) for livro in depois] == [(livro.id, livro.titulo) for livro in antes]
    else:
        assert depois == antes


def test_atualizacao_recusa_titulo_longo_preservando_original(fabrica):
    sistema = sistema_pronto(fabrica)
    with pytest.raises(ErroDominio, match="máximo"):
        sistema.acervo.atualizar({"id": "L1", "titulo": "x" * 201})
    assert sistema.acervo.consultar("L1").titulo == "Livro L1"
    assert sistema.acervo.atualizar({"id": "L1", "titulo": "x" * 200})
    assert sistema.acervo.consultar("L1").titulo == "x" * 200


def test_grupo_e_login_respeitam_limites_do_banco(fabrica):
    sistema = sistema_pronto(fabrica)
    with pytest.raises(ErroDominio, match="máximo"):
        sistema.acervo.criar_grupo("x" * 101, None)
    with pytest.raises(ErroDominio, match="máximo"):
        sistema.acesso.criar_usuario("x" * 51, "senha-de-teste")
    assert sistema.acervo.arvore().contar_livros() == 0
