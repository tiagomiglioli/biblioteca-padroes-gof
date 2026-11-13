# PROMPT MESTRE — IMPLEMENTAÇÃO DA BIBLIOTECA GoF

> Cole este texto no agente de programação (Fable, se ele tiver acesso ao repositório e às ferramentas, ou Claude Code). Antes, coloque na pasta de trabalho todos os PDFs, os slides, os modelos UML e os arquivos do projeto anterior. Não assuma que uma skill está instalada: verifique.

## PAPEL E OBJETIVO

Você atuará como engenheiro de software sênior, professor de padrões GoF e revisor rigoroso de requisitos. Sua missão é **IMPLEMENTAR E TESTAR**, não apenas planejar, um sistema web didático de gestão de empréstimos de livros para a disciplina Modelagem de Sistemas Computacionais da PUCPR, seguindo integralmente o arquivo `Trabalho_Implementacao_GoF_Biblioteca.pdf` (ou nome equivalente), os slides anexos, os diagramas e os contratos do Trabalho 02.

**Critério principal:** criar o menor sistema correto, funcional, demonstrável em cinco minutos e explicável integralmente por qualquer um dos quatro integrantes. A simplicidade não pode remover nenhum padrão, nenhuma classe obrigatória, integridade transacional, autenticação solicitada, nem os testes exigidos.

**Data-limite do enunciado:** 27/11/2026 às 09h40. **Linguagem:** Python orientado a objetos, autorizada verbalmente pelo professor. **Banco relacional obrigatório:** MySQL real, com família adicional em memória para testes. **Interface:** HTML + CSS + JavaScript mínimo, renderizada pelo Flask com Jinja2; evitar React, Next.js e dois servidores de desenvolvimento. **Autenticação:** Flask-Login com sessões seguras. **Testes:** pytest.

## PRIMEIRO: FERRAMENTAS / SKILLS

1. Inspecione as skills e comandos que **existem de verdade neste ambiente**. Utilize as instaladas e relevantes, sem afirmar execução quando não estiverem disponíveis.
2. **Superpowers**, do projeto `obra/superpowers`: usar as skills equivalentes a brainstorming, elaboração de plano, test-driven-development, systematic-debugging e verification-before-completion. Não dependa de um slash command genérico `/superpowers` se a instalação oferecer nomes diferentes. Leia as instruções reais da instalação. Faça planejamento limitado e EXECUTE o plano na mesma tarefa, por incrementos testáveis. Preserve trabalho existente e utilize branch/worktree para evitar alterações diretas em `main`.
3. **Graphify**, do projeto `Graphify-Labs/graphify`: se estiver instalado, executar `/graphify .` (ou `graphify update .`, conforme interface real), consultar grafo com `graphify query`/`graphify explain` para entender o projeto e rodar atualização após refatorações relevantes. Graphify é para **analisar relações do código**, não para desenhar o frontend. Se faltar, continue com leitura convencional e registre a ausência.
4. **Ponytail**, do projeto `DietrichGebert/ponytail`: usar modo `/ponytail full` ou seu equivalente real, conservando lógica, segurança e testes. Aplicar `/ponytail-review` ou equivalente ao final para detectar duplicações, dependências supérfluas, funções gigantes e problemas de correção. Nunca trocar correção por redução de linhas.
5. Se qualquer ferramenta/skill exigir instalação não autorizada, acesso, credencial ou execução indisponível, não invente resultados. Informe o impedimento, continue com o que há e documente os passos necessários.

## BASE DE REFERÊNCIA: REPOSITÓRIO IBK

Repositório público de referência: `https://github.com/joaopdiasdev/IBK_Grupo_6`.

A auditoria preliminar verificou que **não é uma biblioteca**: é um sistema de triagem clínica da Síndrome do X Frágil, com Flask, MySQL e frontend React.

