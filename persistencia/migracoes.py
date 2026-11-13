"""Migração aditiva: histórico sem responsável conhecido permanece NULL.

DDL MySQL confirma cada ALTER; consultar o catálogo permite retomar após falha.
Rollback é voltar o código anterior, preservando as colunas e os dados novos.
Execute uma migração por vez, antes de iniciar a versão nova da aplicação.
"""
import mysql.connector


def migrar_atendentes(parametros):
    """Adiciona responsáveis e FKs ausentes; não apaga nem inventa dados legados."""
    conexao = mysql.connector.connect(**parametros)
    try:
        cursor = conexao.cursor()
        try:
            for tabela, coluna, restricao in (
                ("reserva", "atendente_id", "fk_reserva_atendente"),
                ("emprestimo", "atendente_id", "fk_emprestimo_atendente"),
                ("emprestimo", "atendente_devolucao_id", "fk_devolucao_atendente"),
            ):
                cursor.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE()"
                               " AND table_name = %s AND column_name = %s", (tabela, coluna))
                if not cursor.fetchone():
                    cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} VARCHAR(20) NULL")
                cursor.execute("SELECT 1 FROM information_schema.table_constraints"
                               " WHERE constraint_schema = DATABASE() AND table_name = %s"
                               " AND constraint_name = %s", (tabela, restricao))
                if not cursor.fetchone():
                    cursor.execute(f"ALTER TABLE {tabela} ADD CONSTRAINT {restricao}"
                                   f" FOREIGN KEY ({coluna}) REFERENCES atendente (id)")
            conexao.commit()
        finally:
            cursor.close()
    finally:
        conexao.close()
