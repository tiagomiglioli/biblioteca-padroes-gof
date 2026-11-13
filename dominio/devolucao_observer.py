"""R05 — GoF Observer: reações independentes à devolução de um livro."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from threading import RLock

registro = logging.getLogger("biblioteca")


@dataclass(frozen=True)
class EventoDevolucao:
    """O que aconteceu, com todos os dados que os ouvintes precisam.

    O evento leva os dados para que cada ouvinte não precise consultá-los depois,
    quando o livro já pode ter mudado (ex.: emprestado de novo).
    """
    emprestimo_id: int
    livro_id: str
    estudante_id: str
    cpf: str
    email: str
    vencimento: date
    data_devolucao: date

    @property
    def dias_atraso(self):
        return max((self.data_devolucao - self.vencimento).days, 0)


class OuvinteDevolucao(ABC):
    """GoF Observer — Observer: contrato de quem reage à devolução."""

    @abstractmethod
    def notificar(self, evento): ...


class PublicadorDevolucao:
    """GoF Observer — Subject: mantém os ouvintes registrados e avisa todos."""

    def __init__(self):
        self._ouvintes = []
        self.falhas = []
        self._entregues = set()
        self._trava = RLock()

    def registrar(self, ouvinte):
        self._ouvintes.append(ouvinte)

    def publicar(self, evento):
        """Chamado pela fachada DEPOIS do commit da devolução."""
        # shortcut: deduplicação local; usar registro persistido se houver fila entre processos.
        with self._trava:
            for indice, ouvinte in enumerate(self._ouvintes):
                chave = (evento.emprestimo_id, indice)
                if chave in self._entregues:
                    continue
                # Cada ouvinte é isolado: se um falhar (ex.: e-mail fora do ar), os outros
                # ainda são avisados e a devolução, já confirmada, não é desfeita.
                try:
                    ouvinte.notificar(evento)
                    self._entregues.add(chave)
                except Exception as erro:
                    self.falhas.append((type(ouvinte).__name__, str(erro)))
                    registro.exception("Ouvinte %s falhou na devolução do livro %s",
                                       type(ouvinte).__name__, evento.livro_id)


class ServicoEmail:
    """E-mail simulado: guarda as mensagens numa caixa de saída e registra em log."""

    def __init__(self):
        self.caixa_de_saida = []

    def enviar(self, destinatario, assunto, corpo):
        self.caixa_de_saida.append((destinatario, assunto, corpo))
        registro.info("E-mail para %s: %s", destinatario, assunto)


class OuvinteInspecao(OuvinteDevolucao):
    """GoF Observer — ConcreteObserver: põe o livro na fila de inspeção.

    Só avisa. Quem tira o livro de DEVOLVIDO é a decisão explícita da inspeção.
    """

    def __init__(self):
        self.pendentes = []

    def notificar(self, evento):
        self.pendentes.append(evento.livro_id)


class OuvinteMulta(OuvinteDevolucao):
    """GoF Observer — ConcreteObserver: pede a multa ao Financeiro quando há atraso."""

    def __init__(self, servico_multa):
        self._servico_multa = servico_multa

    def notificar(self, evento):
        if evento.dias_atraso > 0:
            self._servico_multa.emitir_multa(evento)


class OuvinteIndicadores(OuvinteDevolucao):
    """GoF Observer — ConcreteObserver: contadores de devoluções para o painel."""

    def __init__(self):
        self.devolucoes = 0
        self.atrasadas = 0
        self.dias_de_atraso = 0

    def notificar(self, evento):
        self.devolucoes += 1
        if evento.dias_atraso > 0:
            self.atrasadas += 1
            self.dias_de_atraso += evento.dias_atraso


class OuvinteEmail(OuvinteDevolucao):
    """GoF Observer — ConcreteObserver: confirma a devolução ao estudante por e-mail."""

    def __init__(self, email):
        self._email = email

    def notificar(self, evento):
        self._email.enviar(evento.email, "Devolução registrada",
                           f"Livro {evento.livro_id} devolvido em {evento.data_devolucao:%d/%m/%Y}.")
