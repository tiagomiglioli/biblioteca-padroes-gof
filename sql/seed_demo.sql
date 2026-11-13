-- Dados FICTÍCIOS para a demonstração. Pode rodar várias vezes (INSERT IGNORE).
-- O usuário de login NÃO está aqui: crie com  flask --app app criar-usuario admin

INSERT IGNORE INTO pessoa (cpf, nome, sobrenome, email) VALUES
    ('11122233344', 'Ana', 'Silva', 'ana.silva@exemplo.com'),
    ('55566677788', 'Bruno', 'Souza', 'bruno.souza@exemplo.com'),
    ('99988877766', 'Carla', 'Lima', 'carla.lima@exemplo.com');

INSERT IGNORE INTO estudante (id, cpf) VALUES ('E1', '11122233344'), ('E2', '55566677788');

INSERT IGNORE INTO atendente (id, cpf) VALUES ('A1', '99988877766');

INSERT IGNORE INTO grupo_acervo (id, nome, pai_id) VALUES
    (1, 'Unidade Centro', NULL),
    (2, 'Exatas', 1),
    (3, 'Humanas', 1),
    (4, 'Computação', 2);

INSERT IGNORE INTO livro (id, titulo, estado, grupo_id) VALUES
    ('L1', 'Padrões de Projeto', 'LIVRE', 4),
    ('L2', 'Engenharia de Software', 'LIVRE', 4),
    ('L3', 'Cálculo Volume 1', 'LIVRE', 2),
    ('L4', 'Dom Casmurro', 'LIVRE', 3),
    ('L5', 'Sapiens', 'LIVRE', 3);
