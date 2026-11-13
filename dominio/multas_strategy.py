"""R02 — GoF Strategy: políticas de cálculo de multa, e o serviço que as usa."""
from abc import ABC, abstractmethod
from decimal import Decimal

from dominio.bancos_adapter import SolicitacaoCobranca
from dominio.erros import ErroDominio

CENTAVO = Decimal("0.01")
VALOR_POR_DIA = Decimal("1.00")
TETO = Decimal("20.00")
DIAS_DE_TOLERANCIA = 2


class PoliticaMulta(ABC):
    """GoF Strategy — Estrategia: contrato de qualquer política de multa."""

    nome = ""

    @abstractmethod
    def calcular(self, dias_atraso):
        """Recebe os dias de atraso (inteiro >= 0) e devolve o valor em Decimal, com centavos."""


class MultaOriginal(PoliticaMulta):
    """GoF Strategy — EstrategiaConcreta: R$ 1,00 por dia de atraso."""

    nome = "original"

    def calcular(self, dias_atraso):
        return (VALOR_POR_DIA * dias_atraso).quantize(CENTAVO)


class MultaComTeto(PoliticaMulta):
    """GoF Strategy — EstrategiaConcreta: R$ 1,00 por dia, limitada a R$ 20,00."""

    nome = "teto"

    def calcular(self, dias_atraso):
        return min(VALOR_POR_DIA * dias_atraso, TETO).quantize(CENTAVO)


class MultaComTolerancia(PoliticaMulta):
    """GoF Strategy — EstrategiaConcreta: os dois primeiros dias de atraso não são cobrados."""

    nome = "tolerancia"

    def calcular(self, dias_atraso):
        return (VALOR_POR_DIA * max(dias_atraso - DIAS_DE_TOLERANCIA, 0)).quantize(CENTAVO)


# Para incluir uma política: criar a classe e acrescentá-la aqui. O serviço não muda.
POLITICAS = {politica.nome: politica for politica in (MultaOriginal(), MultaComTeto(), MultaComTolerancia())}


def politica_por_nome(nome):
    if nome not in POLITICAS:
        raise ErroDominio(f"Política de multa desconhecida: {nome!r}.")
    return POLITICAS[nome]


class ServicoMulta:
    """GoF Strategy — Contexto (e Client do Adapter, R03).

    Calcula com a política vigente e cobra pelo contrato CobrancaInstitucional.
    Não conhece nenhuma política concreta nem qual é a instituição de cobrança.
    """

    def __init__(self, fabrica, cobranca, configuracao, email):
        self._fabrica = fabrica
        self._cobranca = cobranca
        self._configuracao = configuracao
        self._email = email

    def emitir_multa(self, evento):
        """Emite multa e boleto para uma devolução atrasada. Devolve a Multa, ou None se o valor for zero."""
        politica = politica_por_nome(self._configuracao.politica_multa)
        valor = politica.calcular(evento.dias_atraso)
        if valor <= 0:
            return None
        with self._fabrica.criar_unidade_trabalho() as uow:
            financeiro = self._fabrica.criar_financeiro(uow)
            multa = financeiro.obter_multa_do_emprestimo(evento.emprestimo_id)
            if multa is None:
                # Valor e nome da política ficam gravados: trocar a política depois
                # não recalcula esta multa.
                multa = financeiro.inserir_multa(evento.emprestimo_id, evento.estudante_id,
                                                 evento.dias_atraso, valor, politica.nome)
        return self.emitir_boleto(multa.id)

    def emitir_boleto(self, multa_id):
        """Emite o boleto da multa; se já existe, devolve o mesmo (segunda via)."""
        with self._fabrica.criar_unidade_trabalho() as uow:
            multa = self._fabrica.criar_financeiro(uow).obter_multa(multa_id)
            if multa is None:
                raise ErroDominio("Multa não encontrada.")
            if multa.id_boleto:
                return multa
            relacionamento = self._fabrica.criar_relacionamento(uow)
            pessoa = relacionamento.obter_pessoa(relacionamento.obter_estudante(multa.estudante_id).cpf)

        # A chamada à instituição fica fora da transação: não seguramos o banco de dados
        # enquanto esperamos um sistema externo.
        boleto = self._cobranca.emitir_boleto(SolicitacaoCobranca(f"multa-{multa.id}", pessoa.cpf, multa.valor))

        with self._fabrica.criar_unidade_trabalho() as uow:
            self._fabrica.criar_financeiro(uow).registrar_boleto(multa.id, boleto.banco, boleto.id_boleto)
        multa.banco, multa.id_boleto = boleto.banco, boleto.id_boleto
        self._email.enviar(pessoa.email, "Boleto de multa da biblioteca",
                           f"Multa de R$ {multa.valor} — boleto {boleto.id_boleto} ({boleto.banco}).")
        return multa

    def registrar_pagamento(self, notificacao_externa):
        """Recebe a notificação crua da instituição. Devolve True só se ESTA chamada quitou a multa."""
        pagamento = self._cobranca.traduzir_notificacao(notificacao_externa)
        if not pagamento.pago:
            return False
        with self._fabrica.criar_unidade_trabalho() as uow:
            financeiro = self._fabrica.criar_financeiro(uow)
            multa = financeiro.obter_multa_por_boleto(self._cobranca.nome_banco, pagamento.id_boleto)
            if multa is None:
                return False
            # Idempotência: a repetição é barrada pelas chaves únicas da quitação.
            return financeiro.registrar_quitacao(pagamento.id_notificacao, multa.id)
