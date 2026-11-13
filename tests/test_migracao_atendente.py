"""Migração expansiva: legado intacto e retomada idempotente."""
import pytest
import mysql.connector


@pytest.mark.parametrize("parcial", [False, True])
def test_migracao_preserva_legado_e_pode_ser_repetida(fabrica_mysql, mysql_preparado, parcial, monkeypatch):
    from persistencia.migracoes import migrar_atendentes

    conexao = mysql.connector.connect(**mysql_preparado)
    cursor = conexao.cursor()
    try:
        for tabela, coluna, fk in (
            ("reserva", "atendente_id", "fk_reserva_atendente"),
            ("emprestimo", "atendente_id", "fk_emprestimo_atendente"),
            ("emprestimo", "atendente_devolucao_id", "fk_devolucao_atendente"),
        ):
            cursor.execute(f"ALTER TABLE {tabela} DROP FOREIGN KEY {fk}")
            cursor.execute(f"ALTER TABLE {tabela} DROP COLUMN {coluna}")
        cursor.execute("INSERT INTO pessoa VALUES ('12345678901', 'Legado', 'Teste', 'legado@exemplo.com')")
        cursor.execute("INSERT INTO estudante VALUES ('E', '12345678901')")
        cursor.execute("INSERT INTO livro (id,titulo,estado) VALUES ('L','Legado','LIVRE')")
        cursor.execute("INSERT INTO reserva (livro_id,estudante_id,data,ativa) VALUES ('L','E','2026-11-01',0)")
        cursor.execute("INSERT INTO emprestimo (livro_id,estudante_id,data_emprestimo,data_devolucao)"
                       " VALUES ('L','E','2026-11-01','2026-11-02')")
        conexao.commit()
        if parcial:
            conectar = mysql.connector.connect

            class CursorComFalha:
                def __init__(self, real):
                    self.real = real

                def __getattr__(self, nome):
                    return getattr(self.real, nome)

                def execute(self, sql, *args):
                    if "ADD CONSTRAINT" in sql:
                        raise RuntimeError("falha após adicionar a primeira coluna")
                    return self.real.execute(sql, *args)

            class ConexaoComFalha:
                def __init__(self, **kwargs):
                    self.real = conectar(**kwargs)

                def __getattr__(self, nome):
                    return getattr(self.real, nome)

                def cursor(self):
                    return CursorComFalha(self.real.cursor())

            with monkeypatch.context() as patch:
                patch.setattr(mysql.connector, "connect", ConexaoComFalha)
                with pytest.raises(RuntimeError, match="primeira coluna"):
                    migrar_atendentes(mysql_preparado)
        migrar_atendentes(mysql_preparado)
        migrar_atendentes(mysql_preparado)
        cursor.execute("SELECT livro_id,estudante_id,ativa,atendente_id FROM reserva")
        assert cursor.fetchall() == [("L", "E", 0, None)]
        cursor.execute("SELECT livro_id,estudante_id,atendente_id,atendente_devolucao_id FROM emprestimo")
        assert cursor.fetchall() == [("L", "E", None, None)]
        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute("UPDATE reserva SET atendente_id='INEXISTENTE'")
    finally:
        conexao.rollback()
        cursor.close()
        conexao.close()
