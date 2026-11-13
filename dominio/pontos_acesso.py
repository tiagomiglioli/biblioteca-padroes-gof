"""Pontos internos de acesso do Trabalho 02: Acervo, Movimentacao e Relacionamento.

São os contratos (ProdutoAbstrato do Abstract Factory, R08) que o domínio usa
para guardar e buscar dados. O domínio nunca sabe se por trás há memória ou MySQL.
Financeiro segue o mesmo molde para multas, boletos e quitações.
"""
from abc import ABC, abstractmethod


class Acervo(ABC):
    """Ponto único de acesso aos livros e aos grupos (seções) do acervo."""

    @abstractmethod
    def inserir(self, livro): ...

    @abstractmethod
    def obter(self, livro_id, para_atualizar=False):
        """Devolve o Livro ou None. `para_atualizar` bloqueia a linha até o fim da transação."""

    @abstractmethod
    def atualizar(self, livro): ...

    @abstractmethod
    def excluir(self, livro_id): ...

    @abstractmethod
    def listar(self): ...

    @abstractmethod
    def inserir_grupo(self, nome, pai_id):
        """Cria unidade/seção/subseção e devolve o id gerado."""

    @abstractmethod
    def listar_grupos(self):
        """Tuplas (id, nome, pai_id)."""

    @abstractmethod
    def listar_itens(self):
        """Tuplas (livro_id, grupo_id) dos livros já colocados em algum grupo."""

    @abstractmethod
    def definir_grupo(self, livro_id, grupo_id): ...


class Movimentacao(ABC):
    """Ponto único de acesso a reservas, empréstimos, devoluções e solicitações."""

    @abstractmethod
    def inserir_reserva(self, livro_id, estudante_id, data): ...

    @abstractmethod
    def consultar_reserva(self, livro_id, estudante_id):
        """Reserva ATIVA do livro para o estudante, ou None."""

    @abstractmethod
    def remover_reserva(self, reserva_id):
        """Encerra a reserva ativa (ela vira histórico)."""

    @abstractmethod
    def inserir_emprestimo(self, livro_id, estudante_id, data): ...

    @abstractmethod
    def consultar_emprestimo(self, livro_id):
        """Empréstimo em aberto do livro, ou None."""

    @abstractmethod
    def registrar_devolucao(self, emprestimo_id, data): ...

    @abstractmethod
    def registrar_comando(self, comando_id, tipo, autor, criado_em):
        """Marca a solicitação como executada. Devolve False se o id já existia (R06)."""

    @abstractmethod
    def gravar_resultado_comando(self, comando_id, resultado): ...

    @abstractmethod
    def resultado_comando(self, comando_id): ...


class Relacionamento(ABC):
    """Ponto único de acesso a pessoas, estudantes, atendentes e usuários de login."""

    @abstractmethod
    def inserir_pessoa(self, pessoa): ...

    @abstractmethod
    def obter_pessoa(self, cpf): ...

    @abstractmethod
    def atualizar_pessoa(self, pessoa): ...

    @abstractmethod
    def excluir_pessoa(self, cpf): ...

    @abstractmethod
    def listar_pessoas(self): ...

    @abstractmethod
    def inserir_estudante(self, estudante): ...

    @abstractmethod
    def obter_estudante(self, estudante_id): ...

    @abstractmethod
    def atualizar_estudante(self, estudante): ...

    @abstractmethod
    def excluir_estudante(self, estudante_id): ...

    @abstractmethod
    def listar_estudantes(self): ...

    @abstractmethod
    def inserir_atendente(self, atendente): ...

    @abstractmethod
    def obter_atendente(self, atendente_id): ...

    @abstractmethod
    def atualizar_atendente(self, atendente): ...

    @abstractmethod
    def excluir_atendente(self, atendente_id): ...

    @abstractmethod
    def listar_atendentes(self): ...

    @abstractmethod
    def inserir_usuario(self, usuario): ...

    @abstractmethod
    def obter_usuario(self, login): ...


class Financeiro(ABC):
    """Ponto único de acesso a multas, boletos e quitações."""

    @abstractmethod
    def inserir_multa(self, emprestimo_id, estudante_id, dias_atraso, valor, politica): ...

    @abstractmethod
    def obter_multa(self, multa_id): ...

    @abstractmethod
    def obter_multa_do_emprestimo(self, emprestimo_id): ...

    @abstractmethod
    def obter_multa_por_boleto(self, banco, id_boleto): ...

    @abstractmethod
    def listar_multas(self): ...

    @abstractmethod
    def registrar_boleto(self, multa_id, banco, id_boleto): ...

    @abstractmethod
    def registrar_quitacao(self, id_notificacao, multa_id):
        """Quita a multa. Devolve False se a notificação (ou a multa) já foi quitada (R03)."""
