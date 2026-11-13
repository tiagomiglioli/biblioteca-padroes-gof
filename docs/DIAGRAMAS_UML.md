# Diagramas UML auxiliares

O enunciado pede os modelos no Astah (`.asta`) e em PDF. **O arquivo Astah não foi alterado
por esta implementação**: a ferramenta de IA não edita `.asta`. Os diagramas abaixo estão em
Mermaid (o GitHub os desenha) e servem de guia para a equipe redesenhar no Astah.

## Pendências no Astah (trabalho da equipe)

1. Criar um diagrama de classes para cada padrão (diagramas 1 a 11 abaixo).
2. Na máquina de estados de Livro, conferir a guarda da renovação: o código usa
   `numRenovacoes < 2` (enunciado da implementação e seção 12 do Trabalho 02). A tabela da
   seção 11 do Trabalho 02 cita `<= 2` como exemplo; com a contagem começando em zero,
   `<= 2` permitiria três renovações.
3. Acrescentar a transição `REPARANDO --registrarLaudoIrrecuperavel--> INCINERADO`.
4. Atualizar os diagramas de sequência de empréstimo e devolução para passar pela
   `CirculacaoFacade` (sequências abaixo).
5. Conferir os nomes. Pela leitura do texto do `.asta` do Trabalho 02, o modelo usa
   `AcervoDeLivros`, `GrupoDePessoas`, `GrupoDeAcademicos` e `GrupoDeColaboradores`; o
   enunciado da implementação manda preservar `Acervo`, `Relacionamento` e `Movimentacao`,
   que são os nomes usados no código. Os diagramas do Astah não foram abertos visualmente.
6. Exportar tudo em PDF.

## Máquina de estados de Livro

```mermaid
stateDiagram-v2
    [*] --> LIVRE: inserirLivro
    LIVRE --> RESERVADO: reservar [estudante cadastrado]
    RESERVADO --> EMPRESTADO: emprestar [reserva do mesmo estudante] / vencimento = hoje + 30
    EMPRESTADO --> RENOVADO: renovar [numRenovacoes < 2] / vencimento += 30, numRenovacoes++
    RENOVADO --> RENOVADO: renovar [numRenovacoes < 2] / vencimento += 30, numRenovacoes++
    EMPRESTADO --> DEVOLVIDO: devolver / [atraso] gerarMulta
    RENOVADO --> DEVOLVIDO: devolver / [atraso] gerarMulta
    DEVOLVIDO --> LIVRE: inspecionar [bom estado]
    DEVOLVIDO --> REPARANDO: inspecionar [danificado]
    LIVRE --> REPARANDO: enviarParaReparo
    REPARANDO --> LIVRE: retornarDoReparo
    REPARANDO --> INCINERADO: registrarLaudoIrrecuperavel
    LIVRE --> [*]: excluirLivro
    INCINERADO --> [*]
```

## 1. State

```mermaid
classDiagram
    class Livro {
      +id
      +titulo
      +num_renovacoes
      +vencimento
      +reservar()
      +emprestar(hoje)
      +renovar()
      +devolver()
      +inspecionar(bom_estado)
      +mudar_estado(novo)
    }
    class EstadoLivro {
      <<State>>
      +nome
      +reservar(livro)
      +emprestar(livro, hoje)
      +renovar(livro)
      +devolver(livro)
      +inspecionar(livro, bom_estado)
      +enviar_para_reparo(livro)
      +retornar_do_reparo(livro)
      +registrar_laudo_irrecuperavel(livro)
      +excluir(livro)
    }
    Livro o--> EstadoLivro : estado
    EstadoLivro <|-- EstadoLivre
    EstadoLivro <|-- EstadoReservado
    EstadoLivro <|-- EstadoEmprestado
    EstadoLivro <|-- EstadoRenovado
    EstadoLivro <|-- EstadoDevolvido
    EstadoLivro <|-- EstadoReparando
    EstadoLivro <|-- EstadoIncinerado
```

## 2. Strategy

```mermaid
classDiagram
    class ServicoMulta {
      <<Contexto>>
      +emitir_multa(evento)
      +emitir_boleto(multa_id)
      +registrar_pagamento(notificacao)
    }
    class PoliticaMulta {
      <<Estrategia>>
      +nome
      +calcular(dias_atraso) Decimal
    }
    ServicoMulta --> PoliticaMulta : politica vigente
    PoliticaMulta <|-- MultaOriginal
    PoliticaMulta <|-- MultaComTeto
    PoliticaMulta <|-- MultaComTolerancia
```

## 3. Adapter

```mermaid
classDiagram
    class CobrancaInstitucional {
      <<Target>>
      +emitir_boleto(solicitacao) BoletoEmitido
      +traduzir_notificacao(externa) PagamentoConfirmado
    }
    class BancoA {
      <<Adaptee>>
      +criar_cobranca(valor_centavos, cpf, referencia)
      +avisar_pagamento(codigo)
    }
    class BancoB {
      <<Adaptee>>
      +emitir_titulo(pedido)
      +webhook_pagamento(titulo_id)
    }
    ServicoMulta --> CobrancaInstitucional
    CobrancaInstitucional <|-- AdaptadorBancoA
    CobrancaInstitucional <|-- AdaptadorBancoB
    AdaptadorBancoA --> BancoA
    AdaptadorBancoB --> BancoB
```

