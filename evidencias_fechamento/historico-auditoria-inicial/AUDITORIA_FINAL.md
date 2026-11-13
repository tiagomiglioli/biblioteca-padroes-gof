# Auditoria técnica final — Biblioteca GoF

Data: 13/11/2026. Parecer: **NÃO APTO — NÃO ENTREGAR AINDA**.

## Escopo e decisão

O código implementa os onze padrões de forma identificável, não apenas por comentários. A suíte final executada no projeto corrigido terminou com **305 aprovados, 0 falhas, 0 skips**, incluindo MySQL real. Isso não comprova requisitos ausentes da suíte. Permanece uma regra funcional explícita do Trabalho 02 não implementada: toda transação deve envolver atendente e estudante de pessoas diferentes.

**Astah foi excluído da avaliação e dos bloqueios pela instrução posterior do usuário.** Não há reprovação por arquivo Astah, por seus diagramas ou por sua exportação. Este parecer é técnico no escopo ajustado; não certifica dispensas concedidas pelo professor. Os requisitos de negócio do PDF continuam no escopo.

Enunciado GoF é a fonte principal; Singleton e stack Flask/MySQL são exigências complementares da equipe. Python OO foi aceito conforme informação do usuário. O prompt de auditoria foi lido integralmente como especificação complementar solicitada; não substitui instruções posteriores. Nenhum push, publicação ou modificação do projeto IBK foi feito.

## Evidência da execução

- Base inicial: 274 testes existentes; sandbox impediu TCP local e produziu 181 passes/93 skips. Não era prova de indisponibilidade do MySQL.
- Reexecução autorizada com MySQL 9.4.0 real e base separada: **274 passaram**.
- Provas novas revelaram bugs não cobertos. Reparos pontuais foram feitos com teste vermelho/verde.
- Projeto final: **305 passaram em 23,67 s**; evidências JUnit e lista de cada caso em `evidencias_auditoria/`.
- Navegador real: cadastro Pessoa/Estudante/Atendente/Livro, login com CSRF, reserva, empréstimo, renovação, devolução com cinco dias de atraso, multa R$5, pagamento simulado, repetição recusada e inspeção. Consulta SQL confirmou efeitos; processo Flask foi encerrado e reaberto, dados e multa quitada permaneceram.

## Matriz R01–R11

“APROVADO” nesta tabela significa implementação e cenários funcionais indicados aprovados. Não significa cobertura de toda execução possível, integração bancária externa, tolerância a crash ou aprovação global do trabalho. Comando F01 e nomes completos dos testes estão em `EVIDENCIAS_TESTES.md` e `evidencias_auditoria/RESULTADOS_POR_TESTE.tsv`.

