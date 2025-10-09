"""
carregador_dados.py
Gerencia a ingestão de dados CSV no banco de dados AmazIA.

Fluxo:
1. Lê o CSV de entrada.
2. Aplica validação e limpeza (limpeza_dados.py).
3. Persiste somente registros válidos no SQLite (via SQLAlchemy).
4. Exibe mensagens padronizadas (mensagens_ui.py).
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from backend.banco_dados.conexao import obter_engine
from backend.utilitarios.limpeza_dados import (
    limpar_clientes,
    limpar_supermercados,
    limpar_categorias,
    limpar_marcas,
    limpar_produtos,
    limpar_nfs,
    limpar_avaliacoes_busca,
)
from frontend.streamlit_app.modules.ui_messages import (
    show_success,
    show_error,
    show_warning,
)

# ============================================================
# 🔹 Função genérica de inserção no banco
# ============================================================

def _inserir_no_banco(df: pd.DataFrame, nome_tabela: str):
    """
    Insere o DataFrame no banco SQLite (modo append).
    """
    try:
        if df.empty:
            show_warning(f"Nenhum dado válido para inserir na tabela {nome_tabela}.")
            return

        engine = obter_engine()
        df.to_sql(nome_tabela, con=engine, if_exists="append", index=False)
        show_success(f"{len(df)} registros inseridos na tabela {nome_tabela} com sucesso ✅")

    except Exception as e:
        show_error(f"Erro ao inserir na tabela {nome_tabela}: {e}")

# ============================================================
# 🔸 Funções específicas por tabela
# ============================================================

def carregar_clientes(caminho_csv: str):
    """
    Lê, valida e insere registros de CLIENTES no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_clientes(df)
        _inserir_no_banco(df_limpo, "CLIENTES")
    except FileNotFoundError:
        show_error("Arquivo de CLIENTES não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar CLIENTES: {e}")


def carregar_supermercados(caminho_csv: str):
    """
    Lê, valida e insere registros de SUPERMERCADOS no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_supermercados(df)
        _inserir_no_banco(df_limpo, "SUPERMERCADOS")
    except FileNotFoundError:
        show_error("Arquivo de SUPERMERCADOS não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar SUPERMERCADOS: {e}")


def carregar_categorias(caminho_csv: str):
    """
    Lê, valida e insere registros de CATEGORIA no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_categorias(df)
        _inserir_no_banco(df_limpo, "CATEGORIA")
    except FileNotFoundError:
        show_error("Arquivo de CATEGORIA não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar CATEGORIA: {e}")


def carregar_marcas(caminho_csv: str):
    """
    Lê, valida e insere registros de MARCA no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_marcas(df)
        _inserir_no_banco(df_limpo, "MARCA")
    except FileNotFoundError:
        show_error("Arquivo de MARCA não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar MARCA: {e}")


def carregar_produtos(caminho_csv: str):
    """
    Lê, valida e insere registros de PRODUTOS no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_produtos(df)
        _inserir_no_banco(df_limpo, "PRODUTOS")
    except FileNotFoundError:
        show_error("Arquivo de PRODUTOS não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar PRODUTOS: {e}")


def carregar_nfs(caminho_csv: str):
    """
    Lê, valida e insere registros de NFS (Notas Fiscais) no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_nfs(df)
        _inserir_no_banco(df_limpo, "NFS")
    except FileNotFoundError:
        show_error("Arquivo de NFS não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar NFS: {e}")


def carregar_avaliacoes_busca(caminho_csv: str):
    """
    Lê, valida e insere registros de AVALIACOES_BUSCA no banco AmazIA.
    """
    try:
        df = pd.read_csv(caminho_csv, sep=",")
        df_limpo = limpar_avaliacoes_busca(df)
        _inserir_no_banco(df_limpo, "AVALIACOES_BUSCA")
    except FileNotFoundError:
        show_error("Arquivo de AVALIACOES_BUSCA não encontrado.")
    except Exception as e:
        show_error(f"Erro ao processar AVALIACOES_BUSCA: {e}")

# ============================================================
# 🔹 Função utilitária para execução em lote (opcional)
# ============================================================

def carregar_todos_os_dados(pasta_dados="dados/derivados"):
    """
    Executa a carga completa dos CSVs (modo batch).
    Os arquivos devem estar nomeados conforme as tabelas.
    """
    arquivos = {
        "CATEGORIA": os.path.join(pasta_dados, "categorias.csv"),
        "MARCA": os.path.join(pasta_dados, "marcas.csv"),
        "PRODUTOS": os.path.join(pasta_dados, "produtos.csv"),
        "CLIENTES": os.path.join(pasta_dados, "clientes.csv"),
        "SUPERMERCADOS": os.path.join(pasta_dados, "supermercados.csv"),
        "NFS": os.path.join(pasta_dados, "nfs.csv"),
        "AVALIACOES_BUSCA": os.path.join(pasta_dados, "avaliacoes_busca.csv"),
    }

    for tabela, caminho in arquivos.items():
        if not os.path.exists(caminho):
            show_warning(f"⚠️ {tabela}: arquivo não encontrado ({caminho})")
            continue

        if tabela == "CATEGORIA":
            carregar_categorias(caminho)
        elif tabela == "MARCA":
            carregar_marcas(caminho)
        elif tabela == "PRODUTOS":
            carregar_produtos(caminho)
        elif tabela == "CLIENTES":
            carregar_clientes(caminho)
        elif tabela == "SUPERMERCADOS":
            carregar_supermercados(caminho)
        elif tabela == "NFS":
            carregar_nfs(caminho)
        elif tabela == "AVALIACOES_BUSCA":
            carregar_avaliacoes_busca(caminho)

    show_success("🚀 Carga completa de dados finalizada com sucesso!")
