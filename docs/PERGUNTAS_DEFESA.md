# Perguntas prováveis na arguição

Respostas curtas, com o lugar exato no código. As perguntas marcadas com ★ são as que o
enunciado lista em "Na arguição, saiba explicar".

## State (R01)

- ★ **Onde está a guarda da renovação e por que vem antes do vencimento?**
  Em `_renovar`, `dominio/estados.py`, chamada por `EstadoEmprestado.renovar` e `EstadoRenovado.renovar`.
  Vem antes porque, se o vencimento fosse alterado primeiro, a terceira tentativa ganharia 30 dias antes de ser recusada.
- ★ **O que acontece quando um evento chega a um estado que não o aceita?**
  `EstadoLivro._recusar` lança `TransicaoInvalida`. O livro não muda, a transação faz rollback e a tela mostra a mensagem.
- ★ **Como o estado é gravado e reconstituído?**
  Grava-se `livro.nome_estado` na coluna `livro.estado` (`AcervoMySQL.inserir`/`atualizar`). Ao ler, `_livro` em `persistencia/mysql.py` chama `estado_por_nome`.
- **Diferença entre State e Strategy?**
  A estrutura é parecida. No State, os próprios estados trocam o estado do contexto e o cliente não escolhe. No Strategy, quem escolhe a estratégia é a configuração, e uma estratégia não conhece as outras.

## Strategy (R02)

- ★ **Como incluir uma política sem alterar o serviço de multas?**
  Nova subclasse de `PoliticaMulta` e uma entrada em `POLITICAS` (`dominio/multas_strategy.py`). `ServicoMulta` só chama `politica.calcular`.
- ★ **Por que a troca de política não recalcula multas emitidas?**
  `Financeiro.inserir_multa` grava `valor` e `politica`. Nenhum código relê a política para multas existentes.
- ★ **Como são calculados os dias de atraso e os valores?**
  Dias: `EventoDevolucao.dias_atraso` = data da devolução − vencimento, mínimo zero. Valores: `Decimal` com duas casas (`quantize`), nunca `float`.

## Adapter (R03)

- ★ **Onde ficam as conversões de cada banco?**
  Em `AdaptadorBancoA.emitir_boleto`/`traduzir_notificacao` e nos mesmos métodos de `AdaptadorBancoB`.
- ★ **Como o banco da instalação é escolhido?**
  `BANCO_COBRANCA` no `.env` → `ConfiguracaoSistema.banco_cobranca` → `criar_cobranca`, chamada uma vez em `montar_sistema`.
- ★ **Como a quitação é protegida contra notificações repetidas?**
  Tabela `quitacao`: `id_notificacao` é chave primária e `multa_id` é único. `registrar_quitacao` devolve `False` na repetição.
- **Por que o Adapter não é o banco de dados?**
  `BancoA` e `BancoB` simulam instituições financeiras externas. O MySQL é a persistência e fica atrás da Abstract Factory.

## Facade (R04)

- ★ **Quais classes a fachada coordena e em que ordem?**
  Em `CirculacaoFacade.emprestar`: `Acervo` (lê o livro) → `Movimentacao` (valida e remove a reserva) → `Livro.emprestar` → `Movimentacao` (insere o empréstimo) → `Acervo` (atualiza). `Relacionamento` entra em `reservar` e `devolver`.
- ★ **O que é desfeito se um passo falhar?**
  Tudo. A unidade de trabalho faz rollback (`UnidadeTrabalho.__exit__`): a reserva volta e o livro continua RESERVADO.
- ★ **Por que a interface não acessa Movimentacao diretamente?**
  Para que nenhuma tela consiga, por exemplo, remover a reserva sem criar o empréstimo. A interface só conhece os tratadores.
- **Onde ficam as transações?**
  Em `persistencia/unidade_trabalho.py`. Quem abre é a fachada, o executor de comandos, o cadastro ou o serviço de multas, sempre com `with fabrica.criar_unidade_trabalho()`.

## Observer (R05)

- ★ **Como incluir um ouvinte sem alterar o tratador?**
  Nova subclasse de `OuvinteDevolucao` e um `publicador.registrar(...)` em `montar_sistema`.
- ★ **O que acontece quando o e-mail falha?**
  `PublicadorDevolucao.publicar` captura o erro, guarda em `falhas`, registra no log e chama o próximo ouvinte. A devolução já estava confirmada.
