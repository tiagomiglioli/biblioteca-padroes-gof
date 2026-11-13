# Evidências — fechamento do atendente

Data: 13/11/2026. Projeto desta etapa: `/Users/tiagomiglioli/Documents/ChatGPT/padroes-de-projeto/fechamento-atendente`.

## Suíte integrada executada

Resultado informado pelo auditor principal e conferido no JUnit `/tmp/fechamento-suite.xml`: **374 passed in 28.22s**, zero falhas, zero erros, zero skips. XML registra 28,222 s e timestamp `2026-11-13T12:15:25.807946-03:00`. O tempo não é estimado a partir da contagem.

A execução inclui as famílias memória/MySQL reais e os testes anteriores de concorrência entre quatro processos. O fechamento acrescentou 69 casos aos 305 anteriores. Não foram removidas expectativas anteriores para esconder falhas: a revisão independente conferiu os callers e alterações dos testes.

Comando executado no diretório original `/Users/tiagomiglioli/Documents/bibioteca-gof` (sem valores de credenciais):

```sh
rtk env PYTHONDONTWRITEBYTECODE=1 MYSQL_TEST_DATABASE=biblioteca_gof_fechamento_20261113 /Users/tiagomiglioli/Documents/bibioteca-gof/.venv/bin/python -B -c 'from dotenv import load_dotenv; load_dotenv("/Users/tiagomiglioli/Documents/bibioteca-gof/.env"); import pytest; raise SystemExit(pytest.main(["-q", "-ra", "--tb=short", "-p", "no:cacheprovider", "--junitxml=/tmp/fechamento-original.xml"]))'
```

Resultado final: **374 passed in 36.29s**, exit 0. XML portátil: `evidencias_fechamento/pytest-original.xml`.

| Arquivo | Aprovados | Falhas | Skips |
|---|---:|---:|---:|
| `tests/test_atendente_transacoes.py` | 32 | 0 | 0 |
| `tests/test_auditoria_boleto.py` | 4 | 0 | 0 |
| `tests/test_auditoria_cache.py` | 6 | 0 | 0 |
| `tests/test_auditoria_integridade.py` | 16 | 0 | 0 |
| `tests/test_auditoria_observer.py` | 4 | 0 | 0 |
| `tests/test_auditoria_processos.py` | 1 | 0 | 0 |
| `tests/test_autenticacao.py` | 54 | 0 | 0 |
| `tests/test_fluxo_web.py` | 18 | 0 | 0 |
| `tests/test_migracao_atendente.py` | 2 | 0 | 0 |
| `tests/test_mysql_integracao.py` | 8 | 0 | 0 |
| `tests/test_persistencia_atendente.py` | 17 | 0 | 0 |
| `tests/test_r01_state.py` | 59 | 0 | 0 |
| `tests/test_r02_strategy.py` | 21 | 0 | 0 |
| `tests/test_r03_adapter.py` | 17 | 0 | 0 |
| `tests/test_r04_facade.py` | 14 | 0 | 0 |
| `tests/test_r05_observer.py` | 16 | 0 | 0 |
| `tests/test_r06_command.py` | 14 | 0 | 0 |
| `tests/test_r07_template_method.py` | 12 | 0 | 0 |
| `tests/test_r08_abstract_factory.py` | 10 | 0 | 0 |
| `tests/test_r09_decorator.py` | 13 | 0 | 0 |
| `tests/test_r10_composite.py` | 13 | 0 | 0 |
| `tests/test_r11_singleton.py` | 5 | 0 | 0 |
| `tests/test_validacao_tamanhos.py` | 18 | 0 | 0 |

## Regressões específicas

- `tests/test_atendente_transacoes.py`: ausência/vazio/inexistente/mesma Pessoa nas três operações; responsáveis distintos; rollback do Command inválido e repetição válida; formulário e comprovante.
- `tests/test_persistencia_atendente.py`: responsáveis A2/A3/A4 efetivamente preservados, reserva inativa, exclusão recusada, CPF de papéis com histórico protegido, rollback e JSON antigo legível.
- `tests/test_migracao_atendente.py`: banco legado sem colunas, NULL preservado, FK inválida recusada, falha injetada após primeira coluna, retomada e repetição sem perder linhas.
- `tests/test_validacao_tamanhos.py`: limites dos campos no backend, sem gravação parcial; título dentro do limite aceito, atualização inválida preserva original, grupo/login validados.

## Ciclo vermelho/verde da persistência

