# Guia de defesa — Biblioteca GoF

Este guia descreve o código após as correções da auditoria de 13/11/2026. Este guia também está na raiz em `GUIA_DEFESA.md`. A base desta etapa é a cópia `fechamento-atendente`; o projeto original foi preservado. Os caminhos abaixo são relativos a essa base para facilitar a navegação durante a apresentação.

Validação do fechamento: **374 aprovados** na cópia (28,22 s) e no original (36,29 s), sem falhas, erros ou skips. Consultar `EVIDENCIAS_TESTES.md` e `AUDITORIA_FINAL.md`. Os totais da auditoria inicial descrevem o estado anterior; testes não certificam domínio oral dos integrantes.

As falas abaixo são roteiros de aproximadamente 30–45 segundos em ritmo de apresentação. Ensaiar com cronômetro e apontar o trecho real enquanto explica. Os testes nomeados existem no projeto e integram a suíte; a intenção do teste deve ser explicada, não apenas seu nome.

Fluxo geral: **formulário → rota Flask → tratador → fachada/serviço → domínio e repositórios → unidade de trabalho → comprovante**. A interface exibe e recebe dados. O banco financeiro simulado converte cobranças; o MySQL persiste dados. São responsabilidades diferentes.

Para executar um teste, no diretório do projeto com o ambiente configurado:

```bash
rtk python -m pytest -q tests/test_r01_state.py -k terceira_renovacao
```

## R01 — State

1. **O que é?** O objeto troca de comportamento trocando o objeto de estado que ele guarda.
2. **Problema na biblioteca:** o que o livro aceita (reservar, renovar, devolver…) depende da situação dele, e isso viraria `if` espalhado pelos tratadores.
3. **Onde está?** `dominio/estados.py` (`EstadoLivro` e as sete classes) e `dominio/entidades.py` (`Livro`).
4. **Como funciona?**
   1. `Livro.renovar()` só faz `self._estado.renovar(self)`.
   2. `EstadoLivro` recusa todo evento por padrão (`_recusar` lança `TransicaoInvalida`).
   3. Cada estado concreto sobrescreve apenas os eventos válidos e chama `livro.mudar_estado(...)`.
   4. A renovação (`_renovar`) testa `numRenovacoes < 2` **antes** de somar 30 dias ao vencimento.
   5. O banco guarda o nome do estado; `estado_por_nome` devolve o objeto ao ler.
5. **Teste:** `test_r01_terceira_renovacao_recusada_sem_alterar_vencimento` e `test_r01_devolvido_nao_inspecionado_nao_pode_ser_reservado`.
6. **Sem o padrão:** as decisões tenderiam a ficar em condicionais; seria preciso localizar e preservar cada regra ao adicionar estados.

### Fala de 30–45 segundos

> O Livro é o contexto do State. Ele delega cada operação ao estado atual, que aceita somente eventos válidos. Por exemplo, a renovação verifica o limite antes de acrescentar trinta dias; assim, a terceira tentativa não altera o vencimento. A devolução leva a DEVOLVIDO e só a inspeção libera o exemplar. O banco persiste o nome do estado e reconstrói o objeto correspondente. A vantagem é localizar cada regra no estado responsável, mantendo o tratador fora das decisões sobre disponibilidade.

### Três perguntas difíceis

1. **Por que a guarda vem antes da alteração da data?** Porque uma operação recusada precisa preservar o vencimento. `_renovar` verifica o limite antes da soma e da troca de estado.
2. **State e Strategy são equivalentes?** Compartilham delegação, mas State representa o ciclo de vida e suas transições; Strategy representa algoritmos selecionáveis, como a política administrativa.
3. **Onde está a garantia de que existe empréstimo para renovar?** Na coordenação da fachada e no repositório; o State verifica a transição e a contagem. Uma regra não substitui a outra.

### Extensão mínima e alcance real

Exercício curto: acrescentar um teste de evento inválido a um estado existente. Um estado novo, como EXTRAVIADO, exige classe, registro em ESTADOS, transições autorizadas, persistência compatível, operação de acesso e testes; não prometer que basta criar a classe.

## R02 — Strategy

1. **O que é?** Uma família de algoritmos trocáveis atrás do mesmo contrato.
2. **Problema:** a regra de multa muda (R$ 1/dia, teto, tolerância) e o serviço de multas não pode mudar junto.
3. **Onde está?** `dominio/multas_strategy.py`: `PoliticaMulta`, `MultaOriginal`, `MultaComTeto`, `MultaComTolerancia`, `ServicoMulta`.
4. **Como funciona?**
   1. `ServicoMulta.emitir_multa` lê o nome da política vigente na `ConfiguracaoSistema`.
   2. `politica_por_nome` devolve o objeto da política.
   3. `politica.calcular(dias_atraso)` devolve o valor em `Decimal`.
   4. A multa é gravada com o valor e o nome da política; nunca é recalculada.
5. **Teste:** `test_r02_cinco_dias_de_atraso_custam_5_na_original_e_3_na_tolerancia`, `test_r02_trocar_a_politica_nao_recalcula_multa_ja_emitida`.
6. **Sem o padrão:** um `if politica == ...` dentro do serviço, alterado a cada regra nova.

### Fala de 30–45 segundos

