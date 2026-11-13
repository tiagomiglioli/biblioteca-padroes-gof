# Guia de defesa — uma ficha por padrão

Cada ficha responde às mesmas sete perguntas. Todos os integrantes devem conseguir abrir
o arquivo indicado, apontar as classes e rodar o teste.

Para rodar o teste de uma ficha: `python -m pytest -q tests/<arquivo> -k <nome_do_teste>`.
Na última execução completa (`python -m pytest -q`), todos os testes citados aqui passaram.

---

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
6. **Sem o padrão:** cada tratador testaria o estado com `if/elif`; um estado novo exigiria alterar todos.
7. **Mudança ao vivo:** novo estado `EXTRAVIADO` — criar a classe, incluí-la em `ESTADOS` e criar a transição no estado de origem.

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
7. **Mudança ao vivo:** nova política (ver `docs/DEMO_5_MINUTOS.md`): uma classe e uma entrada em `POLITICAS`.

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
7. **Mudança ao vivo:** banco C — nova classe adaptadora e uma entrada em `criar_cobranca`.

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
7. **Mudança ao vivo:** nova operação (ex.: cancelar reserva) = um método novo na fachada e um no tratador.

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
6. **Sem o padrão:** a fachada chamaria multa, e-mail e indicadores um a um; um e-mail fora do ar derrubaria a devolução.
7. **Mudança ao vivo:** novo ouvinte (ver `docs/DEMO_5_MINUTOS.md`): uma classe e uma linha em `montar_sistema`.

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
6. **Sem o padrão:** a rota chamaria `renovar` direto e um duplo clique somaria 60 dias.
7. **Mudança ao vivo:** `ComandoDevolucao` — nova subclasse com `tipo` e `executar`.

## R07 — Template Method

1. **O que é?** A classe-mãe fixa a ordem do algoritmo; as filhas só preenchem os passos.
2. **Problema:** os quatro cadastros seguem a mesma rotina e não podem pular validação nem pré-requisito.
3. **Onde está?** `dominio/cadastros_template.py`: `CadastroBase.incluir` e as subclasses.
4. **Como funciona?**
   1. `incluir` abre a transação e chama, nesta ordem: buscar existente, validar, verificar pré-requisitos, criar, armazenar, apresentar.
   2. Se já existe, devolve o existente (`ja_existia=True`) e para.
   3. `_verificar_pre_requisitos` é um **gancho**: vazio na base; Estudante e Atendente exigem a Pessoa.
   4. Se o pré-requisito falha, o erro vem antes de `_armazenar`: nada é gravado.
   5. `__init_subclass__` recusa subclasse que tente redefinir `incluir`.
5. **Teste:** `test_r07_estudante_duplicado_retorna_o_cadastro_existente`, `test_r07_estudante_com_cpf_nao_cadastrado_falha_antes_de_qualquer_gravacao`.
6. **Sem o padrão:** quatro rotinas copiadas, cada uma podendo esquecer um passo.
7. **Mudança ao vivo:** `CadastroEditora` — nova subclasse com os cinco passos.

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
7. **Mudança ao vivo:** nova família (ex.: SQLite) — uma fábrica nova e as classes de produto; o domínio não muda.

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
7. **Mudança ao vivo:** `ConsultaComLog` — nova subclasse de `DecoradorConsulta` e mais uma camada na cadeia.

## R10 — Composite

1. **O que é?** Uma árvore em que o grupo e o item respondem às mesmas operações.
2. **Problema:** o acervo tem unidades, seções e subseções em profundidade variável, e é preciso contar e listar em qualquer nível.
3. **Onde está?** `dominio/acervo_composite.py`: `ComponenteAcervo`, `GrupoAcervo`, `ItemLivro`, `mover`, `montar_arvore`.
4. **Como funciona?**
   1. `ItemLivro.contar_livros()` devolve 1; `GrupoAcervo.contar_livros()` soma os filhos.
   2. `adicionar` recusa ciclo (o grupo ou um ancestral dele) e livro que já está na árvore.
   3. `ItemLivro` guarda só o id do livro.
   4. `TratadorDeAcervo.mover_livro` valida no Composite e grava apenas `livro.grupo_id`.
5. **Teste:** `test_r10_unidade_com_secoes_de_tres_e_dois_livros_informa_cinco`, `test_r10_mover_livro_nao_altera_id_estado_nem_emprestimo`.
6. **Sem o padrão:** código diferente para unidade, seção e subseção, e um limite fixo de níveis.
7. **Mudança ao vivo:** nova operação (ex.: `listar_grupos()`) no componente, no grupo e no item.

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
