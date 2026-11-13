# Alterações da auditoria — 13/11/2026

Reparos restritos a falhas reproduzidas. Arquivos anteriores preservados na pasta local `auditoria-final/originais/`; diff em `evidencias_auditoria/alteracoes.patch`. Antes de copiar para o projeto, hashes garantiram que nenhum arquivo original havia mudado desde a revisão. Não houve migração, alteração de `.env`, commit ou push.

| Arquivo | Alteração e motivo | Risco / limite | Regressão |
|---|---|---|---|
| `dominio/multas_strategy.py` | Mantém emissão simulada e associação do boleto na mesma UoW; impede dois IDs concorrentes para mesma multa. | Lock retido durante banco simulado; API remota exigiria idempotência por referência e timeout. | `test_auditoria_boleto.py`, A/B × memória/MySQL,4 passes. |
| `dominio/pontos_acesso.py` | `Financeiro.obter_multa` aceita `para_atualizar=False`. | Argumento opcional preserva callers existentes. | Suíte completa e teste boleto. |
| `persistencia/mysql.py` | SELECT FOR UPDATE quando emissão pede exclusão mútua. | Concorrência na mesma multa serializada até commit. | Boleto MySQL real. |
| `persistencia/memoria.py` | Mesmo contrato de leitura; recusa exclusões Pessoa/Estudante/Livro com vínculos/histórico. | Família memória passa a recusar operações já recusadas por MySQL; não apaga dados automaticamente. | `test_auditoria_integridade.py`. |
| `dominio/devolucao_observer.py` | Registra sucesso por empréstimo/ouvinte; trava publicação concorrente; retry só do ouvinte que falhou. | Deduplicação local ao publicador; não é garantia distribuída/durável. Ouvinte que produz efeito e depois lança erro precisa ser idempotente por conta própria. | `test_auditoria_observer.py`,4 passes. |
| `tests/conftest.py` | Bloqueia banco teste igual ao aplicativo e propaga erros SQL/permissão do bootstrap. | Testes antes ocultos como skip podem agora falhar corretamente; nome diferente ainda deve apontar base descartável. | `test_auditoria_integridade.py`. |
| `tests/test_auditoria_boleto.py` | Nova regressão de corrida A/B nas duas persistências. | Banco externo é simulador real do projeto, não integração bancária. | Falhou antes, passou depois. |
| `tests/test_auditoria_integridade.py` | Novos testes de vínculos/histórico e infraestrutura de testes. | Nenhuma alteração da expectativa para mascarar erro. |8 falhas antes;16 passes finais. |
| `tests/test_auditoria_observer.py` | Replay concorrente e recuperação seletiva de falha. | Mede efeitos locais; não prova pós-crash. |2 falhas antes memória;4 passes finais nas famílias. |
| `tests/test_auditoria_processos.py` | Prova Command em quatro subprocessos com MySQL. | Requer base isolada acessível; não é teste de carga prolongada. |1 passe final. |

Foram acrescentados 31 testes aos274 existentes:4 boleto+16 integridade+4 Observer+1 processos+6 cache. Resultado final305 passes,0 falhas,0 skips. Evidência por caso em XML/TSV.

Os cinco relatórios são novos na raiz; os guias preexistentes em `docs/` foram preservados. Astah excluído do parecer conforme instrução posterior. Não corrigi o vínculo de atendente porque exige decisão/modelagem e migração coordenada, não remendo seguro em uma classe. Não acrescentei dependências, abstrações genéricas nem funcionalidades externas.

## Correção adicional de cache

`dominio/consulta_decorator.py`: contrato público de invalidação, delegação e remoção segura da cópia local. `dominio/tratadores.py`: invalidação somente após commit de atualização/exclusão do Acervo; retorno e erros existentes preservados. `tests/test_auditoria_cache.py`: seis regressões memória/MySQL; seis falhas antes e seis passes depois. Risco: invalidação não distribuída entre workers; não foi introduzido cache externo nem dependência. Comentário de ausência de invalidação foi atualizado por ter ficado obsoleto com a correção.

`README.md` e `REGISTRO_LLM.md` receberam um adendo apontando o parecer e identificando esta auditoria, sem substituir o histórico da equipe.
