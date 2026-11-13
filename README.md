# Biblioteca GoF

Sistema web de cadastro, reserva, empréstimo, renovação e devolução de livros,
com os dez padrões GoF do enunciado mais o Singleton pedido pelo professor.

PUCPR · Modelagem de Sistemas Computacionais · Prof. Edson Emílio Scalabrin · 2º semestre de 2026.

Python orientado a objetos (autorizado pelo professor), Flask + Jinja2, Flask-Login,
MySQL (InnoDB) e pytest. Um único servidor, sem build de frontend.

## Como rodar

Pré-requisitos: Python 3.12 ou mais novo e um MySQL 8 ou mais novo em execução.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # preencha SECRET_KEY, MYSQL_USER e MYSQL_PASSWORD
```

O usuário do MySQL precisa poder criar os bancos `biblioteca_gof` e `biblioteca_gof_teste`.
Se preferir um usuário próprio em vez do `root`, rode uma vez, como administrador do MySQL:

```sql
CREATE USER 'biblioteca'@'localhost' IDENTIFIED BY 'escolha-uma-senha';
GRANT ALL PRIVILEGES ON biblioteca_gof.* TO 'biblioteca'@'localhost';
GRANT ALL PRIVILEGES ON biblioteca_gof_teste.* TO 'biblioteca'@'localhost';
```

Depois:

```bash
flask --app app init-db              # cria o banco e as tabelas (sql/schema.sql)
flask --app app seed-demo            # dados fictícios (sql/seed_demo.sql)
flask --app app criar-usuario admin  # pede a senha no terminal; grava só o hash
flask --app app run                  # http://127.0.0.1:5000
```

Não há usuário nem senha embutidos no código: a credencial de demonstração é a que
você digitar em `criar-usuario`, e vale só para o seu banco local.

## Como rodar os testes

Um comando:

```bash
python -m pytest -q
```

- Os testes de cada requisito ficam em `tests/test_rNN_*.py` e o nome de cada teste
  começa pelo requisito, por exemplo `test_r01_terceira_renovacao_recusada_sem_alterar_vencimento`.
- Os testes que usam persistência rodam **duas vezes**: na família em memória e na família MySQL.
- Os testes MySQL usam o banco `MYSQL_TEST_DATABASE` (padrão `biblioteca_gof_teste`), que é
  esvaziado a cada teste. Nunca aponte essa variável para o banco da demonstração.
- Sem MySQL acessível, as variantes MySQL aparecem como `skipped`, não como aprovadas.

Só os dez cenários do enunciado mais o Singleton:

```bash
python -m pytest -q tests/test_r01_state.py tests/test_r02_strategy.py tests/test_r03_adapter.py \
  tests/test_r04_facade.py tests/test_r05_observer.py tests/test_r06_command.py \
  tests/test_r07_template_method.py tests/test_r08_abstract_factory.py \
  tests/test_r09_decorator.py tests/test_r10_composite.py tests/test_r11_singleton.py
