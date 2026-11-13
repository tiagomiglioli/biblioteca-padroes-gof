"""Fluxo completo pela interface web: cadastro, reserva, empréstimo, renovação, devolução atrasada e multa."""
import uuid
from datetime import timedelta
from decimal import Decimal

import pytest

from app import criar_app
from tests.apoio import ANA, BIA, HOJE, livro_no_banco
from tests.test_autenticacao import CONFIG_TESTE, SENHA


@pytest.fixture
def app(fabrica):
    app = criar_app(CONFIG_TESTE, fabrica=fabrica, relogio=lambda: HOJE)
    app.sistema.acesso.criar_usuario("admin", SENHA)
    return app


@pytest.fixture
def cliente(app):
    cliente = app.test_client()
    cliente.post("/login", data={"login": "admin", "senha": SENHA})
    return cliente


def enviar(cliente, rota, **dados):
    """POST seguido do redirecionamento; devolve o texto da página resultante."""
    resposta = cliente.post(rota, data=dados, follow_redirects=True)
    assert resposta.status_code == 200
    return resposta.get_data(as_text=True)


def cadastrar_basico(cliente):
    enviar(cliente, "/cadastros/pessoa", acao="inserir", **ANA)
    enviar(cliente, "/cadastros/pessoa", acao="inserir", **BIA)
    enviar(cliente, "/cadastros/atendente", acao="inserir", id="A1", cpf=BIA["cpf"])
    enviar(cliente, "/cadastros/estudante", acao="inserir", id="E1", cpf=ANA["cpf"])
    enviar(cliente, "/cadastros/livro", acao="inserir", id="L1", titulo="Padrões de Projeto")


def circular(cliente, operacao, **dados):
    dados.setdefault("livro_id", "L1")
    dados.setdefault("estudante_id", "E1")
    dados.setdefault("atendente_id", "A1")
    dados.setdefault("id_solicitacao", str(uuid.uuid4()))
    return enviar(cliente, "/circulacao", operacao=operacao, **dados)


def test_fluxo_completo_reserva_emprestimo_renovacao_devolucao_atrasada_e_multa(cliente, app, fabrica):
    cadastrar_basico(cliente)

    assert "Reserva registrada" in circular(cliente, "reservar")
    assert "Empréstimo efetivado" in circular(cliente, "emprestar")
    assert "Renovação 1 de 2" in circular(cliente, "renovar")
    vencimento = HOJE + timedelta(days=60)
    assert livro_no_banco(fabrica).vencimento == vencimento

    pagina = circular(cliente, "devolver", data_devolucao=(vencimento + timedelta(days=5)).isoformat())
    assert "5 dia(s) de atraso" in pagina
    assert livro_no_banco(fabrica).nome_estado == "DEVOLVIDO"

    multas = cliente.get("/multas").get_data(as_text=True)
    assert "R$ 5,00" in multas and "Pendente" in multas
    multa = app.sistema.multa.listar()[0]
    assert (multa.valor, multa.politica, multa.quitada) == (Decimal("5.00"), "original", False)

    assert "Pagamento registrado" in enviar(cliente, f"/multas/{multa.id}/pagar")
    assert "já estava quitada" in enviar(cliente, f"/multas/{multa.id}/pagar")
    assert app.sistema.multa.listar()[0].quitada is True

    assert "Inspeção registrada" in circular(cliente, "inspecionar_bom")
    assert livro_no_banco(fabrica).nome_estado == "LIVRE"


def test_regra_violada_vira_mensagem_e_nao_erro(cliente, fabrica):
    cadastrar_basico(cliente)
    circular(cliente, "reservar")

    pagina = circular(cliente, "reservar")           # livro já RESERVADO

    assert "não aceita a operação" in pagina
    assert livro_no_banco(fabrica).nome_estado == "RESERVADO"


def test_formulario_reenviado_com_a_mesma_solicitacao_renova_uma_vez_so(cliente, fabrica):
    cadastrar_basico(cliente)
    circular(cliente, "reservar")
    circular(cliente, "emprestar")
    mesma = str(uuid.uuid4())

    circular(cliente, "renovar", id_solicitacao=mesma)
    circular(cliente, "renovar", id_solicitacao=mesma)      # duplo clique / reenvio do navegador

    assert livro_no_banco(fabrica).num_renovacoes == 1


def test_cadastro_duplicado_e_pre_requisito_aparecem_como_mensagens(cliente, app):
    assert "Cadastre a pessoa" in enviar(cliente, "/cadastros/estudante", acao="inserir", id="E1", cpf=ANA["cpf"])
    assert app.sistema.estudante.listar() == ()

    assert "cadastrado com sucesso" in enviar(cliente, "/cadastros/pessoa", acao="inserir", **ANA)
    assert "já estava cadastrado" in enviar(cliente, "/cadastros/pessoa", acao="inserir", **ANA)


def test_atualizar_e_excluir_cadastros(cliente, app):
    cadastrar_basico(cliente)

    enviar(cliente, "/cadastros/livro", acao="atualizar", id="L1", titulo="Novo título")
    assert app.sistema.acervo.consultar("L1").titulo == "Novo título"

    enviar(cliente, "/cadastros/livro", acao="excluir", id="L1")
    assert app.sistema.acervo.consultar("L1") is None


def test_texto_digitado_pelo_usuario_e_escapado_no_html(cliente):
    enviar(cliente, "/cadastros/livro", acao="inserir", id="X1", titulo="<script>alert(1)</script>")
    pagina = cliente.get("/acervo").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in pagina
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in pagina


def test_acervo_organiza_em_grupos_e_consulta_metadados(cliente, app):
    cadastrar_basico(cliente)
    enviar(cliente, "/acervo/grupo", nome="Unidade Centro", pai_id="")
    unidade = app.sistema.acervo.arvore().filhos[0].id
    enviar(cliente, "/acervo/grupo", nome="Exatas", pai_id=str(unidade))
    secao = app.sistema.acervo.arvore().filhos[0].filhos[0].id

    pagina = enviar(cliente, "/acervo/mover", livro_id="L1", grupo_id=str(secao))
    assert "Unidade Centro" in pagina and "Exatas" in pagina
    assert app.sistema.acervo.arvore().contar_livros() == 1

    cliente.get("/acervo?consulta=L1")
    consulta = cliente.get("/acervo?consulta=L1").get_data(as_text=True)
    assert "Padrões de Projeto" in consulta
    assert app.sistema.medicao.total_consultas == 2


def test_troca_de_politica_pela_tela_vale_para_a_proxima_multa(cliente, app):
    cadastrar_basico(cliente)
    assert "Política de multa alterada" in enviar(cliente, "/multas/politica", politica="tolerancia")
    circular(cliente, "reservar")
    circular(cliente, "emprestar")
    circular(cliente, "devolver", data_devolucao=(HOJE + timedelta(days=35)).isoformat())

    multa = app.sistema.multa.listar()[0]
    assert (multa.valor, multa.politica) == (Decimal("3.00"), "tolerancia")


def test_data_invalida_vira_mensagem(cliente):
    cadastrar_basico(cliente)
    circular(cliente, "reservar")
    circular(cliente, "emprestar")
    assert "Data inválida" in circular(cliente, "devolver", data_devolucao="31/02/2026")
