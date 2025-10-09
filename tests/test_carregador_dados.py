"""
test_carregador_dados.py
Testa o fluxo completo de ingestão de dados no sistema AmazIA:
CSV → limpeza/validação → inserção no banco SQLite → leitura.

Esses testes simulam a inserção de dados pequenos e verificam
se apenas registros válidos são persistidos.
"""

import sys
import os
import pandas as pd
import sqlite3
import pytest

# Garante acesso aos módulos do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.banco_dados.init_db import criar_tabelas
from backend.dados.carregador_dados import (
    carregar_clientes,
    carregar_categorias,
    carregar_marcas,
    carregar_supermercados,
    carregar_produtos,
    carregar_nfs,
    carregar_avaliacoes_busca,
)
from backend.banco_dados.conexao import obter_engine

# ============================================================
# 🔹 Configuração inicial dos testes
# ============================================================

CAMINHO_BANCO = os.path.join("dados", "amazia.db")
PASTA_DERIVADOS = os.path.join("dados", "derivados")

@pytest.fixture(scope="module", autouse=True)
def preparar_banco():
    """Recria o banco e garante que as tabelas estão limpas antes dos testes."""
    criar_tabelas()
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()
    tabelas = ["CLIENTES", "CATEGORIA", "MARCA", "SUPERMERCADOS", "PRODUTOS", "NFS", "AVALIACOES_BUSCA"]
    for tabela in tabelas:
        cursor.execute(f"DELETE FROM {tabela};")
    conn.commit()
    conn.close()
    yield


def _ler_tabela(nome):
    """Lê uma tabela do banco como DataFrame."""
    conn = sqlite3.connect(CAMINHO_BANCO)
    df = pd.read_sql_query(f"SELECT * FROM {nome};", conn)
    conn.close()
    return df


# ============================================================
# 🔸 Testes por tabela
# ============================================================

def test_carregar_clientes(tmp_path):
    """Deve inserir apenas clientes válidos no banco."""
    caminho = tmp_path / "clientes.csv"
    pd.DataFrame([
        {"Cpf": "529.982.247-25", "Nome": "Juliana", "DataNasc": "1998-04-05", "Genero": "F", "Cep": "69077-200"},
        {"Cpf": "111.111.111-11", "Nome": "123Maria", "DataNasc": "31/02/2020", "Genero": "X", "Cep": "68900-000"}
    ]).to_csv(caminho, index=False)

    carregar_clientes(str(caminho))
    df = _ler_tabela("CLIENTES")
    assert len(df) == 1
    assert df.iloc[0]["Nome"] == "Juliana"


def test_carregar_categorias(tmp_path):
    """Deve remover duplicatas ignorando acentuação e inserir apenas válidas."""
    caminho = tmp_path / "categorias.csv"
    pd.DataFrame([
        {"Descricao_Categoria": "Higiene"},
        {"Descricao_Categoria": "higíêne"},  # duplicata acentuada
        {"Descricao_Categoria": "123Invalido"}
    ]).to_csv(caminho, index=False)

    carregar_categorias(str(caminho))
    df = _ler_tabela("CATEGORIA")
    assert len(df) == 1
    assert "higiene" in df.iloc[0]["Descricao_Categoria"].lower()


def test_carregar_marcas(tmp_path):
    """Deve considerar 'Omo', 'OMO', 'ômò' como uma única marca."""
    caminho = tmp_path / "marcas.csv"
    pd.DataFrame([
        {"Descricao_Marca": "Omo"},
        {"Descricao_Marca": "OMO"},
        {"Descricao_Marca": "ômò"}
    ]).to_csv(caminho, index=False)

    carregar_marcas(str(caminho))
    df = _ler_tabela("MARCA")
    assert len(df) == 1
    assert "omo" in df.iloc[0]["Descricao_Marca"].lower()


def test_carregar_supermercados(tmp_path):
    """Deve inserir apenas supermercados válidos (CNPJ e CEP)."""
    caminho = tmp_path / "supermercados.csv"
    pd.DataFrame([
        {"Cnpj": "12.345.678/0001-95", "Nome": "DB", "Cep": "69075-100"},
        {"Cnpj": "123", "Nome": "Inválido", "Cep": "68900-000"}
    ]).to_csv(caminho, index=False)

    carregar_supermercados(str(caminho))
    df = _ler_tabela("SUPERMERCADOS")
    assert len(df) == 1
    assert df.iloc[0]["Nome"] == "DB"


def test_carregar_produtos(tmp_path):
    """Deve inserir apenas produtos com descrição válida e sem duplicatas."""
    caminho = tmp_path / "produtos.csv"
    pd.DataFrame([
        {"Id_Categoria": 1, "Id_Marca": 1, "Descricao_Produto": "Sabão em pó Omo Lavagem Perfeita 800g"},
        {"Id_Categoria": 1, "Id_Marca": 1, "Descricao_Produto": "SABÃO EM PÓ ÔMÔ LAVAGEM PERFEITA 800G"}  # duplicata
    ]).to_csv(caminho, index=False)

    carregar_produtos(str(caminho))
    df = _ler_tabela("PRODUTOS")
    assert len(df) == 1
    assert "omo" in df.iloc[0]["Descricao_Produto"].lower()


def test_carregar_nfs(tmp_path):
    """Deve inserir apenas notas fiscais válidas."""
    caminho = tmp_path / "nfs.csv"
    pd.DataFrame([
        {"Id_Supermercado": "DB001", "Id_Produto": 1, "Preco": 9.99, "TimeStamp_Registro": "2025-10-08 15:00:00"},
        {"Id_Supermercado": "", "Id_Produto": "X", "Preco": -5, "TimeStamp_Registro": "07/10/2025"},
    ]).to_csv(caminho, index=False)

    carregar_nfs(str(caminho))
    df = _ler_tabela("NFS")
    assert len(df) == 1
    assert df.iloc[0]["Preco"] == 9.99


def test_carregar_avaliacoes_busca(tmp_path):
    """Deve inserir apenas avaliações com CPF e notas válidas."""
    caminho = tmp_path / "avaliacoes_busca.csv"
    pd.DataFrame([
        {
            "Cpf_Cliente": "529.982.247-25",
            "Id_Categoria": 1,
            "Avaliacao_Categoria": 4,
            "Qtd_Busca_Categoria": 3,
            "Id_Marca": 2,
            "Avaliacao_Marca": 5,
            "Qtd_Busca_Marca": 10,
            "Id_Produto": 3,
            "Avaliacao_Produto": 2,
            "Qtd_Busca_Produto": 4,
            "Cnpj_Supermercado": "12.345.678/0001-95",
            "Avaliacao_Supermercado": 5,
            "Qtd_Busca_Supermercado": 8,
        },
        {
            "Cpf_Cliente": "123.456.789-00",
            "Id_Categoria": 1,
            "Avaliacao_Categoria": 10,
            "Qtd_Busca_Categoria": 3,
            "Id_Marca": 2,
            "Avaliacao_Marca": -1,
            "Qtd_Busca_Marca": 10,
            "Id_Produto": 3,
            "Avaliacao_Produto": None,
            "Qtd_Busca_Produto": 4,
            "Cnpj_Supermercado": "12.345.678/0001-95",
            "Avaliacao_Supermercado": 5,
            "Qtd_Busca_Supermercado": 8,
        }
    ]).to_csv(caminho, index=False)

    carregar_avaliacoes_busca(str(caminho))
    df = _ler_tabela("AVALIACOES_BUSCA")
    assert len(df) == 1
    assert df.iloc[0]["Cpf_Cliente"] == "529.982.247-25"