> A Strategy separa a fórmula da multa do serviço que registra e cobra. Temos três políticas: um real por dia, teto de vinte reais e tolerância dos dois primeiros dias. Com cinco dias de atraso, a original retorna cinco reais e a tolerância retorna três. A seleção administrativa determina qual objeto calcula, mas o valor e a política são gravados na emissão. Uma troca posterior não recalcula multas antigas. Para acrescentar outra fórmula, criamos uma classe, registramos sua opção e testamos o cálculo, sem alterar o serviço.

### Três perguntas difíceis

1. **A multa antiga muda quando o administrador troca a política?** Não: valor e nome da política ficam registrados na multa. A troca afeta novas emissões.
2. **Por que usar Decimal?** Para representar valores decimais monetários sem o arredondamento binário de float; as políticas quantizam em centavos.
3. **Uma política nova exige mudar o serviço?** Não. Exige a classe e seu registro em POLITICAS. O ponto de montagem muda, mas ServicoMulta continua chamando o contrato calcular.

### Extensão mínima e alcance real

Criar MultaEmDobro, registrá-la em POLITICAS e testar zero e cinco dias, mantendo ServicoMulta intacto. Exemplo executável ao final.

## R03 — Adapter

1. **O que é?** Uma classe que traduz a interface que temos para a interface que o cliente espera.
2. **Problema:** o banco A fala centavos inteiros e o banco B fala reais decimais, com campos e situações diferentes.
3. **Onde está?** `dominio/bancos_adapter.py`: `CobrancaInstitucional` (alvo), `BancoA`/`BancoB` (simulados), `AdaptadorBancoA`/`AdaptadorBancoB`.
4. **Como funciona?**
   1. `ServicoMulta` chama `cobranca.emitir_boleto(SolicitacaoCobranca(...))` sem saber qual banco é.
   2. `AdaptadorBancoA` converte R$ 7,00 em `700` e chama `BancoA.criar_cobranca`.
   3. `AdaptadorBancoB` envia `7.00`, CPF com máscara, e chama `BancoB.emitir_titulo`.
   4. `traduzir_notificacao` converte o aviso de pagamento de cada banco em `PagamentoConfirmado`.
   5. `registrar_quitacao` grava o id da notificação em chave única: repetição não quita de novo.
5. **Teste:** `test_r03_a_mesma_solicitacao_de_7_reais_vira_700_centavos_no_banco_a_e_7_00_no_banco_b`, `test_r03_notificacao_repetida_nao_gera_segunda_quitacao`.
6. **Sem o padrão:** `if banco == "A"` dentro do serviço de multas, com conversões misturadas à regra.


**Correção de concorrência:** `ServicoMulta.emitir_boleto` lê a multa com `para_atualizar=True` e mantém a transação até registrar o boleto retornado pelo banco simulado. A chamada externa real precisaria de idempotência por referência e recuperação após queda.

### Fala de 30–45 segundos

> O Adapter traduz o contrato de cobrança da biblioteca para duas APIs incompatíveis. O banco A recebe centavos inteiros, enquanto o B recebe reais e outros nomes de campos. Uma cobrança de sete reais vira setecentos centavos no A e sete reais no B. As notificações também voltam traduzidas. O serviço não pergunta qual banco está usando. A quitação repetida é barrada por restrições persistidas. Esses bancos são simuladores financeiros; o MySQL é outro assunto, responsável por armazenar os dados da biblioteca.

### Três perguntas difíceis

1. **Adapter garante idempotência sozinho?** Não. Ele traduz formatos. O serviço e a persistência garantem quitação única; a emissão concorrente bloqueia a multa antes de consultar/gravar o boleto.
2. **Por que o banco simulado é chamado dentro da transação?** A correção mantém a trava da multa até a gravação, evitando duas cobranças concorrentes. Uma API real exigiria referência idempotente e recuperação de falhas externas.
3. **Se o banco cobrar e o processo morrer antes do commit, o rollback cancela a cobrança?** Não. Uma transação MySQL não desfaz um efeito externo. O simulador não representa uma garantia distribuída; esse é um limite explícito.

### Extensão mínima e alcance real

Criar AdaptadorBancoC somente após definir a API simulada e o mapeamento de valor/documento/status/notificação; registrar em criar_cobranca e executar os testes do contrato. A seleção é o ponto de montagem, não uma condicional no serviço.

## R04 — Facade

1. **O que é?** Uma porta única e simples para um conjunto de classes que trabalham juntas.
2. **Problema:** emprestar um livro mexe em reserva, empréstimo e livro; se a interface fizesse isso, poderia deixar pela metade.
3. **Onde está?** `dominio/circulacao_facade.py`, classe `CirculacaoFacade`.
4. **Como funciona (`emprestar`)?**
   1. Abre uma unidade de trabalho (uma transação).
   2. Valida a reserva ativa do mesmo estudante em `Movimentacao`.
   3. Remove a reserva, chama `livro.emprestar`, insere o empréstimo, atualiza o livro no `Acervo`.
   4. Devolve um `Comprovante` (objeto imutável), nunca listas.
   5. Qualquer erro no meio faz rollback de tudo.
5. **Teste:** `test_r04_emprestimo_valida_reserva_remove_reserva_cria_emprestimo_e_atualiza_livro`, `test_r04_falha_no_meio_do_emprestimo_desfaz_tudo`.
6. **Sem o padrão:** as rotas chamariam `Movimentacao` e `Acervo` direto, sem transação única.

### Fala de 30–45 segundos

