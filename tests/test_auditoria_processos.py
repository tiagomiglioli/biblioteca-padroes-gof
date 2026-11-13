"""Comando idempotente e persistência entre processos Python realmente distintos."""
import json
import os
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from tests.apoio import HOJE, emprestar, livro_no_banco, sistema_pronto

FILHO = """
import json, sys
from config import parametros_mysql
from dominio.persistencia_factory import FabricaMySQL
from dominio.configuracao_singleton import ConfiguracaoSistema
from dominio.tratadores import montar_sistema
s = montar_sistema(FabricaMySQL(parametros_mysql()), ConfiguracaoSistema.obter_instancia())
c = s.emprestimo.renovar_emprestimo('E1', 'L1', 'auditoria', sys.argv[1])
print(c.para_texto())
"""


def test_mysql_mesmo_comando_em_quatro_processos_renova_uma_vez(fabrica_mysql, mysql_preparado):
    sistema = sistema_pronto(fabrica_mysql)
    emprestar(sistema)
    ambiente = os.environ.copy()
    for campo in ('host', 'port', 'user', 'password', 'database'):
        ambiente['MYSQL_' + campo.upper()] = str(mysql_preparado[campo])
    ambiente['PYTHONDONTWRITEBYTECODE'] = '1'
    identificador = str(uuid.uuid4())

    def executar(_):
        resultado = subprocess.run([sys.executable, '-B', '-c', FILHO, identificador],
                                   env=ambiente, capture_output=True, text=True, timeout=20)
        assert resultado.returncode == 0, resultado.stderr
        return json.loads(resultado.stdout)

    with ThreadPoolExecutor(max_workers=4) as pool:
        respostas = list(pool.map(executar, range(4)))
    assert all(resposta == respostas[0] for resposta in respostas)
    livro = livro_no_banco(fabrica_mysql)
    assert livro.num_renovacoes == 1
    assert livro.vencimento == HOJE + timedelta(days=60)
