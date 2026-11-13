"""Família MYSQL dos repositórios (perfil de produção).

Todo SQL é parametrizado (%s): nenhum dado do usuário é concatenado no comando.
Nenhum repositório faz commit: quem confirma ou desfaz é a unidade de trabalho.
"""
from mysql.connector import errorcode
from mysql.connector.errors import IntegrityError

from dominio.entidades import Atendente, Emprestimo, Estudante, Livro, Multa, Pessoa, Reserva, Usuario
from dominio.erros import ErroDominio
from dominio.estados import estado_por_nome
from dominio.pontos_acesso import Acervo, Financeiro, Movimentacao, Relacionamento
from persistencia.unidade_trabalho import UnidadeTrabalhoMySQL

VINCULOS = (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_NO_REFERENCED_ROW_2)


class _RepositorioMySQL:
    def __init__(self, uow):
        # Impede misturar famílias: repositório MySQL só aceita unidade MySQL.
        if not isinstance(uow, UnidadeTrabalhoMySQL):
            raise TypeError("Repositório MySQL exige UnidadeTrabalhoMySQL.")
        # Conexão da unidade de trabalho: a mesma para todos os repositórios da operação.
        self.conexao = uow.conexao

    def _executar(self, sql, parametros=()):
        """Executa e devolve (linhas, id gerado). Chave estrangeira violada vira erro de domínio."""
        cursor = self.conexao.cursor()
        try:
            cursor.execute(sql, parametros)
            linhas = cursor.fetchall() if cursor.with_rows else []
            return linhas, cursor.lastrowid
        except IntegrityError as erro:
            if erro.errno in VINCULOS:
                raise ErroDominio("Operação recusada: o registro tem vínculos com outros cadastros.") from None
            raise
        finally:
            cursor.close()

    def _linhas(self, sql, parametros=()):
        return self._executar(sql, parametros)[0]

    def _linha(self, sql, parametros=()):
        linhas = self._linhas(sql, parametros)
        return linhas[0] if linhas else None

    def _inserir_unico(self, sql, parametros):
        """INSERT que devolve False quando a chave única já existe (base da idempotência)."""
        try:
            self._executar(sql, parametros)
            return True
        except IntegrityError as erro:
            if erro.errno == errorcode.ER_DUP_ENTRY:
                return False
            raise


def _livro(linha):
    # O banco guarda só o nome do estado; aqui o objeto de estado é reconstituído (R01).
    return Livro(linha[0], linha[1], estado_por_nome(linha[2]), linha[3], linha[4]) if linha else None


def _multa(linha):
    if linha is None:
        return None
    return Multa(linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], bool(linha[6]), linha[7], linha[8])


COLUNAS_LIVRO = "id, titulo, estado, num_renovacoes, vencimento"
COLUNAS_MULTA = "id, emprestimo_id, estudante_id, dias_atraso, valor, politica, quitada, banco, id_boleto"


class AcervoMySQL(_RepositorioMySQL, Acervo):
    """GoF Abstract Factory — ProdutoConcreto (MySQL): repositório de Livro."""

    def inserir(self, livro):
        self._executar(f"INSERT INTO livro ({COLUNAS_LIVRO}) VALUES (%s, %s, %s, %s, %s)",
                       (livro.id, livro.titulo, livro.nome_estado, livro.num_renovacoes, livro.vencimento))

    def obter(self, livro_id, para_atualizar=False):
        # FOR UPDATE bloqueia a linha: duas operações simultâneas no mesmo livro entram em fila.
        trava = " FOR UPDATE" if para_atualizar else ""
        return _livro(self._linha(f"SELECT {COLUNAS_LIVRO} FROM livro WHERE id = %s{trava}", (livro_id,)))

    def atualizar(self, livro):
        self._executar("UPDATE livro SET titulo = %s, estado = %s, num_renovacoes = %s, vencimento = %s"
                       " WHERE id = %s",
                       (livro.titulo, livro.nome_estado, livro.num_renovacoes, livro.vencimento, livro.id))

    def excluir(self, livro_id):
        self._executar("DELETE FROM livro WHERE id = %s", (livro_id,))

    def listar(self):
        return tuple(_livro(linha) for linha in self._linhas(f"SELECT {COLUNAS_LIVRO} FROM livro ORDER BY id"))

    def inserir_grupo(self, nome, pai_id):
        return self._executar("INSERT INTO grupo_acervo (nome, pai_id) VALUES (%s, %s)", (nome, pai_id))[1]

    def listar_grupos(self):
        return tuple(self._linhas("SELECT id, nome, pai_id FROM grupo_acervo ORDER BY id"))

    def listar_itens(self):
        return tuple(self._linhas("SELECT id, grupo_id FROM livro WHERE grupo_id IS NOT NULL ORDER BY id"))

    def definir_grupo(self, livro_id, grupo_id):
        self._executar("UPDATE livro SET grupo_id = %s WHERE id = %s", (grupo_id, livro_id))


