"""
conexao.py
Cria e gerencia a conexão com o banco de dados SQLite do sistema AmazIA.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os

# Caminho padrão do banco local
CAMINHO_BANCO = os.path.join("dados", "amazia.db")

def obter_engine() -> Engine:
    """
    Retorna a engine de conexão com o banco SQLite.

    Retorno:
        sqlalchemy.engine.Engine: objeto de conexão com o banco.
    """
    if not os.path.exists("dados"):
        os.makedirs("dados")

    engine = create_engine(f"sqlite:///{CAMINHO_BANCO}", echo=False)
    return engine
