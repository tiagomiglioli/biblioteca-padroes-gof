# Tabela de rastreabilidade

Para cada requisito: o padrão, as classes que fazem cada papel, os testes que comprovam o
cenário de verificação e o diagrama correspondente. Os diagramas auxiliares estão em
`docs/DIAGRAMAS_UML.md`; os modelos ficaram fora do escopo de avaliação por solicitação da equipe. As referências históricas a modelos abaixo não são critérios de aprovação deste fechamento.

| Nº | Situação | Padrão | Papéis → classes | Arquivo | Testes do cenário de verificação | UML |
|---|---|---|---|---|---|---|
| R01 | Ciclo de vida do livro | State | Context → `Livro`; State → `EstadoLivro`; ConcreteState → `EstadoLivre`, `EstadoReservado`, `EstadoEmprestado`, `EstadoRenovado`, `EstadoDevolvido`, `EstadoReparando`, `EstadoIncinerado` | `dominio/estados.py`, `dominio/entidades.py` | `test_r01_terceira_renovacao_recusada_sem_alterar_vencimento`, `test_r01_devolvido_nao_inspecionado_nao_pode_ser_reservado`, `test_r01_laudo_irrecuperavel_leva_reparando_a_incinerado`, `test_r01_evento_invalido_e_recusado_sem_alterar_o_livro` | Máquina de estados de Livro (Astah, Trabalho 02) + diagrama 1 |
| R02 | Políticas de multa | Strategy | Contexto → `ServicoMulta`; Estrategia → `PoliticaMulta`; EstrategiaConcreta → `MultaOriginal`, `MultaComTeto`, `MultaComTolerancia` | `dominio/multas_strategy.py` | `test_r02_cinco_dias_de_atraso_custam_5_na_original_e_3_na_tolerancia`, `test_r02_sem_atraso_o_valor_e_zero`, `test_r02_trocar_a_politica_nao_recalcula_multa_ja_emitida` | diagrama 2 |
| R03 | Bancos incompatíveis | Adapter | Target → `CobrancaInstitucional`; Adaptee → `BancoA`, `BancoB`; Adapter → `AdaptadorBancoA`, `AdaptadorBancoB`; Client → `ServicoMulta` | `dominio/bancos_adapter.py` | `test_r03_a_mesma_solicitacao_de_7_reais_vira_700_centavos_no_banco_a_e_7_00_no_banco_b`, `test_r03_servico_de_multas_nao_tem_condicionais_por_banco`, `test_r03_notificacao_repetida_nao_gera_segunda_quitacao` | diagrama 3; interfaces `iCobranca` e `iQuitacao` do diagrama de componentes |
| R04 | Entrada única da circulação | Facade | Facade → `CirculacaoFacade`; subsistema → `Relacionamento`, `Movimentacao`, `Acervo`, `Livro`; clientes → `TratadorDeEmprestimo`, `TratadorDeDevolucao` | `dominio/circulacao_facade.py`, `dominio/tratadores.py` | `test_r04_emprestimo_valida_reserva_remove_reserva_cria_emprestimo_e_atualiza_livro`, `test_r04_fachada_devolve_comprovantes_e_nao_colecoes`, `test_r04_falha_no_meio_do_emprestimo_desfaz_tudo` | diagrama 4; sequência "EmprestarLivro" |
| R05 | Reações à devolução | Observer | Subject → `PublicadorDevolucao`; Observer → `OuvinteDevolucao`; ConcreteObserver → `OuvinteInspecao`, `OuvinteMulta`, `OuvinteIndicadores`, `OuvinteEmail`; evento → `EventoDevolucao` | `dominio/devolucao_observer.py` | `test_r05_devolucao_atrasada_alimenta_inspecao_multa_e_indicadores`, `test_r05_devolucao_no_prazo_nao_gera_multa`, `test_r05_livro_permanece_devolvido_ate_a_decisao_da_inspecao`, `test_r05_falha_do_email_nao_afeta_os_demais_nem_desfaz_a_devolucao`, `test_r05_publicacao_ocorre_depois_da_confirmacao_da_devolucao` | diagrama 5; sequência "RegistrarDevolucao" |
| R06 | Solicitações como objetos | Command | Comando → `Comando`; ComandoConcreto → `ComandoReserva`, `ComandoRenovacao`; Invocador → `ExecutorComandos`; Alvo → `CirculacaoFacade`; cliente → `TratadorDeEmprestimo` | `dominio/circulacao_command.py` | `test_r06_renovacao_executada_duas_vezes_com_o_mesmo_identificador_acrescenta_apenas_30_dias`, `test_r06_solicitacoes_diferentes_continuam_sujeitas_ao_limite_de_duas_renovacoes`, `test_r06_submissoes_simultaneas_do_mesmo_identificador_executam_uma_unica_vez` | diagrama 6 |
| R07 | Rotina dos cadastros | Template Method | AbstractClass → `CadastroBase` (método-modelo `incluir`); ConcreteClass → `CadastroPessoa`, `CadastroEstudante`, `CadastroAtendente`, `CadastroLivro`; interfaces → `iPessoa`, `iEstudante`, `iAtendente`, `iLivro` | `dominio/cadastros_template.py`, `dominio/tratadores.py` | `test_r07_estudante_duplicado_retorna_o_cadastro_existente`, `test_r07_estudante_com_cpf_nao_cadastrado_falha_antes_de_qualquer_gravacao`, `test_r07_metodo_modelo_nao_pode_ser_sobrescrito`, `test_r07_a_ordem_dos_passos_e_fixa` | diagrama 7; sequências "InserirPessoa", "InserirEstudante" |
| R08 | Famílias de acesso a dados | Abstract Factory | FabricaAbstrata → `FabricaPersistencia`; FabricaConcreta → `FabricaMemoria`, `FabricaMySQL`; ProdutoAbstrato → `UnidadeTrabalho`, `Acervo`, `Movimentacao`, `Relacionamento`, `Financeiro`; produtos concretos → classes `...Memoria` e `...MySQL` | `dominio/persistencia_factory.py`, `dominio/pontos_acesso.py`, `persistencia/` | `test_r08_perfil_de_teste_fornece_apenas_objetos_em_memoria`, `test_r08_perfil_de_producao_fornece_repositorios_mysql_na_mesma_unidade_de_trabalho`, `test_r08_repositorio_mysql_recusa_unidade_de_trabalho_em_memoria` | diagrama 8; diagrama de implantação (MySQL principal, Oracle réplica) |
| R09 | Consulta com recursos opcionais | Decorator | Componente → `ConsultaAcervo`; Essencia → `ConsultaBase`; Decorador → `DecoradorConsulta`; DecoradorConcreto → `ConsultaComCache`, `ConsultaComMedicao` | `dominio/consulta_decorator.py` | `test_r09_segunda_consulta_usa_cache_e_ainda_gera_medicao`, `test_r09_resultado_antigo_do_cache_nunca_autoriza_reserva`, `test_r09_cache_com_defeito_cai_na_implementacao_original` | diagrama 9 |
| R10 | Hierarquia do acervo | Composite | Componente → `ComponenteAcervo`; Composto → `GrupoAcervo`; Folha → `ItemLivro` | `dominio/acervo_composite.py` | `test_r10_unidade_com_secoes_de_tres_e_dois_livros_informa_cinco`, `test_r10_mover_livro_nao_altera_id_estado_nem_emprestimo`, `test_r10_grupo_recusa_ciclos`, `test_r10_grupo_recusa_livro_que_ja_pertence_a_outro_grupo` | diagrama 10 |
| R11 | Configuração única (pedido do professor) | Singleton | Singleton → `ConfiguracaoSistema` (`obter_instancia`) | `dominio/configuracao_singleton.py` | `test_r11_obter_instancia_devolve_sempre_o_mesmo_objeto`, `test_r11_threads_simultaneas_recebem_a_mesma_instancia` | diagrama 11 |

