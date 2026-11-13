# Auditoria técnica — fechamento do atendente

Data: 13/11/2026. Parecer de entrega: **APTO — PODE ENTREGAR**.

## Resultado verificado

Na cópia `fechamento-atendente`, a suíte integrada terminou com **374 aprovados em 28,22 s, zero falhas, zero erros e zero pulados**, incluindo MySQL real. São **69 casos adicionais** em relação aos 305 da auditoria inicial: 32 de participantes/transações, 17 de persistência dos responsáveis, 2 de migração e 18 de limites de campos. JUnit conferido em `/tmp/fechamento-suite.xml`.

A revisão independente aprovou especificação e qualidade, sem achados P0/P1/P2/P3 (`/tmp/fechamento-review.md`). A migração principal e a aplicação final foram concluídas, com nova execução integral no original registrada abaixo.

**Astah está excluído da avaliação e dos bloqueios por instrução do usuário.** O requisito de negócio do Trabalho 02, página 2, permanece no escopo. Python OO, Flask/MySQL e Singleton seguem as decisões informadas pela equipe. Nenhuma conclusão aqui exige novo RBAC, SMTP ou banco financeiro externo real.

## Fechamento do bloqueio funcional

A ausência do atendente era um bloqueio real na auditoria inicial. Nesta etapa, reserva, empréstimo e devolução recebem seleção explícita de atendente cadastrado. `dominio/circulacao_facade.py:44` (`_validar_participantes`) compara o CPF das Pessoas e recusa ausência, papel inexistente e mesma Pessoa do estudante. As chamadas em `reservar`, `emprestar` e `devolver` validam na mesma unidade de trabalho da mutação. A devolução usa o estudante efetivo do empréstimo.

`Reserva.atendente_id`, `Emprestimo.atendente_id` e `Emprestimo.atendente_devolucao_id` preservam responsáveis separados. A reserva encerrada permanece inativa no histórico, inclusive em memória. Repositórios recusam exclusão e troca de CPF de papel já usado, evitando modificar retrospectivamente seus participantes. O comprovante informa o responsável; JSON antigo sem esse campo continua legível. Autor do Command permanece login do operador, distinto do papel selecionado.

A migração é aditiva: colunas nullable e FKs, sem remover dados nem inventar responsável de legado. `migrar-db` atualiza a base existente; `init-db` também aplica a migração. Execute uma vez por vez, após parar a versão anterior e antes de iniciar a nova. DDL MySQL confirma implicitamente: falha parcial é retomada pelo catálogo, não revertida como uma transação de dados.

**Migração principal/aplicação final:** A migração da base principal foi executada duas vezes, comprovando idempotência. Os dados anteriores das 11 tabelas permaneceram iguais; o catálogo passou a 14 FKs, incluindo as três dos responsáveis. Evidência: `evidencias_fechamento/migracao-e-ui.json`. O auditor principal aplicou 30 arquivos no original, executou novamente a suíte (374 aprovados em 36,29 s, zero falhas/erros/skips, exit 0), conferiu `git diff --check` sem problemas e reiniciou o servidor original em `127.0.0.1:5057`, com login funcional.

## Matriz R01–R11

APROVADO indica os cenários cobertos pela suíte de fechamento, não prova de todos os comportamentos possíveis. Os arquivos abaixo identificam a implementação; nomes, contagens e resultados estão em `EVIDENCIAS_TESTES.md`. A fronteira transacional e os participantes foram revistos sem retirar as expectativas anteriores.

