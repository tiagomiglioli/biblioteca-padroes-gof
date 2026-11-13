# ADENDO OBRIGATÓRIO — CÓDIGO SIMPLES, ORGANIZADO, COMENTADO E FÁCIL DE DEFENDER

**Projeto:** Sistema de Biblioteca com padrões GoF — PUCPR 2026  
**Destinatário:** Fable / Claude Code ou outro agente de programação  
**Natureza:** Instruções complementares ao `PROMPT_COMPLETO_BIBLIOTECA_FABLE_CLAUDE_CODE.md`, aos slides e ao enunciado. **Não substitui os requisitos anteriores.**

## 1. Objetivo acima de tudo

Implemente o sistema de biblioteca **funcional, visualmente organizado e didático**, usando **Python orientado a objetos + Flask + Jinja2 (HTML/CSS/JavaScript simples) + Flask-Login + MySQL relacional + pytest**. O código deverá ser **o mais simples possível sem perder nenhum requisito obrigatório**. Cada um dos quatro integrantes deverá conseguir abrir uma classe, explicar o padrão, mostrar o fluxo no navegador e executar o teste correspondente.

**SINGLETON É OBRIGATÓRIO**, como **11º padrão complementar** solicitado pelo professor. Os **10 padrões do enunciado também são obrigatórios**: State, Strategy, Adapter, Facade, Observer, Command, Template Method, Abstract Factory, Decorator e Composite. Nenhum poderá ser substituído ou implementado de maneira apenas decorativa.

**Critério de sucesso:** clareza + funcionamento real + coerência com os diagramas UML + testes executados + documentação de defesa. Não otimizar para quantidade de arquivos ou sofisticação de arquitetura.

## 2. Organize por camadas, sem criar engenharia desnecessária

Use uma estrutura objetiva e siga-a consistentemente (pode adaptar nomes já existentes com justificativa):

```text
biblioteca-gof/
├── app.py                       # inicia e configura o Flask
├── config.py                    # variáveis/configurações da execução
├── requirements.txt
├── .env.example                 # exemplo SEM credenciais reais
├── README.md
├── REGISTRO_LLM.md
├── web/
│   ├── rotas.py                 # requisição HTTP -> tratador -> resposta
│   └── autenticacao.py          # login, logout, Flask-Login
├── dominio/
│   ├── entidades.py             # Livro, Pessoa, Estudante etc.
│   ├── erros.py                 # erros de regra de negócio
│   ├── tratadores.py            # pontos de entrada exigidos no Trabalho 02
│   ├── circulacao_facade.py
│   ├── estados.py               # State: sete classes de estado
│   ├── multas_strategy.py
│   ├── bancos_adapter.py
│   ├── devolucao_observer.py
│   ├── circulacao_command.py
│   ├── cadastros_template.py
│   ├── persistencia_factory.py
│   ├── consulta_decorator.py
│   ├── acervo_composite.py
│   └── configuracao_singleton.py # SINGLETON OBRIGATÓRIO
├── persistencia/
│   ├── memoria.py               # repositórios de teste
│   ├── mysql.py                 # repositórios reais, SQL parametrizado
│   └── unidade_trabalho.py      # transação / commit / rollback
├── templates/
│   ├── base.html                # layout comum
│   ├── login.html
│   ├── painel.html
│   ├── cadastros.html
│   ├── acervo.html
│   ├── circulacao.html
│   └── multas.html
├── static/
│   ├── css/style.css            # design centralizado, sem duplicações
│   └── js/app.js                # somente interações indispensáveis
├── sql/
│   ├── schema.sql               # MySQL/InnoDB, FKs, UNIQUE
│   └── seed_demo.sql            # dados fictícios para a apresentação
├── tests/
│   ├── test_r01_state.py
│   ├── test_r02_strategy.py
│   ├── test_r03_adapter.py
│   ├── test_r04_facade.py
│   ├── test_r05_observer.py
│   ├── test_r06_command.py
│   ├── test_r07_template_method.py
│   ├── test_r08_abstract_factory.py
│   ├── test_r09_decorator.py
│   ├── test_r10_composite.py
│   ├── test_r11_singleton.py    # identidade da instância e limites
│   ├── test_autenticacao.py
│   └── test_mysql_integracao.py
└── docs/
    ├── RASTREABILIDADE.md
    ├── GUIA_DEFESA.md
    └── DIAGRAMAS_UML.md
```

