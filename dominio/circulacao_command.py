"""R06 — GoF Command: solicitações de reserva e renovação como objetos.

Quem cria: o tratador, com os dados que a tela enviou (inclusive o id).
Quem invoca: ExecutorComandos.  Quem executa de fato: CirculacaoFacade (o Alvo).
Não há desfazer: reserva e renovação têm efeitos externos (o estudante já foi
informado) e a regra de negócio não prevê cancelamento.
"""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from dominio.entidades import Comprovante
from dominio.erros import ErroDominio


class Comando(ABC):
    """GoF Command — Comando: identificador, autor, instante de criação e executar()."""

    tipo = ""

    def __init__(self, fachada, estudante_id, livro_id, autor, id=None, criado_em=None):
        try:
            self.id = str(uuid.UUID(id)) if id else str(uuid.uuid4())
        except ValueError:
            raise ErroDominio("Identificador de solicitação inválido.") from None
        self.autor = autor
        self.criado_em = criado_em or datetime.now()
        self.estudante_id = estudante_id
        self.livro_id = livro_id
        self._fachada = fachada

    @abstractmethod
    def executar(self, uow):
        """Executa na unidade de trabalho do executor e devolve um Comprovante."""


class ComandoReserva(Comando):
    """GoF Command — ComandoConcreto: pedido de reserva de um livro."""

    tipo = "reserva"

    def executar(self, uow):
        return self._fachada.reservar(self.estudante_id, self.livro_id, uow)


class ComandoRenovacao(Comando):
    """GoF Command — ComandoConcreto: pedido de renovação de um empréstimo."""

    tipo = "renovacao"

    def executar(self, uow):
        return self._fachada.renovar(self.estudante_id, self.livro_id, uow)


class ExecutorComandos:
    """GoF Command — Invocador: executa cada solicitação no máximo uma vez."""

    def __init__(self, fabrica):
        self._fabrica = fabrica

    def executar(self, comando):
        """Devolve o Comprovante; se o id já foi executado, devolve o comprovante original."""
        # Idempotência: o registro do id e o efeito do comando ficam na MESMA transação.
        # O id é chave única; uma segunda submissão (até simultânea) espera a primeira
        # terminar, não consegue registrar o id e recebe a resposta já gravada.
        # Se o comando for recusado, o rollback apaga também o registro do id.
        with self._fabrica.criar_unidade_trabalho() as uow:
            movimentacao = self._fabrica.criar_movimentacao(uow)
            if not movimentacao.registrar_comando(comando.id, comando.tipo, comando.autor, comando.criado_em):
                return Comprovante.de_texto(movimentacao.resultado_comando(comando.id))
            comprovante = comando.executar(uow)
            movimentacao.gravar_resultado_comando(comando.id, comprovante.para_texto())
            return comprovante
