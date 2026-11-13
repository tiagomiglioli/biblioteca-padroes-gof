"""Rotas das páginas: requisição HTTP -> tratador -> resposta.

Nenhuma regra da biblioteca mora aqui. As rotas leem o formulário, chamam um
tratador e mostram o resultado; quem aceita ou recusa é o domínio.
"""
import uuid
from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from dominio.erros import ErroDominio

paginas = Blueprint("paginas", __name__)


@paginas.before_request
@login_required
def exigir_login():
    """Toda rota deste blueprint exige login, verificado no servidor."""


def sistema():
    return current_app.sistema


def tentar(acao):
    """Executa a ação; regra violada vira mensagem amigável em vez de página de erro."""
    try:
        mensagem = acao()
        if mensagem:
            flash(mensagem, "ok")
    except ErroDominio as erro:
        flash(str(erro), "erro")


def texto_comprovante(comprovante):
    texto = f"{comprovante.mensagem} Livro {comprovante.livro_id}: {comprovante.estado}."
    if comprovante.vencimento:
        texto += f" Vencimento: {comprovante.vencimento:%d/%m/%Y}."
    return texto


def inteiro(texto):
    """Converte campo de formulário em inteiro; vazio vira None."""
    try:
        return int(texto) if texto else None
    except ValueError:
        raise ErroDominio("Identificador inválido.") from None


@paginas.route("/")
def painel():
    s = sistema()
    livros = s.acervo.listar()
    por_estado = {}
    for livro in livros:
        por_estado[livro.nome_estado] = por_estado.get(livro.nome_estado, 0) + 1
    return render_template("painel.html", total_livros=len(livros), por_estado=por_estado,
                           indicadores=s.indicadores, medicao=s.medicao,
                           multas_pendentes=sum(not multa.quitada for multa in s.multa.listar()))


# ---------------------------------------------------------------- cadastros

def tratador_de(tipo):
    return {"pessoa": sistema().pessoa, "estudante": sistema().estudante,
            "atendente": sistema().atendente, "livro": sistema().acervo}.get(tipo)


@paginas.route("/cadastros")
def cadastros():
    s = sistema()
    return render_template("cadastros.html", pessoas=s.pessoa.listar(), estudantes=s.estudante.listar(),
                           atendentes=s.atendente.listar(), livros=s.acervo.listar())


@paginas.route("/cadastros/<tipo>", methods=["POST"])
def cadastrar(tipo):
    tratador = tratador_de(tipo)
    if tratador is None:
        return render_template("erro.html", mensagem="Cadastro desconhecido."), 404
    dados = request.form
    chave = (dados.get("cpf") if tipo == "pessoa" else dados.get("id")) or ""

    def inserir():
        resultado = tratador.inserir(dados)
        return f"Registro de {tipo} " + ("já estava cadastrado." if resultado.ja_existia
                                         else "cadastrado com sucesso.")

    def atualizar():
        return f"Registro de {tipo} atualizado." if tratador.atualizar(dados) \
            else f"Registro de {tipo} não encontrado; nada foi alterado."

    def excluir():
        tratador.excluir(chave.strip())
        return f"Registro de {tipo} excluído."

    acoes = {"inserir": inserir, "atualizar": atualizar, "excluir": excluir}
    tentar(acoes.get(dados.get("acao"), inserir))
    return redirect(url_for("paginas.cadastros"))


# ------------------------------------------------------------------- acervo

@paginas.route("/acervo")
def acervo():
    s = sistema()
    consulta = request.args.get("consulta", "").strip()
    return render_template("acervo.html", livros=s.acervo.listar(), arvore=s.acervo.arvore(),
                           consulta=consulta, medicao=s.medicao,
                           metadados=s.acervo.consultar_metadados(consulta) if consulta else None)


@paginas.route("/acervo/grupo", methods=["POST"])
def criar_grupo():
    def acao():
        sistema().acervo.criar_grupo(request.form.get("nome", ""), inteiro(request.form.get("pai_id")))
        return "Grupo criado."
    tentar(acao)
    return redirect(url_for("paginas.acervo"))


