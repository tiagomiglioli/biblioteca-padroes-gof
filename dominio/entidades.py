"""Entidades e comprovantes do domínio da biblioteca."""
import json
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal

from dominio.estados import EstadoLivre


class Livro:
    """GoF State — Context: delega cada evento ao objeto de estado atual.

    Guarda também os dados do empréstimo em curso (vencimento e número de
    renovações), porque as guardas da máquina de estados dependem deles.
    """

    def __init__(self, id, titulo, estado=None, num_renovacoes=0, vencimento=None):
        self.id = id
        self.titulo = titulo
        self._estado = estado or EstadoLivre()      # T1: todo livro nasce LIVRE
        self.num_renovacoes = num_renovacoes
        self.vencimento = vencimento

    @property
    def nome_estado(self):
        """Nome do estado atual; é o que a persistência grava."""
        return self._estado.nome

    def mudar_estado(self, novo_estado):
        """Chamado pelos estados concretos ao concluir uma transição."""
        self._estado = novo_estado

    def reservar(self):
        self._estado.reservar(self)

    def emprestar(self, hoje):
        self._estado.emprestar(self, hoje)

    def renovar(self):
        self._estado.renovar(self)

    def devolver(self):
        self._estado.devolver(self)

    def inspecionar(self, bom_estado):
        self._estado.inspecionar(self, bom_estado)

    def enviar_para_reparo(self):
        self._estado.enviar_para_reparo(self)

    def retornar_do_reparo(self):
        self._estado.retornar_do_reparo(self)

    def registrar_laudo_irrecuperavel(self):
        self._estado.registrar_laudo_irrecuperavel(self)

    def excluir(self):
        self._estado.excluir(self)


@dataclass
class Pessoa:
    cpf: str
    nome: str
    sobrenome: str
    email: str


@dataclass
class Estudante:
    """Papel assumido por uma Pessoa (vínculo pelo CPF)."""
    id: str
    cpf: str


@dataclass
class Atendente:
    """Papel assumido por uma Pessoa (vínculo pelo CPF)."""
    id: str
    cpf: str


@dataclass
class Usuario:
    """Quem faz login na interface web. Só o hash da senha é guardado."""
    login: str
    senha_hash: str


@dataclass
class Reserva:
    id: int
    livro_id: str
    estudante_id: str
    data: date
    atendente_id: str | None = None
    ativa: bool = True


@dataclass
class Emprestimo:
    id: int
    livro_id: str
    estudante_id: str
    data_emprestimo: date
    data_devolucao: date | None = None
    atendente_id: str | None = None
    atendente_devolucao_id: str | None = None


@dataclass
class Multa:
    """Valor e política ficam gravados na emissão e não são recalculados (R02)."""
    id: int
    emprestimo_id: int
    estudante_id: str
    dias_atraso: int
    valor: Decimal
    politica: str
    quitada: bool = False
    banco: str | None = None
    id_boleto: str | None = None


@dataclass(frozen=True)
class Comprovante:
    """O que a fachada devolve à interface: um resumo imutável, nunca coleções."""
    operacao: str
    livro_id: str
    estudante_id: str | None
    estado: str
    vencimento: date | None
    mensagem: str
    atendente_id: str | None = None

    def para_texto(self):
        """Texto guardado junto ao id da solicitação, para repetir a mesma resposta (R06)."""
        dados = asdict(self)
        dados["vencimento"] = self.vencimento.isoformat() if self.vencimento else None
        return json.dumps(dados)

    @classmethod
    def de_texto(cls, texto):
        dados = json.loads(texto)
        if dados["vencimento"]:
            dados["vencimento"] = date.fromisoformat(dados["vencimento"])
        return cls(**dados)