> A fachada reúne os passos necessários para concluir uma operação de circulação. No empréstimo, ela consulta o livro e a reserva do mesmo estudante, valida o atendente cadastrado de Pessoa distinta, encerra a reserva, cria o empréstimo e atualiza o livro. Todos esses passos usam a mesma unidade de trabalho. Se a gravação do empréstimo falha, o rollback restaura a reserva e o estado anterior. O tratador recebe um comprovante, sem precisar manipular coleções internas. A fachada coordena o processo; o State continua responsável por decidir quais eventos o livro aceita.

### Três perguntas difíceis

1. **Quais passos o rollback desfaz no empréstimo?** O encerramento da reserva, a inclusão do empréstimo e a atualização do livro, porque compartilham a unidade de trabalho.
2. **A fachada absorve todas as regras?** Não. Coordena subsistemas e valida vínculos; estados e políticas continuam responsáveis pelas regras específicas.
3. **Quem registra o atendente responsável pela transação?** O operador seleciona o atendente cadastrado; `CirculacaoFacade._validar_participantes` confere que seu CPF difere do estudante. Reserva, empréstimo e devolução preservam seus responsáveis separadamente. O login é autor da solicitação, não substituto desse vínculo.

### Extensão mínima e alcance real

Adicionar uma operação de fachada apenas se sua regra estiver definida. Para cancelar reserva, seriam necessários evento State, atualização da reserva/livro, método de tratador e testes transacionais; não é uma extensão de dois métodos pronta por definição.

## R05 — Observer

1. **O que é?** Um publicador avisa uma lista de ouvintes quando algo acontece, sem conhecê-los.
2. **Problema:** a devolução dispara inspeção, multa, indicadores e e-mail; a fachada não deve conhecer cada reação.
3. **Onde está?** `dominio/devolucao_observer.py`: `PublicadorDevolucao`, `OuvinteDevolucao`, os quatro ouvintes e `EventoDevolucao`.
4. **Como funciona?**
   1. `CirculacaoFacade.devolver` grava a devolução e faz commit.
   2. Depois do commit, chama `publicador.publicar(evento)`.
   3. O publicador chama `notificar(evento)` em cada ouvinte, dentro de `try/except`.
   4. Se um falhar, registra em `falhas` e segue para o próximo.
   5. O livro continua DEVOLVIDO: `OuvinteInspecao` só põe na fila.
5. **Teste:** `test_r05_devolucao_atrasada_alimenta_inspecao_multa_e_indicadores`, `test_r05_falha_do_email_nao_afeta_os_demais_nem_desfaz_a_devolucao`.
6. **Sem o padrão:** a fachada chamaria multa, e-mail e indicadores um a um; o isolamento de falhas teria de ser implementado nessa coordenação; a ausência do padrão, por si só, não implica falha inevitável.


**Correção e limite atual:** `PublicadorDevolucao.publicar` usa uma trava e registra `(emprestimo_id, índice_do_ouvinte)` somente após sucesso. Republicação local evita repetir os ouvintes concluídos. Essa estrutura não sobrevive ao reinício nem coordena workers; e-mail e indicadores permanecem simulados/em memória.

### Fala de 30–45 segundos

> A devolução produz um evento imutável com estudante, vencimento e data de devolução. A fachada só o publica depois do commit. Inspeção, multa, indicadores e e-mail são ouvintes independentes, então a falha de um não desfaz a devolução nem impede os demais. A correção da auditoria registra entregas bem-sucedidas por empréstimo e ouvinte no processo, evitando repetir efeitos numa republicação local. Isso não é uma fila durável: reinícios e falhas externas exigiriam persistência e tratamento adicional. O livro continua DEVOLVIDO até a inspeção explícita.

### Três perguntas difíceis

1. **Quando um ouvinte falha, os demais são chamados?** Sim. O publicador captura a falha por ouvinte e continua; a devolução já estava confirmada.
2. **Republicar o evento sempre é seguro depois de reiniciar?** Não. O controle de entregas é local ao publicador/processo. Multa/quitação têm restrições no banco, mas fila, indicadores e e-mail não têm replay durável completo.
3. **E se um ouvinte fizer um efeito e depois lançar exceção?** Ele não é marcado como concluído e pode ser chamado novamente. O próprio efeito externo precisaria de idempotência; não prometemos exatamente uma vez para qualquer ouvinte.

### Extensão mínima e alcance real

Criar OuvinteAuditoria que registra no log e adicioná-lo à montagem, com teste da entrega. Não alterar CirculacaoFacade nem TratadorDeDevolucao. Especificar que log não é uma trilha durável de auditoria.

## R06 — Command

1. **O que é?** Um pedido vira um objeto, com dados próprios e um método `executar`.
2. **Problema:** o usuário clica duas vezes ou o navegador reenvia; a mesma renovação não pode valer duas vezes.
3. **Onde está?** `dominio/circulacao_command.py`: `Comando`, `ComandoReserva`, `ComandoRenovacao`, `ExecutorComandos`.
4. **Como funciona?**
   1. A tela envia o `id_solicitacao` (UUID criado junto com o formulário).
   2. `TratadorDeEmprestimo` cria o comando (id, autor, instante) e entrega ao `ExecutorComandos`.
   3. O executor tenta gravar o id (chave única) na mesma transação do efeito.
   4. Id novo: chama `comando.executar(uow)`, que chama a fachada, e guarda o comprovante.
   5. Id repetido: devolve o comprovante guardado, sem executar.
