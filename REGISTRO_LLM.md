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
- "Atualizar" estudante/atendente troca a pessoa vinculada (são os únicos dados do papel).

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
