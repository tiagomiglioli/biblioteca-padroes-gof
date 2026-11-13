# Roteiro da demonstração (5 minutos)

Antes de entrar na sala: MySQL ligado, `.env` preenchido e banco migrado. Para base existente, parar a versão antiga, executar `flask --app app migrar-db` uma vez por vez e só então iniciar esta versão. Para instalação nova, uma vez só:

```bash
flask --app app init-db && flask --app app seed-demo && flask --app app criar-usuario admin
```

Os dados de demonstração são: estudantes `E1` e `E2`, atendente `A1`, livros `L1` a `L5`,
já organizados em Unidade Centro › Exatas › Computação e Humanas. Confira os dados efetivamente carregados e que A1 representa Pessoa diferente de E1. Se o ensaio anterior usou L1, selecione outro livro LIVRE ou prepare conscientemente os dados; seed não deve ser tratado como reset.

| Tempo | O que fazer | O que deve aparecer |
|---|---|---|
| 0:00–1:00 | Terminal: `python -m pytest -q` | todos os testes aprovados, nenhum pulado |
| 1:00–1:20 | `flask --app app run`, abrir `http://127.0.0.1:5000`, fazer login | Painel com 5 livros no acervo |
| 1:20–1:50 | **Circulação** → Reservar, livro `L1`, estudante `E1`, atendente `A1` → Executar | "Reserva registrada. Livro L1: RESERVADO." |
| 1:50–2:10 | Efetivar empréstimo, `L1`, `E1`, atendente `A1` | "Empréstimo efetivado… EMPRESTADO. Vencimento: (hoje + 30 dias)" |
| 2:10–2:40 | Renovar, `L1`, `E1` — três vezes | 1ª e 2ª: "Renovação 1 de 2", "2 de 2". 3ª: "Limite de duas renovações atingido." e o vencimento não muda |
| 2:40–3:10 | Registrar devolução, `L1`, atendente `A1`, **Data da devolução = vencimento + 5 dias** | "Devolução registrada com 5 dia(s) de atraso. Livro L1: DEVOLVIDO." |
| 3:10–3:40 | **Multas** | multa de R$ 5,00, política `original`, boleto do banco A, "Pendente" |
| 3:40–4:00 | "Simular pagamento no banco" duas vezes | 1ª: "multa quitada". 2ª: "a multa já estava quitada" |
| 4:00–4:20 | **Circulação** → Reservar `L1`, `E1`, `A1` (ainda DEVOLVIDO) | recusa: "Livro DEVOLVIDO não aceita a operação 'reservar'." Depois "Inspeção: bom estado" → LIVRE |
| 4:20–5:00 | **Acervo**: consultar `L1` duas vezes; mostrar a árvore e as contagens | metadados do livro; contador de consultas medidas sobe; "Unidade Centro 5 livro(s)" |

## Se o professor pedir uma alteração ao vivo

**Nova política de multa** (Strategy) — em `dominio/multas_strategy.py`:

```python
class MultaEmDobro(PoliticaMulta):
    """GoF Strategy — EstrategiaConcreta: R$ 2,00 por dia de atraso."""

    nome = "dobro"

    def calcular(self, dias_atraso):
        return (2 * VALOR_POR_DIA * dias_atraso).quantize(CENTAVO)
```

e acrescentar `MultaEmDobro()` na tupla de `POLITICAS`. `ServicoMulta` não muda; a opção
aparece sozinha na tela Multas.

**Novo ouvinte da devolução** (Observer) — em `dominio/devolucao_observer.py`:

```python
class OuvinteAuditoria(OuvinteDevolucao):
    """GoF Observer — ConcreteObserver: registra cada devolução no log."""

    def notificar(self, evento):
        registro.info("Auditoria: livro %s devolvido por %s", evento.livro_id, evento.estudante_id)
```

e registrar em `montar_sistema` (`dominio/tratadores.py`), na tupla do `for ouvinte in (...)`.
Nem a fachada nem o tratador de devolução mudam.

## Plano B

Se o MySQL da sala falhar, os testes continuam rodando (as variantes MySQL aparecem como
`skipped`) e as regras podem ser mostradas pelos testes em memória. A interface web precisa do MySQL.

## Conferência dos responsáveis

A tela mostra o atendente no comprovante. A reserva encerrada mantém seu responsável; escolher outro atendente no empréstimo ou na devolução não sobrescreve o anterior. Renovação não solicita um novo responsável. Antes do ensaio cronometrado, exercitar uma seleção ausente/inexistente e um atendente ligado ao mesmo CPF do estudante: o servidor deve recusar sem alterar livro ou movimentação. Não confundir login do operador com atendente selecionado.

Total da validação integrada: **374**; conferir as evidências finais e o parecer no relatório principal. Este roteiro descreve resultados esperados e não é registro de uma apresentação já realizada.
