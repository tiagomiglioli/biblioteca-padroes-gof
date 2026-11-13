"""R07 — Template Method: rotina comum dos cadastros."""
import pytest

from dominio.cadastros_template import (CadastroAtendente, CadastroBase, CadastroEstudante,
                                         CadastroLivro, CadastroPessoa)
from dominio.erros import ErroDominio

ANA = {"cpf": "11122233344", "nome": "Ana", "sobrenome": "Silva", "email": "ana@exemplo.com"}


def estudantes(fabrica):
    with fabrica.criar_unidade_trabalho() as uow:
        return fabrica.criar_relacionamento(uow).listar_estudantes()


def test_r07_estudante_duplicado_retorna_o_cadastro_existente(fabrica):
    CadastroPessoa(fabrica).incluir(ANA)
    primeiro = CadastroEstudante(fabrica).incluir({"id": "E1", "cpf": ANA["cpf"]})

    segundo = CadastroEstudante(fabrica).incluir({"id": "E1", "cpf": "99999999999"})

    assert not primeiro.ja_existia
    assert segundo.ja_existia
    assert segundo.entidade == primeiro.entidade
    assert len(estudantes(fabrica)) == 1


def test_r07_estudante_com_cpf_nao_cadastrado_falha_antes_de_qualquer_gravacao(fabrica):
    with pytest.raises(ErroDominio):
        CadastroEstudante(fabrica).incluir({"id": "E1", "cpf": "00000000000"})

    assert estudantes(fabrica) == ()


def test_r07_atendente_tambem_exige_pessoa_cadastrada(fabrica):
    with pytest.raises(ErroDominio):
        CadastroAtendente(fabrica).incluir({"id": "A1", "cpf": ANA["cpf"]})

    CadastroPessoa(fabrica).incluir(ANA)
    assert CadastroAtendente(fabrica).incluir({"id": "A1", "cpf": ANA["cpf"]}).entidade.id == "A1"


def test_r07_pessoa_e_livro_duplicados_retornam_o_existente(fabrica):
    CadastroPessoa(fabrica).incluir(ANA)
    repetida = CadastroPessoa(fabrica).incluir({**ANA, "nome": "Outro"})
    assert repetida.ja_existia and repetida.entidade.nome == "Ana"

    CadastroLivro(fabrica).incluir({"id": "L1", "titulo": "Original"})
    repetido = CadastroLivro(fabrica).incluir({"id": "L1", "titulo": "Cópia"})
    assert repetido.ja_existia and repetido.entidade.titulo == "Original"
    assert repetido.entidade.nome_estado == "LIVRE"


def test_r07_dados_invalidos_nao_sao_gravados(fabrica):
    with pytest.raises(ErroDominio):
        CadastroPessoa(fabrica).incluir({**ANA, "cpf": "123"})
    with pytest.raises(ErroDominio):
        CadastroLivro(fabrica).incluir({"id": "L1", "titulo": "  "})

    with fabrica.criar_unidade_trabalho() as uow:
        assert fabrica.criar_relacionamento(uow).listar_pessoas() == ()
        assert fabrica.criar_acervo(uow).listar() == ()


def test_r07_metodo_modelo_nao_pode_ser_sobrescrito():
    with pytest.raises(TypeError):
        class CadastroTrapaceiro(CadastroBase):
            def incluir(self, dados):
                return "pulei a validação"


def test_r07_a_ordem_dos_passos_e_fixa():
    from dominio.persistencia_factory import FabricaMemoria
    passos = []

    class CadastroEspiao(CadastroBase):
        def _repositorio(self, uow):
            return None

        def _buscar_existente(self, repositorio, dados):
            passos.append("buscar existente")

        def _validar(self, dados):
            passos.append("validar")

        def _verificar_pre_requisitos(self, repositorio, dados):
            passos.append("verificar pré-requisitos")

        def _criar(self, dados):
            passos.append("criar")

        def _armazenar(self, repositorio, entidade):
            passos.append("armazenar")

        def _apresentar(self, entidade, ja_existia):
            passos.append("apresentar")

    CadastroEspiao(FabricaMemoria()).incluir({})

    assert passos == ["buscar existente", "validar", "verificar pré-requisitos",
                      "criar", "armazenar", "apresentar"]
