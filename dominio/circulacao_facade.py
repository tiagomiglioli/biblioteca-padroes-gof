"""R04 — GoF Facade: entrada única para as operações de circulação."""
from contextlib import contextmanager
from datetime import date

from dominio.devolucao_observer import EventoDevolucao
from dominio.entidades import Comprovante
from dominio.erros import ErroDominio


class CirculacaoFacade:
    """GoF Facade: coordena Relacionamento, Movimentacao, Acervo e Livro.

    Cada método é uma operação completa e transacional e devolve um Comprovante.
    Os tratadores só falam com esta classe; a interface só fala com os tratadores.
    As regras de estado continuam no Livro (State); aqui fica a ordem dos passos.
    """

    def __init__(self, fabrica, publicador, relogio=date.today):
        self._fabrica = fabrica
        self._publicador = publicador
        self._relogio = relogio          # data injetável: os testes e a demonstração não mexem no relógio

    @contextmanager
    def _transacao(self, uow=None):
        """Abre uma unidade de trabalho, ou participa da que o executor de comandos já abriu."""
        if uow is not None:
            yield uow
        else:
            with self._fabrica.criar_unidade_trabalho() as nova:
                yield nova

    def _livro(self, acervo, livro_id):
        # para_atualizar=True bloqueia o livro até o fim da transação: duas
        # operações simultâneas no mesmo exemplar não se atropelam.
        livro = acervo.obter(livro_id, para_atualizar=True)
        if livro is None:
            raise ErroDominio(f"Livro {livro_id!r} não está cadastrado no acervo.")
        return livro

    def _comprovante(self, operacao, livro, estudante_id, mensagem):
        vencimento = livro.vencimento if livro.nome_estado in ("EMPRESTADO", "RENOVADO") else None
        return Comprovante(operacao, livro.id, estudante_id, livro.nome_estado, vencimento, mensagem)

    def reservar(self, estudante_id, livro_id, uow=None):
        """Regra 5: reserva livro LIVRE para estudante cadastrado. Lança ErroDominio se recusada."""
        with self._transacao(uow) as uow:
            acervo = self._fabrica.criar_acervo(uow)
            livro = self._livro(acervo, livro_id)
            if self._fabrica.criar_relacionamento(uow).obter_estudante(estudante_id) is None:
                raise ErroDominio(f"Estudante {estudante_id!r} não está cadastrado.")
            # A decisão usa o estado ATUAL lido do repositório, nunca um cache de consulta (R09).
            livro.reservar()
            self._fabrica.criar_movimentacao(uow).inserir_reserva(livro_id, estudante_id, self._relogio())
            acervo.atualizar(livro)
            return self._comprovante("reserva", livro, estudante_id, "Reserva registrada.")

    def consultar_reserva(self, estudante_id, livro_id):
        """Regra 6: comprovante da reserva ativa; ErroDominio se não houver."""
        with self._transacao() as uow:
            livro = self._livro(self._fabrica.criar_acervo(uow), livro_id)
            reserva = self._fabrica.criar_movimentacao(uow).consultar_reserva(livro_id, estudante_id)
            if reserva is None:
                raise ErroDominio("Não há reserva ativa deste livro para este estudante.")
            return self._comprovante("consulta de reserva", livro, estudante_id,
                                     f"Reserva nº {reserva.id} ativa desde {reserva.data:%d/%m/%Y}.")

    def emprestar(self, estudante_id, livro_id):
        """Regra 7: efetiva o empréstimo de um livro reservado pelo MESMO estudante."""
        # Os quatro passos abaixo usam a mesma transação. Se qualquer um falhar,
        # o rollback devolve a reserva e o livro continua RESERVADO.
        with self._transacao() as uow:
            acervo = self._fabrica.criar_acervo(uow)
            movimentacao = self._fabrica.criar_movimentacao(uow)
            livro = self._livro(acervo, livro_id)
            reserva = movimentacao.consultar_reserva(livro_id, estudante_id)       # 1. valida a reserva
            if reserva is None:
                raise ErroDominio("Não há reserva ativa deste livro para este estudante.")
            movimentacao.remover_reserva(reserva.id)                               # 2. remove a reserva ativa
            livro.emprestar(self._relogio())
            movimentacao.inserir_emprestimo(livro_id, estudante_id, self._relogio())   # 3. cria o empréstimo
            acervo.atualizar(livro)                                                # 4. atualiza o Livro
            return self._comprovante("emprestimo", livro, estudante_id, "Empréstimo efetivado.")

    def renovar(self, estudante_id, livro_id, uow=None):
        """Regra 8: +30 dias, no máximo duas vezes (a guarda está no State)."""
        with self._transacao(uow) as uow:
            acervo = self._fabrica.criar_acervo(uow)
            livro = self._livro(acervo, livro_id)
            emprestimo = self._fabrica.criar_movimentacao(uow).consultar_emprestimo(livro_id)
            if emprestimo is not None and emprestimo.estudante_id != estudante_id:
                raise ErroDominio("O livro está emprestado a outro estudante.")
            livro.renovar()
            acervo.atualizar(livro)
            return self._comprovante("renovacao", livro, estudante_id,
                                     f"Renovação {livro.num_renovacoes} de 2 registrada.")

    def devolver(self, livro_id, data_devolucao=None):
        """Regra 9: registra a devolução; depois do commit, avisa os ouvintes (Observer)."""
        data_devolucao = data_devolucao or self._relogio()
        with self._transacao() as uow:
            acervo = self._fabrica.criar_acervo(uow)
            movimentacao = self._fabrica.criar_movimentacao(uow)
            relacionamento = self._fabrica.criar_relacionamento(uow)
            livro = self._livro(acervo, livro_id)
            vencimento = livro.vencimento
            livro.devolver()
            emprestimo = movimentacao.consultar_emprestimo(livro_id)
            if emprestimo is None:
                raise ErroDominio("Não há empréstimo em aberto para este livro.")
            if data_devolucao < emprestimo.data_emprestimo:
                raise ErroDominio("A data de devolução não pode ser anterior ao empréstimo.")
            movimentacao.registrar_devolucao(emprestimo.id, data_devolucao)
            acervo.atualizar(livro)
            pessoa = relacionamento.obter_pessoa(relacionamento.obter_estudante(emprestimo.estudante_id).cpf)
            evento = EventoDevolucao(emprestimo.id, livro_id, emprestimo.estudante_id, pessoa.cpf,
                                     pessoa.email, vencimento, data_devolucao)
            comprovante = self._comprovante("devolucao", livro, emprestimo.estudante_id,
                                            f"Devolução registrada com {evento.dias_atraso} dia(s) de atraso.")
        # Só aqui, com a devolução já confirmada (commit), os ouvintes são avisados.
        # Se o commit falhasse, ninguém receberia notícia de algo que não aconteceu.
        self._publicador.publicar(evento)
        return comprovante

    def _evento_simples(self, livro_id, operacao, evento, mensagem):
        """Operações que só movem o estado do livro (inspeção e reparo)."""
        with self._transacao() as uow:
            acervo = self._fabrica.criar_acervo(uow)
            livro = self._livro(acervo, livro_id)
            evento(livro)
            acervo.atualizar(livro)
            return self._comprovante(operacao, livro, None, mensagem)

    def inspecionar(self, livro_id, bom_estado):
        """Decisão da inspeção: bom estado -> LIVRE; danificado -> REPARANDO."""
        return self._evento_simples(livro_id, "inspecao", lambda livro: livro.inspecionar(bom_estado),
                                    "Inspeção registrada.")

    def enviar_para_reparo(self, livro_id):
        return self._evento_simples(livro_id, "envio para reparo", lambda livro: livro.enviar_para_reparo(),
                                    "Livro enviado para reparo.")

    def retornar_do_reparo(self, livro_id):
        return self._evento_simples(livro_id, "retorno do reparo", lambda livro: livro.retornar_do_reparo(),
                                    "Livro de volta ao acervo.")

    def registrar_laudo_irrecuperavel(self, livro_id):
        return self._evento_simples(livro_id, "laudo irrecuperavel",
                                    lambda livro: livro.registrar_laudo_irrecuperavel(),
                                    "Laudo irrecuperável: livro incinerado.")
