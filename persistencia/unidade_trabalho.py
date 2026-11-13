"""Unidade de trabalho: uma transação por operação (commit ou rollback).

Uso:  with fabrica.criar_unidade_trabalho() as uow: ...
Saiu do bloco sem erro -> commit. Saiu com erro -> rollback de TUDO.
"""
import copy
from abc import ABC, abstractmethod

import mysql.connector


class UnidadeTrabalho(ABC):
    """GoF Abstract Factory — ProdutoAbstrato: a transação que os repositórios compartilham."""

    def __enter__(self):
        self._iniciar()
        return self

    def __exit__(self, tipo_erro, erro, traceback):
        # Tudo ou nada: se qualquer passo da operação falhou, nenhum efeito permanece.
        if tipo_erro is None:
            self._confirmar()
        else:
            self._desfazer()
        return False            # o erro original continua subindo para quem chamou

    @abstractmethod
    def _iniciar(self): ...

    @abstractmethod
    def _confirmar(self): ...

    @abstractmethod
    def _desfazer(self): ...


class UnidadeTrabalhoMemoria(UnidadeTrabalho):
    """GoF Abstract Factory — ProdutoConcreto (família memória).

    Imita a transação com uma cópia das tabelas: no rollback, a cópia volta.
    A trava faz uma operação por vez, como o bloqueio de linha faz no MySQL.
    """

    def __init__(self, banco):
        self.banco = banco

    def _iniciar(self):
        self.banco.trava.acquire()
        self._copia = copy.deepcopy(self.banco.tabelas)

    def _confirmar(self):
        self.banco.trava.release()

    def _desfazer(self):
        self.banco.tabelas = self._copia
        self.banco.trava.release()


class UnidadeTrabalhoMySQL(UnidadeTrabalho):
    """GoF Abstract Factory — ProdutoConcreto (família MySQL).

    Abre UMA conexão para a operação; todos os repositórios criados com esta
    unidade usam essa mesma conexão, logo a mesma transação. A conexão é
    fechada ao final: nada de conexão global compartilhada entre requisições.
    """

    def __init__(self, parametros):
        self._parametros = parametros
        self.conexao = None

    def _iniciar(self):
        self.conexao = mysql.connector.connect(**self._parametros, autocommit=False)

    def _confirmar(self):
        try:
            self.conexao.commit()
        finally:
            self.conexao.close()

    def _desfazer(self):
        try:
            self.conexao.rollback()
        finally:
            self.conexao.close()
