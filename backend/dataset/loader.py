"""
loader.py
---------
Funções para carregar, salvar, limpar e pré-visualizar datasets (produtos e clientes).
Inclui funções utilitárias de normalização de texto.
"""

import os
import re
import unicodedata
import pandas as pd
from backend.utils.preprocessing import normalize_text


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

RAW_RECEIPTS = os.path.join(BASE_DIR, "data/raw/receipts_nf.csv")
RAW_CLIENTS = os.path.join(BASE_DIR, "data/raw/clients.csv")
RATINGS = os.path.join(BASE_DIR,"data/derived/ratings.csv")
DERIVED_PRODUCTS = os.path.join(BASE_DIR, "data/derived/products.csv")
DERIVED_SUPERMARKETS = os.path.join(BASE_DIR, "data/derived/supermarkets.csv")



# Funções utilitárias de limpeza

def clean_dataframe(df: pd.DataFrame, subset_cols: list[str] = None) -> pd.DataFrame:
    """
    Limpa DataFrame removendo nulos, duplicatas e normalizando textos.
    - subset_cols: colunas usadas para deduplicação (ex.: CODIGO, CPF, etc.)
    """
    if df.empty:
        return df

    # Remove linhas totalmente nulas
    df = df.dropna(how="all")

    # Preenche valores nulos com vazio
    df = df.fillna("")

    # Normaliza textos em colunas object
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(normalize_text)

    # Remove duplicatas
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols, keep="first")
    else:
        df = df.drop_duplicates(keep="first")

    return df.reset_index(drop=True)



#  Funções de Produtos

def load_raw_receipts(path: str = RAW_RECEIPTS) -> pd.DataFrame:
    """
    Carrega produtos brutos de notas fiscais (raw).
    Retorna DataFrame vazio se não existir.
    """
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return pd.DataFrame(columns=["CODIGO", "DESCRICAO", "QTD", "UN",
                                     "VALOR_UNITARIO", "VALOR_TOTAL",
                                     "NOME_SUPERMERCADO", "CNPJ", "ENDERECO",
                                     "NUMERO_NFCE", "SERIE", "DATA_HORA_COMPRA"])
    df = pd.read_csv(path)
    df.columns = [c.strip().upper() for c in df.columns]
    return df