Principais arquivos úteis do projeto anterior:
- `frontend/src/pages/Home.css`: aparência do formulário de login, cor azul `#202b5c`, fundo `#f4f7fb`.
- `frontend/src/pages/Pacientes.css`: sidebar fixa, tabela, busca, cards, espaços e estados de hover.
- `frontend/src/pages/NovaTriagem.css`: layout de formulários.
- `frontend/src/pages/Home.jsx`, `Pacientes.jsx`, `NovaTriagem.jsx`: referência do conteúdo e organização visual, mas **não copiar a lógica de triagem**.
- `frontend/src/services/api.js`: exemplo de comunicação Axios/Flask, que **não precisa ser mantido** se adotarmos Jinja2.
- `backend/app.py`, `backend/auth.py`, `backend/controllers/rotas.py`, `backend/dataBase/conexao.py`: referências de rotas, autenticação e conexão; **não copiar diretamente credenciais, chave secreta de desenvolvimento, token no localStorage ou regras clínicas**.
- `backend/dataBase/schema.sql`: referência da abordagem relacional; construir schema **novo** da biblioteca, sem misturar tabelas clínicas.
- `LICENSE`: verificar e preservar os avisos de licença necessários ao reaproveitar CSS/código.

**Obrigatório:** trabalhar em uma **nova pasta/projeto `biblioteca-gof/` ou branch isolada**. Não apagar nem sobrescrever o IBK original. Se o repositório Git não puder ser clonado, usar os arquivos locais enviados como referência. Não afirmar que transferiu arquivos se eles não estiverem presentes.

**Design mínimo:** adaptar apenas sidebar, cartões, formulário de login, tabela, cores e responsividade para a biblioteca. Remover logos, textos, entidades e fluxos clínicos. Preferir um CSS central com poucas classes reaproveitáveis. JavaScript apenas para confirmação, filtro simples ou interações realmente necessárias. Backend renderiza páginas Jinja2 e recebe POST de formulários. Criar JSON API apenas para um caso concreto em que seja indispensável; não duplicar tudo em endpoints REST.

## PRIORIDADE E FONTES DA VERDADE

1. Primeiro, ler **integralmente** enunciado e requisitos por padrão (páginas 1–5), slides 40+68 páginas, `src.zip` e qualquer documentação nova que eu adicionar.
2. Ler os diagramas `.asta`/PDF do Trabalho 02 e a lista original de situações GoF, se presentes. Inventariar diagramas/classes/invariantes já existentes.
3. O enunciado prevalece sobre exemplos genéricos dos slides; as regras do domínio devem corresponder aos diagramas anteriores. Em caso de conflito entre enunciado e UML, registrar divergência e adotar interpretação explícita que respeite o enunciado, sinalizando o ajuste UML necessário.
4. Se o professor verbalmente exigiu Singleton, implementá-lo como padrão COMPLEMENTAR. Os dez padrões obrigatórios **continuam obrigatórios**.
5. Não substituir Abstract Factory por Factory Method; não substituir State por um único `if/elif` ou enum; não substituir Command por uma função direta; não confundir Decorator GoF com `@decorator` de Python.
6. Só afirmar que algo está funcional se houve execução real e teste correspondente.

## STACK EXATA E RESTRIÇÕES

- Python 3.12+ (ou versão local compatível), Flask, Jinja2, Flask-Login, Werkzeug para hashing, mysql-connector-python e pytest.
- CSRF em formulários POST (Flask-WTF `CSRFProtect` se adequado); cookie `HttpOnly`, `SameSite=Lax`, `Secure` quando HTTPS, chave `SECRET_KEY` exclusivamente por ambiente, sem default inseguro fora de teste.
- `python-dotenv` é opcional se simplificar uso local; usar `.env.example`, jamais versionar `.env`, senhas ou dados pessoais.
- `decimal.Decimal` para dinheiro, `datetime.date` para vencimentos, calendário/injeção de data para simular devolução atrasada sem alterar relógio da máquina.
- MySQL com tabelas **InnoDB**, chaves estrangeiras, constraints `UNIQUE`, queries parametrizadas e transações explícitas. `root` não é credencial embutida no código.
- **Uma conexão/unidade de trabalho por operação transacional** no perfil MySQL; todos os repositórios da mesma operação compartilham essa conexão. Nunca manter uma conexão global Singleton, mesmo que o professor tenha demonstrado `GerenciadorBD` como Singleton em um slide. Expliquem o motivo na defesa.
- Não acrescentar Docker, Redis, Celery, SQLAlchemy, React, Tailwind, ORM, microsserviços, filas, autenticação JWT ou arquitetura hexagonal sem necessidade efetiva. Se Docker Compose simplificar MySQL, fazê-lo OPCIONAL, não requisito para rodar.
- Nomes de classes fáceis de ler, funções curtas, sem meta-programação desnecessária, comentários apenas para guardas/transações/racional GoF, texto da UI e documentação em português.