@paginas.route("/acervo/mover", methods=["POST"])
def mover_livro():
    def acao():
        sistema().acervo.mover_livro(request.form.get("livro_id", ""), inteiro(request.form.get("grupo_id")))
        return "Livro colocado no grupo."
    tentar(acao)
    return redirect(url_for("paginas.acervo"))


# --------------------------------------------------------------- circulação

def data_do_formulario(texto):
    """Data de devolução informada na tela (para demonstrar atraso sem mexer no relógio)."""
    if not texto:
        return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise ErroDominio("Data inválida. Use o seletor de data.") from None


def operacoes_de_circulacao(f, autor):
    """Cada opção do formulário aponta para UM método de tratador. Sem regra de negócio aqui."""
    s = sistema()
    estudante, livro, solicitacao = f.get("estudante_id", ""), f.get("livro_id", ""), f.get("id_solicitacao")
    return {
        "reservar": lambda: s.emprestimo.solicitar_reserva(estudante, livro, autor, solicitacao),
        "consultar_reserva": lambda: s.emprestimo.consultar_reserva(estudante, livro),
        "emprestar": lambda: s.emprestimo.realizar_emprestimo(estudante, livro),
        "renovar": lambda: s.emprestimo.renovar_emprestimo(estudante, livro, autor, solicitacao),
        "devolver": lambda: s.devolucao.registrar_devolucao(livro, data_do_formulario(f.get("data_devolucao"))),
        "inspecionar_bom": lambda: s.devolucao.inspecionar(livro, True),
        "inspecionar_danificado": lambda: s.devolucao.inspecionar(livro, False),
        "enviar_reparo": lambda: s.devolucao.enviar_para_reparo(livro),
        "retornar_reparo": lambda: s.devolucao.retornar_do_reparo(livro),
        "laudo_irrecuperavel": lambda: s.devolucao.registrar_laudo_irrecuperavel(livro),
    }


@paginas.route("/circulacao", methods=["GET", "POST"])
def circulacao():
    s = sistema()
    if request.method == "POST":
        operacao = operacoes_de_circulacao(request.form, current_user.id).get(request.form.get("operacao"))
        if operacao is None:
            flash("Operação desconhecida.", "erro")
        else:
            tentar(lambda: texto_comprovante(operacao()))
        return redirect(url_for("paginas.circulacao"))
    # O id da solicitação nasce com o formulário: reenviar o mesmo formulário
    # (duplo clique, F5) repete o mesmo id e o Command não executa de novo.
    return render_template("circulacao.html", livros=s.acervo.listar(), estudantes=s.estudante.listar(),
                           id_solicitacao=str(uuid.uuid4()), hoje=date.today().isoformat())


# ------------------------------------------------------------------- multas

@paginas.route("/multas")
def multas():
    s = sistema()
    return render_template("multas.html", multas=s.multa.listar(), vigente=s.multa.politica_vigente(),
                           politicas=s.multa.politicas_disponiveis())


@paginas.route("/multas/politica", methods=["POST"])
def definir_politica():
    def acao():
        sistema().multa.definir_politica(request.form.get("politica", ""))
        return "Política de multa alterada. Vale para as próximas multas."
    tentar(acao)
    return redirect(url_for("paginas.multas"))


@paginas.route("/multas/<int:multa_id>/boleto", methods=["POST"])
def segunda_via(multa_id):
    def acao():
        multa = sistema().devolucao.emitir_boleto_de_multa(multa_id)
        return f"Boleto {multa.id_boleto} (banco {multa.banco}) no valor de R$ {multa.valor}."
    tentar(acao)
    return redirect(url_for("paginas.multas"))


@paginas.route("/multas/<int:multa_id>/pagar", methods=["POST"])
def simular_pagamento(multa_id):
    def acao():
        if sistema().multa.simular_pagamento(multa_id):
            return "Pagamento registrado: multa quitada."
        return "Notificação ignorada: a multa já estava quitada."
    tentar(acao)
    return redirect(url_for("paginas.multas"))
