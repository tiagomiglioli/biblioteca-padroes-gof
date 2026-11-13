-- Esquema da biblioteca (MySQL / InnoDB). Idempotente: pode rodar várias vezes.

CREATE TABLE IF NOT EXISTS usuario (
    login       VARCHAR(50)  PRIMARY KEY,
    senha_hash  VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pessoa (
    cpf        CHAR(11)     PRIMARY KEY,
    nome       VARCHAR(80)  NOT NULL,
    sobrenome  VARCHAR(80)  NOT NULL,
    email      VARCHAR(120) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudante (
    id   VARCHAR(20) PRIMARY KEY,
    cpf  CHAR(11)    NOT NULL,
    CONSTRAINT fk_estudante_pessoa FOREIGN KEY (cpf) REFERENCES pessoa (cpf)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS atendente (
    id   VARCHAR(20) PRIMARY KEY,
    cpf  CHAR(11)    NOT NULL,
    CONSTRAINT fk_atendente_pessoa FOREIGN KEY (cpf) REFERENCES pessoa (cpf)
) ENGINE=InnoDB;

-- Composite (R10): unidade > seção > subseção, em qualquer profundidade.
CREATE TABLE IF NOT EXISTS grupo_acervo (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    nome    VARCHAR(100) NOT NULL,
    pai_id  INT NULL,
    CONSTRAINT fk_grupo_pai FOREIGN KEY (pai_id) REFERENCES grupo_acervo (id)
) ENGINE=InnoDB;

-- State (R01): a coluna estado guarda o NOME do estado e o objeto é reconstituído ao ler.
-- Uma única coluna grupo_id: o mesmo livro não cabe em dois grupos.
CREATE TABLE IF NOT EXISTS livro (
    id              VARCHAR(20)  PRIMARY KEY,
    titulo          VARCHAR(200) NOT NULL,
    estado          VARCHAR(12)  NOT NULL,
    num_renovacoes  INT          NOT NULL DEFAULT 0,
    vencimento      DATE         NULL,
    grupo_id        INT          NULL,
    CONSTRAINT fk_livro_grupo FOREIGN KEY (grupo_id) REFERENCES grupo_acervo (id)
) ENGINE=InnoDB;

-- ativa = 1 é reserva em vigor, ativa = 0 é histórico (já virou empréstimo).
CREATE TABLE IF NOT EXISTS reserva (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    livro_id      VARCHAR(20) NOT NULL,
    estudante_id  VARCHAR(20) NOT NULL,
    data          DATE        NOT NULL,
    ativa         TINYINT(1)  NOT NULL DEFAULT 1,
    CONSTRAINT fk_reserva_livro FOREIGN KEY (livro_id) REFERENCES livro (id),
    CONSTRAINT fk_reserva_estudante FOREIGN KEY (estudante_id) REFERENCES estudante (id)
) ENGINE=InnoDB;

-- data_devolucao NULL é empréstimo em aberto, preenchida é devolução registrada.
CREATE TABLE IF NOT EXISTS emprestimo (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    livro_id         VARCHAR(20) NOT NULL,
    estudante_id     VARCHAR(20) NOT NULL,
    data_emprestimo  DATE        NOT NULL,
    data_devolucao   DATE        NULL,
    CONSTRAINT fk_emprestimo_livro FOREIGN KEY (livro_id) REFERENCES livro (id),
    CONSTRAINT fk_emprestimo_estudante FOREIGN KEY (estudante_id) REFERENCES estudante (id)
) ENGINE=InnoDB;

-- Strategy (R02): valor e política ficam gravados na emissão.
-- Adapter (R03): banco + id_boleto identificam o boleto no banco externo.
CREATE TABLE IF NOT EXISTS multa (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    emprestimo_id  INT           NOT NULL,
    estudante_id   VARCHAR(20)   NOT NULL,
    dias_atraso    INT           NOT NULL,
    valor          DECIMAL(10,2) NOT NULL,
    politica       VARCHAR(30)   NOT NULL,
    quitada        TINYINT(1)    NOT NULL DEFAULT 0,
    banco          VARCHAR(20)   NULL,
    id_boleto      VARCHAR(60)   NULL,
    CONSTRAINT uq_multa_emprestimo UNIQUE (emprestimo_id),
    CONSTRAINT uq_multa_boleto UNIQUE (banco, id_boleto),
    CONSTRAINT fk_multa_emprestimo FOREIGN KEY (emprestimo_id) REFERENCES emprestimo (id),
    CONSTRAINT fk_multa_estudante FOREIGN KEY (estudante_id) REFERENCES estudante (id)
) ENGINE=InnoDB;

-- Notificação repetida do banco esbarra na PRIMARY KEY e a segunda quitação da mesma multa, no UNIQUE.
CREATE TABLE IF NOT EXISTS quitacao (
    id_notificacao  VARCHAR(80) PRIMARY KEY,
    multa_id        INT         NOT NULL,
    CONSTRAINT uq_quitacao_multa UNIQUE (multa_id),
    CONSTRAINT fk_quitacao_multa FOREIGN KEY (multa_id) REFERENCES multa (id)
) ENGINE=InnoDB;

-- Command (R06): o id da solicitação é PRIMARY KEY, então a mesma solicitação não executa duas vezes.
CREATE TABLE IF NOT EXISTS comando_executado (
    id         CHAR(36)    PRIMARY KEY,
    tipo       VARCHAR(40) NOT NULL,
    autor      VARCHAR(50) NOT NULL,
    criado_em  DATETIME    NOT NULL,
    resultado  TEXT        NULL
) ENGINE=InnoDB;