## ARQUITETURA MÍNIMA

Preferência de pastas (ajuste somente com justificativa):

```text
biblioteca-gof/
  app.py
  config.py
  requirements.txt
  .env.example
  README.md
  REGISTRO_LLM.md
  docs/
    REQUISITOS_RASTREABILIDADE.md
    DEFESA_GOF.md
    DIAGRAMAS_UML.md
  dominio/
    entidades.py
    erros.py
    tratadores.py
    circulacao_facade.py
    estados.py
    multas_strategy.py
    bancos_adapter.py
    devolucao_observer.py
    circulacao_command.py
    cadastros_template.py
    persistencia_factory.py
    consulta_decorator.py
    acervo_composite.py
    configuracao_singleton.py
  persistencia/
    memoria.py
    mysql.py
    unidade_trabalho.py
  web/
    rotas.py
    autenticacao.py
  templates/
    base.html
    login.html
    painel.html
    cadastros.html
    acervo.html
    circulacao.html
    multas.html
  static/
    css/style.css
    js/app.js
  sql/
    schema.sql
    seed_demo.sql
  tests/
    conftest.py
    test_r01_state.py
    ... test_r10_composite.py
    test_singleton.py
    test_web_auth.py
    test_integracao_mysql.py
```

**Mantenha os pontos internos de acesso `Acervo`, `Relacionamento`, `Movimentacao` e os TRATADORES do Trabalho 02**. A página chama tratador, tratador chama `CirculacaoFacade`/serviços, serviços executam domínio e repositórios. Nenhuma regra de disponibilidade, multa ou limite de renovação dentro de rotas/Jinja2/JS.

## REQUISITOS OBRIGATÓRIOS E TESTES DE ACEITAÇÃO

**R01 — State.** `Livro` é contexto e delega a objetos de estado; criar sete classes distintas para `LIVRE`, `RESERVADO`, `EMPRESTADO`, `RENOVADO`, `DEVOLVIDO`, `REPARANDO`, `INCINERADO`. Cada classe só implementa os eventos válidos; inválidos geram erro de domínio sem mutação. Guardar nome do estado no MySQL e reconstituir objeto ao carregar. A guarda `numRenovacoes < 2` deve ser avaliada ANTES de alterar o vencimento. Terceira renovação recusada, sem alterar data. Livro DEVOLVIDO ainda não inspecionado não pode reservar. Evento de laudo irrecuperável em REPARANDO leva a INCINERADO. Representar transições de maneira compatível com máquina de estados original.

**R02 — Strategy.** Contrato de política de multa, classes `MultaOriginal` (R$1/dia), `MultaComTeto` (máximo R$20) e `MultaComTolerancia` (dois primeiros dias sem cobrança). Política escolhida na configuração administrativa. Para 5 dias: original R$5 e tolerância R$3; sem atraso R$0. Multa emitida registra `valor` e `politica` imutáveis; mudar política no futuro não recalcula multa antiga. Cálculo monetário com Decimal; boleto não depende de qual política está em uso.

**R03 — Adapter.** Contrato `CobrancaInstitucional`; APIs externas incompatíveis simuladas por `BancoA` (700 centavos para R$7,00) e `BancoB` (7,00 reais). Adaptadores convertem valor, documento, identificador, status e notificação de pagamento. `ServicoMulta` desconhece tipo concreto do banco e não usa `if banco == ...`. Notificação de pagamento repetida não gera quitação repetida: exigir identificador externo único/constraint no MySQL.

