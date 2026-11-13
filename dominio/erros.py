"""Erros de regra de negócio. A interface mostra a mensagem; nunca SQL ou traceback."""


class ErroDominio(Exception):
    """Regra da biblioteca violada (mensagem em português, segura para exibir)."""


class TransicaoInvalida(ErroDominio):
    """Evento que o estado atual do Livro não aceita (R01)."""
