"""
test_banco_dados.py
Verifica a integridade e funcionamento do banco de dados SQLite do sistema AmazIA.

Testes executados:
1. Existência do arquivo amazia.db.
2. Criação de todas as tabelas obrigatórias.
3. Verificação das colunas esperadas em cada tabela.
4. Inserção de teste e leitura de dados.
"""

import os
import sqlite3
import pytest
from sqlalchemy import text
from backend.banco_dados.init_db import criar_tabelas
from backend.banco_dados.conexao import obter_engine

# ============================================================
# Configuração inicial
# ============================================================

CAMINHO_BANCO = os.path.join("dados", "amazia.db")

@pytest.fixture(scope="module", autouse=True)
def preparar_banco():
    """Cria o banco e as tabelas antes dos testes."""
    criar_tabelas()
    yield
    # Nenhum teardown necessário (mantém o banco para inspeção manual)


# ============================================================
# Teste 1 — Verificar se o arquivo do banco existe
# ============================================================

def test_banco_existe():
    """Verifica se o arquivo amazia.db foi criado."""
    assert os.path.exists(CAMINHO_BANCO), "❌ O arquivo amazia.db não foi encontrado."


# ============================================================
# Teste 2 — Verificar se todas as tabelas foram criadas
# ============================================================

def test_tabelas_existem():
    """Confirma a existência de todas as tabelas principais."""
    engine = obter_engine()
    tabelas_esperadas = {
        "CATEGORIA", "MARCA", "PRODUTOS", "CLIENTES",
        "SUPERMERCADOS", "NFS", "AVALIACOES_BUSCA"
    }

    with engine.connect() as conexao:
        resultado = conexao.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tabelas_existentes = {r[0] for r in resultado.fetchall()}

    faltando = tabelas_esperadas - tabelas_existentes
    assert not faltando, f"❌ Tabelas ausentes no banco: {faltando}"
    assert tabelas_esperadas.issubset(tabelas_existentes), "❌ Tabelas obrigatórias não encontradas."


# ============================================================
# Teste 3 — Verificar estrutura das colunas de cada tabela
# ============================================================

def test_estrutura_colunas():
    """Valida se as colunas principais existem conforme o modelo lógico."""
    estrutura_esperada = {
        "CATEGORIA": {"Id_Categoria", "Descricao_Categoria"},
        "MARCA": {"Id_Marca", "Descricao_Marca"},
        "PRODUTOS": {"Id_Produto", "Id_Categoria", "Id_Marca", "Descricao_Produto"},
        "CLIENTES": {"Cpf", "Nome", "DataNasc", "Genero", "Cep"},
        "SUPERMERCADOS": {"Id_Supermercado", "Cnpj", "Nome", "Cep", "Bairro", "Rua", "Num"},
        "NFS": {"Id", "Id_Supermercado", "Id_Produto", "Preco", "TimeStamp_Registro"},
        "AVALIACOES_BUSCA": {
            "Id", "Cpf_Cliente", "Id_Categoria", "Avaliacao_Categoria", "Qtd_Busca_Categoria",
            "Id_Marca", "Avaliacao_Marca", "Qtd_Busca_Marca",
            "Id_Produto", "Avaliacao_Produto", "Qtd_Busca_Produto",
            "Cnpj_Supermercado", "Avaliacao_Supermercado", "Qtd_Busca_Supermercado"
        }
    }

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    for tabela, colunas_esperadas in estrutura_esperada.items():
        cursor.execute(f"PRAGMA table_info({tabela});")
        colunas_encontradas = {linha[1] for linha in cursor.fetchall()}
        faltando = colunas_esperadas - colunas_encontradas
        assert not faltando, f"❌ Colunas ausentes na tabela {tabela}: {faltando}"

    conn.close()


# ============================================================
# Teste 4 — Inserção de dados e leitura
# ============================================================

def test_insercao_e_leitura_basica():
    """Testa uma inserção simples e verifica se o registro pode ser lido."""
    engine = obter_engine()
    with engine.begin() as conexao:
        conexao.execute(text("""
            INSERT INTO CATEGORIA (Descricao_Categoria)
            VALUES ('Teste_Categoria_Validacao');
        """))

        resultado = conexao.execute(text("""
            SELECT Descricao_Categoria
            FROM CATEGORIA
            WHERE Descricao_Categoria='Teste_Categoria_Validacao';
        """))
        linha = resultado.fetchone()
        assert linha is not None, "❌ Inserção de teste falhou."
        assert linha[0] == "Teste_Categoria_Validacao", "❌ Dados incorretos após inserção."
