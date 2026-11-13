"""R03 — GoF Adapter: bancos com APIs incompatíveis atrás de um contrato único.

BancoA e BancoB SIMULAM sistemas externos (não são o MySQL). Os adaptadores
são reais: toda conversão de valor, documento, identificador e situação mora neles.
"""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from dominio.erros import ErroDominio


@dataclass(frozen=True)
class SolicitacaoCobranca:
    """Pedido de cobrança no formato da instituição: valor em reais (Decimal), CPF com 11 dígitos."""
    referencia: str
    cpf: str
    valor: Decimal


@dataclass(frozen=True)
class BoletoEmitido:
    banco: str
    id_boleto: str
    situacao: str


@dataclass(frozen=True)
class PagamentoConfirmado:
    id_notificacao: str
    id_boleto: str
    pago: bool


class CobrancaInstitucional(ABC):
    """GoF Adapter — Target: o contrato de cobrança que o ServicoMulta conhece."""

    nome_banco = ""

    @abstractmethod
    def emitir_boleto(self, solicitacao):
        """Recebe SolicitacaoCobranca e devolve BoletoEmitido."""

    @abstractmethod
    def traduzir_notificacao(self, notificacao_externa):
        """Converte a notificação crua do banco em PagamentoConfirmado."""

    @abstractmethod
    def simular_pagamento(self, id_boleto):
        """Apoio à demonstração: pede ao banco simulado a notificação que ele enviaria."""


class BancoA:
    """GoF Adapter — Adaptee (simulado): trabalha em CENTAVOS inteiros e CPF só com dígitos."""

    def __init__(self):
        self.recebido = None

    def criar_cobranca(self, valor_centavos, cpf, referencia):
        self.recebido = {"valor_centavos": valor_centavos, "cpf": cpf, "referencia": referencia}
        return {"codigo": f"A-{uuid.uuid4().hex[:12]}", "situacao": "REGISTRADO"}

    def avisar_pagamento(self, codigo):
        return {"evento": f"evt-{uuid.uuid4().hex}", "codigo": codigo, "situacao": "LIQUIDADO"}


class BancoB:
    """GoF Adapter — Adaptee (simulado): trabalha em REAIS decimais, CPF com máscara e status numérico."""

    def __init__(self):
        self.recebido = None

    def emitir_titulo(self, pedido):
        self.recebido = pedido
        return {"titulo_id": uuid.uuid4().int % 10**12, "status": 1}

    def webhook_pagamento(self, titulo_id):
        return {"notification_uuid": str(uuid.uuid4()), "titulo_id": titulo_id, "status": 2}


class AdaptadorBancoA(CobrancaInstitucional):
    """GoF Adapter — Adapter do Banco A."""

    nome_banco = "A"
    _SITUACOES = {"REGISTRADO": "EMITIDO", "LIQUIDADO": "PAGO"}

    def __init__(self, banco):
        self._banco = banco

    def emitir_boleto(self, solicitacao):
        # Conversão de centavos: R$ 7,00 -> 700. Decimal evita o erro de arredondamento do float.
        centavos = int(solicitacao.valor * 100)
        resposta = self._banco.criar_cobranca(centavos, solicitacao.cpf, solicitacao.referencia)
        return BoletoEmitido(self.nome_banco, resposta["codigo"], self._SITUACOES[resposta["situacao"]])

    def traduzir_notificacao(self, notificacao_externa):
        situacao = self._SITUACOES.get(notificacao_externa["situacao"])
        return PagamentoConfirmado(notificacao_externa["evento"], notificacao_externa["codigo"], situacao == "PAGO")

    def simular_pagamento(self, id_boleto):
        return self._banco.avisar_pagamento(id_boleto)


class AdaptadorBancoB(CobrancaInstitucional):
    """GoF Adapter — Adapter do Banco B."""

    nome_banco = "B"
    _SITUACOES = {1: "EMITIDO", 2: "PAGO"}

    def __init__(self, banco):
        self._banco = banco

    def emitir_boleto(self, solicitacao):
        cpf = solicitacao.cpf
        resposta = self._banco.emitir_titulo({
            "amount": solicitacao.valor.quantize(Decimal("0.01")),               # reais: 7.00
            "document": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",            # 111.222.333-44
            "our_number": solicitacao.referencia,
        })
        # O banco B usa id numérico; a instituição guarda identificadores como texto.
        return BoletoEmitido(self.nome_banco, str(resposta["titulo_id"]), self._SITUACOES[resposta["status"]])

    def traduzir_notificacao(self, notificacao_externa):
        situacao = self._SITUACOES.get(notificacao_externa["status"])
        return PagamentoConfirmado(notificacao_externa["notification_uuid"],
                                   str(notificacao_externa["titulo_id"]), situacao == "PAGO")

    def simular_pagamento(self, id_boleto):
        return self._banco.webhook_pagamento(int(id_boleto))


def criar_cobranca(banco):
    """Escolhe o banco da instalação UMA vez, na inicialização, pela configuração (BANCO_COBRANCA)."""
    adaptadores = {"A": lambda: AdaptadorBancoA(BancoA()), "B": lambda: AdaptadorBancoB(BancoB())}
    if banco not in adaptadores:
        raise ErroDominio(f"Banco de cobrança desconhecido: {banco!r}. Use 'A' ou 'B'.")
    return adaptadores[banco]()
