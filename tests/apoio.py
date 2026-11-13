"""Cenário comum dos testes: uma pessoa, dois estudantes e livros cadastrados."""
from datetime import date

from dominio.configuracao_singleton import ConfiguracaoSistema
from dominio.tratadores import montar_sistema

HOJE = date(2026, 11, 1)
ANA = {"cpf": "11122233344", "nome": "Ana", "sobrenome": "Silva", "email": "ana@exemplo.com"}
BIA = {"cpf": "55566677788", "nome": "Bia", "sobrenome": "Souza", "email": "bia@exemplo.com"}


def sistema_pronto(fabrica, livros=("L1",)):
    """Monta o sistema com a data fixa em HOJE e cadastra o cenário básico."""
    sistema = montar_sistema(fabrica, ConfiguracaoSistema.obter_instancia(), relogio=lambda: HOJE)
    sistema.pessoa.inserir(ANA)
    sistema.pessoa.inserir(BIA)
    sistema.estudante.inserir({"id": "E1", "cpf": ANA["cpf"]})
    sistema.estudante.inserir({"id": "E2", "cpf": BIA["cpf"]})
    sistema.atendente.inserir({"id": "A1", "cpf": BIA["cpf"]})
    for livro_id in livros:
        sistema.acervo.inserir({"id": livro_id, "titulo": f"Livro {livro_id}"})
    return sistema


def livro_no_banco(fabrica, livro_id="L1"):
    with fabrica.criar_unidade_trabalho() as uow:
        return fabrica.criar_acervo(uow).obter(livro_id)


def emprestar(sistema, estudante_id="E1", livro_id="L1"):
    sistema.fachada.reservar(estudante_id, livro_id)
    return sistema.fachada.emprestar(estudante_id, livro_id)