5. **Teste:** `test_r06_renovacao_executada_duas_vezes_com_o_mesmo_identificador_acrescenta_apenas_30_dias`, `test_r06_submissoes_simultaneas_do_mesmo_identificador_executam_uma_unica_vez`.
6. **Sem o padrão:** o pedido não teria uma representação própria; ainda seria possível implementar idempotência separadamente, mas ela não surgiria automaticamente.

### Fala de 30–45 segundos

> O Command transforma a reserva ou renovação em um objeto com identificador, autor e instante. O tratador cria o comando e o executor registra seu identificador antes de executar. Registro, efeito e comprovante pertencem à mesma transação. Se o mesmo identificador chegar novamente, o executor devolve o comprovante original. A renovação acrescenta trinta dias uma única vez. Identificadores diferentes ainda passam pelo limite de duas renovações do State. No MySQL a chave única coordena processos; um conjunto Python sozinho não resolveria essa concorrência.

### Três perguntas difíceis

1. **Como dois processos evitam renovar duas vezes?** A chave única do identificador e a transação MySQL coordenam as execuções; o efeito e o resultado são gravados juntos. A auditoria incluiu quatro processos concorrentes.
2. **Por que não há undo?** Reserva e renovação não possuem cancelamento previsto no fluxo implementado. Desfazer exigiria regras compensatórias, estado e persistência, e não apenas inverter uma soma.
3. **O UUID autentica quem pode executar o comando?** Não. É uma chave de idempotência, não credencial. A autenticação fica na camada web; não apresentar UUID como autorização nem prova da identidade do estudante.

### Extensão mínima e alcance real

Adicionar um tipo de comando para uma operação já definida exige subclasse, criação no tratador e testes de repetição/falha. ComandoDevolucao exige cuidado adicional com publicação pós-commit e não é troca direta da chamada atual.

## R07 — Template Method

1. **O que é?** A classe-mãe fixa a ordem do algoritmo; as filhas só preenchem os passos.
2. **Problema:** os quatro cadastros seguem a mesma rotina e não podem pular validação nem pré-requisito.
3. **Onde está?** `dominio/cadastros_template.py`: `CadastroBase.incluir`, `CadastroPessoa`, `CadastroLivro`, `_CadastroPapel`, `CadastroEstudante` e `CadastroAtendente`.
4. **Como funciona?**
   1. `incluir` abre a transação e chama, nesta ordem: buscar existente, validar, verificar pré-requisitos, criar, armazenar, apresentar.
   2. Se já existe, devolve o existente (`ja_existia=True`) e para.
   3. `_verificar_pre_requisitos` é um **gancho**: vazio na base; Estudante e Atendente exigem a Pessoa.
   4. Se o pré-requisito falha, o erro vem antes de `_armazenar`: nada é gravado.
   5. `__init_subclass__` recusa subclasse que tente redefinir `incluir`.
5. **Teste:** `test_r07_estudante_duplicado_retorna_o_cadastro_existente`, `test_r07_estudante_com_cpf_nao_cadastrado_falha_antes_de_qualquer_gravacao`.
6. **Sem o padrão:** quatro rotinas copiadas, cada uma podendo esquecer um passo.

### Fala de 30–45 segundos

> O Template Method centraliza a inclusão dos quatro cadastros. CadastroBase fixa a ordem: buscar existente, validar, verificar pré-requisitos, criar, armazenar e apresentar. As subclasses implementam os passos próprios. Um estudante duplicado retorna o existente; um estudante novo sem Pessoa cadastrada falha antes de qualquer gravação. A transação também protege contra falhas posteriores. Em Python, o projeto usa init_subclass para recusar subclasses que redefinam incluir. É uma proteção explícita do desenho, não uma promessa de impedir qualquer alteração dinâmica possível na linguagem.

### Três perguntas difíceis

1. **O estudante duplicado ainda precisa passar por criação?** Não. A busca retorna o cadastro existente e encerra a inclusão sem gravar novamente.
2. **Qual é o gancho?** `_verificar_pre_requisitos` tem implementação padrão; `_CadastroPapel` exige Pessoa para Estudante e Atendente. `_apresentar` também pode especializar a apresentação.
3. **A proteção equivale a final em uma linguagem estática?** Não. `__init_subclass__` barra sobrescrita ao definir subclasses normais e tem teste. Não impede toda manipulação dinâmica de classes Python.

### Extensão mínima e alcance real

Para um novo cadastro persistido, criar entidade, validações, repositórios nas duas famílias e armazenamento, além da subclasse e testes. Exercício mínimo seguro: especializar _apresentar em subclasse de teste e comprovar que a ordem de incluir continua fixa.

## R08 — Abstract Factory

1. **O que é?** Uma fábrica que cria uma família inteira de objetos que combinam entre si.
2. **Problema:** os testes usam memória e a produção usa MySQL; misturar um repositório de cada quebraria a transação.
3. **Onde está?** `dominio/persistencia_factory.py` (`FabricaPersistencia`, `FabricaMemoria`, `FabricaMySQL`), contratos em `dominio/pontos_acesso.py`, produtos em `persistencia/`.
4. **Como funciona?**
   1. `app.py` chama `criar_fabrica(perfil)` uma única vez.
   2. O domínio pede `fabrica.criar_unidade_trabalho()` e `fabrica.criar_acervo(uow)` etc.
   3. Na família MySQL, todos os repositórios recebem a conexão da mesma unidade de trabalho.
   4. Cada repositório confere o tipo da unidade no construtor e recusa a de outra família.
