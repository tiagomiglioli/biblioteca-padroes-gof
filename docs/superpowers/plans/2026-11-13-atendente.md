# Vínculo transacional do atendente — plano de implementação

> Execução autorizada pelo usuário após auditoria: resolver o bloqueio para entrega. Superpowers, Ponytail e Migration orientam testes e preservação.

**Objetivo:** novas reservas, empréstimos e devoluções exigem atendente cadastrado cuja Pessoa difere da Pessoa do estudante. Astah permanece fora do escopo.

**Arquitetura:** seleção explícita no formulário, propagada por tratadores/Command até Facade. Facade valida na UoW, repositórios persistem IDs com FK. Manter atendente da reserva, do empréstimo e da devolução separadamente; podem ser diferentes. Não vincular login automaticamente a um papel nem inventar responsável para histórico.

**Alternativa descartada:** vincular toda conta a atendente exigiria mudanças em autenticação/cadastro sem necessidade para satisfazer este requisito. Seleção explícita é suficiente para a aplicação acadêmica operada por usuário autenticado.

**Migração:** adicionar colunas nullable para preservar registros legados sem responsável conhecido, criar FKs, ser idempotente; novas operações exigem atendente no domínio. Sem apagar/backfill inventado. Rollback de código pode ignorar colunas novas; não remover colunas/dados.

## Contratos

- Reserva recebe atendente_id ao final e ativa=True para conservar histórico também em memória.
- Emprestimo recebe atendente_id e atendente_devolucao_id ao final dos campos existentes.
- Movimentacao.inserir_reserva/inserir_emprestimo(livro_id, estudante_id, data, atendente_id).
- Movimentacao.registrar_devolucao(emprestimo_id, data, atendente_id).
- Relacionamento.obter_estudante/obter_atendente(id, para_atualizar=False); bloqueio das linhas durante validação.
- Facade.reservar(estudante_id,livro_id,uow=None,atendente_id=None), emprestar(estudante_id,livro_id,atendente_id=None), devolver(livro_id,data_devolucao=None,atendente_id=None). None recusa com ErroDominio; nunca assume A1.
- Command guarda atendente_id opcional no final do construtor; ComandoReserva encaminha.
- Comprovante.atendente_id opcional ao final permite ler JSON antigo; novas três transações exibem responsável.

## Etapas

- [ ] Testes vermelhos: atendente ausente/inexistente/mesma Pessoa recusa sem efeito; válido persiste nas três transações; rollback mantém reserva e responsáveis; exclusão/revínculo de papel usado recusados.
- [ ] Persistência/schema/migração: atualizar entidades/contratos/produtos; testar memória/MySQL e migração com dados antigos, repetição e falha parcial recuperável.
- [ ] Domínio/UI: validar na fachada antes de mutar; encaminhar parâmetro, mostrar seletor e comprovante; preservar onze padrões.
- [ ] Atualizar callers/testes existentes com atendente explícito; não relaxar asserts anteriores. Ajustar fixture para estudante e atendente serem Pessoas diferentes.
- [ ] Validar limites de tamanho do backend expostos na auditoria e erros amigáveis, sem depender de maxlength.
- [ ] Suíte completa MySQL isolada, revisão independente, migração aditiva na base local, fluxo navegador incluindo recusa da mesma Pessoa e persistência após reinício.
- [ ] Atualizar relatórios/README/registro/rastreabilidade e montar pacote sem segredos; parecer somente após evidências.

## Foco de revisão

Ausência de responsável não pode ser aceita; CPF iguais com IDs diferentes devem ser recusados; troca de atendente entre operações não deve sobrescrever histórico; falhas não deixam transação parcial; migração não pode apagar dados ou inventar autor. CPF de papéis com histórico não deve ser trocado silenciosamente. Sem commit/push automático.