## 4. Facade

```mermaid
classDiagram
    class CirculacaoFacade {
      +reservar(estudante_id, livro_id) Comprovante
      +consultar_reserva(estudante_id, livro_id) Comprovante
      +emprestar(estudante_id, livro_id) Comprovante
      +renovar(estudante_id, livro_id) Comprovante
      +devolver(livro_id, data) Comprovante
      +inspecionar(livro_id, bom_estado) Comprovante
    }
    TratadorDeEmprestimo --> CirculacaoFacade
    TratadorDeDevolucao --> CirculacaoFacade
    CirculacaoFacade --> Acervo
    CirculacaoFacade --> Movimentacao
    CirculacaoFacade --> Relacionamento
    CirculacaoFacade --> Livro
    CirculacaoFacade --> PublicadorDevolucao
```

## 5. Observer

```mermaid
classDiagram
    class PublicadorDevolucao {
      <<Subject>>
      +registrar(ouvinte)
      +publicar(evento)
    }
    class OuvinteDevolucao {
      <<Observer>>
      +notificar(evento)
    }
    class EventoDevolucao {
      +emprestimo_id
      +livro_id
      +estudante_id
      +cpf
      +email
      +vencimento
      +data_devolucao
      +dias_atraso
    }
    PublicadorDevolucao o--> "0..*" OuvinteDevolucao
    OuvinteDevolucao <|-- OuvinteInspecao
    OuvinteDevolucao <|-- OuvinteMulta
    OuvinteDevolucao <|-- OuvinteIndicadores
    OuvinteDevolucao <|-- OuvinteEmail
    OuvinteMulta --> ServicoMulta
    OuvinteEmail --> ServicoEmail
    PublicadorDevolucao ..> EventoDevolucao
```

## 6. Command

```mermaid
classDiagram
    class Comando {
      <<Comando>>
      +id
      +autor
      +criado_em
      +executar(uow) Comprovante
    }
    class ExecutorComandos {
      <<Invocador>>
      +executar(comando) Comprovante
    }
    TratadorDeEmprestimo ..> Comando : cria
    TratadorDeEmprestimo --> ExecutorComandos
    ExecutorComandos --> Comando
    Comando <|-- ComandoReserva
    Comando <|-- ComandoRenovacao
    ComandoReserva ..> CirculacaoFacade : reservar
    ComandoRenovacao ..> CirculacaoFacade : renovar
```

## 7. Template Method

```mermaid
classDiagram
    class CadastroBase {
      <<AbstractClass>>
      +incluir(dados) ResultadoCadastro
      #_buscar_existente(repositorio, dados)*
      #_validar(dados)*
      #_verificar_pre_requisitos(repositorio, dados)
      #_criar(dados)*
      #_armazenar(repositorio, entidade)*
      #_apresentar(entidade, ja_existia)
    }
    CadastroBase <|-- CadastroPessoa
    CadastroBase <|-- CadastroEstudante
    CadastroBase <|-- CadastroAtendente
    CadastroBase <|-- CadastroLivro
    class iPessoa { <<interface>> }
    class iEstudante { <<interface>> }
    class iAtendente { <<interface>> }
    class iLivro { <<interface>> }
    iPessoa <|.. TratadorDePessoa
    iEstudante <|.. TratadorDeEstudante
    iAtendente <|.. TratadorDeAtendente
    iLivro <|.. TratadorDeAcervo
    TratadorDePessoa ..> CadastroPessoa
    TratadorDeEstudante ..> CadastroEstudante
    TratadorDeAtendente ..> CadastroAtendente
    TratadorDeAcervo ..> CadastroLivro
```

## 8. Abstract Factory

```mermaid
classDiagram
    class FabricaPersistencia {
      <<FabricaAbstrata>>
      +criar_unidade_trabalho() UnidadeTrabalho
      +criar_acervo(uow) Acervo
      +criar_movimentacao(uow) Movimentacao
      +criar_relacionamento(uow) Relacionamento
      +criar_financeiro(uow) Financeiro
    }
    FabricaPersistencia <|-- FabricaMemoria
    FabricaPersistencia <|-- FabricaMySQL
    UnidadeTrabalho <|-- UnidadeTrabalhoMemoria
    UnidadeTrabalho <|-- UnidadeTrabalhoMySQL
    Acervo <|-- AcervoMemoria
    Acervo <|-- AcervoMySQL
    Movimentacao <|-- MovimentacaoMemoria
    Movimentacao <|-- MovimentacaoMySQL
    Relacionamento <|-- RelacionamentoMemoria
    Relacionamento <|-- RelacionamentoMySQL
    FabricaMemoria ..> UnidadeTrabalhoMemoria
    FabricaMemoria ..> AcervoMemoria
    FabricaMemoria ..> MovimentacaoMemoria
    FabricaMemoria ..> RelacionamentoMemoria
    FabricaMySQL ..> UnidadeTrabalhoMySQL
    FabricaMySQL ..> AcervoMySQL
    FabricaMySQL ..> MovimentacaoMySQL
    FabricaMySQL ..> RelacionamentoMySQL
```