**Responsabilidade de cada camada:**

- `templates/`, `static/`, `web/`: exibem informações, recebem formulários e chamam **tratadores**; **sem decisões de regras de negócio**.
- `dominio/`: entidades, validações, regras de biblioteca e os padrões GoF. Regras de disponibilidade/renovação/multa ficam **aqui**.
- `persistencia/`: armazenamento e consultas ao banco, sem decidir regras da biblioteca.
- `tests/`: comprova comportamento, inclusive erros, concorrência e transações.
- `docs/`: explica cada padrão com linguagem que um estudante consegue apresentar.

Fluxo padrão: **HTML → rota Flask → tratador → Facade/serviços → domínio + repositórios → MySQL → resultado → HTML**.

## 3. Comentários e nomes para facilitar a arguição

1. Use **nomes legíveis em português** para classes e métodos de domínio: `Livro`, `EstadoEmprestado`, `PoliticaMultaOriginal`, `CirculacaoFacade`, `reservar()`, `renovar()` etc. Use termos consagrados de bibliotecas quando necessário, mantendo consistência.
2. Cada classe de padrão deve ter **docstring curta (2–4 linhas)** com: padrão usado, papel GoF (contexto, estratégia concreta, adaptador, observador etc.) e por que a classe existe.
3. Cada método de negócio relevante deve ter docstring curta que diga o que recebe, o que valida ou altera e qual erro pode lançar. Não documentar métodos triviais excessivamente.
4. Coloque **comentários pontuais explicando o PORQUÊ**, sobretudo antes de: limite `numRenovacoes < 2`, atualização de vencimento, `commit/rollback`, evento pós-confirmação, idempotência, conversões de centavos, proteção contra cache desatualizado, proteção contra ciclos no Composite e compartilhamento de transação.
5. NÃO comentar cada linha, NÃO criar comentários óbvios (`# soma 1`), NÃO deixar blocos mortos/TODOs que escondem requisito não implementado.
6. Prefira métodos curtos e um único propósito. Evite funções gigantes, heranças profundas, reflexão, metaclasses e abstrações extras. **Mas nunca compacte tudo em um arquivo só** nem destrua os papéis dos padrões para economizar linhas.
7. Onde existir uma implementação de padrão, marque no topo da classe, por exemplo: `"""GoF — Strategy / ConcreteStrategy: calcula multa com 2 dias de tolerância."""`.
8. Mantenha erros legíveis em português na interface, sem expor credenciais, SQL ou tracebacks ao usuário.

## 4. SINGLETON — obrigação explícita e não negociável

Implemente `ConfiguracaoSistema` como **Singleton real, demonstrável e testável**, com um ponto de acesso explícito (ex.: `obter_instancia()`) que retorna sempre a mesma instância dentro do processo Python. Use-o para **configurações da execução**: política de multa selecionada, perfil de repositórios ou opções simples. A inicialização deve ocorrer apenas uma vez, ser previsível e não reconfigurar silenciosamente o objeto a cada acesso. Se houver uso em múltiplas threads, proteger a primeira criação adequadamente.

Obrigatório demonstrar com **teste pytest**:

```python
primeiro = ConfiguracaoSistema.obter_instancia()
segundo = ConfiguracaoSistema.obter_instancia()
assert primeiro is segundo
```

Explicação para a defesa: **problema** (evitar configurações independentes conflitantes), **solução** (controlar a instância), **papel** (`ConfiguracaoSistema` administra o acesso), **limitação** (uma instância por processo, não por todos os workers), **diferença** para Abstract Factory (a fábrica cria famílias compatíveis; Singleton controla quantidade de instâncias).