**R04 — Facade.** `CirculacaoFacade` coordena `Relacionamento`, `Movimentacao`, `Acervo` e `Livro`, retorna comprovantes/DTOs, não coleções. Ao efetivar empréstimo: verificar reserva válida, remover reserva ativa, criar empréstimo, atualizar Livro, tudo na MESMA transação. Falha intermediária -> rollback integral e estado anterior preservado. Interface chama apenas tratadores. Testar falha injetada no meio.

**R05 — Observer.** Publicador de devolução com ouvintes de `Inspecao`, `Multa`, `Indicadores`, `Email`. Evento imutável contém estudante, vencimento, data de devolução e identificadores. Publicar somente DEPOIS do commit da devolução; falha de um ouvinte não impede os outros nem desfaz devolução. Se atraso, gerar multa e registrar indicadores; sem atraso, sem multa. Livro permanece DEVOLVIDO até inspeção explícita; a notificação para inspeção não muda o estado automaticamente. E-mail pode ser simulado por log ou caixa de saída de teste, sem credenciais externas.

**R06 — Command.** `ComandoReserva`, `ComandoRenovacao` com UUID, autor, instante e `executar()`. Tela cria a solicitação; executor a invoca, regras ficam no domínio. Mesma ID submetida 2x, inclusive concorrente, deve gerar efeito UMA vez e retorno consistente; comandos diferentes continuam sujeitos a 2 renovações. Persistir IDs no MySQL com UNIQUE, concorrência garantida por transação/constraints e bloqueio de linha quando necessário; em memória, lock. Não implementar undo sem justificativa funcional; explicar no README.

**R07 — Template Method.** Classe abstrata `CadastroBase` com `incluir()` como sequência fixa: buscar existente -> validar -> verificar pré-requisitos -> criar -> armazenar -> apresentar. Implementações para Pessoa, Estudante, Atendente e Livro; preservar contratos `iPessoa`, `iEstudante`, `iAtendente`, `iLivro` no desenho/implementação adequada a Python. Estudante duplicado retorna existente. Novo estudante com CPF de Pessoa inexistente falha ANTES de gravar. Evitar que subclasses alterem o algoritmo fixo (por convenção clara e proteção simples verificável; `@final` sozinho é apenas auxílio de tipagem).

**R08 — Abstract Factory.** `FabricaPersistencia` define criação de UnitOfWork e repositórios de Livro, Movimentacao e Relacionamento; `FabricaMemoria` fornece família inteira em memória e `FabricaMySQL` fornece família inteira MySQL. Perfil é escolhido UMA vez por configuração ao iniciar. Não misturar famílias. No MySQL todos compartilham a mesma unidade de trabalho/transação. Testar família memória sem conexão SQL e família MySQL com transação real; não escrever em Oracle (se houver réplica de contexto do Trabalho 02, apenas reconhecer esse limite).

**R09 — Decorator.** Interface de consulta ao acervo; implementação base intacta; `ConsultaComCache` e `ConsultaComMedicao` envolvem o mesmo contrato, permitindo composição. Em segunda consulta pode vir de cache e ainda assim gerar medição. Cache contém APENAS metadados, nunca autorização para reserva; operação de reserva consulta sempre estado atual em repositório. Simular metadados antigos em cache e garantir reserva negada quando livro não estiver LIVRE. Cache quebrado deve cair na implementação base sem derrubar o domínio.

**R10 — Composite.** Componente comum com `contar_livros()` e `listar_livros()`. `GrupoAcervo` (unidade, seção, subseção em profundidade variável) e `ItemLivro` (apenas ID do livro). Dois grupos contendo 3 e 2 livros somam 5. Proibir ciclos e o mesmo livro em dois grupos. Mover item entre seções não altera ID, status nem empréstimo do Livro. Não armazenar cópia mutável do objeto Livro dentro do composite.