- ★ **Por que o evento leva os dados?**
  Quando o ouvinte roda, o livro pode já ter mudado. `EventoDevolucao` é imutável e traz estudante, vencimento e data da devolução daquele momento.
- **Por que publicar só depois do commit?**
  Para ninguém reagir a uma devolução que pode ser desfeita. Está no fim de `CirculacaoFacade.devolver`, fora do bloco `with`.

## Command (R06)

- ★ **Quem cria, quem invoca e quem executa?**
  Cria: `TratadorDeEmprestimo` (com os dados da tela). Invoca: `ExecutorComandos.executar`. Executa: `CirculacaoFacade` (alvo), chamada por `comando.executar`.
- ★ **Como a repetição é detectada com duas submissões simultâneas?**
  O id é chave primária de `comando_executado` e o `INSERT` fica na mesma transação do efeito. A segunda transação espera a primeira, falha por duplicidade e devolve o comprovante gravado.
- ★ **Por que não há desfazer?**
  As regras do Trabalho 02 não preveem cancelamento de reserva nem de renovação, e o estudante já recebeu a resposta.

## Template Method (R07)

- ★ **Quais passos são fixos e quais variam?**
  Fixa é a ordem em `CadastroBase.incluir`. Variam `_buscar_existente`, `_validar`, `_criar` e `_armazenar` em cada subclasse.
- ★ **O que é um gancho e onde é usado?**
  Passo com implementação padrão que a subclasse pode sobrescrever. `_verificar_pre_requisitos` (vazio na base, usado por Estudante e Atendente) e `_apresentar`.
- ★ **Por que a falha do pré-requisito não permite gravação parcial?**
  O pré-requisito roda antes de `_armazenar`, e tudo está numa transação que faz rollback.

## Abstract Factory (R08)

- ★ **Onde a família é escolhida?**
  `criar_fabrica`, chamada uma vez em `criar_app` (`app.py`), a partir de `PERSISTENCE_PROFILE`.
- ★ **Como os repositórios compartilham a transação?**
  Todos recebem a mesma `UnidadeTrabalhoMySQL` e guardam `uow.conexao`.
- ★ **O que impede misturar memória com MySQL?**
  O construtor de cada repositório confere o tipo da unidade (`_RepositorioMySQL.__init__`, `_RepositorioMemoria.__init__`) e lança `TypeError`.

## Decorator (R09)

- ★ **Como a cadeia é montada e por que a ordem importa?**
  Em `montar_sistema`: medição por fora, cache por dentro. Assim a consulta atendida pelo cache também é medida. Invertendo, o cache responde antes e a medição não vê.
- ★ **O que acontece se o cache falhar?**
  `ConsultaComCache.consultar` captura o erro e chama a consulta original.
- ★ **Por que o cache não participa da reserva?**
  `MetadadosLivro` não tem estado, e `CirculacaoFacade.reservar` lê o livro no `Acervo` com bloqueio de linha.

## Composite (R10)

- ★ **Como a contagem percorre a árvore?**
  `GrupoAcervo.contar_livros` soma `contar_livros()` de cada filho; o item devolve 1.
- ★ **Quais regras impedem ciclos e livros em dois grupos?**
  As duas checagens em `GrupoAcervo.adicionar`. No MySQL, o livro tem uma só coluna `grupo_id`.
- ★ **Por que mover um item não toca no Livro nem na Movimentacao?**
  O item guarda só o id, e `mover_livro` grava apenas `grupo_id`.

## Singleton (R11)

- **Por que usar Singleton aqui?** Para todos lerem a mesma política de multa e o mesmo perfil.
- **Por que a conexão do banco não é Singleton, como no slide?** Uma conexão global misturaria transações de requisições diferentes. Cada operação abre e fecha a sua.
- **Qual o limite?** Uma instância por processo; com vários workers, cada um tem a sua.

## Segurança

- **Como a senha é guardada?** Só o hash (`generate_password_hash` em `TratadorDeAcesso.criar_usuario`).
- **Como evitam SQL injection?** Todo SQL usa `%s` com parâmetros (`_RepositorioMySQL._executar`).
- **O que protege os formulários?** Token CSRF em todo POST (`CSRFProtect` em `app.py`) e login exigido no servidor (`exigir_login` em `web/rotas.py`).