5. **Teste:** `test_r08_perfil_de_teste_fornece_apenas_objetos_em_memoria`, `test_r08_perfil_de_producao_fornece_repositorios_mysql_na_mesma_unidade_de_trabalho`.
6. **Sem o padrão:** o domínio faria `if perfil == "mysql"` a cada acesso e poderia misturar famílias.

### Fala de 30–45 segundos

> A Abstract Factory cria famílias compatíveis de acesso aos dados. A aplicação escolhe uma fábrica ao iniciar: memória ou MySQL. Depois, os serviços pedem unidade de trabalho e repositórios por contratos comuns, sem decidir a tecnologia em cada operação. Na família MySQL, Acervo, Movimentacao, Relacionamento e Financeiro recebem a mesma unidade de trabalho daquela operação, compartilhando sua conexão e transação. Os construtores recusam unidades de outra família. A fábrica não é a conexão e não substitui commit ou rollback; ela garante a montagem coerente das peças.

### Três perguntas difíceis

1. **Fábrica e Singleton fazem a mesma coisa?** Não. A fábrica entrega uma família compatível; Singleton controla a identidade da configuração. Cada operação cria sua própria unidade de trabalho.
2. **Por que todos os repositórios recebem a mesma unidade?** Para que a operação tenha uma única fronteira commit/rollback. Conexões independentes poderiam confirmar partes separadamente.
3. **Como adicionar SQLite?** Implementar unidade de trabalho e todos produtos da família, a fábrica e a seleção de perfil, além de testes de contratos, integridade e transação. Não é só acrescentar um if.

### Extensão mínima e alcance real

Exercício mínimo: adicionar teste de rejeição de família misturada. Uma nova família completa envolve todos os repositórios, UoW, esquema quando aplicável, seleção e testes; não há extensão de uma linha.

## R09 — Decorator

1. **O que é?** Um objeto embrulha outro do mesmo contrato e acrescenta comportamento.
2. **Problema:** cache e medição da consulta são opcionais e combináveis; a consulta original não deve mudar.
3. **Onde está?** `dominio/consulta_decorator.py`: `ConsultaAcervo`, `ConsultaBase`, `DecoradorConsulta`, `ConsultaComCache`, `ConsultaComMedicao`.
4. **Como funciona?**
   1. `montar_sistema` cria `ConsultaComMedicao(ConsultaComCache(ConsultaBase(fabrica)))`.
   2. A medição conta e repassa ao cache; o cache responde ou repassa à base.
   3. O cache guarda só `MetadadosLivro` (id e título): não tem estado do livro.
   4. Se o cache der erro, a consulta original responde.
   5. A reserva (`CirculacaoFacade.reservar`) lê o livro no repositório, nunca na consulta.
5. **Teste:** `test_r09_segunda_consulta_usa_cache_e_ainda_gera_medicao`, `test_r09_resultado_antigo_do_cache_nunca_autoriza_reserva`.
6. **Sem o padrão:** cache e medição dentro da consulta, sempre ligados, ou uma subclasse para cada combinação.

**Correção de cache:** `TratadorDeAcervo.atualizar/excluir` chama `invalidar` depois do commit. A cadeia de decoradores encaminha a invalidação. Falha de remoção descarta a cópia local. Os seis casos de `tests/test_auditoria_cache.py` comprovam atualização/exclusão e tolerância a falhas em memória/MySQL. Outros workers não são sincronizados por esse cache local.

### Fala de 30–45 segundos

> O Decorator adiciona recursos à consulta sem modificar sua implementação base. A composição usada é medição por fora, cache por dentro e consulta base no centro. Por isso, a segunda consulta pode vir do cache e ainda assim incrementar a medição. O cache guarda somente identificador e título, não a disponibilidade. Ao reservar, a fachada consulta o estado atual no repositório. Se o cache falhar, a consulta volta à base. Isso permite combinar recursos pelo mesmo contrato sem confundir metadados antigos com autorização de negócio.

### Três perguntas difíceis

1. **O que acontece se inverter cache e medição?** Um acerto no cache externo pode retornar antes de chamar a medição. A ordem atual mede também cache hits.
2. **O cache desatualizado pode permitir reservar livro emprestado?** Não: ele guarda metadados, e reservar lê o estado atual pelo Acervo na transação da fachada.
3. **Decorator aqui é o mesmo que @decorator de Python?** Não. É composição de objetos do mesmo contrato. A sintaxe @ pode aplicar outras transformações e não define o padrão GoF por si só.

### Extensão mínima e alcance real

Adicionar ConsultaComLog como DecoradorConsulta, delegar uma única vez ao componente e testar o retorno e a chamada. Compor no ponto de montagem; preservar a medição externa para que continue cobrindo o cache.

## R10 — Composite

1. **O que é?** Uma árvore em que o grupo e o item respondem às mesmas operações.
2. **Problema:** o acervo tem unidades, seções e subseções em profundidade variável, e é preciso contar e listar em qualquer nível.
3. **Onde está?** `dominio/acervo_composite.py`: `ComponenteAcervo`, `GrupoAcervo`, `ItemLivro`, `mover`, `montar_arvore`.
4. **Como funciona?**
   1. `ItemLivro.contar_livros()` devolve 1; `GrupoAcervo.contar_livros()` soma os filhos.
   2. `adicionar` recusa ciclo (o grupo ou um ancestral dele) e livro que já está na árvore.
   3. `ItemLivro` guarda só o id do livro.
   4. `TratadorDeAcervo.mover_livro` valida no Composite e chama `Acervo.definir_grupo`; no MySQL, só a coluna `livro.grupo_id` muda. O objeto Python `Livro` não tem esse atributo.