**R11 — Singleton complementar, solicitado pelo professor.** `ConfiguracaoSistema` expõe uma única instância por processo de aplicação para dados de configuração não sensíveis ou para definição do perfil de execução. Mostrar com teste `a is b`, manter inicialização controlada e dar suporte à injeção/configuração isolada em testes. Não usar como trava global de reservas nem como conexão MySQL compartilhada; reconhecer que cada worker/processo pode ter sua instância. Explicar utilidade, limites e diferença para Abstract Factory.

## BANCO DE DADOS MYSQL REAL

Criar `sql/schema.sql` idempotente com InnoDB, relações e constraints suficientes para as entidades do trabalho: Pessoa, Estudante, Atendente, Livro, grupos do acervo, reservas, empréstimos/renovações/devoluções, multa, boleto/cobrança/quitação, comandos executados e usuários de login. Preferir modelo pequeno, sem tabelas artificiais. Diferenciar reserva ativa de histórico encerrado. Persistir numRenovacoes, vencimento e estado atual do livro. Usar unicidade de CPF, identificador do comando e notificação externa quando aplicável.

A configuração em `.env.example` deve incluir `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `SECRET_KEY`, `PERSISTENCE_PROFILE` e parâmetros mínimos da política de multa. Não salvar senha real em Git. `seed_demo.sql` deve criar cenário com pessoa, estudante, livro e usuário de demonstração de modo seguro (senha hash criada por script/bootstrap e credenciais de demonstração claramente restritas ao ambiente local).

Exigir teste de integração que conecte a MySQL real, grave dados, feche conexão, reabra e confirme persistência; testar rollback, sessão compartilhada dos repositórios e comando duplicado. Caso MySQL indisponível no ambiente do agente, NÃO simular sucesso: rodar testes em memória, marcar bloqueio e entregar roteiro preciso para testes MySQL locais; não afirmar integração validada.

## AUTENTICAÇÃO / FLASK

Flask-Login, sessões server-side assinadas pelo Flask, `login_user`, `login_required`, `logout_user`, duas funções de perfil no máximo (administrador/atendente) se exigidas por interface. Senhas em hash `werkzeug.security`, consulta a usuário no MySQL, sem senha em texto puro, sem JWT/localStorage, sem CORS aberto, sem credenciais embutidas. Exigir CSRF para POST. Segurança validada no backend, nunca confiar na ocultação de botão HTML. Testar login válido, inválido, logout, acesso protegido e CSRF. Se simples login de um administrador for suficiente, não fazer sistema avançado de permissões.

## TELAS E DEMONSTRAÇÃO

Criar **somente as telas necessárias**:
1. Login.
2. Painel inicial com acesso a operações.
3. Cadastros (Pessoa, Estudante, Atendente, Livro).
4. Acervo (busca, metadados, seções/subseções).
5. Circulação (reservar, emprestar, renovar, devolver, inspecionar), com estados e mensagens claros.
6. Multas (política, valor, boleto, bancos A/B simulados).

Estética baseada no IBK, sem imagens clínicas; menu lateral azul, fundo cinza claro, cartões brancos e tabelas legíveis. Tudo deve funcionar em navegador local por um único servidor Flask; sem frontend React separado. Preparar dados com atrasos simulados por injeção de datas para demonstrar multa em segundos. Demonstrar fluxo reserva -> empréstimo -> renovação -> devolução atrasada -> multa.

## TESTES E DEFESA

Criar no mínimo 10 arquivos/testes pytest com nomes R01–R10 correspondentes **exatamente** aos cenários descritos pelo professor, e teste extra de Singleton. Complementar com testes de falha/concorrência, persistência MySQL e autenticação. A UI deve ser testada com Flask test client, e se navegador disponível validar visualmente o fluxo real. Não contar casos que apenas testam mocks quando o cenário exige persistência real.

Produzir:
- `README.md`: instalação Python, setup MySQL, SQL, autenticação, execução, comando de testes, credenciais só de demo e como simular datas; registrar ferramenta/modelo de IA usados.
- `REGISTRO_LLM.md`: pedidos importantes, decisões aceitas, corrigidas e descartadas; sem afirmar que foi feito algo não executado.
- `docs/REQUISITOS_RASTREABILIDADE.md`: linha por padrão com requisito, intenção, classes (Context/Strategy/Adapter etc.), arquivo/método, teste e UML.
- `docs/DEFESA_GOF.md`: explicação simples de cada padrão — problema, participantes, fluxo, efeito de trocar implementação, exercício prático, perguntas possíveis e respostas sucintas; todos os quatro integrantes precisam dominar os onze padrões.
- `docs/DIAGRAMAS_UML.md`: mapa para corrigir diagramas Astah. Se ferramenta não permitir modificar `.asta`, NÃO alegar que o atualizou; registrar o trabalho pendente e gerar diagramas PlantUML/Mermaid auxiliares compatíveis para edição posterior no Astah.
- `docs/DEMO_5_MINUTOS.md`: roteiro cronometrado, comando de rodar testes, percurso web e resultado esperado.

## ORDEM OBRIGATÓRIA DE EXECUÇÃO

**Fase 0 — Auditoria sem alterações:** listar arquivos realmente encontrados, regras extraídas, códigos reutilizáveis, lacunas UML e decisão de persistência. Consultar Graphify se disponível. Criar matriz de verificação. Não inventar arquivos ausentes.

**Fase 1 — Esqueleto + MySQL:** criar pasta/branch, requirements enxuto, App Factory simples, modelos, SQL, factory memória/MySQL, UoW, autenticação básica e primeira tela. Rodar smoke test e testes de conexão se disponível.

**Fase 2 — Fluxo central:** implementar Template Method, State, Facade e Command com testes antes da lógica. Conseguir registrar estudante/livro, reservar, emprestar e renovar. Validar rollback, duplicação e limite de duas renovações.

**Fase 3 — Devolução/multa:** Observer, Strategy e Adapter, com emissão de multa, notificações e teste de idempotência. Garantir DEVOLVIDO até inspeção.

**Fase 4 — Consulta/acervo:** Decorator e Composite, integrados ao fluxo sem duplicar regras.

**Fase 5 — Singleton + interface final:** incluir singleton correto, adaptar CSS IBK para páginas Jinja2 e conectar formulários às operações já testadas.

**Fase 6 — Auditoria rigorosa:** rodar `python -m pytest -q`; integrar MySQL real; testar sessão nova, duplicações e rollback; usar Graphify atualizado, Ponytail Review e verificação Superpowers. Preparar documentação e defesa. Não declarar sucesso antes de executar comandos. Corrigir regressões antes de avançar.

## POLÍTICA DE AUTONOMIA

Não pare após entregar um plano. Comece a IMPLEMENTAR, rodar testes e corrigir. Use decisões conservadoras quando houver opções equivalentes. Se algo estiver bloqueado por credenciais MySQL, permissão ou arquivos UML ausentes, siga nas outras partes e documente o bloqueio de modo claro. Nunca apagar trabalho alheio, forçar push, mudar branch principal ou realizar ações irreversíveis sem autorização. Não publicar no GitHub automaticamente; trabalhar em branch isolada e preparar diff/PR para revisão.

**Após CADA fase**, informe objetivamente: arquivos criados/alterados, teste executado, testes aprovados/falhos, como executar e próximo passo. Não relatar testes imaginários, diagramas inexistentes ou módulos não integrados.

**No relatório final**, mostrar checklist dos dez padrões + Singleton, estados de testes, MySQL real, fluxo web, riscos/pendências e instruções para a demonstração, com referências concretas de arquivos e métodos. A implementação só está pronta quando as dez situações obrigatórias foram comprovadas com código executável e o fluxo completo está funcional.

COMECE AGORA: faça auditoria dos arquivos realmente existentes, mostre a matriz resumida dos 11 padrões e em seguida implemente por fases sem produzir complexidade extra.