def save_raw_receipts(df: pd.DataFrame, path: str = RAW_RECEIPTS):
    """
    Salva notas fiscais (raw).
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def load_derived_products(path: str = DERIVED_PRODUCTS) -> pd.DataFrame:
    """
    Carrega produtos derivados (normalizados).
    Retorna DataFrame vazio com colunas padrão se o arquivo não existir ou estiver vazio.
    """
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return pd.DataFrame(columns=["ID", "CATEGORIA", "MARCA", "DESCRICAO"])

    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=["ID", "CATEGORIA", "MARCA", "DESCRICAO"])
    df.columns = [c.strip().capitalize() for c in df.columns]
    return df


def save_derived_products(df: pd.DataFrame):
    """
    Salva produtos derivados (normalizados) no CSV.
    """
    os.makedirs(os.path.dirname(DERIVED_PRODUCTS), exist_ok=True)
    df = clean_dataframe(df, subset_cols=["ID"])
    df.to_csv(DERIVED_PRODUCTS, index=False)



# Funções de Clientes

def load_raw_clients() -> pd.DataFrame:
    if os.path.exists(RAW_CLIENTS):
        df = pd.read_csv(RAW_CLIENTS, dtype=str)
        df.columns = [c.strip().upper() for c in df.columns]
        rename_map = {
            "CPF": "CPF",
            "NAME": "NOME",
            "BIRTHDATE": "DATA_NASC",
            "CEP": "CEP",
            "GENDER": "SEXO",
        }
        df = df.rename(columns=rename_map)

        return df
    return pd.DataFrame(columns=["CPF", "NOME", "DATA_NASC", "CEP", "SEXO"])


def save_raw_clients(df: pd.DataFrame):
    """
    Salva clientes brutos (raw) no CSV.
    """
    os.makedirs(os.path.dirname(RAW_CLIENTS), exist_ok=True)
    df = clean_dataframe(df, subset_cols=["CPF"])
    df.to_csv(RAW_CLIENTS, index=False)



# Funções de Preview (Produtos e Clientes)

def preview_table(path: str, n_head: int = 5, n_tail: int = 5) -> dict:
    """
    Retorna preview de um CSV qualquer:
    - primeiras linhas
    - últimas linhas
    - quantidade total
    """
    if not os.path.exists(path):
        return {"head": pd.DataFrame(), "tail": pd.DataFrame(), "total": 0}

    df = pd.read_csv(path)
    return {
        "head": df.head(n_head),
        "tail": df.tail(n_tail),
        "total": len(df),
    }

def preview_raw_receipts(path: str = RAW_RECEIPTS, n_head: int = 5, n_tail: int = 5) -> dict:
    """
    Retorna preview das notas fiscais (raw).
    """
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return {"head": pd.DataFrame(), "tail": pd.DataFrame(), "total": 0}

    df = pd.read_csv(path)
    return {
        "head": df.head(n_head),
        "tail": df.tail(n_tail),
        "total": len(df),
    }

def preview_clean_products(n: int = 10) -> dict:
    """
    Retorna preview dos produtos derivados:
    - primeiras n linhas (ID, Categoria, Marca, Descricao)
    - quantidade total
    """
    if not os.path.exists(DERIVED_PRODUCTS):
        return {"preview": pd.DataFrame(), "total": 0}

    df = pd.read_csv(DERIVED_PRODUCTS)
    return {
        "preview": df[["ID", "CATEGORIA", "MARCA", "DESCRICAO"]].head(n),
        "total": len(df),
    }


def preview_derived_clients(n: int = 10) -> dict:
    """
    Retorna preview da base de clientes derivada (com zona atribuída):
    - primeiras n linhas (sem duplicação para bases pequenas)
    - últimas n linhas
    - total de registros
    """
    if not os.path.exists(RAW_CLIENTS):
        return {"preview": pd.DataFrame(), "total": 0}

    df = pd.read_csv(RAW_CLIENTS)
    total = len(df)

    if total <= 2 * n:
        preview = df
    else:
        preview = pd.concat([df.head(n), df.tail(n)])

    return {"preview": preview, "total": total}



# Funções de Avaliações (Ratings)

def load_ratings() -> pd.DataFrame:
    """
    Carrega a tabela de avaliações.
    """
    cols = ["CPF_CLIENTE","ID_PRODUTO","RATING_DESCRICAO","RATING_CATEGORIA","RATING_MARCA"]

    if os.path.exists(RATINGS):
        try:
            df = pd.read_csv(RATINGS, dtype=str)
            if df.empty or set(df.columns) != set(cols):
                return pd.DataFrame(columns=cols)
            return df[cols]
        except Exception:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)


def save_ratings(df: pd.DataFrame):
    """
    Salva avaliações, exigindo ID_PRODUTO e RATING_DESCRICAO.
    """
    os.makedirs(os.path.dirname(RATINGS), exist_ok=True)

    cols = ["CPF_CLIENTE","ID_PRODUTO","RATING_DESCRICAO","RATING_CATEGORIA","RATING_MARCA"]

    # Garante colunas
    for col in cols:
        if col not in df.columns:
            df[col] = None

    # Remove nulos no CPF
    df = df[df["CPF_CLIENTE"].notna() & (df["CPF_CLIENTE"].astype(str).str.strip() != "")]

    # Exige ID_PRODUTO e RATING_DESCRICAO
    df = df[df["ID_PRODUTO"].notna() & df["RATING_DESCRICAO"].notna()]

    # Remove duplicatas
    df = df.drop_duplicates(subset=["CPF_CLIENTE", "ID_PRODUTO"], keep="last")

    df.to_csv(RATINGS, index=False, columns=cols)

