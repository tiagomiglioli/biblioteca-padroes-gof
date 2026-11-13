"""R01 — GoF State: os sete estados do Livro.

Cada transição da máquina de estados (T1–T11 do Trabalho 02) é um método da
classe do estado de ORIGEM; a guarda e a ação ficam no corpo desse método.
"""
from datetime import timedelta

from dominio.erros import TransicaoInvalida

PRAZO_EMPRESTIMO_DIAS = 30
PRAZO_RENOVACAO_DIAS = 30
LIMITE_RENOVACOES = 2


class EstadoLivro:
    """GoF State — State: contrato dos eventos do Livro.

    Por padrão todo evento é recusado; cada estado concreto sobrescreve
    apenas os eventos que aceita. Recusar não altera o livro.
    """

    nome = ""

    def _recusar(self, evento):
        raise TransicaoInvalida(f"Livro {self.nome} não aceita a operação '{evento}'.")

    def reservar(self, livro):
        self._recusar("reservar")

    def emprestar(self, livro, hoje):
        self._recusar("emprestar")

    def renovar(self, livro):
        self._recusar("renovar")

    def devolver(self, livro):
        self._recusar("devolver")

    def inspecionar(self, livro, bom_estado):
        self._recusar("inspecionar")

    def enviar_para_reparo(self, livro):
        self._recusar("enviar para reparo")

    def retornar_do_reparo(self, livro):
        self._recusar("retornar do reparo")

    def registrar_laudo_irrecuperavel(self, livro):
        self._recusar("registrar laudo irrecuperável")

    def excluir(self, livro):
        self._recusar("excluir")


class EstadoLivre(EstadoLivro):
    """GoF State — ConcreteState: livro disponível para reserva."""

    nome = "LIVRE"

    def reservar(self, livro):                       # T2
        livro.mudar_estado(EstadoReservado())

    def enviar_para_reparo(self, livro):             # T9
        livro.mudar_estado(EstadoReparando())

    def excluir(self, livro):                        # T11: só livro LIVRE pode sair do acervo
        pass


class EstadoReservado(EstadoLivro):
    """GoF State — ConcreteState: há reserva ativa; só resta efetivar o empréstimo."""

    nome = "RESERVADO"

    def emprestar(self, livro, hoje):                # T3
        livro.num_renovacoes = 0
        livro.vencimento = hoje + timedelta(days=PRAZO_EMPRESTIMO_DIAS)
        livro.mudar_estado(EstadoEmprestado())


def _renovar(livro):
    """Guarda e ação da renovação, comuns a EMPRESTADO (T4) e RENOVADO (T5)."""
    # A guarda vem ANTES de mexer no vencimento: se viesse depois, a terceira
    # tentativa já teria ganhado 30 dias quando fosse recusada.
    if not livro.num_renovacoes < LIMITE_RENOVACOES:
        raise TransicaoInvalida("Limite de duas renovações atingido.")
    livro.vencimento = livro.vencimento + timedelta(days=PRAZO_RENOVACAO_DIAS)
    livro.num_renovacoes += 1
    livro.mudar_estado(EstadoRenovado())


class EstadoEmprestado(EstadoLivro):
    """GoF State — ConcreteState: livro com o estudante, ainda sem renovação."""

    nome = "EMPRESTADO"

    def renovar(self, livro):                        # T4
        _renovar(livro)

    def devolver(self, livro):                       # T6
        livro.mudar_estado(EstadoDevolvido())


class EstadoRenovado(EstadoLivro):
    """GoF State — ConcreteState: empréstimo renovado uma ou duas vezes."""

    nome = "RENOVADO"

    def renovar(self, livro):                        # T5 (autotransição)
        _renovar(livro)

    def devolver(self, livro):                       # T6
        livro.mudar_estado(EstadoDevolvido())


class EstadoDevolvido(EstadoLivro):
    """GoF State — ConcreteState: recebido pelo atendente, aguardando inspeção.

    Não aceita reservar: o livro só volta a LIVRE por decisão da inspeção.
    """

    nome = "DEVOLVIDO"

    def inspecionar(self, livro, bom_estado):        # T7 / T8
        livro.mudar_estado(EstadoLivre() if bom_estado else EstadoReparando())


class EstadoReparando(EstadoLivro):
    """GoF State — ConcreteState: livro no setor de reparos."""

    nome = "REPARANDO"

    def retornar_do_reparo(self, livro):             # T10
        livro.mudar_estado(EstadoLivre())

    def registrar_laudo_irrecuperavel(self, livro):  # premissa da lista de problemas
        livro.mudar_estado(EstadoIncinerado())


class EstadoIncinerado(EstadoLivro):
    """GoF State — ConcreteState: estado final; nenhum evento é aceito."""

    nome = "INCINERADO"


# Os estados não têm atributos, então uma instância de cada pode ser compartilhada.
ESTADOS = {classe.nome: classe() for classe in (
    EstadoLivre, EstadoReservado, EstadoEmprestado, EstadoRenovado,
    EstadoDevolvido, EstadoReparando, EstadoIncinerado)}


def estado_por_nome(nome):
    """Reconstitui o objeto de estado a partir do nome gravado no banco."""
    return ESTADOS[nome]