## Requisitos técnicos do enunciado

| Requisito | Onde é atendido | Teste |
|---|---|---|
| Interface web que chama apenas os tratadores | `web/rotas.py` usa só `current_app.sistema.<tratador>` | `tests/test_fluxo_web.py` |
| Tratadores, delegação e pontos de acesso do Trabalho 02 | `dominio/tratadores.py` (`TratadorDeEmprestimo`, `TratadorDeDevolucao`, `TratadorDeAcervo`, `TratadorDePessoa`, `TratadorDeEstudante`, `TratadorDeAtendente`, `TratadorDeMulta`); `dominio/pontos_acesso.py` (`Acervo`, `Movimentacao`, `Relacionamento`) | `test_r04_tratadores_delegam_a_fachada` |
| Duas famílias de persistência criadas pela fábrica | `FabricaMemoria` e `FabricaMySQL` | fixture `fabrica` roda os testes nas duas |
| Bancos A e B simulados, adaptadores reais | `dominio/bancos_adapter.py` | `tests/test_r03_adapter.py` |
| Um teste por cenário, com o requisito no nome | `tests/test_r01_*.py` … `tests/test_r11_*.py` | — |
| Testes com um único comando | `python -m pytest -q` (README) | — |
| Fluxo completo pela interface | Circulação e Multas | `test_fluxo_completo_reserva_emprestimo_renovacao_devolucao_atrasada_e_multa` |
| MySQL real, transações, persistência após reinício | `persistencia/mysql.py`, `persistencia/unidade_trabalho.py`, `sql/schema.sql` | `tests/test_mysql_integracao.py` |
| Login, hash de senha, CSRF, sessão | `web/autenticacao.py`, `app.py`, `config.py` | `tests/test_autenticacao.py` |
| README, rastreabilidade, registro de LLM | `README.md`, este arquivo, `REGISTRO_LLM.md` | — |

