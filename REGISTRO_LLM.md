# Registro de uso de LLM

**Ferramenta:** Claude Code (Anthropic). **Modelo:** Claude Fable 5.2.
**Data da sessão:** 13/11/2026.
**Partes do sistema com participação do modelo:** todas (código, testes, SQL, telas, documentação).

Este arquivo resume os pedidos principais e o que foi aceito, corrigido ou descartado.
A equipe deve completar a coluna "Revisão da equipe" depois de ler e executar cada parte.

## Material entregue ao modelo

- `Trabalho_Implementacao_GoF_Biblioteca.pdf` (enunciado).
- `Trabalho 02-1.pdf` e `DiagramasFinal.asta` do Trabalho 02 (o `.asta` foi lido só como texto, para conferir nomes).
- Slides `01_OperacoesReeduzido.pdf` e `Padroes Extensao Responsabilidade E Fabrica.pdf`.
- `src.zip` com os exemplos Java do professor (Adapter, Composite, Decorator, Singleton, Delegation).
- `PROMPT_COMPLETO_BIBLIOTECA_FABLE_CLAUDE_CODE.md` e `ADENDO_ORGANIZACAO_COMENTARIOS_SINGLETON_DEFESA.md`, escritos pela equipe.

## Pedidos principais

| # | Pedido | Resultado |
|---|---|---|
| 1 | Ler todo o material, listar requisitos e propor plano (padrões, pastas, banco) antes de codar | Plano apresentado e aprovado pela equipe |
| 2 | Implementar com testes primeiro, por padrão | Feito por fases: State → persistência/Abstract Factory/Template Method/Singleton → Facade/Command/Observer/Strategy/Adapter → Decorator/Composite → web |
| 3 | Seguir os papéis dos padrões como nos slides do professor | Nomes de papéis dos slides nas docstrings (Contexto/Estrategia, Componente/Essencia/Decorador, Comando, FabricaAbstrata…). Observer, Facade e Template Method não aparecem nos slides: papéis do livro GoF |
| 4 | Testar de verdade, inclusive MySQL | Suíte rodada em memória e em MySQL real; resultado no relatório final da sessão |
| 5 | Revisão de segurança | Senhas, SQL, sessão e CSRF conferidos; itens no README |

## Decisões aceitas

- Python + Flask + Jinja2 + MySQL + pytest, como definido pela equipe e autorizado pelo professor.
- `Acervo`, `Movimentacao` e `Relacionamento` são, ao mesmo tempo, os pontos de acesso do Trabalho 02 e os produtos abstratos da Abstract Factory.
- `Livro` guarda `num_renovacoes` e `vencimento` do empréstimo em curso, porque as guardas do State dependem deles.
- Idempotência por restrição do banco (chave primária em `comando_executado` e em `quitacao`), não por estrutura em memória.
- Testes de persistência rodam nas duas famílias pela mesma fixture.
- Uma operação por formulário na tela Circulação, para a interface não decidir o que é válido.

## Correções feitas durante a sessão

- A máquina de estados proposta no plano tinha "cancelar reserva"; depois de ler o Trabalho 02, foi trocada pelas transições T1–T11 (entraram `enviarParaReparo` a partir de LIVRE e `excluirLivro`; saiu o cancelamento).
- Comentários do `schema.sql` continham `;` e quebravam a execução do arquivo comando a comando; os comentários foram reescritos.
- O comando `flask --app app ...` não encontrava a aplicação porque a fábrica se chamava só `criar_app`; o erro apareceu ao subir o servidor de verdade e foi corrigido com o apelido `create_app`.
- O teste de "mesmo evento entregue duas vezes" foi acrescentado depois de uma verificação por sabotagem mostrar que nenhum teste cobria essa proteção.

## Descartado

- Reaproveitar o repositório IBK (a equipe dispensou): o visual foi feito do zero, só com as cores indicadas.
- React, API REST duplicada, ORM, Docker, JWT: fora do necessário.
- Conexão MySQL como Singleton (exemplo `GerenciadorBD` do slide): substituída por unidade de trabalho por operação; o Singleton é a `ConfiguracaoSistema`.
- Operação de desfazer no Command: sem base nas regras do domínio.
- Tabela de configuração no banco: a política de multa vigente fica no Singleton e volta ao `.env` ao reiniciar.

## Suposições do modelo que a equipe deve confirmar

- Prazo inicial do empréstimo de 30 dias (o Trabalho 02 só fixa os 30 dias da renovação).
- Guarda `numRenovacoes < 2` em vez do `<= 2` citado como exemplo na tabela da seção 11 do Trabalho 02.
- Suposição original: "Atualizar" estudante/atendente trocava a pessoa vinculada. O fechamento abaixo restringe essa troca quando o papel já tem movimentação.

## O que o modelo NÃO fez