5. **Teste:** `test_r10_unidade_com_secoes_de_tres_e_dois_livros_informa_cinco`, `test_r10_mover_livro_nao_altera_id_estado_nem_emprestimo`.
6. **Sem o padrão:** código diferente para unidade, seção e subseção, e um limite fixo de níveis.

### Fala de 30–45 segundos

> O Composite representa o acervo como uma árvore. GrupoAcervo contém grupos ou itens, e todos respondem a contar e listar livros. Um item representa um livro pelo identificador; um grupo soma os resultados dos filhos. Assim, duas seções com três e dois livros totalizam cinco, sem limite fixo de níveis. A inserção recusa ciclos e duplicidades na árvore. Ao mover um livro, o tratador valida a estrutura e atualiza apenas seu grupo na persistência. O identificador, o estado e o empréstimo do livro permanecem iguais.

### Três perguntas difíceis

1. **Como o ciclo é detectado?** A inserção verifica se o componente é o próprio grupo ou um ancestral; aceitar isso causaria recursão infinita.
2. **A proteção em uma árvore garante unicidade em qualquer processo?** Não sozinha. A árvore verifica o contexto montado; o banco usa um único grupo_id por livro. São níveis diferentes de proteção.
3. **Mover altera o atributo grupo_id do objeto Livro?** O objeto Livro não possui esse atributo. O tratador chama Acervo.definir_grupo; no MySQL altera a coluna livro.grupo_id, preservando os dados de circulação.

### Extensão mínima e alcance real

Exercício curto: montar mais uma subseção com GrupoAcervo e verificar contagem/listagem, sem mudar classes. Nova operação do contrato, como listar_grupos, exige definir comportamento em grupo e folha e testar ambos.

## R11 — Singleton

1. **O que é?** Uma classe com uma única instância e um ponto de acesso global a ela.
2. **Problema:** duas configurações independentes poderiam dizer políticas de multa diferentes na mesma execução.
3. **Onde está?** `dominio/configuracao_singleton.py`, `ConfiguracaoSistema.obter_instancia()`.
4. **Como funciona?**
   1. O construtor exige uma chave interna; chamar `ConfiguracaoSistema()` direto dá `TypeError`.
   2. `obter_instancia` cria o objeto na primeira chamada, protegido por uma trava de threads.
   3. Nas chamadas seguintes devolve o mesmo objeto.
   4. O ambiente (`.env`) é lido uma única vez, na criação.
5. **Teste:** `test_r11_obter_instancia_devolve_sempre_o_mesmo_objeto`, `test_r11_threads_simultaneas_recebem_a_mesma_instancia`.
6. **Sem o padrão:** cada parte criaria a sua configuração e a troca de política valeria só para uma delas.
7. **Limites e diferença:** é uma instância por processo (cada worker tem a sua). Não guarda conexão de banco. A Abstract Factory decide **quais** objetos criar (famílias compatíveis); o Singleton decide **quantas** instâncias existem.

### Fala de 30–45 segundos

> O Singleton controla o acesso à configuração da execução. A primeira chamada a obter_instancia cria o objeto sob uma trava; as seguintes devolvem exatamente a mesma referência. O construtor direto é protegido por uma chave interna. O teste compara os objetos com is, inclusive sob acesso simultâneo de threads. A instância é única somente dentro do processo: outros workers têm suas próprias configurações. Não usamos Singleton para conexão MySQL, pois isso misturaria transações. Abstract Factory escolhe famílias de objetos; Singleton controla a quantidade de instâncias de uma classe.

### Três perguntas difíceis

1. **A instância é única em toda a instalação com vários workers?** Não, somente no processo. Cada worker tem sua própria instância; configuração dinâmica compartilhada exigiria armazenamento e sincronização externos.
2. **Por que a conexão não é Singleton?** Porque requisições/operações simultâneas precisam de transações independentes. Cada UoW MySQL abre e fecha a conexão da operação.
3. **Como os testes evitam vazamento de configuração?** Usam o mecanismo explícito de reinicialização para testes e fixtures. Esse recurso não deve ser usado durante uma operação de produção.

### Extensão mínima e alcance real

Exercício mínimo: ampliar o teste de leitura única do ambiente ou de identidade entre pontos de acesso. Novo parâmetro exige leitura inicial, consumidor e teste; configuração compartilhada entre processos exige outra solução, não outro atributo.

## Demonstração em cinco minutos

Preparar antes: MySQL acessível, ambiente e chave de sessão configurados, usuário criado com senha própria, dados de demonstração conhecidos e política `original`. Confirmar que o livro escolhido está LIVRE; executar seed não deve ser tratado como reset automático de uma demonstração já usada. Usar base de teste distinta da base da demonstração.

