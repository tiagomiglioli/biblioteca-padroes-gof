# Evidências da auditoria — 13/11/2026

## Ambiente e isolamento

macOS arm64; Python 3.13.1 (Clang15); Flask 3.1.3; Flask-Login 0.6.3; Flask-WTF 1.3.0; mysql-connector-python 26.10.0; python-dotenv 1.2.4; pytest 9.2.0. MySQL real 9.4.0. Versões foram consultadas com `importlib.metadata.version`, não inferidas do requirements.

Projeto: `/Users/tiagomiglioli/Documents/bibioteca-gof`. Branch inicial `implementacao-gof`, HEAD inicial `034a5feddf898b0c4bd7a14a9e968520b85db5f2`. Alterações locais da auditoria não foram commitadas. `.DS_Store` e `.vscode/` já eram untracked e foram preservados.

Bases exclusivas: `biblioteca_gof_auditoria_20261113` (suíte), `biblioteca_gof_auditoria_ui_20261113` (navegador), `biblioteca_gof_auditoria_boleto_20261113`, `biblioteca_gof_auditoria_integridade_20261113` e `biblioteca_gof_auditoria_cache_20261113` (regressões isoladas). Dados fictícios; credenciais lidas de `.env`, não gravadas aqui. Fixtures truncam SOMENTE a base selecionada de teste. Bases mantidas para conferência, sem DROP.

## F01 — comando final efetivamente executado

Diretório: `/Users/tiagomiglioli/Documents/bibioteca-gof`.

```sh
rtk env PYTHONDONTWRITEBYTECODE=1 MYSQL_TEST_DATABASE=biblioteca_gof_auditoria_20261113 .venv/bin/python -B -m pytest -q -ra --tb=short -p no:cacheprovider --junitxml=/Users/tiagomiglioli/Documents/ChatGPT/padroes-de-projeto/auditoria-final/final.xml
```

Executado com acesso local MySQL autorizado fora da restrição TCP do sandbox. Resultado observado: **305 passed in 23.67s**, exit0. **0 falhas e 0 skips.** JUnit copiado para `evidencias_auditoria/final.xml`. Nomes individuais e tempos em `evidencias_auditoria/RESULTADOS_POR_TESTE.tsv`; não é contagem estimada. Tempo de wall-clock da ferramenta não deve ser confundido com tempo informado por pytest.

| Arquivo de teste | Aprovados | Falhas | Skips |
|---|---:|---:|---:|
| `tests/test_auditoria_boleto.py` | 4 | 0 | 0 |
| `tests/test_auditoria_cache.py` | 6 | 0 | 0 |
| `tests/test_auditoria_integridade.py` | 16 | 0 | 0 |
| `tests/test_auditoria_observer.py` | 4 | 0 | 0 |
| `tests/test_auditoria_processos.py` | 1 | 0 | 0 |
| `tests/test_autenticacao.py` | 54 | 0 | 0 |
| `tests/test_fluxo_web.py` | 18 | 0 | 0 |
| `tests/test_mysql_integracao.py` | 8 | 0 | 0 |
| `tests/test_r01_state.py` | 59 | 0 | 0 |
| `tests/test_r02_strategy.py` | 21 | 0 | 0 |
| `tests/test_r03_adapter.py` | 17 | 0 | 0 |
| `tests/test_r04_facade.py` | 14 | 0 | 0 |
| `tests/test_r05_observer.py` | 16 | 0 | 0 |
| `tests/test_r06_command.py` | 14 | 0 | 0 |
| `tests/test_r07_template_method.py` | 12 | 0 | 0 |
| `tests/test_r08_abstract_factory.py` | 10 | 0 | 0 |
| `tests/test_r09_decorator.py` | 13 | 0 | 0 |
| `tests/test_r10_composite.py` | 13 | 0 | 0 |
| `tests/test_r11_singleton.py` | 5 | 0 | 0 |

## Histórico de execução e falhas reais