- Não alterou o arquivo Astah nem gerou PDF dos diagramas; há diagramas Mermaid em `docs/DIAGRAMAS_UML.md` para a equipe redesenhar.
- Não abriu o navegador: o fluxo web foi exercitado pelo cliente de testes do Flask e por requisições HTTP reais (curl) contra o servidor em execução, incluindo um reinício. A aparência das telas não foi conferida visualmente.
- Não testou no MySQL da equipe (sem credenciais): a integração foi validada em uma instância MySQL 9.4 local e temporária.

## Revisão da equipe

| Parte | Quem revisou | Entendeu e sabe explicar? | Observações |
|---|---|---|---|
| State | | | |
| Strategy | | | |
| Adapter | | | |
| Facade | | | |
| Observer | | | |
| Command | | | |
| Template Method | | | |
| Abstract Factory | | | |
| Decorator | | | |
| Composite | | | |
| Singleton | | | |
| Web e autenticação | | | |
| Persistência MySQL | | | |

## Histórico — auditoria inicial assistida de 13/11/2026 — Codex/OpenAI

Solicitação: auditoria final rigorosa dos dez padrões GoF e Singleton, execução real de testes/MySQL/interface, correções conservadoras e relatórios de entrega/defesa. O usuário posteriormente excluiu o Astah da avaliação.

Ferramenta: Codex desktop/OpenAI, com subagentes de domínio, persistência e documentação. A identificação exata do modelo desta execução não foi confirmada; este registro não modifica a identificação histórica declarada anteriormente pela equipe. Skills usadas: Superpowers (investigação, testes e verificação), Graphify, Ponytail e leitura de PDF. RTK nas execuções shell; CUA no navegador real.

Aceito/aplicado: proteção da emissão concorrente de boletos; deduplicação local do Observer; integridade de exclusões em memória; proteção da base de testes e propagação de erros SQL; invalidação local do cache após commit. Foram acrescentados 31 testes aos 274 existentes. Resultado daquela auditoria inicial: 305 aprovados, zero falhas e zero skips, MySQL real. Evidências e limites em EVIDENCIAS_TESTES.md.

Não aplicado naquela auditoria inicial: reestruturação para vínculo transacional do atendente, pois exige decisão e alteração coordenada de domínio/schema/tela/testes. Não foi presumida dispensa do requisito do Trabalho 02. Não foram acrescentadas integrações bancárias reais, SMTP, fila durável ou dependências. Não houve commit, push ou publicação.

Decisão histórica da auditoria inicial: NÃO APTO no escopo funcional, independentemente de Astah. Naquele momento, a recomendação era conferir o diff, resolver o vínculo do atendente e realizar a defesa/ensaio pessoalmente; geração assistida não comprova domínio oral. O fechamento autorizado está registrado a seguir.

## Fechamento autorizado — vínculo transacional do atendente

Pedido posterior da equipe: resolver o requisito de atendente identificado na auditoria inicial, em cópia isolada, preservando os onze padrões e os dados existentes. A ausência apontada anteriormente é contexto histórico, não descrição do código desta etapa.

Decisão aceita: seleção explícita de atendente cadastrado em reserva, empréstimo e devolução; validação de Pessoa distinta do estudante na fachada, dentro da transação; três responsáveis persistidos separadamente; reserva encerrada mantida como histórico; exclusão e troca de CPF de papel já usado recusadas. Autor do Command continua sendo o login do operador e não substitui o responsável selecionado.

Migração aceita: colunas e FKs aditivas, com NULL para legado desconhecido, catálogo para repetição/retomada e nenhum preenchimento inventado. `migrar-db` prepara base existente; `init-db` também aplica a migração. Parar a versão anterior, executar um migrador por vez e só então iniciar a nova. DDL MySQL pode confirmar parcialmente; recuar código preserva as colunas, sem DROP.

Também foram tratados limites de campos no servidor e mensagens de erro da interface. Descartado: redesenhar autenticação para vincular toda conta a Atendente ou criar RBAC novo. Permanecem os limites documentados de replay durável do Observer, configuração entre processos e efeitos de APIs bancárias reais.

Total final da suíte: **374 aprovados**, zero falhas/erros/skips: 28,22 s na cópia de fechamento e 36,29 s no original após aplicação. O parecer **APTO — PODE ENTREGAR** refere-se ao escopo acadêmico auditado, com Astah excluído. Evidências em `AUDITORIA_FINAL.md`, `EVIDENCIAS_TESTES.md` e `evidencias_fechamento/`. Os resultados da auditoria inicial pertencem ao estado anterior e foram preservados como histórico; a suíte não certifica domínio oral dos integrantes.

A migração da base principal foi executada duas vezes, comprovando idempotência. Os dados anteriores das 11 tabelas permaneceram iguais; o catálogo passou a 14 FKs, incluindo as três dos responsáveis. Evidência: `evidencias_fechamento/migracao-e-ui.json`. O auditor principal aplicou 30 arquivos no original, executou novamente a suíte (374 aprovados em 36,29 s, zero falhas/erros/skips, exit 0), conferiu `git diff --check` sem problemas e reiniciou o servidor original em `127.0.0.1:5057`, com login funcional.
