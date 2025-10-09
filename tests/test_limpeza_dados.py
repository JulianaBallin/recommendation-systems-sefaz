"""
test_limpeza_dados.py
Testa as funções de limpeza e validação linha a linha dos datasets
no módulo backend/utilitarios/limpeza_dados.py.
"""

import sys
import os
import pandas as pd
import pytest

# Garante que o backend seja importável
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.utilitarios.limpeza_dados import (
    limpar_clientes,
    limpar_supermercados,
    limpar_categorias,
    limpar_marcas,
    limpar_produtos,
    limpar_nfs,
    limpar_avaliacoes_busca,
)

# ============================================================
# 🔹 CLIENTES
# ============================================================

def test_limpar_clientes_remove_invalidos():
    """Deve manter apenas clientes válidos."""
    df = pd.DataFrame([
        {"Cpf": "529.982.247-25", "Nome": "Juliana", "DataNasc": "1998-04-05", "Genero": "F", "Cep": "69077-200"},
        {"Cpf": "123.456.789-00", "Nome": "123Maria", "DataNasc": "31/02/2025", "Genero": "X", "Cep": "68900-000"}
    ])

    df_limpo = limpar_clientes(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["Nome"] == "Juliana"


# ============================================================
# 🔹 SUPERMERCADOS
# ============================================================

def test_limpar_supermercados_valida_campos():
    """Deve aceitar apenas supermercados com CNPJ e CEP válidos."""
    df = pd.DataFrame([
        {"Cnpj": "12.345.678/0001-95", "Nome": "DB Supermercados", "Cep": "69077-200"},
        {"Cnpj": "12345678", "Nome": "Mercado Inválido", "Cep": "68900-000"}
    ])

    df_limpo = limpar_supermercados(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["Nome"] == "DB Supermercados"


# ============================================================
# 🔹 CATEGORIAS E MARCAS
# ============================================================

def test_limpar_categorias_remove_duplicatas_e_invalidos():
    """Deve remover duplicatas e categorias inválidas."""
    df = pd.DataFrame([
        {"Descricao_Categoria": "Higiene"},
        {"Descricao_Categoria": "higiene"},  # duplicada
        {"Descricao_Categoria": "123Invalido"}
    ])

    df_limpo = limpar_categorias(df)
    assert len(df_limpo) == 1
    assert "Higiene" in df_limpo["Descricao_Categoria"].values or "higiene" in df_limpo["Descricao_Categoria"].values


def test_limpar_marcas_valida_texto():
    """Deve manter apenas marcas com texto simples."""
    df = pd.DataFrame([
        {"Descricao_Marca": "Omo"},
        {"Descricao_Marca": "Marca123"}
    ])

    df_limpo = limpar_marcas(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["Descricao_Marca"] == "Omo"


# ============================================================
# 🔹 PRODUTOS
# ============================================================

def test_limpar_produtos_valida_relacoes():
    """Deve aceitar apenas produtos com IDs válidos e descrição <= 150 caracteres."""
    df = pd.DataFrame([
        {"Id_Categoria": 1, "Id_Marca": 2, "Descricao_Produto": "Sabão em pó Omo Lavagem Perfeita 800g"},
        {"Id_Categoria": "X", "Id_Marca": 2, "Descricao_Produto": ""},
    ])

    df_limpo = limpar_produtos(df)
    assert len(df_limpo) == 1
    assert "Omo" in df_limpo.iloc[0]["Descricao_Produto"]


# ============================================================
# 🔹 NFS
# ============================================================

def test_limpar_nfs_valida_campos():
    """Deve manter apenas notas fiscais com preço e timestamp válidos."""
    df = pd.DataFrame([
        {"Id_Supermercado": "DB001", "Id_Produto": 1, "Preco": 9.99, "TimeStamp_Registro": "2025-10-07 15:00:00"},
        {"Id_Supermercado": None, "Id_Produto": "X", "Preco": -5, "TimeStamp_Registro": "07/10/2025"},
    ])

    df_limpo = limpar_nfs(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["Id_Produto"] == 1


# ============================================================
# 🔹 AVALIAÇÕES E BUSCAS
# ============================================================

def test_limpar_avaliacoes_busca_valida_notas_e_cpf():
    """Deve aceitar apenas registros com CPF válido e notas entre 0 e 5."""
    df = pd.DataFrame([
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
            "Cpf_Cliente": "123.456.789-00",  # inválido
            "Id_Categoria": 1,
            "Avaliacao_Categoria": 10,  # fora da faixa
            "Qtd_Busca_Categoria": 3,
            "Id_Marca": 2,
            "Avaliacao_Marca": -1,  # fora da faixa
            "Qtd_Busca_Marca": 10,
            "Id_Produto": 3,
            "Avaliacao_Produto": None,
            "Qtd_Busca_Produto": 4,
            "Cnpj_Supermercado": "12.345.678/0001-95",
            "Avaliacao_Supermercado": 5,
            "Qtd_Busca_Supermercado": 8,
        }
    ])

    df_limpo = limpar_avaliacoes_busca(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["Cpf_Cliente"] == "529.982.247-25"