1. Original, mesmo comando F01 com `--junitxml=.../baseline.xml`, sem liberação de TCP: **181 passed,93 skipped,4.25s**. Erro `Can't connect to MySQL server on '127.0.0.1:3306' (1)`. São verificações NÃO REALIZADAS nessa execução, não falhas do produto nem aprovação MySQL.
2. Original, com liberação de TCP, XML `baseline-mysql.xml`: **274 passed,18.23s**. Bases de teste separadas. Esse resultado não detectava bugs fora dos testes existentes.
3. Boleto concorrente, teste novo antes do reparo: **2 failed,2 skipped**; esperava1 emissão e recebeu2 em memória A/B. Após reparo, com MySQL real: **4 passed,4.62s**. Comando: Python original `.venv/bin/python -B -c` carregando dotenv original e `pytest.main(["tests/test_auditoria_boleto.py","-p","no:cacheprovider","-q","-rs"])`, cwd cópia `auditoria-final/revisao`, MYSQL_TEST_DATABASE exclusivo boleto.
4. Observer, teste novo: `rtk env PYTHONDONTWRITEBYTECODE=1 /Users/tiagomiglioli/Documents/bibioteca-gof/.venv/bin/python -B -m pytest tests/test_auditoria_observer.py -q -k memoria -p no:cacheprovider --junitxml=../observer-red.xml` na cópia. **2 failed,2 deselected**. Lista de inspeção recebeu9 entradas em vez de 1; ouvinte recuperável recebeu3 chamadas em vez de 2. Depois do reparo, incluindo `tests/test_r05_observer.py`: **10 passed,10 deselected**, XML `observer-green.xml`.
5. Integridade/proteção fixture: antes **8 failed,1 passed**, após memória **9 passed**, após famílias memória/MySQL **16 passed**. Logs compactos reproduzidos no relatório; os testes exatos estão em `tests/test_auditoria_integridade.py` e no JUnit final.
6. Uma execução intermediária durante edição concorrente importou módulos antigos: **286 passed,12 failed**. Falhas: seis casos de integridade em memória (pessoa vinculada×2, estudante com movimentação×3, livro com histórico), dois casos proteção/bootstrap de fixture, quatro casos Observer (duas famílias×dois cenários). Não foi usada como estado final; todos esses casos passaram em F01. A execução intermediária não foi apagada da narrativa.
7. Cópia estabilizada antes de aplicar ao projeto: **299 passed,23.99s**, XML `revisao-final.xml`.
8. Primeira F01 no original corrigido: **299 passed,24.28s** antes da correção adicional de cache.
9. Cache: **6 failed,0.92s** antes; **6 passed,0.54s** depois, memória/MySQL em base `biblioteca_gof_auditoria_cache_20261113`.
10. Última F01 após cache no projeto final: **305 passed,23.67s**, exit0, nenhum skip. Nenhum teste foi marcado xfail nem teve expectativa relaxada para esconder defeito.

## Transações e concorrência realmente exercitadas

- `test_r04_falha_no_meio_do_emprestimo_desfaz_tudo`: falha injetada depois de remover reserva; reserva e estado retornam, empréstimo não sobra; memória e MySQL.
- R08: mesma conexão nos repositórios, recusa de misturar famílias, commit/rollback, reconstrução de estado.
- R06: oito submissões simultâneas do mesmo ID, limite de renovações com IDs distintos, comando inválido não deixa registro.
- `test_mysql_mesmo_comando_em_quatro_processos_renova_uma_vez`: quatro intérpretes Python separados, mesma chave, MySQL compartilhado, comprovantes iguais, uma renovação, vencimento original+30. Não são quatro objetos no mesmo processo.
- Regressão boleto: A/B × memória/MySQL, duas chamadas concorrentes, um boleto emitido, respostas iguais, uma mensagem de boleto e quitação válida uma única vez.
- Observer: oito reentregas concorrentes, uma inspeção/indicador/e-mail; ouvinte com falha transitória é tentado de novo, ouvintes bem-sucedidos não são repetidos. Isso prova deduplicação local, não garantia distribuída.
- Integridade: exclusões recusadas preservam Pessoa/Estudante/Livro vinculados e histórico. Testes da fixture verificam proteção contra banco igual e erro SQL não convertido em skip.

## Navegador real, CSRF habilitado e MySQL real

Servidor temporário: `127.0.0.1:5057`, montado por `servidor_auditoria.py` na pasta local de evidências; banco exclusivo UI. Login fictício de auditoria criado somente nessa base; não é credencial de entrega. Navegação por CUA/controles reais, sem forjar fetchs, estado JS ou páginas estáticas.

