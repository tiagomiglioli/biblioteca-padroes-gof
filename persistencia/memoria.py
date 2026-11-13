"""Família EM MEMÓRIA dos repositórios (perfil de testes). Nenhum SQL aqui.

Tudo que entra ou sai é copiado, como num banco de verdade: alterar um
objeto lido não altera o que está guardado até alguém chamar atualizar().
"""
import copy
import threading

from dominio.entidades import Emprestimo, Multa, Reserva
from dominio.pontos_acesso import Acervo, Financeiro, Movimentacao, Relacionamento
from persistencia.unidade_trabalho import UnidadeTrabalhoMemoria

TABELAS = ("livros", "grupos", "itens", "reservas", "emprestimos", "comandos", "pessoas",
           "estudantes", "atendentes", "usuarios", "multas", "quitacoes")


class BancoMemoria:
    """Os 'dados do banco' da família em memória, vivos enquanto o processo viver."""

    def __init__(self):
        self.trava = threading.RLock()
        self.tabelas = {nome: {} for nome in TABELAS}
        self._ultimo_id = 0

    def proximo_id(self):
        self._ultimo_id += 1
        return self._ultimo_id


class _RepositorioMemoria:
    def __init__(self, uow):
        # Impede misturar famílias: repositório em memória só aceita unidade em memória.
        if not isinstance(uow, UnidadeTrabalhoMemoria):
            raise TypeError("Repositório em memória exige UnidadeTrabalhoMemoria.")
        self._banco = uow.banco

    def _tabela(self, nome):
        return self._banco.tabelas[nome]

    def _guardar(self, tabela, chave, valor):
        self._tabela(tabela)[chave] = copy.deepcopy(valor)

    def _ler(self, tabela, chave):
        return copy.deepcopy(self._tabela(tabela).get(chave))

    def _todos(self, tabela):
        linhas = self._tabela(tabela)
        return tuple(copy.deepcopy(linhas[chave]) for chave in sorted(linhas))


class AcervoMemoria(_RepositorioMemoria, Acervo):
    """GoF Abstract Factory — ProdutoConcreto (memória): repositório de Livro."""

    def inserir(self, livro):
        self._guardar("livros", livro.id, livro)

    def obter(self, livro_id, para_atualizar=False):
        return self._ler("livros", livro_id)      # a trava da unidade já isola a operação

    def atualizar(self, livro):
        self._guardar("livros", livro.id, livro)

    def excluir(self, livro_id):
        self._tabela("livros").pop(livro_id, None)
        self._tabela("itens").pop(livro_id, None)

    def listar(self):
        return self._todos("livros")

    def inserir_grupo(self, nome, pai_id):
        grupo_id = self._banco.proximo_id()
        self._guardar("grupos", grupo_id, (grupo_id, nome, pai_id))
        return grupo_id

    def listar_grupos(self):
        return self._todos("grupos")

    def listar_itens(self):
        return tuple(sorted(self._tabela("itens").items()))

    def definir_grupo(self, livro_id, grupo_id):
        self._tabela("itens")[livro_id] = grupo_id


class MovimentacaoMemoria(_RepositorioMemoria, Movimentacao):
    """GoF Abstract Factory — ProdutoConcreto (memória): repositório de Movimentacao."""

    def inserir_reserva(self, livro_id, estudante_id, data):
        reserva = Reserva(self._banco.proximo_id(), livro_id, estudante_id, data)
        self._guardar("reservas", reserva.id, reserva)
        return reserva

    def consultar_reserva(self, livro_id, estudante_id):
        for reserva in self._todos("reservas"):
            if (reserva.livro_id, reserva.estudante_id) == (livro_id, estudante_id):
                return reserva
        return None

    def remover_reserva(self, reserva_id):
        del self._tabela("reservas")[reserva_id]

    def inserir_emprestimo(self, livro_id, estudante_id, data):
        emprestimo = Emprestimo(self._banco.proximo_id(), livro_id, estudante_id, data)
        self._guardar("emprestimos", emprestimo.id, emprestimo)
        return emprestimo

    def consultar_emprestimo(self, livro_id):
        for emprestimo in self._todos("emprestimos"):
            if emprestimo.livro_id == livro_id and emprestimo.data_devolucao is None:
                return emprestimo
        return None

    def registrar_devolucao(self, emprestimo_id, data):
        self._tabela("emprestimos")[emprestimo_id].data_devolucao = data

    def registrar_comando(self, comando_id, tipo, autor, criado_em):
        if comando_id in self._tabela("comandos"):
            return False
        self._tabela("comandos")[comando_id] = None
        return True

    def gravar_resultado_comando(self, comando_id, resultado):
        self._tabela("comandos")[comando_id] = resultado

    def resultado_comando(self, comando_id):
        return self._tabela("comandos").get(comando_id)