| Req. | Padrão / status funcional | Evidência arquivo:linha | Comportamento comprovado | Testes e resultado final | Correção / limite |
|---|---|---|---|---|---|
| R01 | State — APROVADO nos cenários abaixo | `dominio/entidades.py:10; dominio/estados.py:15,55,70,81,92,104,116,128,140,152` | Livro delega a sete estados; guarda anterior à soma; DEVOLVIDO recusa reserva; laudo incinera. | `tests/test_r01_state.py`: **59 passaram**; comando F01 | Nenhuma correção no State. Reconstrução persistida também em R08/MySQL. |
| R02 | Strategy — APROVADO nos cenários abaixo | `dominio/multas_strategy.py:14,24,33,42,61; dominio/tratadores.py:309` | 5 dias: R$5/R$3; teto20; zero; Decimal; política/valor congelados. | `tests/test_r02_strategy.py`: **21 passaram**; comando F01 | Política administrativa por processo; não persiste escolha após reiniciar. |
| R03 | Adapter — APROVADO nos cenários abaixo | `dominio/bancos_adapter.py:36,54,68,82,105; dominio/multas_strategy.py:90` | R$7 vira 700/7.00; CPF, identificadores e status traduzidos; quitação única. | `tests/test_r03_adapter.py`: **17 passaram**; comando F01 | Corrigida emissão concorrente; mais 4 testes A/B × memória/MySQL. |
| R04 | Facade — APROVADO nos cenários abaixo | `dominio/circulacao_facade.py:10,44,67,84,97; dominio/tratadores.py:243` | Reserva encerrada, empréstimo criado e estado atualizado na mesma UoW; falha injetada desfaz tudo. | `tests/test_r04_facade.py`: **14 passaram**; comando F01 | Rollback provado nas duas famílias. Vínculo de atendente herdado continua ausente, ver B01. |
| R05 | Observer — APROVADO nos cenários abaixo | `dominio/devolucao_observer.py:12,31,38,80,93,104,119; dominio/circulacao_facade.py:119` | Evento imutável depois commit; quatro ouvintes independentes; falha isolada; prazo sem multa. | `tests/test_r05_observer.py`: **16 passaram**; comando F01 | Corrigido replay no mesmo publicador, incluindo concorrência/retry: +4 testes. Não é fila durável. |
| R06 | Command — APROVADO nos cenários abaixo | `dominio/circulacao_command.py:16,37,46,55; persistencia/mysql.py:165` | ID, autor, instante; efeito+ID+resultado atômicos; mesmo ID soma30 uma vez; IDs distintos respeitam2. | `tests/test_r06_command.py`: **14 passaram**; comando F01 | Acrescentado teste real com quatro processos independentes e MySQL. |
| R07 | Template Method — APROVADO nos cenários abaixo | `dominio/cadastros_template.py:31,41,48,87,108,123,136,149; dominio/tratadores.py:27` | Buscar→validar→pré-requisito→criar→armazenar→apresentar; duplicado retorna existente; sem Pessoa não grava. | `tests/test_r07_template_method.py`: **12 passaram**; comando F01 | Proteção __init_subclass__ existe; não é proteção contra monkeypatch deliberado. |
| R08 | Abstract Factory — APROVADO nos cenários abaixo | `dominio/persistencia_factory.py:9,33,55,80; persistencia/unidade_trabalho.py:12,36,59` | Famílias completas; repositórios MySQL compartilham conexão da UoW; commit/rollback real; perfil único. | `tests/test_r08_abstract_factory.py`: **10 passaram**; comando F01 | Corrigidas exclusões órfãs na família memória; +16 testes de integridade e infraestrutura. |
| R09 | Decorator — APROVADO nos cenários abaixo | `dominio/consulta_decorator.py:22,33,45,58,91; dominio/tratadores.py:385` | medição(cache(base)); segundo acesso cacheado medido; reserva relê estado bloqueado; falha cache tolerada. | `tests/test_r09_decorator.py`: **13 passaram**; comando F01 | Corrigida invalidação local após commit de edição/exclusão: +6 testes. Nunca autoriza reserva. |
| R10 | Composite — APROVADO nos cenários abaixo | `dominio/acervo_composite.py:7,21,39,67,87,100; dominio/tratadores.py:217` | 3+2=5; profundidade variável; ciclo/duplicação recusados; folha ID; mover preserva estado/empréstimo. | `tests/test_r10_composite.py`: **13 passaram**; comando F01 | Nenhuma mudança no Composite. |
| R11 | Singleton — APROVADO nos cenários abaixo | `dominio/configuracao_singleton.py:6,20,29` | Mesma instância no processo; construção controlada; threads protegidas; nenhuma conexão compartilhada. | `tests/test_r11_singleton.py`: **5 passaram**; comando F01 | Cinco testes; limite entre workers declarado. Astah excluído por solicitação posterior. |

## Pendências por severidade

### B01 — BLOQUEANTE: atendente ausente das transações

**NÃO IMPLEMENTADO.** `Trabalho 02-1.pdf`, página 2, estabelece reserva, empréstimo e devolução como transações com data, livro, estudante e atendente, sendo pessoas diferentes. A fonte foi localizada em `/Users/tiagomiglioli/Downloads/Trabalho 02-1.pdf` e lida integralmente. A conclusão não depende do Astah.

`dominio/entidades.py:91` (`Reserva`) e `:99` (`Emprestimo`) não têm atendente; `sql/schema.sql:48` e `:60` também não. `CirculacaoFacade.emprestar` e `devolver` não recebem nem validam atendente. `Usuario` só tem login/hash, sem vínculo ao papel. O autor do Command não resolve isso: não representa atendente de todas as transações nem valida pessoas diferentes. O cadastro de Atendente funciona, mas seu uso transacional não existe.

