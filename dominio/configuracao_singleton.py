"""R11 — GoF Singleton: configuração única da execução."""
import os
import threading


class ConfiguracaoSistema:
    """GoF Singleton: uma única configuração por processo Python.

    Evita que partes do sistema enxerguem políticas de multa ou perfis de
    persistência diferentes. Guarda só opções simples e não sensíveis.
    NÃO guarda conexão com o banco: cada operação abre a sua unidade de
    trabalho (ver persistencia/unidade_trabalho.py).
    Limite: cada processo/worker do servidor tem a sua própria instância.
    """

    _instancia = None
    _trava = threading.Lock()
    _CHAVE = object()          # só obter_instancia() conhece: faz o papel do construtor privado

    def __init__(self, chave=None):
        if chave is not ConfiguracaoSistema._CHAVE:
            raise TypeError("Use ConfiguracaoSistema.obter_instancia().")
        # O ambiente é lido uma única vez, aqui. Mudanças posteriores só por atribuição explícita.
        self.perfil_persistencia = os.environ.get("PERSISTENCE_PROFILE", "mysql")
        self.politica_multa = os.environ.get("POLITICA_MULTA", "original")
        self.banco_cobranca = os.environ.get("BANCO_COBRANCA", "A")

    @classmethod
    def obter_instancia(cls):
        """Ponto de acesso global; cria a instância na primeira chamada."""
        # A trava impede que duas threads criem duas instâncias ao mesmo tempo.
        with cls._trava:
            if cls._instancia is None:
                cls._instancia = cls(cls._CHAVE)
            return cls._instancia

    @classmethod
    def reiniciar_para_testes(cls):
        """Descarta a instância para que cada teste comece com configuração conhecida."""
        with cls._trava:
            cls._instancia = None
