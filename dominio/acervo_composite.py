"""R10 — GoF Composite: unidades, seções e subseções do acervo em árvore."""
from abc import ABC, abstractmethod

from dominio.erros import ErroDominio


class ComponenteAcervo(ABC):
    """GoF Composite — Componente: grupos e itens respondem às mesmas operações."""

    def __init__(self):
        self.pai = None

    @abstractmethod
    def contar_livros(self): ...

    @abstractmethod
    def listar_livros(self):
        """Lista de identificadores de livro."""


class ItemLivro(ComponenteAcervo):
    """GoF Composite — Folha: referencia um livro SÓ pelo identificador.

    Não guarda o objeto Livro: mover o item na árvore não tem como tocar
    no estado do livro nem na Movimentacao.
    """

    def __init__(self, livro_id):
        super().__init__()
        self.livro_id = livro_id

    def contar_livros(self):
        return 1

    def listar_livros(self):
        return [self.livro_id]


class GrupoAcervo(ComponenteAcervo):
    """GoF Composite — Composto: unidade, seção ou subseção, em qualquer profundidade."""

    def __init__(self, nome, id=None):
        super().__init__()
        self.nome = nome
        self.id = id
        self.filhos = []

    def contar_livros(self):
        # Recursão: cada filho responde por si, seja item (1) ou grupo (soma dos seus filhos).
        return sum(filho.contar_livros() for filho in self.filhos)

    def listar_livros(self):
        return [livro_id for filho in self.filhos for livro_id in filho.listar_livros()]

    def _raiz(self):
        grupo = self
        while grupo.pai is not None:
            grupo = grupo.pai
        return grupo

    def _ancestrais_e_eu(self):
        grupo = self
        while grupo is not None:
            yield grupo
            grupo = grupo.pai

    def adicionar(self, componente):
        """Coloca o componente neste grupo. Lança ErroDominio em ciclo ou livro repetido."""
        # Proteção contra ciclo: um grupo não pode entrar em si mesmo nem num descendente,
        # senão a contagem recursiva nunca terminaria.
        if any(componente is grupo for grupo in self._ancestrais_e_eu()):
            raise ErroDominio("Um grupo não pode conter a si mesmo nem a um de seus ancestrais.")
        if componente.pai is not None:
            raise ErroDominio("Este componente já pertence a outro grupo; use mover().")
        # Um livro em um único lugar: confere a árvore inteira, a partir da raiz.
        repetidos = set(componente.listar_livros()) & set(self._raiz().listar_livros())
        if repetidos:
            raise ErroDominio(f"Livro já pertence a outro grupo: {', '.join(sorted(repetidos))}.")
        componente.pai = self
        self.filhos.append(componente)

    def remover(self, componente):
        self.filhos.remove(componente)
        componente.pai = None


def mover(componente, destino):
    """Tira o componente do grupo atual e o coloca em `destino`. Se o destino recusar, nada muda."""
    origem = componente.pai
    posicao = origem.filhos.index(componente)
    origem.remover(componente)
    try:
        destino.adicionar(componente)
    except ErroDominio:
        componente.pai = origem
        origem.filhos.insert(posicao, componente)
        raise


def montar_arvore(grupos, itens):
    """Reconstrói a árvore a partir das linhas guardadas.

    `grupos`: tuplas (id, nome, pai_id); `itens`: tuplas (livro_id, grupo_id).
    Devolve (raiz, grupos_por_id, itens_por_livro). A raiz "Acervo" reúne as unidades.
    """
    raiz = GrupoAcervo("Acervo")
    grupos_por_id = {grupo_id: GrupoAcervo(nome, grupo_id) for grupo_id, nome, _ in grupos}
    for grupo_id, _, pai_id in grupos:
        grupos_por_id.get(pai_id, raiz).adicionar(grupos_por_id[grupo_id])
    itens_por_livro = {}
    for livro_id, grupo_id in itens:
        itens_por_livro[livro_id] = ItemLivro(livro_id)
        grupos_por_id[grupo_id].adicionar(itens_por_livro[livro_id])
    return raiz, grupos_por_id, itens_por_livro
