"""R07 — GoF Template Method: rotina comum dos cadastros."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from dominio.entidades import Atendente, Estudante, Livro, Pessoa
from dominio.erros import ErroDominio


@dataclass(frozen=True)
class ResultadoCadastro:
    """O que o cadastro apresenta: a entidade e se ela já existia antes."""
    entidade: object
    ja_existia: bool


LIMITES_CAMPOS = {"id": 20, "titulo": 200, "nome": 80, "sobrenome": 80, "email": 120}


def campo(dados, nome):
    """Texto do formulário sem espaços nas pontas ('' se ausente)."""
    valor = str(dados.get(nome, "")).strip()
    limite = LIMITES_CAMPOS.get(nome)
    if limite is not None and len(valor) > limite:
        raise ErroDominio(f"O campo {nome} aceita no máximo {limite} caracteres.")
    return valor


def campo_cpf(dados):
    """CPF só com dígitos (aceita 111.222.333-44)."""
    return "".join(caractere for caractere in campo(dados, "cpf") if caractere.isdigit())


def exigir(condicao, mensagem):
    if not condicao:
        raise ErroDominio(mensagem)


class CadastroBase(ABC):
    """GoF Template Method — AbstractClass.

    incluir() é o método-modelo: fixa a ordem dos passos. As subclasses só
    preenchem os passos; não podem trocar a ordem nem pular a validação.
    """

    def __init__(self, fabrica):
        self._fabrica = fabrica

    def __init_subclass__(cls, **argumentos):
        super().__init_subclass__(**argumentos)
        # Python não tem 'final' de verdade: esta checagem recusa, na definição da
        # classe, qualquer subclasse que tente sobrescrever o método-modelo.
        if "incluir" in cls.__dict__:
            raise TypeError("incluir() é o método-modelo e não pode ser sobrescrito.")

    def incluir(self, dados):
        """Método-modelo. Devolve ResultadoCadastro; lança ErroDominio se algo for inválido."""
        # Uma transação para a rotina toda: se validar ou o pré-requisito falhar,
        # o erro acontece ANTES de armazenar e nada fica gravado pela metade.
        with self._fabrica.criar_unidade_trabalho() as uow:
            repositorio = self._repositorio(uow)
            existente = self._buscar_existente(repositorio, dados)          # 1
            if existente is not None:
                return self._apresentar(existente, True)
            self._validar(dados)                                            # 2
            self._verificar_pre_requisitos(repositorio, dados)              # 3 (gancho)
            entidade = self._criar(dados)                                   # 4
            self._armazenar(repositorio, entidade)                          # 5
            return self._apresentar(entidade, False)                        # 6

    @abstractmethod
    def _repositorio(self, uow):
        """Ponto de acesso usado pelo cadastro (Relacionamento ou Acervo)."""

    @abstractmethod
    def _buscar_existente(self, repositorio, dados): ...

    @abstractmethod
    def _validar(self, dados): ...

    def _verificar_pre_requisitos(self, repositorio, dados):
        """Gancho: por padrão não há pré-requisito. Estudante e Atendente sobrescrevem."""

    @abstractmethod
    def _criar(self, dados): ...

    @abstractmethod
    def _armazenar(self, repositorio, entidade): ...

    def _apresentar(self, entidade, ja_existia):
        """Gancho com comportamento padrão: devolve a entidade e se já existia."""
        return ResultadoCadastro(entidade, ja_existia)


class CadastroPessoa(CadastroBase):
    """GoF Template Method — ConcreteClass: cadastro de Pessoa (regra 2.1)."""

    def _repositorio(self, uow):
        return self._fabrica.criar_relacionamento(uow)

    def _buscar_existente(self, relacionamento, dados):
        return relacionamento.obter_pessoa(campo_cpf(dados))

    def _validar(self, dados):
        exigir(len(campo_cpf(dados)) == 11, "CPF deve ter 11 dígitos.")
        exigir(campo(dados, "nome") and campo(dados, "sobrenome"), "Nome e sobrenome são obrigatórios.")
        exigir("@" in campo(dados, "email"), "E-mail inválido.")

    def _criar(self, dados):
        return Pessoa(campo_cpf(dados), campo(dados, "nome"), campo(dados, "sobrenome"), campo(dados, "email"))

    def _armazenar(self, relacionamento, pessoa):
        relacionamento.inserir_pessoa(pessoa)


class _CadastroPapel(CadastroBase):
    """Passos comuns a Estudante e Atendente: ambos são papéis de uma Pessoa."""

    def _repositorio(self, uow):
        return self._fabrica.criar_relacionamento(uow)

    def _validar(self, dados):
        exigir(campo(dados, "id"), "Identificador é obrigatório.")

    def _verificar_pre_requisitos(self, relacionamento, dados):
        # Regras 3.1 e 4.1: o papel só existe vinculado a uma Pessoa já cadastrada.
        exigir(relacionamento.obter_pessoa(campo_cpf(dados)) is not None,
               "Cadastre a pessoa (CPF) antes de cadastrar o papel.")


class CadastroEstudante(_CadastroPapel):
    """GoF Template Method — ConcreteClass: cadastro de Estudante (regra 3.1)."""

    def _buscar_existente(self, relacionamento, dados):
        return relacionamento.obter_estudante(campo(dados, "id"))

    def _criar(self, dados):
        return Estudante(campo(dados, "id"), campo_cpf(dados))

    def _armazenar(self, relacionamento, estudante):
        relacionamento.inserir_estudante(estudante)


class CadastroAtendente(_CadastroPapel):
    """GoF Template Method — ConcreteClass: cadastro de Atendente (regra 4.1)."""

    def _buscar_existente(self, relacionamento, dados):
        return relacionamento.obter_atendente(campo(dados, "id"))

    def _criar(self, dados):
        return Atendente(campo(dados, "id"), campo_cpf(dados))

    def _armazenar(self, relacionamento, atendente):
        relacionamento.inserir_atendente(atendente)


class CadastroLivro(CadastroBase):
    """GoF Template Method — ConcreteClass: cadastro de Livro (regra 1.1); nasce LIVRE."""

    def _repositorio(self, uow):
        return self._fabrica.criar_acervo(uow)

    def _buscar_existente(self, acervo, dados):
        return acervo.obter(campo(dados, "id"))

    def _validar(self, dados):
        exigir(campo(dados, "id") and campo(dados, "titulo"), "Identificador e título são obrigatórios.")

    def _criar(self, dados):
        return Livro(campo(dados, "id"), campo(dados, "titulo"))

    def _armazenar(self, acervo, livro):
        acervo.inserir(livro)