**PROIBIDO:** tornar a conexão MySQL um Singleton global; compartilhar cursor/conexão entre requisições; usar Singleton para substituir transação, concorrência, idempotência ou Abstract Factory. Cada operação MySQL usa **unidade de trabalho própria** e repositórios da operação compartilham a mesma conexão/transação.

## 5. Não perder nenhum dos dez padrões obrigatórios

| Requisito | Prova concreta da implementação |
|---|---|
| R01 State | Sete classes (`LIVRE`, `RESERVADO`, `EMPRESTADO`, `RENOVADO`, `DEVOLVIDO`, `REPARANDO`, `INCINERADO`); terceira renovação recusada **sem mudar vencimento**; livro devolvido aguarda inspeção; laudo irrecuperável leva à incineração. |
| R02 Strategy | Políticas original, teto R$ 20 e tolerância de 2 dias; 5 dias = R$ 5 ou R$ 3; `Decimal` e política registrada na emissão da multa. |
| R03 Adapter | Bancos A e B externos **simulados**, mas adaptadores reais: R$ 7 → 700 centavos no A e 7,00 no B; tratar confirmação repetida sem dupla quitação. **Eles não são o MySQL**. |
| R04 Facade | Entrada única coordena reserva, empréstimo, renovação, devolução; empréstimo remove reserva ativa, grava movimentação e atualiza estado **numa única transação**. |
| R05 Observer | Ouvintes independentes de inspeção, multa, indicadores e e-mail; notificação após confirmação da devolução; falha do e-mail não cancela nem bloqueia os demais. |
| R06 Command | `ComandoReserva` e `ComandoRenovacao` com ID, autor e data; **idempotência inclusive em solicitações simultâneas**; mesma solicitação não renova duas vezes. |
| R07 Template Method | Fluxo fixo de cadastro: procurar existente → validar → pré-requisitos → criar → armazenar → apresentar; cadastros de Livro/Pessoa/Estudante/Atendente; sem gravação parcial. |
| R08 Abstract Factory | Uma fábrica entrega **toda** a família em memória e outra entrega **toda** a família MySQL; mesma unidade de trabalho para os repositórios envolvidos; sem mistura de famílias. |
| R09 Decorator | Consulta base + `CacheConsulta` + `MedicaoConsulta`, combináveis; cache somente metadados; nunca usar cache como prova de disponibilidade para reserva. |
| R10 Composite | Árvore `Unidade → Seção → Subseção → ItemLivro`; contagem recursiva; impedir ciclos e duplicidade de pertencimento; mover livro sem alterar empréstimo/estado. |

O **R11 Singleton é adicional**, não substitui nenhum item acima.

## 6. Interface bonita, mas pequena e funcional

Reaproveite **apenas a inspiração visual** do `IBK_Grupo_6`: sidebar azul-escura (`#202b5c`), fundo claro (`#f4f7fb`), cartões brancos, tabelas legíveis e formulários bem espaçados. **Não copie a lógica clínica e não mantenha React**. Use Jinja2 com `base.html` e CSS reutilizável.

Criar somente o essencial: **Login**, **Painel**, **Cadastros**, **Acervo**, **Circulação** e **Multas**. Permitir uma demonstração de reserva → empréstimo → renovação → devolução atrasada → multa sem sair da aplicação. Use dados fictícios predefinidos e opção de demonstrar data de devolução por parâmetro controlado no backend. Não adulterar o relógio, nem adicionar regra de domínio ao JavaScript.

Um único servidor Flask; sem build frontend, sem Node.js, sem React, sem API duplicada sem necessidade. A autenticação usa **Flask-Login + hash de senha + CSRF**, sem token no `localStorage`, senha hardcoded, credencial no Git ou rota protegida apenas por CSS.

## 7. MySQL de verdade e comportamento transacional