## Transições da máquina de estados (Trabalho 02, seção 11) → método

| # | Origem | Evento [guarda] | Destino | Método |
|---|---|---|---|---|
| T1 | início | inserirLivro | LIVRE | `Livro.__init__` (via `CadastroLivro._criar`) |
| T2 | LIVRE | reservar [estudante cadastrado] | RESERVADO | `EstadoLivre.reservar` (guarda do estudante em `CirculacaoFacade.reservar`) |
| T3 | RESERVADO | emprestar [reserva do mesmo estudante] | EMPRESTADO | `EstadoReservado.emprestar` (guarda da reserva em `CirculacaoFacade.emprestar`) |
| T4 | EMPRESTADO | renovar [numRenovacoes < 2] | RENOVADO | `EstadoEmprestado.renovar` |
| T5 | RENOVADO | renovar [numRenovacoes < 2] | RENOVADO | `EstadoRenovado.renovar` |
| T6 | EMPRESTADO ou RENOVADO | devolver [empréstimo registrado] | DEVOLVIDO | `EstadoEmprestado.devolver`, `EstadoRenovado.devolver` |
| T7 | DEVOLVIDO | inspecionar [bom estado] | LIVRE | `EstadoDevolvido.inspecionar` |
| T8 | DEVOLVIDO | inspecionar [danificado] | REPARANDO | `EstadoDevolvido.inspecionar` |
| T9 | LIVRE | enviarParaReparo | REPARANDO | `EstadoLivre.enviar_para_reparo` |
| T10 | REPARANDO | retornarDoReparo | LIVRE | `EstadoReparando.retornar_do_reparo` |
| T11 | LIVRE | excluirLivro | fim | `EstadoLivre.excluir` (chamado por `TratadorDeAcervo.excluir`) |
| — | REPARANDO | laudo irrecuperável | INCINERADO | `EstadoReparando.registrar_laudo_irrecuperavel` |

## Fechamento do requisito herdado — participantes das transações

| Regra | Implementação | Teste correspondente |
|---|---|---|
| Atendente presente/cadastrado e Pessoa distinta do estudante | `CirculacaoFacade._validar_participantes`, chamada por `reservar`, `emprestar`, `devolver` | `tests/test_atendente_transacoes.py::test_atendente_invalido_recusa_sem_mudar_livro`, `test_omitir_atendente_nao_cria_reserva` |
| Seleção na interface e comprovante com responsável | `web/rotas.py`, formulário Circulação, `Comprovante.atendente_id` | `tests/test_atendente_transacoes.py::test_web_exige_atendente_e_mostra_responsavel` |
| Responsáveis separados nas três etapas, reserva inativa preservada | `Reserva.atendente_id`, `Emprestimo.atendente_id`, `Emprestimo.atendente_devolucao_id`, repositórios memória/MySQL | `test_responsavel_de_cada_operacao_nao_sobrescreve_o_anterior`, `tests/test_persistencia_atendente.py::test_responsaveis_distintos_persistem_e_reserva_vira_historico` |
| Falha não consome Command e não muda histórico | `ExecutorComandos`, Facade e UoW | `test_reserva_sem_atendente_faz_rollback_do_command_e_permite_corrigir`, `test_rollback_preserva_reserva_e_responsavel` |
| Preservação da identidade dos papéis usados | Relacionamento memória/MySQL recusa exclusão ou troca de CPF após uso | `tests/test_persistencia_atendente.py::test_papel_usado_nao_pode_trocar_pessoa`; teste de responsáveis também verifica exclusão |
| Compatibilidade com comprovante legado | Campo opcional em `Comprovante.de_texto` | `tests/test_persistencia_atendente.py::test_comprovante_antigo_permanece_legivel` |
| Migração aditiva, repetível e retomável; legado NULL sem responsável inventado | `persistencia/migracoes.py`, `app.py` comandos `migrar-db`/`init-db`, `sql/schema.sql` | `tests/test_migracao_atendente.py::test_migracao_preserva_legado_e_pode_ser_repetida` |

O autor do Command é o login do operador; não se confunde com atendente selecionado. A renovação conserva o responsável do empréstimo. Os limites dos campos são validados no backend; não foi introduzido RBAC. Migração deve preceder esta versão e ser executada serialmente, com a anterior parada.

Total final da suíte: **374 aprovados**, zero falhas/erros/skips: 28,22 s na cópia de fechamento e 36,29 s no original após aplicação. O parecer **APTO — PODE ENTREGAR** refere-se ao escopo acadêmico auditado, com Astah excluído. Evidências em `AUDITORIA_FINAL.md`, `EVIDENCIAS_TESTES.md` e `evidencias_fechamento/`. Os resultados da auditoria inicial pertencem ao estado anterior e foram preservados como histórico; a suíte não certifica domínio oral dos integrantes.
