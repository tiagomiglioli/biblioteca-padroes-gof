"""R08 — GoF Abstract Factory: famílias compatíveis de acesso aos dados."""
from abc import ABC, abstractmethod

from dominio.erros import ErroDominio
from persistencia import memoria, mysql
from persistencia.unidade_trabalho import UnidadeTrabalhoMemoria, UnidadeTrabalhoMySQL


class FabricaPersistencia(ABC):
    """GoF Abstract Factory — FabricaAbstrata.

    Cria a unidade de trabalho e os repositórios. O domínio só conhece esta
    classe e os contratos de dominio/pontos_acesso.py; nunca cita memória ou MySQL.
    """

    @abstractmethod
    def criar_unidade_trabalho(self): ...

    @abstractmethod
    def criar_acervo(self, uow):
        """Repositório de Livro."""

    @abstractmethod
    def criar_movimentacao(self, uow): ...

    @abstractmethod
    def criar_relacionamento(self, uow): ...

    @abstractmethod
    def criar_financeiro(self, uow): ...


class FabricaMemoria(FabricaPersistencia):
    """GoF Abstract Factory — FabricaConcreta: família inteira em memória (testes)."""

    def __init__(self):
        self._banco = memoria.BancoMemoria()

    def criar_unidade_trabalho(self):
        return UnidadeTrabalhoMemoria(self._banco)

    def criar_acervo(self, uow):
        return memoria.AcervoMemoria(uow)

    def criar_movimentacao(self, uow):
        return memoria.MovimentacaoMemoria(uow)

    def criar_relacionamento(self, uow):
        return memoria.RelacionamentoMemoria(uow)

    def criar_financeiro(self, uow):
        return memoria.FinanceiroMemoria(uow)


class FabricaMySQL(FabricaPersistencia):
    """GoF Abstract Factory — FabricaConcreta: família inteira MySQL (produção).

    Guarda só os parâmetros de conexão; cada unidade de trabalho abre a sua.
    """

    def __init__(self, parametros_conexao):
        self._parametros = parametros_conexao

    def criar_unidade_trabalho(self):
        return UnidadeTrabalhoMySQL(self._parametros)

    def criar_acervo(self, uow):
        return mysql.AcervoMySQL(uow)

    def criar_movimentacao(self, uow):
        return mysql.MovimentacaoMySQL(uow)

    def criar_relacionamento(self, uow):
        return mysql.RelacionamentoMySQL(uow)

    def criar_financeiro(self, uow):
        return mysql.FinanceiroMySQL(uow)


def criar_fabrica(perfil, parametros_mysql=None):
    """Escolhe a família UMA vez, na inicialização (app.py), pelo perfil de execução."""
    if perfil == "memoria":
        return FabricaMemoria()
    if perfil == "mysql":
        return FabricaMySQL(parametros_mysql)
    raise ErroDominio(f"Perfil de persistência desconhecido: {perfil!r}. Use 'memoria' ou 'mysql'.")