class MovimentacaoMySQL(_RepositorioMySQL, Movimentacao):
    """GoF Abstract Factory — ProdutoConcreto (MySQL): repositório de Movimentacao."""

    def inserir_reserva(self, livro_id, estudante_id, data):
        novo_id = self._executar("INSERT INTO reserva (livro_id, estudante_id, data) VALUES (%s, %s, %s)",
                                 (livro_id, estudante_id, data))[1]
        return Reserva(novo_id, livro_id, estudante_id, data)

    def consultar_reserva(self, livro_id, estudante_id):
        linha = self._linha("SELECT id, livro_id, estudante_id, data FROM reserva"
                            " WHERE livro_id = %s AND estudante_id = %s AND ativa = 1",
                            (livro_id, estudante_id))
        return Reserva(*linha) if linha else None

    def remover_reserva(self, reserva_id):
        self._executar("UPDATE reserva SET ativa = 0 WHERE id = %s", (reserva_id,))

    def inserir_emprestimo(self, livro_id, estudante_id, data):
        novo_id = self._executar("INSERT INTO emprestimo (livro_id, estudante_id, data_emprestimo)"
                                 " VALUES (%s, %s, %s)", (livro_id, estudante_id, data))[1]
        return Emprestimo(novo_id, livro_id, estudante_id, data)

    def consultar_emprestimo(self, livro_id):
        linha = self._linha("SELECT id, livro_id, estudante_id, data_emprestimo, data_devolucao"
                            " FROM emprestimo WHERE livro_id = %s AND data_devolucao IS NULL", (livro_id,))
        return Emprestimo(*linha) if linha else None

    def registrar_devolucao(self, emprestimo_id, data):
        self._executar("UPDATE emprestimo SET data_devolucao = %s WHERE id = %s", (data, emprestimo_id))

    def registrar_comando(self, comando_id, tipo, autor, criado_em):
        # A PRIMARY KEY decide: se outra transação já gravou este id (mesmo ao mesmo tempo),
        # o INSERT espera ela terminar e então falha por duplicidade.
        return self._inserir_unico("INSERT INTO comando_executado (id, tipo, autor, criado_em)"
                                   " VALUES (%s, %s, %s, %s)", (comando_id, tipo, autor, criado_em))

    def gravar_resultado_comando(self, comando_id, resultado):
        self._executar("UPDATE comando_executado SET resultado = %s WHERE id = %s", (resultado, comando_id))

    def resultado_comando(self, comando_id):
        linha = self._linha("SELECT resultado FROM comando_executado WHERE id = %s", (comando_id,))
        return linha[0] if linha else None


