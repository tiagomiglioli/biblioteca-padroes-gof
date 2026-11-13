# Alterações — fechamento do atendente

Data: 13/11/2026. Alterações desenvolvidas e revisadas na cópia `/Users/tiagomiglioli/Documents/ChatGPT/padroes-de-projeto/fechamento-atendente`. A auditoria inicial e seus reparos permanecem como histórico. Esta etapa recebeu autorização posterior para corrigir o vínculo transacional do atendente de forma coordenada; não presumiu dispensa da regra.

## Mudanças desta etapa

| Arquivo/camada | Alteração e motivo | Risco/limite | Verificação |
|---|---|---|---|
| `dominio/entidades.py` | Responsáveis de Reserva/Emprestimo/devolução separados; ativa na reserva; Comprovante com campo opcional | JSON antigo permanece legível; histórico desconhecido não ganha responsável inventado | Persistência e compatibilidade JSON |
| `dominio/pontos_acesso.py` | Contratos de gravação com atendente e leitura de papéis bloqueável | Callers precisam encaminhar o responsável; revisão conferiu propagação | Suíte e revisão independente |
| `persistencia/memoria.py` | Conserva reserva inativa; grava responsáveis; recusa exclusão/revínculo de papéis usados | Memória respeita integridade do histórico como família relacional | 17 casos de persistência nas famílias |
| `persistencia/mysql.py` | Leitura/gravação responsáveis; FOR UPDATE dos papéis e proteção do CPF com leitura atual | Operações concorrentes sobre identidade são serializadas | Persistência/rollback e revisão |
| `sql/schema.sql` | Três colunas nullable e três FKs para responsáveis | Nullable serve ao legado; novas operações são protegidas pelo domínio | Migração/integração MySQL |
| `persistencia/migracoes.py` | Expansão aditiva pelo catálogo, idempotente e retomável | DDL com commit implícito; não executar migradores em paralelo | Dois casos de migração com repetição/falha parcial |
| `app.py` | `init-db` aplica migração; novo `migrar-db` para base existente | Parar código anterior, migrar e iniciar a nova versão | Testes e procedimento documentado |
| `dominio/circulacao_facade.py` | Valida atendente cadastrado de Pessoa distinta no mesmo escopo transacional | Sem default A1 e sem vínculo automático de login | 32 casos de domínio/web e fluxo navegador |
| `dominio/circulacao_command.py` | Reserva encaminha atendente; autor continua login | Idempotência devolve comprovante histórico, não reescreve responsável | Rollback/repetição e testes existentes |
| `dominio/tratadores.py`, `web/rotas.py`, `templates/circulacao.html` | Propagam seleção explícita e exibem responsável | Não introduz RBAC; operador declara responsável cadastrado | Navegador e testes web |
| `dominio/cadastros_template.py`, `dominio/tratadores.py` | Limites backend alinhados a colunas, inclusive grupo/login | Validação de tamanho não prova identidade documental | 18 casos de limites |
| Testes/fixtures/callers | Atendente explícito e Pessoa distinta; quatro arquivos novos de regressão | Não relaxar asserts anteriores; revisão confirmou preservação | Suíte integrada 374 passes |
| README, registro, guias, perguntas, roteiro, rastreabilidade e relatórios | Descrevem fluxo/migração atual e preservam contexto histórico | Histórico não é confundido com o estado final | Revisão documental e evidências finais |

## Resultados

**374 aprovados em 28,22 s**, zero falhas, zero erros e zero skips. São 69 casos adicionais sobre 305: 32 participantes/transações + 17 persistência + 2 migração + 18 tamanhos. JUnit `/tmp/fechamento-suite.xml` conferido; revisão independente `/tmp/fechamento-review.md` aprovada sem findings. Houve prova de navegador real com recusas, A1/A2/A1, multa R$5 e quitação simulada.

A migração da base principal foi executada duas vezes, comprovando idempotência. Os dados anteriores das 11 tabelas permaneceram iguais; o catálogo passou a 14 FKs, incluindo as três dos responsáveis. Evidência: `evidencias_fechamento/migracao-e-ui.json`. O auditor principal aplicou 30 arquivos no original, executou novamente a suíte (374 aprovados em 36,29 s, zero falhas/erros/skips, exit 0), conferiu `git diff --check` sem problemas e reiniciou o servidor original em `127.0.0.1:5057`, com login funcional.

Parecer: **APTO — PODE ENTREGAR** no escopo acadêmico auditado, com Astah excluído, sem certificar defesa humana ou produção distribuída.

## Preservação e recuo

Migração não apaga, não faz backfill inventado e conserva NULL de legado. Após falha parcial, corrigir causa e executar novamente serialmente. Recuo operacional pode voltar ao código anterior mantendo colunas/dados; não fazer DROP. Versão antiga poderá escrever NULL, portanto não mantê-la concorrendo com a nova durante a transição.

## Histórico da auditoria inicial

Antes deste fechamento foram reparados: emissão concorrente de boleto na mesma UoW, exclusões órfãs em memória, proteção da base de testes, propagação de erros SQL, deduplicação local de Observer e invalidação local de cache após commit. A suíte cresceu de 274 para 305. Naquele momento não havia migração nem atendente transacional implementado e o parecer era NÃO APTO; isso motivou a autorização posterior e não descreve o estado atual.

## Limites preservados

Não foram adicionados dependências, banco financeiro real, SMTP, fila durável ou RBAC novo. A transação SQL não desfaz efeito externo após crash; Observer e configuração/cache continuam com limites por processo. Astah excluído do escopo. Não presumir commit, push, publicação ou preparo oral dos quatro integrantes.

Os quatro relatórios integrais da auditoria inicial estão preservados em `evidencias_fechamento/historico-auditoria-inicial/`. As evidências finais portáveis estão em `evidencias_fechamento/pytest-original.xml`, `casos-testados.tsv`, `resumo-testes.json`, `interface.md`, `revisao-independente.md`, `migracao-e-ui.json` e `devolucao-responsavel.png`.