`Financeiro`, `FinanceiroMemoria` e `FinanceiroMySQL` seguem o mesmo desenho.

## 9. Decorator

```mermaid
classDiagram
    class ConsultaAcervo {
      <<Componente>>
      +consultar(livro_id) MetadadosLivro
    }
    class DecoradorConsulta {
      <<Decorador>>
    }
    ConsultaAcervo <|-- ConsultaBase
    ConsultaAcervo <|-- DecoradorConsulta
    DecoradorConsulta o--> "1" ConsultaAcervo : componente
    DecoradorConsulta <|-- ConsultaComCache
    DecoradorConsulta <|-- ConsultaComMedicao
    TratadorDeAcervo --> ConsultaAcervo
```

## 10. Composite

```mermaid
classDiagram
    class ComponenteAcervo {
      <<Componente>>
      +pai
      +contar_livros() int
      +listar_livros() list
    }
    class GrupoAcervo {
      +nome
      +adicionar(componente)
      +remover(componente)
    }
    class ItemLivro {
      +livro_id
    }
    ComponenteAcervo <|-- GrupoAcervo
    ComponenteAcervo <|-- ItemLivro
    GrupoAcervo o--> "0..*" ComponenteAcervo : filhos
```

## 11. Singleton

```mermaid
classDiagram
    class ConfiguracaoSistema {
      <<singleton>>
      -_instancia$
      +obter_instancia()$ ConfiguracaoSistema
      +perfil_persistencia
      +politica_multa
      +banco_cobranca
    }
```

## Sequência: efetivar empréstimo (R04)

```mermaid
sequenceDiagram
    actor Estudante
    Estudante->>Rota: POST /circulacao (emprestar)
    Rota->>TratadorDeEmprestimo: realizar_emprestimo(estudante, livro)
    TratadorDeEmprestimo->>CirculacaoFacade: emprestar(estudante, livro)
    CirculacaoFacade->>UnidadeTrabalho: iniciar transação
    CirculacaoFacade->>Acervo: obter(livro, para_atualizar)
    CirculacaoFacade->>Movimentacao: consultar_reserva(livro, estudante)
    CirculacaoFacade->>Movimentacao: remover_reserva(reserva)
    CirculacaoFacade->>Livro: emprestar(hoje)
    Livro->>EstadoReservado: emprestar(livro, hoje)
    CirculacaoFacade->>Movimentacao: inserir_emprestimo(livro, estudante, hoje)
    CirculacaoFacade->>Acervo: atualizar(livro)
    CirculacaoFacade->>UnidadeTrabalho: commit (ou rollback se algo falhou)
    CirculacaoFacade-->>Rota: Comprovante
```

## Sequência: devolução atrasada (R05, R02, R03)

```mermaid
sequenceDiagram
    actor Atendente
    Atendente->>Rota: POST /circulacao (devolver, data)
    Rota->>TratadorDeDevolucao: registrar_devolucao(livro, data)
    TratadorDeDevolucao->>CirculacaoFacade: devolver(livro, data)
    CirculacaoFacade->>Livro: devolver()
    CirculacaoFacade->>Movimentacao: registrar_devolucao(emprestimo, data)
    CirculacaoFacade->>UnidadeTrabalho: commit
    CirculacaoFacade->>PublicadorDevolucao: publicar(evento)
    PublicadorDevolucao->>OuvinteInspecao: notificar(evento)
    PublicadorDevolucao->>OuvinteMulta: notificar(evento)
    OuvinteMulta->>ServicoMulta: emitir_multa(evento)
    ServicoMulta->>PoliticaMulta: calcular(dias_atraso)
    ServicoMulta->>CobrancaInstitucional: emitir_boleto(solicitacao)
    PublicadorDevolucao->>OuvinteIndicadores: notificar(evento)
    PublicadorDevolucao->>OuvinteEmail: notificar(evento)
    CirculacaoFacade-->>Rota: Comprovante
```

## Sequência: renovação com Command (R06)

```mermaid
sequenceDiagram
    Rota->>TratadorDeEmprestimo: renovar_emprestimo(estudante, livro, autor, id)
    TratadorDeEmprestimo->>ComandoRenovacao: criar(id, autor, instante)
    TratadorDeEmprestimo->>ExecutorComandos: executar(comando)
    ExecutorComandos->>Movimentacao: registrar_comando(id)
    alt id novo
        ExecutorComandos->>ComandoRenovacao: executar(uow)
        ComandoRenovacao->>CirculacaoFacade: renovar(estudante, livro, uow)
        ExecutorComandos->>Movimentacao: gravar_resultado_comando(id, comprovante)
    else id repetido
        ExecutorComandos->>Movimentacao: resultado_comando(id)
    end
    ExecutorComandos-->>TratadorDeEmprestimo: Comprovante
```