class RelacionamentoMySQL(_RepositorioMySQL, Relacionamento):
    """GoF Abstract Factory — ProdutoConcreto (MySQL): repositório de Relacionamento."""

    def inserir_pessoa(self, pessoa):
        self._executar("INSERT INTO pessoa (cpf, nome, sobrenome, email) VALUES (%s, %s, %s, %s)",
                       (pessoa.cpf, pessoa.nome, pessoa.sobrenome, pessoa.email))

    def obter_pessoa(self, cpf):
        linha = self._linha("SELECT cpf, nome, sobrenome, email FROM pessoa WHERE cpf = %s", (cpf,))
        return Pessoa(*linha) if linha else None

    def atualizar_pessoa(self, pessoa):
        self._executar("UPDATE pessoa SET nome = %s, sobrenome = %s, email = %s WHERE cpf = %s",
                       (pessoa.nome, pessoa.sobrenome, pessoa.email, pessoa.cpf))

    def excluir_pessoa(self, cpf):
        self._executar("DELETE FROM pessoa WHERE cpf = %s", (cpf,))

    def listar_pessoas(self):
        return tuple(Pessoa(*linha) for linha in
                     self._linhas("SELECT cpf, nome, sobrenome, email FROM pessoa ORDER BY cpf"))

    def inserir_estudante(self, estudante):
        self._executar("INSERT INTO estudante (id, cpf) VALUES (%s, %s)", (estudante.id, estudante.cpf))

    def obter_estudante(self, estudante_id):
        linha = self._linha("SELECT id, cpf FROM estudante WHERE id = %s", (estudante_id,))
        return Estudante(*linha) if linha else None

    def atualizar_estudante(self, estudante):
        self._executar("UPDATE estudante SET cpf = %s WHERE id = %s", (estudante.cpf, estudante.id))

    def excluir_estudante(self, estudante_id):
        self._executar("DELETE FROM estudante WHERE id = %s", (estudante_id,))

    def listar_estudantes(self):
        return tuple(Estudante(*linha) for linha in self._linhas("SELECT id, cpf FROM estudante ORDER BY id"))

    def inserir_atendente(self, atendente):
        self._executar("INSERT INTO atendente (id, cpf) VALUES (%s, %s)", (atendente.id, atendente.cpf))

    def obter_atendente(self, atendente_id):
        linha = self._linha("SELECT id, cpf FROM atendente WHERE id = %s", (atendente_id,))
        return Atendente(*linha) if linha else None

    def atualizar_atendente(self, atendente):
        self._executar("UPDATE atendente SET cpf = %s WHERE id = %s", (atendente.cpf, atendente.id))

    def excluir_atendente(self, atendente_id):
        self._executar("DELETE FROM atendente WHERE id = %s", (atendente_id,))

    def listar_atendentes(self):
        return tuple(Atendente(*linha) for linha in self._linhas("SELECT id, cpf FROM atendente ORDER BY id"))

    def inserir_usuario(self, usuario):
        self._executar("INSERT INTO usuario (login, senha_hash) VALUES (%s, %s)"
                       " ON DUPLICATE KEY UPDATE senha_hash = VALUES(senha_hash)",
                       (usuario.login, usuario.senha_hash))

    def obter_usuario(self, login):
        linha = self._linha("SELECT login, senha_hash FROM usuario WHERE login = %s", (login,))
        return Usuario(*linha) if linha else None


class FinanceiroMySQL(_RepositorioMySQL, Financeiro):
    """GoF Abstract Factory — ProdutoConcreto (MySQL): multas, boletos e quitações."""

    def inserir_multa(self, emprestimo_id, estudante_id, dias_atraso, valor, politica):
        novo_id = self._executar("INSERT INTO multa (emprestimo_id, estudante_id, dias_atraso, valor, politica)"
                                 " VALUES (%s, %s, %s, %s, %s)",
                                 (emprestimo_id, estudante_id, dias_atraso, valor, politica))[1]
        return Multa(novo_id, emprestimo_id, estudante_id, dias_atraso, valor, politica)

    def _buscar(self, condicao, parametros):
        return _multa(self._linha(f"SELECT {COLUNAS_MULTA} FROM multa WHERE {condicao}", parametros))

    def obter_multa(self, multa_id):
        return self._buscar("id = %s", (multa_id,))

    def obter_multa_do_emprestimo(self, emprestimo_id):
        return self._buscar("emprestimo_id = %s", (emprestimo_id,))

    def obter_multa_por_boleto(self, banco, id_boleto):
        return self._buscar("banco = %s AND id_boleto = %s", (banco, id_boleto))

    def listar_multas(self):
        return tuple(_multa(linha) for linha in self._linhas(f"SELECT {COLUNAS_MULTA} FROM multa ORDER BY id"))

    def registrar_boleto(self, multa_id, banco, id_boleto):
        self._executar("UPDATE multa SET banco = %s, id_boleto = %s WHERE id = %s", (banco, id_boleto, multa_id))

    def registrar_quitacao(self, id_notificacao, multa_id):
        # As restrições PRIMARY KEY/UNIQUE da tabela quitacao recusam a repetição,
        # mesmo que duas notificações cheguem ao mesmo tempo.
        if not self._inserir_unico("INSERT INTO quitacao (id_notificacao, multa_id) VALUES (%s, %s)",
                                   (id_notificacao, multa_id)):
            return False
        self._executar("UPDATE multa SET quitada = 1 WHERE id = %s", (multa_id,))
        return True
