"""R09 — GoF Decorator: consulta ao acervo com recursos opcionais.

É o padrão Decorator do GoF (objetos que embrulham objetos do mesmo contrato),
não o @decorator de funções do Python.
"""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

registro = logging.getLogger("biblioteca")


@dataclass(frozen=True)
class MetadadosLivro:
    """Só dados descritivos. De propósito NÃO tem estado nem vencimento:
    assim, nada que saia do cache serve para decidir uma reserva."""
    id: str
    titulo: str


class ConsultaAcervo(ABC):
    """GoF Decorator — Componente: contrato da consulta de metadados."""

    @abstractmethod
    def consultar(self, livro_id):
        """Devolve MetadadosLivro, ou None se o livro não existe."""


class ConsultaBase(ConsultaAcervo):
    """GoF Decorator — Essencia: a consulta original, direto no repositório."""

    def __init__(self, fabrica):
        self._fabrica = fabrica

    def consultar(self, livro_id):
        with self._fabrica.criar_unidade_trabalho() as uow:
            livro = self._fabrica.criar_acervo(uow).obter(livro_id)
        return MetadadosLivro(livro.id, livro.titulo) if livro else None


class DecoradorConsulta(ConsultaAcervo):
    """GoF Decorator — Decorador: guarda o componente embrulhado e repassa a chamada."""

    def __init__(self, componente):
        self._componente = componente

    def consultar(self, livro_id):
        return self._componente.consultar(livro_id)


class ConsultaComCache(DecoradorConsulta):
    """GoF Decorator — DecoradorConcreto: lembra dos metadados já consultados."""

    def __init__(self, componente, cache=None):
        super().__init__(componente)
        # shortcut: cache sem expiração nem invalidação; trocar por um com prazo
        # se os títulos passarem a ser editados com frequência.
        self._cache = {} if cache is None else cache

    def consultar(self, livro_id):
        # O cache é um acessório: se ele falhar, a consulta original responde.
        try:
            if livro_id in self._cache:
                return self._cache[livro_id]
        except Exception:
            registro.warning("Cache de consulta indisponível; usando a consulta original.")
            return super().consultar(livro_id)
        metadados = super().consultar(livro_id)
        if metadados is not None:
            try:
                self._cache[livro_id] = metadados
            except Exception:
                registro.warning("Não foi possível gravar no cache de consulta.")
        return metadados


class ConsultaComMedicao(DecoradorConsulta):
    """GoF Decorator — DecoradorConcreto: conta as consultas e soma o tempo gasto."""

    def __init__(self, componente):
        super().__init__(componente)
        self.total_consultas = 0
        self.segundos = 0.0

    def consultar(self, livro_id):
        inicio = time.perf_counter()
        try:
            return super().consultar(livro_id)
        finally:
            self.total_consultas += 1
            self.segundos += time.perf_counter() - inicio
