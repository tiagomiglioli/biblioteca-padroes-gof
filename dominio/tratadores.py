"""Tratadores do Trabalho 02: os únicos pontos de entrada que a interface chama.

Cada tratador só DELEGA: aos cadastros (Template Method), ao executor de
comandos (Command), à fachada (Facade) ou ao serviço de multas. Nenhum tratador
testa o estado do livro; quem decide é o State.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

from dominio.acervo_composite import ItemLivro, montar_arvore, mover
from dominio.bancos_adapter import criar_cobranca
from dominio.cadastros_template import (CadastroAtendente, CadastroEstudante, CadastroLivro,
                                         CadastroPessoa, campo, campo_cpf, exigir)
from dominio.circulacao_command import ComandoRenovacao, ComandoReserva, ExecutorComandos
from dominio.circulacao_facade import CirculacaoFacade
from dominio.consulta_decorator import ConsultaBase, ConsultaComCache, ConsultaComMedicao
from dominio.devolucao_observer import (OuvinteEmail, OuvinteIndicadores, OuvinteInspecao,
                                         OuvinteMulta, PublicadorDevolucao, ServicoEmail)
from dominio.entidades import Usuario
from dominio.erros import ErroDominio
from dominio.multas_strategy import POLITICAS, ServicoMulta, politica_por_nome


class iCadastro(ABC):
    """Operações de 'manter' comuns às interfaces iLivro, iPessoa, iEstudante e iAtendente."""

    @abstractmethod
    def inserir(self, dados): ...

    @abstractmethod
    def consultar(self, chave): ...

    @abstractmethod
    def atualizar(self, dados): ...

    @abstractmethod
    def excluir(self, chave): ...


class iLivro(iCadastro):
    """Interface de manter Livro (realizada por TratadorDeAcervo)."""


class iPessoa(iCadastro):
    """Interface de manter Pessoa (realizada por TratadorDePessoa)."""


class iEstudante(iCadastro):
    """Interface de manter Estudante (realizada por TratadorDeEstudante)."""


class iAtendente(iCadastro):
    """Interface de manter Atendente (realizada por TratadorDeAtendente)."""


class _TratadorBase:
    def __init__(self, fabrica):
        self._fabrica = fabrica

    def _no_relacionamento(self, operacao):
        """Executa `operacao(relacionamento)` dentro de uma unidade de trabalho."""
        with self._fabrica.criar_unidade_trabalho() as uow:
            return operacao(self._fabrica.criar_relacionamento(uow))

    def _no_acervo(self, operacao):
        with self._fabrica.criar_unidade_trabalho() as uow:
            return operacao(self._fabrica.criar_acervo(uow))


class TratadorDePessoa(_TratadorBase, iPessoa):
    """Manter Pessoa (regras 2.1 a 2.4), delegando ao Relacionamento."""

    def inserir(self, dados):
        return CadastroPessoa(self._fabrica).incluir(dados)

    def consultar(self, cpf):
        return self._no_relacionamento(lambda rel: rel.obter_pessoa(cpf))

    def atualizar(self, dados):
        """Atualiza nome, sobrenome e e-mail. Devolve False se a pessoa não está cadastrada."""
        cadastro = CadastroPessoa(self._fabrica)
        cadastro._validar(dados)

        def operacao(rel):
            if rel.obter_pessoa(campo_cpf(dados)) is None:
                return False
            rel.atualizar_pessoa(cadastro._criar(dados))
            return True
        return self._no_relacionamento(operacao)

    def excluir(self, cpf):
        return self._no_relacionamento(lambda rel: rel.excluir_pessoa(cpf))

    def listar(self):
        return self._no_relacionamento(lambda rel: rel.listar_pessoas())


class TratadorDeEstudante(_TratadorBase, iEstudante):
    """Manter Estudante (regras 3.1 a 3.4), delegando ao Relacionamento."""

    def inserir(self, dados):
        return CadastroEstudante(self._fabrica).incluir(dados)

    def consultar(self, estudante_id):
        return self._no_relacionamento(lambda rel: rel.obter_estudante(estudante_id))

    def atualizar(self, dados):
        """Troca a pessoa vinculada. Devolve False se o estudante não está cadastrado."""
        cadastro = CadastroEstudante(self._fabrica)

        def operacao(rel):
            if rel.obter_estudante(campo(dados, "id")) is None:
                return False
            cadastro._verificar_pre_requisitos(rel, dados)
            rel.atualizar_estudante(cadastro._criar(dados))
            return True
        return self._no_relacionamento(operacao)

    def excluir(self, estudante_id):
        return self._no_relacionamento(lambda rel: rel.excluir_estudante(estudante_id))

    def listar(self):
        return self._no_relacionamento(lambda rel: rel.listar_estudantes())


class TratadorDeAtendente(_TratadorBase, iAtendente):
    """Manter Atendente (regras 4.1 a 4.4), delegando ao Relacionamento."""

    def inserir(self, dados):
        return CadastroAtendente(self._fabrica).incluir(dados)

    def consultar(self, atendente_id):
        return self._no_relacionamento(lambda rel: rel.obter_atendente(atendente_id))

    def atualizar(self, dados):
        """Troca a pessoa vinculada. Devolve False se o atendente não está cadastrado."""
        cadastro = CadastroAtendente(self._fabrica)

        def operacao(rel):
            if rel.obter_atendente(campo(dados, "id")) is None:
                return False
            cadastro._verificar_pre_requisitos(rel, dados)
            rel.atualizar_atendente(cadastro._criar(dados))
            return True
        return self._no_relacionamento(operacao)

    def excluir(self, atendente_id):
        return self._no_relacionamento(lambda rel: rel.excluir_atendente(atendente_id))

    def listar(self):
        return self._no_relacionamento(lambda rel: rel.listar_atendentes())


class TratadorDeAcervo(_TratadorBase, iLivro):
    """Manter Livro (regras 1.1 a 1.4), delegando ao Acervo; consulta e organização do acervo."""

    def __init__(self, fabrica, consulta):
        super().__init__(fabrica)
        self._consulta = consulta          # cadeia de decoradores montada na inicialização (R09)

    def inserir(self, dados):
        return CadastroLivro(self._fabrica).incluir(dados)

    def consultar(self, livro_id):
        return self._no_acervo(lambda acervo: acervo.obter(livro_id))

    def atualizar(self, dados):
        """Atualiza o título. Devolve False se o livro não está cadastrado."""
        exigir(campo(dados, "titulo"), "Título é obrigatório.")

        def operacao(acervo):
            livro = acervo.obter(campo(dados, "id"), para_atualizar=True)
            if livro is None:
                return False
            livro.titulo = campo(dados, "titulo")
            acervo.atualizar(livro)
            return True
        atualizado = self._no_acervo(operacao)
        if atualizado:
            self._consulta.invalidar(campo(dados, "id"))
        return atualizado

    def excluir(self, livro_id):
        """Exclui o livro; o State só aceita excluir livro LIVRE (T11)."""
        def operacao(acervo):
            livro = acervo.obter(livro_id, para_atualizar=True)
            if livro is None:
                return False
            livro.excluir()
            acervo.excluir(livro_id)
            return True
        excluido = self._no_acervo(operacao)
        if excluido:
            self._consulta.invalidar(livro_id)
        return excluido

    def listar(self):
        return self._no_acervo(lambda acervo: acervo.listar())

    def consultar_metadados(self, livro_id):
        """Consulta só de leitura (pode vir do cache). Nunca decide reserva."""
        return self._consulta.consultar(livro_id)

    def criar_grupo(self, nome, pai_id):
        """Cria unidade (pai_id None), seção ou subseção. Devolve o id do grupo."""
        exigir(nome.strip(), "Nome do grupo é obrigatório.")
        exigir(len(nome.strip()) <= 100, "Nome do grupo aceita no máximo 100 caracteres.")

        def operacao(acervo):
            _, grupos, _ = montar_arvore(acervo.listar_grupos(), acervo.listar_itens())
            exigir(pai_id is None or pai_id in grupos, "Grupo pai não encontrado.")
            return acervo.inserir_grupo(nome.strip(), pai_id)
        return self._no_acervo(operacao)

    def mover_livro(self, livro_id, grupo_id):
        """Coloca (ou move) o livro no grupo. Só a árvore muda: Livro e Movimentacao não são tocados."""
        def operacao(acervo):
            _, grupos, itens = montar_arvore(acervo.listar_grupos(), acervo.listar_itens())
            if acervo.obter(livro_id) is None or grupo_id not in grupos:
                raise ErroDominio("Livro ou grupo não encontrado.")
            # As regras (ciclo, livro em dois grupos) são conferidas pelo Composite antes de gravar.
            if livro_id in itens:
                mover(itens[livro_id], grupos[grupo_id])
            else:
                grupos[grupo_id].adicionar(ItemLivro(livro_id))
            acervo.definir_grupo(livro_id, grupo_id)
        self._no_acervo(operacao)

    def arvore(self):
        """Raiz do Composite, para exibir a hierarquia e as contagens."""
        return self._no_acervo(lambda acervo: montar_arvore(acervo.listar_grupos(), acervo.listar_itens())[0])


class TratadorDeEmprestimo:
    """Serviços do Estudante (interface iEmprestimo): f1 a f4."""

    def __init__(self, fachada, executor):
        self._fachada = fachada
        self._executor = executor

    def solicitar_reserva(self, estudante_id, livro_id, autor, id_solicitacao=None, atendente_id=None):
        """f1 — cria a solicitação (Command) e a encaminha ao executor."""
        comando = ComandoReserva(self._fachada, estudante_id, livro_id, autor, id_solicitacao, atendente_id=atendente_id)
        return self._executor.executar(comando)

    def consultar_reserva(self, estudante_id, livro_id):
        """f2."""
        return self._fachada.consultar_reserva(estudante_id, livro_id)

    def realizar_emprestimo(self, estudante_id, livro_id, atendente_id=None):
        """f3."""
        return self._fachada.emprestar(estudante_id, livro_id, atendente_id=atendente_id)

    def renovar_emprestimo(self, estudante_id, livro_id, autor, id_solicitacao=None):
        """f4 — cria a solicitação (Command) e a encaminha ao executor."""
        comando = ComandoRenovacao(self._fachada, estudante_id, livro_id, autor, id_solicitacao)
        return self._executor.executar(comando)


class TratadorDeDevolucao:
    """Serviços do Atendente (interface iDevolucao): f5, f6, inspeção e reparo."""

    def __init__(self, fachada, servico_multa):
        self._fachada = fachada
        self._servico_multa = servico_multa

    def registrar_devolucao(self, livro_id, data_devolucao=None, atendente_id=None):
        """f5."""
        return self._fachada.devolver(livro_id, data_devolucao, atendente_id=atendente_id)

    def emitir_boleto_de_multa(self, multa_id):
        """f6 — segunda via: devolve a multa com o boleto já emitido (ou emite, se faltava)."""
        return self._servico_multa.emitir_boleto(multa_id)

    def inspecionar(self, livro_id, bom_estado):
        return self._fachada.inspecionar(livro_id, bom_estado)

    def enviar_para_reparo(self, livro_id):
        return self._fachada.enviar_para_reparo(livro_id)

    def retornar_do_reparo(self, livro_id):
        return self._fachada.retornar_do_reparo(livro_id)

    def registrar_laudo_irrecuperavel(self, livro_id):
        return self._fachada.registrar_laudo_irrecuperavel(livro_id)


class TratadorDeMulta(_TratadorBase):
    """Financeiro (interfaces iMulta e iQuitacao): multas, política vigente e quitação."""

    def __init__(self, fabrica, servico_multa, cobranca, configuracao):
        super().__init__(fabrica)
        self._servico_multa = servico_multa
        self._cobranca = cobranca
        self._configuracao = configuracao

    def listar(self):
        with self._fabrica.criar_unidade_trabalho() as uow:
            return self._fabrica.criar_financeiro(uow).listar_multas()

    def politica_vigente(self):
        return self._configuracao.politica_multa

    def politicas_disponiveis(self):
        return tuple(POLITICAS)

    def definir_politica(self, nome):
        """Configuração administrativa: vale para as PRÓXIMAS multas. ErroDominio se o nome não existe."""
        politica_por_nome(nome)
        self._configuracao.politica_multa = nome

    def registrar_quitacao(self, notificacao_externa):
        """Entrada da notificação de pagamento vinda do banco."""
        return self._servico_multa.registrar_pagamento(notificacao_externa)

    def simular_pagamento(self, multa_id):
        """Demonstração: faz o banco simulado notificar o pagamento do boleto da multa."""
        with self._fabrica.criar_unidade_trabalho() as uow:
            multa = self._fabrica.criar_financeiro(uow).obter_multa(multa_id)
        exigir(multa is not None and multa.id_boleto, "Multa sem boleto emitido.")
        return self.registrar_quitacao(self._cobranca.simular_pagamento(multa.id_boleto))


class TratadorDeAcesso(_TratadorBase):
    """Login da interface web: só o hash da senha é guardado e comparado."""

    _HASH_FALSO = generate_password_hash("senha-que-ninguem-usa")

    def criar_usuario(self, login, senha):
        exigir(login.strip() and len(senha) >= 8, "Informe o login e uma senha de pelo menos 8 caracteres.")
        exigir(len(login.strip()) <= 50, "Login aceita no máximo 50 caracteres.")
        usuario = Usuario(login.strip(), generate_password_hash(senha))
        self._no_relacionamento(lambda rel: rel.inserir_usuario(usuario))

    def autenticar(self, login, senha):
        """Devolve o Usuario se login e senha conferem; senão None (sem dizer qual dos dois errou)."""
        usuario = self.obter(login)
        # Mesmo sem usuário, um hash é conferido: o tempo de resposta não revela se o login existe.
        confere = check_password_hash(usuario.senha_hash if usuario else self._HASH_FALSO, senha)
        return usuario if usuario is not None and confere else None

    def obter(self, login):
        return self._no_relacionamento(lambda rel: rel.obter_usuario(login))


@dataclass
class Sistema:
    """Tudo já montado e ligado; a interface usa só os tratadores."""
    fachada: CirculacaoFacade
    executor: ExecutorComandos
    publicador: PublicadorDevolucao
    servico_multa: ServicoMulta
    cobranca: object
    email: ServicoEmail
    inspecao: OuvinteInspecao
    indicadores: OuvinteIndicadores
    medicao: ConsultaComMedicao
    emprestimo: TratadorDeEmprestimo
    devolucao: TratadorDeDevolucao
    acervo: TratadorDeAcervo
    pessoa: TratadorDePessoa
    estudante: TratadorDeEstudante
    atendente: TratadorDeAtendente
    multa: TratadorDeMulta
    acesso: TratadorDeAcesso


def montar_sistema(fabrica, configuracao, relogio=date.today):
    """Liga as peças uma única vez, na inicialização. `relogio` permite fixar a data nos testes."""
    email = ServicoEmail()
    cobranca = criar_cobranca(configuracao.banco_cobranca)       # banco da instalação
    servico_multa = ServicoMulta(fabrica, cobranca, configuracao, email)

    publicador = PublicadorDevolucao()
    inspecao, indicadores = OuvinteInspecao(), OuvinteIndicadores()
    # Para acrescentar uma reação à devolução, basta registrar outro ouvinte aqui.
    for ouvinte in (inspecao, OuvinteMulta(servico_multa), indicadores, OuvinteEmail(email)):
        publicador.registrar(ouvinte)

    fachada = CirculacaoFacade(fabrica, publicador, relogio)
    executor = ExecutorComandos(fabrica)
    # Cadeia de decoradores da instalação: medição por fora, para medir também
    # as consultas atendidas pelo cache. Trocar a ordem muda o que é medido.
    medicao = ConsultaComMedicao(ConsultaComCache(ConsultaBase(fabrica)))
    return Sistema(
        fachada=fachada, executor=executor, publicador=publicador, servico_multa=servico_multa,
        cobranca=cobranca, email=email, inspecao=inspecao, indicadores=indicadores, medicao=medicao,
        emprestimo=TratadorDeEmprestimo(fachada, executor),
        devolucao=TratadorDeDevolucao(fachada, servico_multa),
        acervo=TratadorDeAcervo(fabrica, medicao), pessoa=TratadorDePessoa(fabrica),
        estudante=TratadorDeEstudante(fabrica), atendente=TratadorDeAtendente(fabrica),
        multa=TratadorDeMulta(fabrica, servico_multa, cobranca, configuracao),
        acesso=TratadorDeAcesso(fabrica),
    )
