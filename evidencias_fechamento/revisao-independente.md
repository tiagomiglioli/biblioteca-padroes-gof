# Revisão independente — fechamento do atendente

Cópia revisada: `/Users/tiagomiglioli/Documents/ChatGPT/padroes-de-projeto/fechamento-atendente`.
Entradas: `/tmp/fechamento-review.patch` e `docs/superpowers/plans/2026-11-13-atendente.md`.
Revisão somente leitura; nenhum arquivo do projeto alterado. Critério: aplicação acadêmica Flask/MySQL/memória e escopo explícito de reserva, empréstimo e devolução. Astah fora do escopo.

**Veredicto de especificação: APROVADO na revisão de código.**
**Veredicto de qualidade: APROVADO; nenhum defeito concreto bloqueante identificado.**
**Findings P0/P1/P2/P3: nenhum.**

A alteração exige um atendente explicitamente selecionado, compara a Pessoa pelo CPF e preserva responsáveis separados de reserva, empréstimo e devolução. A migração mantém responsáveis desconhecidos como NULL; não atribui autores inventados ao legado.

## Conferências com evidências

| Critério | Evidência | Avaliação |
|---|---|---|
| Ausente, inexistente e mesma Pessoa recusados | `dominio/circulacao_facade.py:44–56`; chamadas :63, :91, :125 | Validação compartilhada antes da mutação; compara CPF e não IDs dos papéis. None não recebe default artificial. |
| Devolução valida estudante real do empréstimo | `dominio/circulacao_facade.py:120–127` | Não confia no estudante selecionado no formulário para identificar o dono do empréstimo. |
| Validação e mutação na mesma UoW | `dominio/circulacao_facade.py:60–68`, :84–96, :114–133 | Rejeição não encerra reserva nem devolve livro parcialmente. Pós-commit Observer preservado :134–136. |
| Bloqueio de identidade durante transação | `persistencia/mysql.py:207–219`, :230–243; `persistencia/memoria.py:159–169`, :183–190 | MySQL usa FOR UPDATE ao ler papéis; operações que trocam CPF obtêm a mesma trava e consultam vínculos com leitura atual. Memória usa a trava da UoW. |
| Responsáveis separados e persistidos | `dominio/entidades.py:91–108`; `persistencia/mysql.py:138–166`; `persistencia/memoria.py:92–120` | Reserva mantém atendente_id; empréstimo mantém seu próprio atendente_id; devolução só preenche atendente_devolucao_id. |
| Histórico de reserva em memória preservado | `persistencia/memoria.py:97–104` | Encerra por ativa=False; consulta filtra ativas. A mudança corrige a antiga divergência em relação ao MySQL. |
| Exclusão/revínculo não corrompe autores históricos | `persistencia/memoria.py:162–200`; `persistencia/mysql.py:212–246`; `sql/schema.sql:54–57`, :67–72 | Guardas de troca de CPF incluem histórico; exclusão MySQL é protegida por FKs; memória confere reserva, empréstimo e devolução. Pessoa continua vinculada pelo CPF imutável da chave. |
| Migração conserva dados e aceita retomada | `persistencia/migracoes.py:16–30` | Só ALTER ADD de colunas nullable/FKs faltantes, baseado no catálogo. Não há DELETE, UPDATE de backfill ou DROP. Documentação no arquivo informa DDL com commit implícito e execução única antes da nova versão. |
| Inicialização antiga/instalação nova | `app.py:61–75`, schema novo | init-db aplica schema e migração; migrar-db permite atualização explícita sem inventar histórico. |
| Idempotência original mantida | `dominio/circulacao_command.py:21–44`, executor restante sem mudança; `dominio/entidades.py:126–147` | Atendente é dado do comando de reserva. Registro ID/efeito/resultado continuam mesma transação. JSON antigo lê por campo opcional com default None. Repetição é resposta histórica, não nova transação que precise inventar atendente. |
| UI encaminha e informa | `web/rotas.py:38–41`, :146–160, :174–177; `templates/circulacao.html:35–44` | Seletor explícito, aviso sobre operações obrigatórias, responsável no comprovante. Ausência fica permitida no HTML porque o mesmo formulário inclui operações que não exigem atendente; servidor decide corretamente. |
| Limites backend | `dominio/cadastros_template.py:16–27`; `dominio/tratadores.py` criar_grupo/criar_usuario | Limites correspondem a VARCHAR do schema (IDs20/título200/nome80/sobrenome80/email120/grupo100/login50). Erro de domínio antes da escrita. Não depende só de maxlength. |

## Testes inspecionados e não enfraquecidos

- `tests/test_atendente_transacoes.py:14` cobre três operações × None/vazio/inexistente/mesmo CPF; livro, multa e indicadores preservados.
- :40 cobre responsáveis diferentes por operação e efeito de atraso; :58 comprova rollback do ID de Command recusado e repetição do ID válido; :69 cobre formulário/retorno.
- `tests/test_persistencia_atendente.py:23` verifica IDs efetivamente armazenados nas três posições, inclusive reserva inativa; :56 rollback; :73 impede trocar Pessoa para estudante/atendente em cada fase; :98 JSON antigo.
- `tests/test_migracao_atendente.py:7` parametriza migração inteira/interrompida depois da primeira coluna; repete a migração, verifica NULL legado, linhas preservadas e FK recusando ID inexistente.
- `tests/test_validacao_tamanhos.py` cobre limites sem gravação, título no limite aceito, grupo e login.
- Comparei linhas removidas do patch em testes existentes: não foram removidas expectativas de estado, vencimento, multa, rollback, pagamento ou idempotência. As mudanças adaptam chamadas com atendente_id="A1", atualizam Comprovante esperado e cadastram Pessoa distinta no fixture web. Os únicos asserts removidos textualmente são substituídos pelo mesmo assert com o argumento de atendente.
- Busquei todos os callers Python fora dos testes de reservar/emprestar/devolver e dos métodos de Movimentacao alterados: propagação consistente; nenhum caller de produção antigo identificado.

## Limites da aprovação

Não repeti testes: o auditor principal executa a suíte completa e informou previamente 19 passes de persistência e 25 passes memória de domínio/limites. Esses números são informados pelo principal, não execuções minhas. Aprovação de revisão não substitui resultado final da suíte nem prova de navegador/migração no ambiente de entrega.

Não houve solicitação adicional de RBAC, SMTP ou banco externo real. SQL direto fora dos repositórios não é uma API suportada da aplicação; nullable existe deliberadamente para legado e novas operações públicas recusam ausência.

README/guias de migração/entrega ainda devem refletir a nova etapa antes de empacotar, como previsto no plano; não classifiquei trabalho documental ainda em execução como defeito do patch. Não examinei Astah e não exigi mudanças nele.

**Conclusão:** a mudança implementa o requisito sem introduzir camada desnecessária ou enfraquecer testes existentes. Pode seguir para fechamento com a evidência final da suíte e demonstração coletada pelo auditor principal.