```

## Como simular datas (atraso e multa)

Ninguém mexe no relógio da máquina. Na tela **Circulação**, a operação
"Registrar devolução" tem o campo **Data da devolução**: informe uma data depois do
vencimento e a multa é gerada. Nos testes, a data de "hoje" é injetada (`relogio`).

## Organização

| Pasta | O que tem | O que NÃO tem |
|---|---|---|
| `templates/`, `static/`, `web/` | páginas, formulários, rotas que chamam tratadores | regras da biblioteca |
| `dominio/` | entidades, regras e os padrões GoF | SQL, HTML |
| `persistencia/` | repositórios em memória e MySQL, unidade de trabalho | decisões de negócio |
| `sql/` | `schema.sql` e `seed_demo.sql` | |
| `tests/` | um arquivo por requisito, autenticação, fluxo web, MySQL | |
| `docs/` | rastreabilidade, guia de defesa, perguntas, UML, roteiro da demo | |

Fluxo de uma operação:
**HTML → rota Flask → tratador → fachada/serviço → domínio + repositórios → MySQL → comprovante → HTML**.

## Onde está cada padrão

| Nº | Padrão | Arquivo | Teste |
|---|---|---|---|
| R01 | State | `dominio/estados.py`, `dominio/entidades.py` (`Livro`) | `tests/test_r01_state.py` |
| R02 | Strategy | `dominio/multas_strategy.py` | `tests/test_r02_strategy.py` |
| R03 | Adapter | `dominio/bancos_adapter.py` | `tests/test_r03_adapter.py` |
| R04 | Facade | `dominio/circulacao_facade.py` | `tests/test_r04_facade.py` |
| R05 | Observer | `dominio/devolucao_observer.py` | `tests/test_r05_observer.py` |
| R06 | Command | `dominio/circulacao_command.py` | `tests/test_r06_command.py` |
| R07 | Template Method | `dominio/cadastros_template.py` | `tests/test_r07_template_method.py` |
| R08 | Abstract Factory | `dominio/persistencia_factory.py`, `persistencia/` | `tests/test_r08_abstract_factory.py` |
| R09 | Decorator | `dominio/consulta_decorator.py` | `tests/test_r09_decorator.py` |
| R10 | Composite | `dominio/acervo_composite.py` | `tests/test_r10_composite.py` |
| R11 | Singleton | `dominio/configuracao_singleton.py` | `tests/test_r11_singleton.py` |

Detalhes em `docs/RASTREABILIDADE.md`; explicações para a arguição em `docs/GUIA_DEFESA.md`
e `docs/PERGUNTAS_DEFESA.md`; roteiro da apresentação em `docs/DEMO_5_MINUTOS.md`.

## Decisões que valem explicar

- **Sem desfazer no Command.** Reserva e renovação não têm cancelamento nas regras do
  Trabalho 02, e o estudante já recebeu a resposta; por isso os comandos só têm `executar`.
- **Conexão MySQL não é Singleton.** O slide do professor usa `GerenciadorBD` como exemplo
  de Singleton. Aqui o Singleton é a `ConfiguracaoSistema`. Cada operação abre a sua conexão
  (unidade de trabalho) e a fecha no fim: uma conexão global compartilhada misturaria as
  transações de requisições diferentes e impediria o rollback de uma só operação.
- **Política de multa e banco de cobrança** começam com o valor do `.env`. A política pode ser
  trocada na tela Multas; a troca vale no processo em execução e volta ao `.env` ao reiniciar.
- **Oracle** é réplica no Trabalho 02: a aplicação não tem família Oracle e não escreve nele.
- **Prazo do empréstimo: 30 dias.** O Trabalho 02 só fixa os 30 dias de cada renovação; o prazo
  inicial foi assumido igual. Está em `PRAZO_EMPRESTIMO_DIAS`, em `dominio/estados.py`.

## Segurança

- Senhas: só o hash (`werkzeug.security`, scrypt) é gravado; mínimo de 8 caracteres.
- SQL: todos os comandos usam parâmetros `%s`; há testes com tentativas de injeção.
- Sessão: cookie assinado, `HttpOnly`, `SameSite=Lax`, `Secure` quando `SESSION_COOKIE_SECURE=1`;
  `SECRET_KEY` obrigatória e só no `.env`; sessão renovada a cada login; logout só por POST.
- CSRF: todo formulário POST leva token (Flask-WTF).
- Autorização: todas as rotas exigem login, verificado no servidor.
- Limite conhecido: não há bloqueio por excesso de tentativas de login. Para uso real,
  acrescente um limitador (por exemplo, Flask-Limiter) e HTTPS.

## Uso de LLM

Código, testes e documentação foram gerados com **Claude Code (Anthropic), modelo
Claude Fable 5.2**, a partir do enunciado, do Trabalho 02, dos slides e dos exemplos do
professor. Todas as partes do sistema tiveram participação do modelo. O que foi pedido,
aceito, corrigido e descartado está em `REGISTRO_LLM.md`. A equipe é responsável por
entender e explicar todo o código.