- `schema.sql` com tabelas relacionais necessárias, **InnoDB**, chaves primárias/estrangeiras e restrições de unicidade.
- Credenciais somente no ambiente (`.env.example` não contém senhas reais).
- SQL parametrizado com `mysql-connector-python`; no backend, criação, fechamento, `commit()` e `rollback()` explícitos.
- Todos os repositórios envolvidos em um empréstimo compartilham **a mesma conexão da unidade de trabalho**, para rollback integral.
- Gravar identificadores únicos de Command e confirmação de pagamento para garantir idempotência sob concorrência; usar restrições MySQL e transações, não apenas `set()` global Python.
- Testar reinicialização da aplicação, continuidade dos dados, falha no meio de operação e rollback; diferenciar testes em memória de testes MySQL reais.
- Não declarar integração validada sem acessar MySQL real.

## 8. Documentação e roteiro de defesa obrigatórios

Crie `docs/GUIA_DEFESA.md` com **uma ficha de cada um dos 11 padrões** (10 + Singleton), contendo **no máximo meia página por padrão**:

1. **O que é?** (1 frase simples).
2. **Qual problema resolve na biblioteca?** (1 frase).
3. **Onde está?** (arquivo, classe e método reais).
4. **Como funciona?** (3–5 passos curtos usando classes reais).
5. **Qual teste comprova?** (nome real do teste e resultado da execução).
6. **O que aconteceria se removêssemos o padrão?** (resposta curta).
7. **Qual mudança ao vivo o professor poderia pedir?** (exemplo simples: nova estratégia de multa ou novo observador).

Crie `docs/RASTREABILIDADE.md`: requisito → padrão → classe(s) → teste(s) → arquivo UML correspondente. Atualize Astah/PDF quando houver fonte disponível; **não invente UML que não tenha sido verificada**. Prepare `README.md` com instalação local, criação do MySQL, comandos de teste, execução Flask, credenciais de demonstração criadas por script (não hardcoded na aplicação), e roteiro de apresentação de 5 minutos. Atualize `REGISTRO_LLM.md` com prompts e decisões da IA, conforme enunciado.

Faça também `docs/PERGUNTAS_DEFESA.md` com questões que o professor poderia fazer, respostas curtas e localização exata no código. Treine especialmente: diferença State/Strategy, por que Adapter não é banco de dados, onde ficam as transações, Command duplicado, Observer falho, cache, Abstract Factory e Singleton.

## 9. Ritual obrigatório antes de concluir

1. Verifique as skills disponíveis e use **Superpowers**, **Graphify** e **Ponytail** conforme instaladas. Se alguma não existir, **registre** e siga sem simular que executou.
2. Leia o enunciado, slides, `.asta` ou diagramas disponibilizados e o prompt mestre antes de modificar arquivos. Preserve o código original em branch/pasta separada.
3. Implemente em incrementos executáveis: entidades/State → persistência e Factory → Facade/Command → demais GoF → Singleton → interface → autenticação → revisão.
4. Rode `python -m pytest -q` e informe **quantos passaram, falharam ou foram pulados**. Rode também testes reais de integração MySQL e autenticação.
5. Execute o fluxo completo no navegador ou cliente Flask e comprove persistência após reinício.
6. Revise imports, nomes, duplicações, classe/método grande, código morto, comentários enganosos e coesão entre arquivos. Simplifique somente se preservar invariantes e testes.
7. Confira se todas as **11 fichas de defesa** apontam para classes/testes que realmente existem.
8. Faça relatório final honesto: arquivos criados/alterados, padrões implementados, resultado dos testes, banco conectado, fluxo web e pendências. **Não declare sucesso sem prova.**

## 10. Instrução final ao agente

> **Você não deve apenas planejar ou entregar um esqueleto. Implemente a aplicação funcional do jeito mais simples, organizado, comentado e visualmente apresentável possível; respeite os dez GoF, acrescente Singleton obrigatório, use Flask-Login, MySQL real e testes. Entregue código que um universitário consiga explicar sem decorar centenas de abstrações. Quando um trecho ficar difícil de explicar, simplifique-o preservando o comportamento, documente-o em português e execute novamente seus testes.**