Correção necessária: definir o vínculo usuário/atendente ou seleção explícita, registrar atendente em reserva/empréstimo/devolução, validar Pessoa distinta do estudante no domínio, preservar histórico e acrescentar testes positivos/negativos nas duas persistências e na interface. Exige mudança coordenada em schema, entidades, contratos, repositórios, fachada, tratadores, tela e fixtures. Não fiz migração de dados nem inventei um atendente padrão. Alternativa: obter dispensa explícita dessa regra do professor; nenhuma dispensa dessa regra foi apresentada. A autorização para Python e a exclusão do Astah não dispensam esse comportamento.

### A01 — ALTO, CORRIGIDO: dois boletos concorrentes para uma multa

Original lia multa, encerrava transação, emitia boleto e gravava em outra transação. Duas requisições geravam IDs diferentes; o último sobrescrevia o primeiro. Prova original: duas cobranças, pagamentos aceitos `[False, True]`. Agora `ServicoMulta.emitir_boleto` bloqueia a multa até emissão simulada e gravação. MySQL usa `FOR UPDATE`; memória usa trava da UoW. Testes A/B em ambas famílias aprovados. Limite: crash entre emissão externa e commit não está coberto; banco real exigiria idempotência externa por referência.

### A02 — ALTO, CORRIGIDO: exclusão em memória criava órfãos

Excluir Pessoa vinculada era permitido e devolução posterior falhava com AttributeError. Excluir Estudante e Livro com histórico também divergia das FKs MySQL. Repositórios em memória agora recusam exclusões vinculadas; dados permanecem e devolução continua possível. Testes exercitam vínculos e histórico nas duas famílias.

### A03 — ALTO condicional, CORRIGIDO: testes podiam truncar base de aplicação

`tests/conftest.py` agora recusa igualdade entre `MYSQL_TEST_DATABASE` e `MYSQL_DATABASE`, inclusive diferença apenas de caixa. Todas as execuções desta auditoria usaram bases exclusivas. Nenhuma base de demonstração foi truncada. A proteção não adivinha se outro nome representa dados importantes; ainda é necessário selecionar uma base descartável.

### M01 — MÉDIO, CORRIGIDO LOCALMENTE: metadados antigos após edição/exclusão

O cache não invalidava dados embora a interface permitisse editar/excluir livros. Foram acrescentados contrato público `invalidar`, delegação pelos decoradores e invalidação pelo tratador após commit. Se o cache falhar na remoção, a cópia local é descartada e a alteração confirmada não é desfeita. Seis regressões falharam antes e passaram depois em memória/MySQL, incluindo leitura por outra transação no instante da invalidação. Limite: não há invalidação coordenada entre workers nem prova de todas as corridas entre consulta e edição simultâneas. A reserva continua consultando o repositório atualizado.

### M02 — MÉDIO, CORRIGIDO NO PROCESSO: replay do Observer duplicava efeitos

Repetir o publicador duplicava inspeção, indicadores e e-mail; o teste antigo verificava só emissão de multa. Publicador agora registra entregas por empréstimo/ouvinte após sucesso e serializa reentregas; ouvinte que falhou pode ser tentado novamente. Testes verificam oito reentregas concorrentes e retry seletivo. **NÃO VERIFICADO como garantia durável:** registro é local ao publicador, não sobrevive reinício e não coordena workers. Não existe outbox/fila persistida para recuperar uma queda entre commit da devolução e publicação. E-mail é simulado; não há SMTP real.

### M03 — MÉDIO, ABERTO: validação e autorização têm limites

Login, CSRF, hash, SQL parametrizado, XSS básico e proteção de rotas passaram. Todos usuários autenticados possuem as mesmas operações; não há RBAC administrativo. Os atores do Trabalho 02 não são mapeados a contas. Limites `maxlength` do HTML não são integralmente repetidos no domínio; requisição manual pode ultrapassar VARCHAR e virar erro500 MySQL em vez de mensagem de validação. CPF valida formato/comprimento, não dígitos verificadores; e-mail verifica presença de @. Não trate essas validações como confirmação documental. Esses limites não foram promovidos a vulnerabilidades exploradas sem prova.

### M04 — MÉDIO, CORRIGIDO: erro estrutural SQL podia virar skip