| Tempo | Ação | Resultado que deve ser apontado |
|---|---|---|
| 0:00–0:40 | Executar `rtk python -m pytest -q` no projeto | Resultado atual real; verificar também skips. Conferir o conjunto de testes e o total integrado no relatório final. |
| 0:40–1:00 | Entrar na interface e selecionar estudante/livro da demonstração | Login válido, estudante cadastrado e livro LIVRE. |
| 1:00–1:25 | Reservar e efetivar empréstimo para o mesmo estudante, selecionando atendente válido em cada formulário | RESERVADO → EMPRESTADO; reserva ativa encerrada. |
| 1:25–2:05 | Renovar duas vezes e tentar uma terceira | Vencimento +30 em cada sucesso; terceira recusa sem alterar data. |
| 2:05–2:40 | Devolver com atendente selecionado e data controlada igual ao vencimento +5 dias | DEVOLVIDO e multa de R$5 na política original. |
| 2:40–3:10 | Mostrar multa/boleto e simular pagamento repetido | Uma quitação; repetição não cria outro pagamento. |
| 3:10–3:35 | Tentar reservar antes de inspecionar; depois inspecionar bom estado | Recusa em DEVOLVIDO e retorno a LIVRE após inspeção. |
| 3:35–4:00 | Consultar metadados duas vezes e mostrar árvore | Cache atendendo e medição aumentando; contagem recursiva. |
| 4:00–5:00 | Apontar State, fronteira transacional e uma extensão preparada | Explicar guarda, rollback e ponto de montagem da nova política/ouvinte. |

A ordem e o tempo da arguição são definidos pelo professor. Se os testes excederem a janela ensaiada, ajustar a demonstração previamente; não substituir execução por alegação de que passou antes. Se o MySQL estiver indisponível, declarar a limitação e não apresentar testes pulados como integração aprovada.

## Exercício ao vivo A — nova política de multa

Alteração proposta para ensaio, **não aplicada por este guia**. Em `dominio/multas_strategy.py`, acrescentar a classe abaixo e incluir `MultaEmDobro()` na tupla que forma `POLITICAS`:

```python
class MultaEmDobro(PoliticaMulta):
    """R$ 2,00 por dia de atraso, usando o contrato das políticas existentes."""

    nome = "dobro"

    def calcular(self, dias_atraso):
        return (2 * VALOR_POR_DIA * dias_atraso).quantize(CENTAVO)
```

Acrescentar um teste pequeno em `tests/test_r02_strategy.py` (ajustando o import):

```python
def test_r02_politica_em_dobro_calcula_zero_e_cinco_dias():
    assert MultaEmDobro().calcular(0) == Decimal("0.00")
    assert MultaEmDobro().calcular(5) == Decimal("10.00")
```

Executar `rtk python -m pytest -q tests/test_r02_strategy.py`. A tela usa as políticas registradas; selecionar `dobro` e emitir uma multa nova. Explicar que uma multa anterior permanece com seu valor e política. O serviço de emissão não foi modificado; o registro da instalação foi estendido. Os valores de entrada seguem o contrato existente de dias não negativos, calculados pelo evento.

## Exercício ao vivo B — novo ouvinte

Alteração proposta para ensaio. Em `dominio/devolucao_observer.py`:

```python
class OuvinteAuditoria(OuvinteDevolucao):
    """Registra a devolução no log da demonstração."""

    def notificar(self, evento):
        registro.info("Auditoria: livro %s devolvido por %s",
                      evento.livro_id, evento.estudante_id)
```

Registrar `OuvinteAuditoria()` na lista de montagem em `dominio/tratadores.py`, incluindo o import correspondente. Criar teste que registre o ouvinte em um `PublicadorDevolucao`, publique um `EventoDevolucao` válido, capture o log e confira livro e estudante; republicar o mesmo evento no mesmo publicador e conferir uma única mensagem. Executar `rtk python -m pytest -q tests/test_r05_observer.py`.

O exemplo adiciona um consumidor sem alterar a fachada ou o tratador de devolução. Não chamar isso de auditoria financeira durável: o log e a deduplicação local não garantem recuperação após reinício. Uma fila persistida ou integração externa exige outro escopo e testes de falha próprios.

## O que os quatro integrantes precisam dominar

Cada integrante deve conseguir percorrer todos os onze padrões, não apenas uma divisão por arquivos. Fazer rodízio entre quatro tarefas de ensaio: explicar o fluxo no navegador, localizar classes e métodos, executar e interpretar um teste, e responder uma pergunta sobre falha ou extensão. A cada rodada, trocar essas tarefas para que todos atravessem todo o sistema.

| Verificação individual | Integrante 1 | Integrante 2 | Integrante 3 | Integrante 4 |
|---|---|---|---|---|
| Explica cada um dos onze padrões sem leitura literal | A verificar | A verificar | A verificar | A verificar |
| Localiza guarda, transação e publicação pós-commit | A verificar | A verificar | A verificar | A verificar |
| Explica teste negativo e idempotência concorrente | A verificar | A verificar | A verificar | A verificar |
| Executa fluxo completo e interpreta erros | A verificar | A verificar | A verificar | A verificar |
| Faz extensão pequena e executa teste correspondente | A verificar | A verificar | A verificar | A verificar |
| Explica as limitações abaixo | A verificar | A verificar | A verificar | A verificar |

## Limitações que devem ser explicadas com precisão

- **Atendente na transação:** implementado nesta etapa por seleção explícita e validação no servidor. O histórico legado sem responsável conhecido permanece NULL; o sistema não inventa identidades nem vincula automaticamente login ao papel. Migrar a base antes de iniciar a versão nova.
- **Observer:** a deduplicação é por ouvinte e empréstimo dentro do processo. Não há entrega/replay durável completo após reinício; a devolução confirmada pode existir sem todos os efeitos se o processo cair antes de publicar.
- **Banco financeiro simulado:** o bloqueio da multa evita emissão concorrente no cenário atual. Uma API financeira real tem efeitos externos que o rollback MySQL não desfaz; exigiria idempotência e reconciliação próprias.
- **Configuração:** Singleton não sincroniza workers; troca de política em um processo não é configuração global persistente. O prazo inicial de 30 dias é uma decisão documentada da equipe, enquanto +30 por renovação é regra expressa.
- **Prova humana:** os testes e este guia ajudam a estudar, mas não demonstram que alguém consegue defender o código. O ensaio e a revisão dos quatro integrantes ainda precisam ser realizados e registrados.

