# Checklist de entrega — fechamento

Data: 13/11/2026. Parecer: **APTO — PODE ENTREGAR**. Prazo do enunciado: 27/11/2026 às 09h40; demonstração de cinco minutos. Astah excluído da avaliação e dos bloqueios por instrução do usuário.

## Código e provas concluídas

- [x] Onze padrões identificáveis e cenários da suíte preservados.
- [x] 374 testes aprovados em 28,22 s, zero falhas/erros/skips, incluindo MySQL real; 69 casos novos sobre os 305 anteriores.
- [x] Revisão independente de especificação e qualidade aprovada, sem findings.
- [x] Atendente obrigatório em reserva, empréstimo e devolução, validado no domínio.
- [x] Pessoa/CPF do atendente diferente do estudante; ausência e mesma Pessoa recusadas no navegador real.
- [x] Responsáveis separados nas três etapas e reserva inativa conservada.
- [x] Troca de CPF e exclusão de papéis usados recusadas; rollback preserva histórico.
- [x] Autor do Command continua login, distinto do atendente selecionado; não foi criado RBAC.
- [x] Limites de campos validados no backend, sem depender exclusivamente do HTML.
- [x] Migração aditiva testada sobre legado, repetição e falha parcial; NULL legado não é preenchido por suposição.
- [x] Fluxo real: reserva A1 → empréstimo A2 → renovação → devolução A1 com cinco dias de atraso → multa R$5 → pagamento simulado quitado.

## Confirmação operacional e pacote

- [x] Migração principal executada duas vezes; dados anteriores das 11 tabelas preservados e 14 FKs confirmadas.
- [x] Aplicação de 30 arquivos no original; 374 testes aprovados em 36,29 s, zero falhas/erros/skips, exit 0.
- [x] `git diff --check` limpo; servidor original reiniciado em `127.0.0.1:5057` e login confirmado.
- [ ] Em futuras instalações/atualizações: parar versão anterior, fazer backup e executar um migrador por vez antes de iniciar a nova versão.
- [x] Evidências preservadas em `evidencias_fechamento/`: JUnit original, 374 casos em TSV, resumo JSON, interface, revisão independente, migração/SQL e captura de devolução.
- [ ] Conferir inclusão dessas evidências no pacote final.
- [x] Código do original confere com o revisado; após o teste final houve apenas atualização documental.
- [x] README, registro LLM, guias, roteiro, perguntas e rastreabilidade atualizados para responsáveis e migração.
- [x] Quatro relatórios principais atualizados sem confundir auditoria inicial com fechamento.
- [x] Parecer final consolidado após migração, aplicação e suíte no original.
- [x] ZIP validado por CRC e manifesto SHA256; sem `.env`, bases locais, caches e backups privados.
- [ ] Fazer instalação limpa pelo README com usuário MySQL adequado e chave de sessão própria.
- [ ] Identificar integrantes, revisar créditos dos exemplos/terceiros e escolher branch/commit final; nenhum commit é presumido por este checklist.

## Defesa humana e limites conhecidos

- [ ] Cada integrante explica todos os onze padrões, transação e migração.
- [ ] Ensaiar cinco minutos com estudante e atendente de Pessoas distintas e livro LIVRE.
- [ ] Demonstrar terceira renovação recusada sem mudar vencimento e apontar teste de rollback.
- [ ] Explicar autor do Command versus responsável transacional; mostrar responsáveis diferentes preservados.
- [ ] Executar extensão Strategy/Observer com teste correspondente.
- [ ] Explicar NULL legado, commit implícito DDL e retomada serial da migração.
- [ ] Explicar bancos/e-mail simulados, configuração por processo, cache local e ausência de replay durável Observer.

As pendências humanas e operacionais acima não devem ser marcadas como feitas apenas porque a suíte passou. O antigo bloqueio de ausência do atendente e a lacuna de limites backend foram corrigidos nesta etapa; não permanecem como defeitos atuais.