| Req. | Padrão / status funcional | Arquivos de implementação | Comportamento comprovado | Testes e resultado final | Correção / limite |
|---|---|---|---|---|---|
| R01 | State — APROVADO nos cenários abaixo | `dominio/entidades.py; dominio/estados.py` | Livro delega a sete estados; guarda anterior à soma; DEVOLVIDO recusa reserva; laudo incinera. | `tests/test_r01_state.py`: **59 passaram**; suíte de fechamento | Nenhuma correção no State. Reconstrução persistida também em R08/MySQL. |
| R02 | Strategy — APROVADO nos cenários abaixo | `dominio/multas_strategy.py; dominio/tratadores.py` | 5 dias: R$5/R$3; teto20; zero; Decimal; política/valor congelados. | `tests/test_r02_strategy.py`: **21 passaram**; suíte de fechamento | Política administrativa por processo; não persiste escolha após reiniciar. |
| R03 | Adapter — APROVADO nos cenários abaixo | `dominio/bancos_adapter.py; dominio/multas_strategy.py` | R$7 vira 700/7.00; CPF, identificadores e status traduzidos; quitação única. | `tests/test_r03_adapter.py`: **17 passaram**; suíte de fechamento | Corrigida emissão concorrente; mais 4 testes A/B × memória/MySQL. |
| R04 | Facade — APROVADO nos cenários abaixo | `dominio/circulacao_facade.py; dominio/tratadores.py` | Reserva encerrada, empréstimo criado e estado atualizado na mesma UoW; falha injetada desfaz tudo. | `tests/test_r04_facade.py`: **14 passaram**; suíte de fechamento | Rollback provado nas duas famílias. Responsável validado/persistido nesta etapa; testes adicionais de participantes e histórico. |
| R05 | Observer — APROVADO nos cenários abaixo | `dominio/devolucao_observer.py; dominio/circulacao_facade.py` | Evento imutável depois commit; quatro ouvintes independentes; falha isolada; prazo sem multa. | `tests/test_r05_observer.py`: **16 passaram**; suíte de fechamento | Corrigido replay no mesmo publicador, incluindo concorrência/retry: +4 testes. Não é fila durável. |
| R06 | Command — APROVADO nos cenários abaixo | `dominio/circulacao_command.py; persistencia/mysql.py` | ID, autor, instante; efeito+ID+resultado atômicos; mesmo ID soma30 uma vez; IDs distintos respeitam2. | `tests/test_r06_command.py`: **14 passaram**; suíte de fechamento | Acrescentado teste real com quatro processos independentes e MySQL. |
| R07 | Template Method — APROVADO nos cenários abaixo | `dominio/cadastros_template.py; dominio/tratadores.py` | Buscar→validar→pré-requisito→criar→armazenar→apresentar; duplicado retorna existente; sem Pessoa não grava. | `tests/test_r07_template_method.py`: **12 passaram**; suíte de fechamento | Proteção __init_subclass__ existe; não é proteção contra monkeypatch deliberado. |
| R08 | Abstract Factory — APROVADO nos cenários abaixo | `dominio/persistencia_factory.py; persistencia/unidade_trabalho.py` | Famílias completas; repositórios MySQL compartilham conexão da UoW; commit/rollback real; perfil único. | `tests/test_r08_abstract_factory.py`: **10 passaram**; suíte de fechamento | Corrigidas exclusões órfãs na família memória; +16 testes de integridade e infraestrutura. |
| R09 | Decorator — APROVADO nos cenários abaixo | `dominio/consulta_decorator.py; dominio/tratadores.py` | medição(cache(base)); segundo acesso cacheado medido; reserva relê estado bloqueado; falha cache tolerada. | `tests/test_r09_decorator.py`: **13 passaram**; suíte de fechamento | Corrigida invalidação local após commit de edição/exclusão: +6 testes. Nunca autoriza reserva. |
| R10 | Composite — APROVADO nos cenários abaixo | `dominio/acervo_composite.py; dominio/tratadores.py` | 3+2=5; profundidade variável; ciclo/duplicação recusados; folha ID; mover preserva estado/empréstimo. | `tests/test_r10_composite.py`: **13 passaram**; suíte de fechamento | Nenhuma mudança no Composite. |
| R11 | Singleton — APROVADO nos cenários abaixo | `dominio/configuracao_singleton.py` | Mesma instância no processo; construção controlada; threads protegidas; nenhuma conexão compartilhada. | `tests/test_r11_singleton.py`: **5 passaram**; suíte de fechamento | Cinco testes; limite entre workers declarado. Sem conexão global. |


## Fluxo real adicional no navegador

