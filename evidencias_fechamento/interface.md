# Verificação manual de interface — 13/11/2026

Navegador real, Flask sem debug, MySQL isolado biblioteca_gof_fechamento_ui_20261113.

1. Login de teste aceito, painel e Circulação carregados.
2. Reserva sem atendente recusada; livro continuou LIVRE.
3. Reserva com AS (mesma Pessoa de E1) recusada; livro continuou LIVRE.
4. Reserva E1/L1 com A1: RESERVADO; comprovante Atendente: A1.
5. Empréstimo com A2: EMPRESTADO; vencimento 13/12/2026; comprovante A2.
6. Renovação: RENOVADO, vencimento 12/01/2027, contador 1.
7. Devolução em 17/01/2027 com A1: DEVOLVIDO, atraso 5 dias; comprovante A1.
8. Multa original R$ 5,00 e boleto visíveis. Pagamento simulado confirmou quitação.
9. Inspeção bom estado: LIVRE.
10. Conexão SQL independente confirmou os três responsáveis A1/A2/A1, multa de 5,00 quitada e uma quitação.
11. Servidor temporário encerrado. Projeto original corrigido iniciado na porta 5057, banco biblioteca_gof. Recarga do navegador exigiu login, como esperado para sessão de teste de outra configuração.

Captura: devolucao-responsavel.png. Dados SQL e migração: migracao-e-ui.json. Pagamento é simulado, sem movimentação financeira real. Testes automatizados cobrem replay de pagamento; não foi necessário um segundo clique manual na UI.