Bootstrap de testes pulava qualquer erro MySQL. Agora apenas códigos de conectividade 2002/2003/2005 geram skip; erros SQL/permissão falham. Teste de regressão confirma que sintaxe inválida não aparece como indisponibilidade.

### L01 — BAIXO: documentação e preparação humana

Guia antigo dizia “todos passaram” sem log associado; esta auditoria fornece execução rastreável. O guia final complementa falas, perguntas e extensões e corrige a referência a `livro.grupo_id`: é coluna SQL, não atributo da entidade. Dependências têm intervalos mínimos sem lock; versões usadas estão registradas. `REGISTRO_LLM.md` existe, mas sua declaração histórica de modelo é informação da equipe, não verificada independentemente. A revisão dos quatro integrantes e o ensaio de cinco minutos ainda precisam ser realizados pela equipe.

## Arquitetura, segurança e simplicidade

Rotas chamam tratadores; cadastros usam Template Method, circulação usa Command/Facade/State, financeiro usa Strategy/Adapter. Repositórios ficam atrás de contratos e fábricas. HTML/Jinja apresentam e enviam dados; JS apenas confirma exclusão e filtra tabela. Nenhum SQL de circulação foi encontrado nas rotas. UoW abre/fecha conexão por operação e não é Singleton. A configuração é Singleton por processo; mudar política em um worker não sincroniza outros e reiniciar restaura `.env`, comportamento declarado no README.

MySQL real possui 11 tabelas InnoDB, 11 PK, 11 FK e 3 UNIQUE. IDs de comando, multa por empréstimo, boleto e quitação têm proteção de unicidade. Não há restrição específica de unicidade de empréstimo/reserva ativos: fluxo regular depende do bloqueio do Livro na fachada; escrita direta que ignore a fachada não recebe essa garantia. Consultas de valores usam parâmetros; nome de base tem validação. Schema/seed e comandos CLI foram executados pela suíte. Não existe família Oracle nem escrita em Oracle no projeto; a referência documental é somente a réplica legada.

Flask-Login verifica usuário a cada requisição; login limpa sessão, cookie HttpOnly/SameSite, Secure configurável, logout só POST, chave obrigatória e CSRF em POST. `.env` não está no índice Git nem no histórico desse caminho. Não foi feita perícia completa de todos blobs históricos. Credenciais fornecidas na conversa não foram copiadas para relatórios nem versionadas. Limitador de login e HTTPS não fazem parte desta demonstração local.

Não introduzi dependências, classes de infraestrutura desnecessárias, React, Node, servidor extra ou abstrações novas. Travas e validações adicionadas corrigem falhas reproduzidas. Manter os dois repositórios é exigência da Abstract Factory, não duplicação a eliminar. O custo de copiar todas tabelas em memória e carregar listas completas é aceitável para a demonstração, sem prova de carga de produção.

## Materiais e entregáveis

Lidos: enunciado GoF (5p), slides `01_OperacoesReeduzido.pdf` (40p), `Padroes Extensao Responsabilidade E Fabrica.pdf` (68p), Trabalho02 (10p), todos arquivos de código/testes/documentação disponíveis no projeto e exemplos Java de `src.zip`. Os exemplos são material didático, não outra implementação da biblioteca. A cópia do enunciado em Downloads é idêntica à do projeto. Graphify existente (1116 nós) auxiliou localização; conclusões foram confirmadas nos arquivos e testes, não inferidas apenas do grafo.

README, requirements, schema/seed, testes, rastreabilidade e registro LLM estão presentes. Os cinco relatórios solicitados foram gerados sem substituir os guias em `docs/`. Materiais Astah estão fora deste parecer. Não foi feita comparação remota linha a linha com IBK: registro declara apenas referência visual, sem reuso; ausência de licença/créditos de código copiado não pode ser concluída sem evidência de cópia. Confirmar origem antes de distribuir os exemplos de terceiros.

## Parecer inequívoco

Os cenários funcionais executados dos onze padrões, autenticação, MySQL e interface passaram. **O trabalho não está integralmente comprovado contra todos requisitos herdados:** B01 permanece. Fechar B01, decidir tratamento de M03, atualizar testes e repetir a auditoria antes da entrega. Astah não participa desta decisão. **NÃO ENTREGAR AINDA.**