O auditor principal demonstrou: ausência de atendente recusada; atendente ligado ao mesmo CPF recusado; reserva com A1; empréstimo com A2; renovação com vencimento em 12/01/2027; devolução em 17/01/2027 com A1, cinco dias de atraso e multa de R$5; pagamento simulado marcado como quitado. Isso comprova o fluxo informado com responsáveis diferentes por etapa. A consulta SQL confirmou A1/A2/A1, multa de R$5 quitada e uma única quitação; a inspeção final deixou o livro LIVRE. Evidências em `evidencias_fechamento/interface.md`, `migracao-e-ui.json` e `devolucao-responsavel.png`. Após aplicação no original, reinício e login também foram confirmados; o fluxo completo de navegador descrito foi exercitado na cópia de fechamento.

## Achados resolvidos nesta etapa

| Item | Situação atual | Evidência |
|---|---|---|
| Atendente ausente das transações | Corrigido no domínio, persistência, Command de reserva, tratadores e interface | `test_atendente_transacoes.py`, `test_persistencia_atendente.py`, navegador real |
| Pessoa do estudante igual à do atendente | Recusada no servidor antes de concluir a operação | Casos None/vazio/inexistente/mesmo CPF nas três operações |
| Sobrescrita da identidade histórica | Responsáveis separados; bloqueio de exclusão e troca de CPF de papel usado | Persistência real nas duas famílias, rollback e revisão independente |
| Schema antigo sem responsáveis | Migração aditiva testada com legado NULL e interrupção/repetição | `test_migracao_atendente.py`; duas execuções na base principal e preservação dos dados comprovadas |
| Limites somente HTML/erro SQL por campos longos | Limites backend alinhados aos VARCHAR; mensagens de domínio antes da gravação | `test_validacao_tamanhos.py`, 18 casos |

## Limites remanescentes do escopo acadêmico

- Seleção do atendente é feita pelo operador autenticado; não existe vínculo automático login/Pessoa nem RBAC novo. Não apresentar isso como autenticação da pessoa física selecionada.
- Responsáveis antigos desconhecidos ficam NULL. Isso conserva a verdade histórica e não dispensa responsável em novas operações públicas.
- Observer deduplica no publicador/processo; não há replay durável completo após queda entre commit e publicação. Indicadores e e-mail são locais/simulados.
- Banco financeiro é simulado. O lock da multa protege emissão concorrente local ao cenário; uma API real precisaria de idempotência por referência e reconciliação após crash externo.
- Configuração Singleton e invalidação de cache são por processo; não há coordenação geral de múltiplos workers. Reserva lê o estado atual no repositório.
- CPF é validado por formato, não por consulta documental; e-mail não é confirmação de titularidade. Não foi adicionada segurança ofensiva ampla, carga prolongada ou certificação de acessibilidade.
- O domínio oral dos quatro integrantes, ensaio de cinco minutos, identificação da equipe e decisão de commit/entrega exigem revisão humana.

## Histórico preservado

A auditoria inicial tinha 305 aprovações e parecer NÃO APTO por ausência do atendente. Naquela etapa foram corrigidos boleto concorrente, integridade em memória, fixture de teste, replay local Observer e invalidação de cache. Esse resultado histórico não era aprovação do requisito agora implementado. O fechamento autorizado adicionou 69 casos e obteve 374 aprovações; não houve dispensa presumida da regra.

## Parecer

**APTO — PODE ENTREGAR, no escopo solicitado, com Astah excluído.** Nenhum defeito funcional bloqueante conhecido permanece após as correções e verificações descritas. Os onze padrões e requisitos funcionais auditados têm evidência na suíte e documentação. Isso não representa garantia de ausência de qualquer bug nem certificação de produção distribuída.

A suíte no projeto original aplicado terminou com **374 aprovados em 36,29 s, zero falhas, erros ou skips**. Migração e comparação de todos os registros anteriores passaram. Revisão independente aprovada. Relatórios completos da auditoria inicial permanecem em `evidencias_fechamento/historico-auditoria-inicial/`, explicitamente históricos.