Fluxo observado:

1. Login levou ao painel; formulário tinha CSRF ativo.
2. Pessoa Ana e pessoa Bia fictícias, estudante E-AUD, atendente A-AUD e livro L-AUD criados pelos formulários; mensagens confirmadas.
3. Reservar: RESERVADO.
4. Emprestar em 13/11/2026: EMPRESTADO, vencimento13/12/2026.
5. Renovar: RENOVADO, uma renovação, vencimento12/01/2027.
6. Data de devolução controlada17/01/2027: DEVOLVIDO,5 dias atraso.
7. Multas: R$5,00, política original, BancoA simulado; screenshot `ui-multa.png`.
8. Simular pagamento: Quitada. Repetir: “a multa já estava quitada”. Não houve pagamento financeiro externo.
9. Inspeção bom estado: LIVRE; screenshot `ui-inspecao.png`.
10. Acervo: consulta de metadados executada duas vezes, contador1→2; filtro JS “inexistente” ocultou a linha.
11. Processo Flask de PID4436 encerrado; novo processo subiu no mesmo banco, agora com código corrigido. Navegador confirmou multa de R$5,00 quitada; screenshot `ui-reinicio.png`.
12. SQL direto após reinício confirmou Livro LIVRE, uma renovação, vencimento2027-01-12, reserva inativa, empréstimo com devolução2027-01-17, multa5.00 original quitada,1 quitação,1 comando reserva e 1 renovação. JSON: `ui-mysql-reinicio.json`.

A persistência do vencimento anterior em Livro LIVRE não é empréstimo ativo: tabela Emprestimo registra devolução e tela esconde o prazo fora de EMPRESTADO/RENOVADO. Próximo empréstimo reinicia contador e prazo, coberto pelos testes State.

## Documentos, Graphify e verificação de código

Enunciado GoF Downloads/projeto SHA256 idêntico: `87d87ec1533c2d5ecf09e4837e852a3a349decf06f5a24f8895c730aad986aba`. PDFs foram extraídos com pypdf e renderizados com pypdfium2; 108 páginas de slides lidas, imagens revisadas em folhas de contato, diagramas relevantes ampliados. Trabalho02 10p e enunciado 5p lidos integralmente. Exemplos Java do ZIP lidos; não executados como biblioteca.

Graphify: grafo existente 1116 nós, consulta efetivamente executada `rtk graphify query 'CirculacaoFacade ExecutorComandos UnidadeTrabalhoMySQL' --budget 1600`. Retornou 216 nós,48 exibidos por limite; fontes principais `circulacao_command.py:55`, `circulacao_facade.py:10`, `unidade_trabalho.py:59`. O grafo foi mapa de navegação; trechos truncados não contam como código lido. Não reconstruí grafo nem quantifiquei economia de tokens.

Checagem Git somente leitura confirmou `.env` fora do índice e ausência desse caminho no histórico. SHA/branch inicial registrados. Não imprimi valores de configuração privada. Não houve commit/push.

## Não realizado / limites da evidência

- Astah excluído por instrução posterior do usuário: não utilizado como bloqueio de entrega.
- SMTP e bancos financeiros externos reais: não integrados; implementações são simulações identificadas no código. MySQL foi real.
- Garantia de entrega de evento após queda entre commit/publicação, deduplicação Observer entre processos, recuperação de emissão bancária após crash: não comprovadas.
- Teste de carga prolongada, todos navegadores/dispositivos, auditoria WCAG formal, segurança ofensiva ampla e todos blobs históricos do Git: não realizados.
- Aprovação individual dos quatro integrantes e ensaio cronometrado: não verificáveis pelo agente.
- Comparação remota de licença/código IBK: não realizada; declaração local informa referência visual sem cópia de código.
- A ausência de atendente transacional foi constatada no contrato/código/schema e no fluxo web. A suíte não testa essa regra; passes não a tornam implementada.

A verificação final `rtk git diff --check` terminou com exit0 e sem saída. As capturas do fluxo web antecedem a última correção de cache; a suíte final validou novamente o fluxo web e as seis regressões específicas.