class RelacionamentoMemoria(_RepositorioMemoria, Relacionamento):
    """GoF Abstract Factory — ProdutoConcreto (memória): repositório de Relacionamento."""

    def inserir_pessoa(self, pessoa):
        self._guardar("pessoas", pessoa.cpf, pessoa)

    def obter_pessoa(self, cpf):
        return self._ler("pessoas", cpf)

    def atualizar_pessoa(self, pessoa):
        self._guardar("pessoas", pessoa.cpf, pessoa)

    def excluir_pessoa(self, cpf):
        self._tabela("pessoas").pop(cpf, None)

    def listar_pessoas(self):
        return self._todos("pessoas")

    def inserir_estudante(self, estudante):
        self._guardar("estudantes", estudante.id, estudante)

    def obter_estudante(self, estudante_id):
        return self._ler("estudantes", estudante_id)

    def atualizar_estudante(self, estudante):
        self._guardar("estudantes", estudante.id, estudante)

    def excluir_estudante(self, estudante_id):
        self._tabela("estudantes").pop(estudante_id, None)

    def listar_estudantes(self):
        return self._todos("estudantes")

    def inserir_atendente(self, atendente):
        self._guardar("atendentes", atendente.id, atendente)

    def obter_atendente(self, atendente_id):
        return self._ler("atendentes", atendente_id)

    def atualizar_atendente(self, atendente):
        self._guardar("atendentes", atendente.id, atendente)

    def excluir_atendente(self, atendente_id):
        self._tabela("atendentes").pop(atendente_id, None)

    def listar_atendentes(self):
        return self._todos("atendentes")

    def inserir_usuario(self, usuario):
        self._guardar("usuarios", usuario.login, usuario)

    def obter_usuario(self, login):
        return self._ler("usuarios", login)


class FinanceiroMemoria(_RepositorioMemoria, Financeiro):
    """GoF Abstract Factory — ProdutoConcreto (memória): multas, boletos e quitações."""

    def inserir_multa(self, emprestimo_id, estudante_id, dias_atraso, valor, politica):
        multa = Multa(self._banco.proximo_id(), emprestimo_id, estudante_id, dias_atraso, valor, politica)
        self._guardar("multas", multa.id, multa)
        return multa

    def obter_multa(self, multa_id):
        return self._ler("multas", multa_id)

    def _primeira(self, condicao):
        return next((multa for multa in self._todos("multas") if condicao(multa)), None)

    def obter_multa_do_emprestimo(self, emprestimo_id):
        return self._primeira(lambda multa: multa.emprestimo_id == emprestimo_id)

    def obter_multa_por_boleto(self, banco, id_boleto):
        return self._primeira(lambda multa: (multa.banco, multa.id_boleto) == (banco, id_boleto))

    def listar_multas(self):
        return self._todos("multas")

    def registrar_boleto(self, multa_id, banco, id_boleto):
        multa = self._tabela("multas")[multa_id]
        multa.banco, multa.id_boleto = banco, id_boleto

    def registrar_quitacao(self, id_notificacao, multa_id):
        quitacoes = self._tabela("quitacoes")
        # Mesma regra das restrições UNIQUE do MySQL: uma quitação por notificação e por multa.
        if id_notificacao in quitacoes or multa_id in quitacoes.values():
            return False
        quitacoes[id_notificacao] = multa_id
        self._tabela("multas")[multa_id].quitada = True
        return True