Relato de execução do agente de persistência em `/tmp/fechamento-persistencia.md`: inicialmente 4 falhas/3 deselected em memória e 2 falhas de módulo de migração ainda ausente. Primeiro verde memória: 4 passes/3 deselected. Famílias e migração: 9 passes, depois 17 e finalmente 19 passes em 0,94 s com casos ampliados. O total integrado de 374 substitui esses resultados parciais como referência do fechamento.

Na execução parcial foi usada a base exclusiva `biblioteca_gof_fechamento_persistencia_20261113`, Python original `.venv/bin/python -B` na cópia, dotenv local e `pytest.main(['-q', '--tb=short', '-p', 'no:cacheprovider', 'tests/test_persistencia_atendente.py', 'tests/test_migracao_atendente.py'])`. O teste de migração reconstrói cenário legado removendo apenas suas colunas na base descartável; nunca deve ser apontado para produção.

## Revisão independente

`/tmp/fechamento-review.md`: especificação APROVADA, qualidade APROVADA, nenhum finding P0/P1/P2/P3. Revisão somente leitura de código/diff/plano. Conferiu validação antes da mutação, CPF e bloqueio de identidade, histórico separado, migração, JSON antigo, UI, limites backend e manutenção dos asserts anteriores. O revisor não reexecutou a suíte; a evidência de execução é do auditor principal e do JUnit.

## Navegador real — execução informada pelo auditor principal

| Passo | Resultado observado |
|---|---|
| Submeter sem atendente | Recusa |
| Selecionar atendente da mesma Pessoa/CPF do estudante | Recusa |
| Reservar com A1 | Reserva registrada |
| Emprestar com A2 | Empréstimo registrado com outro responsável |
| Renovar | Vencimento 12/01/2027 |
| Devolver em 17/01/2027 com A1 | Cinco dias de atraso; multa R$5 |
| Simular pagamento | Multa quitada |

O fluxo foi realizado no navegador real, não apenas no cliente Flask. Não houve transferência financeira externa. Captura: `evidencias_fechamento/devolucao-responsavel.png`. Consulta SQL: `evidencias_fechamento/migracao-e-ui.json`.

## Migração principal e aplicação final

A migração da base principal foi executada duas vezes, comprovando idempotência. Os dados anteriores das 11 tabelas permaneceram iguais; o catálogo passou a 14 FKs, incluindo as três dos responsáveis. Evidência: `evidencias_fechamento/migracao-e-ui.json`. O auditor principal aplicou 30 arquivos no original, executou novamente a suíte (374 aprovados em 36,29 s, zero falhas/erros/skips, exit 0), conferiu `git diff --check` sem problemas e reiniciou o servidor original em `127.0.0.1:5057`, com tela de login carregada.

O JUnit do original (`evidencias_fechamento/pytest-original.xml`; fonte `/tmp/fechamento-original.xml`) registra 374 testes, zero falhas/erros/skips e 36,296 s, timestamp `2026-11-13T12:22:31.953079-03:00`. A consulta SQL da prova de interface confirmou responsáveis A1/A2/A1, multa 5,00 quitada e uma única quitação. A inspeção final deixou o livro LIVRE. O fluxo completo de interface foi exercitado na cópia; após aplicação no original, o reinício e a tela de login foram confirmados.

## Histórico da auditoria inicial

O estado anterior teve 274 testes originais; a primeira tentativa sandbox teve 181 passes/93 skips por restrição TCP, seguida de 274 passes com MySQL autorizado. Correções de boleto, Observer, integridade, fixture e cache levaram a 305 passes em 23,67 s. A ausência do atendente foi então identificada como requisito não atendido e motivou esta etapa. Evidências antigas de navegador/reinício descrevem aquele estado; não são prova automática do novo schema ou dos responsáveis.

## Limites da comprovação

Astah excluído por instrução do usuário. Bancos financeiros e e-mail são simulados; MySQL dos testes foi real. Não há comprovação de replay durável Observer entre processos/reinícios nem compensação de efeitos bancários externos após crash. Não foram informados nesta etapa novos testes de carga prolongada, múltiplos navegadores, segurança ofensiva ampla ou certificação WCAG. Preparação oral dos integrantes e instalação limpa pelo usuário não são resultados da suíte.

Parecer operacional consolidado: **APTO — PODE ENTREGAR**.

Os quatro relatórios integrais da auditoria inicial estão preservados em `evidencias_fechamento/historico-auditoria-inicial/`. As evidências finais portáveis estão em `evidencias_fechamento/pytest-original.xml`, `casos-testados.tsv`, `resumo-testes.json`, `interface.md`, `revisao-independente.md`, `migracao-e-ui.json` e `devolucao-responsavel.png`.
