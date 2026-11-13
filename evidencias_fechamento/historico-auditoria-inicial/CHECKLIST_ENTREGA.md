# Checklist de entrega — 13/11/2026

Parecer atual: **NÃO ENTREGAR AINDA**. Prazo do enunciado: **27/11/2026 às 09h40**; demonstração 5min.

## Bloqueio funcional

- [ ] Registrar atendente em reserva, empréstimo e devolução, conforme Trabalho02p2.
- [ ] Validar que atendente e estudante correspondem a pessoas diferentes.
- [ ] Testar regra nas duas famílias e na interface, com rollback dos casos recusados.
- [ ] Se o professor dispensar essa regra, registrar sua decisão explicitamente; não presumir dispensa por autorização de Python.

## Implementação e evidências

- [x] State: sete classes, guarda<2, terceira tentativa sem mudar vencimento, inspeção e incineração.
- [x] Strategy: original/teto/tolerância, Decimal e congelamento da multa.
- [x] Adapter: dois bancos simulados, formatos distintos, quitação idempotente.
- [x] Facade: empréstimo atômico com rollback real MySQL.
- [x] Observer: quatro ouvintes, evento após commit, isolamento e replay local.
- [x] Command: reserva/renovação, IDs, autor/data, concorrência com quatro processos MySQL.
- [x] Template Method: quatro cadastros, seis passos, pré-requisito e proteção do fluxo.
- [x] Abstract Factory: famílias completas, UoW compartilhada por operação.
- [x] Decorator: cache e medição encadeáveis, reserva não usa estado cacheado.
- [x] Composite: árvore variável, contagem5, sem ciclos/duplicação, movimento preserva vínculo.
- [x] Singleton: instância por processo, teste concorrente e nenhuma conexão global.
- [x] Flask/Flask-Login/Jinja/HTML/CSS/JS e CSRF em fluxo real.
- [x] Schema/seed,11 tabelas InnoDB, PK/FK/UNIQUE, dados persistem após reinício real.
- [x] Correções aplicadas com regressões;305 testes aprovados no projeto final.
- [ ] Reexecutar suíte depois de QUALQUER alteração posterior e atualizar XML/relatórios.
- [x] Invalidar metadados após commit de edição/exclusão no processo local.
- [ ] Completar validações de tamanho no backend; definir se haverá múltiplos workers.

## Pacote e documentação

- [x] Código, testes, requirements, README, schema e seed presentes.
- [x] Rastreabilidade `docs/RASTREABILIDADE.md` presente; matriz atual auditada em `AUDITORIA_FINAL.md`.
- [x] `AUDITORIA_FINAL.md`, `EVIDENCIAS_TESTES.md`, `GUIA_DEFESA.md`, `CHECKLIST_ENTREGA.md`, `ALTERACOES_AUDITORIA.md` gerados.
- [x] Evidências XML/TSV/PNG/JSON anexadas em `evidencias_auditoria/`.
- [x] Registro LLM preexistente preservado; adicionar revisão atual sem atribuir modelo histórico não verificado.
- [ ] Integrantes identificados e matriz de revisão humana do `REGISTRO_LLM.md` preenchida.
- [ ] Conferir créditos e termos de distribuição dos exemplos do professor/terceiros. Registro declara IBK apenas referência visual.
- [ ] Fazer instalação limpa pelo README com versões registradas e usuário MySQL apropriado ao ambiente de entrega.
- [ ] Configurar `.env` local e chave própria; não incluir `.env`, bancos de auditoria nem credenciais na entrega.
- [ ] Revisar diff e escolher commit/branch final. Auditoria não fez commit/push; HEAD de referência034a5feddf898b0c4bd7a14a9e968520b85db5f2, branch implementacao-gof.

**Astah e seus artefatos/exportações: fora desta avaliação por solicitação posterior do usuário.** Nenhum item Astah impede este parecer técnico. Confirmar separadamente com o professor o pacote acadêmico exigido; não confundir exclusão da auditoria com dispensa formal.

## Defesa e operação

- [ ] Cada um dos quatro integrantes explica TODOS onze padrões, não apenas sua divisão de trabalho.
- [ ] Ensaiar5min com banco de demonstração pronto, usuário local, dados fictícios e data controlada.
- [ ] Demonstrar terceira renovação recusada e mostrar vencimento inalterado.
- [ ] Apontar teste rollback, concorrência e persistência sem ler resultados inventados.
- [ ] Executar extensão Strategy/Observer conforme guia, sem alterar comportamento original.
- [ ] Explicar limitações: bancos/e-mail simulados, Singleton/config por processo, Observer sem fila durável.
- [ ] Não anunciar PODE ENTREGAR antes de fechar regra de atendente e repetir verificação.