## Responsáveis pelas transações

Reserva, empréstimo e devolução exigem a seleção explícita de um atendente cadastrado na tela Circulação. A Pessoa do atendente deve ter CPF diferente da Pessoa do estudante; comparar apenas os IDs dos papéis não basta. A fachada valida os participantes no servidor, dentro da unidade de trabalho, antes de gravar os efeitos. O comprovante mostra o responsável escolhido.

Os responsáveis podem ser diferentes em cada etapa: `reserva.atendente_id`, `emprestimo.atendente_id` e `emprestimo.atendente_devolucao_id` são preservados separadamente. Encerrar a reserva mantém seu histórico. Papéis referenciados por movimentações não podem ser excluídos nem ter seu CPF trocado, evitando alterar silenciosamente a identidade histórica. Isso não impede editar dados permitidos da Pessoa ou manter o mesmo CPF.

O `autor` do Command continua sendo o login de quem enviou a solicitação; `atendente_id` identifica o responsável de domínio escolhido. Não há associação automática entre login e papel, nem novo sistema de permissões por perfil. A seleção é uma declaração do operador autenticado, validada contra os cadastros; não comprova por si só quem está fisicamente operando o balcão. Renovar mantém o responsável do empréstimo e não exige um novo atendente.

## Atualização de banco existente

Antes de iniciar esta versão, faça backup e pare a versão anterior. Com o ambiente apontando para a base correta, execute **um único migrador por vez**, sem instâncias concorrentes da aplicação gravando:

```bash
flask --app app migrar-db
```

Para uma instalação nova, `flask --app app init-db` cria o schema e aplica a mesma migração aditiva. A migração consulta o catálogo, acrescenta as três colunas de responsáveis e suas chaves estrangeiras quando faltam, e pode ser repetida. Registros legados permanecem com responsável `NULL` quando desconhecido: não se atribui A1 nem outro atendente por suposição. Novas operações são obrigadas pelo domínio a informar um responsável válido; `NULL` existe para compatibilidade histórica, não como opção de novo formulário.

DDL MySQL tem commit implícito: não há promessa de rollback integral de schema. Se ocorrer falha parcial, corrija a causa e execute novamente o migrador, que retoma pelo catálogo. Não execute duas migrações em paralelo. Para recuar operacionalmente, mantenha colunas e dados novos e volte o código anterior; não faça DROP. Enquanto a versão anterior estiver ativa, ela poderá gravar responsáveis ausentes, por isso não misture as versões durante a transição.

## Validação do fechamento

Total final da suíte: **374 aprovados**, zero falhas/erros/skips: 28,22 s na cópia de fechamento e 36,29 s no original após aplicação. O parecer **APTO — PODE ENTREGAR** refere-se ao escopo acadêmico auditado, com Astah excluído. Evidências em `AUDITORIA_FINAL.md`, `EVIDENCIAS_TESTES.md` e `evidencias_fechamento/`. Os resultados da auditoria inicial pertencem ao estado anterior e foram preservados como histórico; a suíte não certifica domínio oral dos integrantes.

Os limites de tamanho dos campos são validados também no backend, com erros de domínio e mensagens para o usuário; os atributos HTML apenas auxiliam o preenchimento. Não há nova regra exclusiva de frontend nem novo RBAC. A cobertura adicional está em `tests/test_atendente_transacoes.py`, `tests/test_persistencia_atendente.py` e `tests/test_migracao_atendente.py`.

## Perguntas adicionais do fechamento

1. **Por que o ID do atendente não basta para provar que é outra Pessoa?** Estudante e Atendente têm IDs de papel diferentes e ainda podem apontar ao mesmo CPF; a regra compara as Pessoas dentro da transação.
2. **Se A1 reservou, A2 emprestou e A3 recebeu, quem fica registrado?** Os três: a reserva inativa conserva A1, o empréstimo conserva A2 e o campo de responsável da devolução registra A3.
3. **Por que impedir trocar o CPF de um papel com histórico?** Porque as transações referenciam esse papel; trocar sua Pessoa mudaria retrospectivamente quem participou delas.
4. **O que ocorre com comprovante JSON anterior sem atendente?** O campo opcional mantém a leitura compatível, sem atribuir responsável inexistente. Novos comprovantes das três operações incluem o atendente.
5. **A migração corrige dados legados desconhecidos?** Não. Ela conserva NULL e deixa explícito o desconhecimento; uma investigação ou correção documental posterior seria outro procedimento.

Testes para abrir durante a defesa: `test_atendente_invalido_recusa_sem_mudar_livro`, `test_responsavel_de_cada_operacao_nao_sobrescreve_o_anterior`, `test_reserva_sem_atendente_faz_rollback_do_command_e_permite_corrigir`, `test_rollback_preserva_reserva_e_responsavel`, `test_papel_usado_nao_pode_trocar_pessoa` e `test_migracao_preserva_legado_e_pode_ser_repetida`.
