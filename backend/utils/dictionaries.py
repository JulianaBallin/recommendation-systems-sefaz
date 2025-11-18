"""
dictionaries.py
---------------
Carregamento dos dicionários auxiliares usados para normalizar
produtos e clientes (categorias, marcas, bairros, etc.).
"""

import pandas as pd
import os
import unicodedata
import re

from backend.dataset import loader  # usa normalize_text

# Caminho base do projeto (2 níveis acima deste arquivo)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

CATEGORY_CSV = os.path.join(BASE_DIR, "data/dictionaries/category_map.csv")
BRAND_CSV = os.path.join(BASE_DIR, "data/dictionaries/brand_map.csv")


# ======================================================
# 🔹 Funções de carregamento de dicionários
# ======================================================

def _normalize_text(value: str) -> str:
    """Normaliza texto: maiúsculo, sem acento, sem caracteres especiais extras."""
    if pd.isna(value):
        return ""
    text = str(value).upper().strip()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)   # normaliza múltiplos espaços
    return text


def load_category_map() -> pd.DataFrame:
    if not os.path.exists(CATEGORY_CSV):
        return pd.DataFrame(columns=["CHAVE_CATEGORIA", "CATEGORIA"])
    df = pd.read_csv(CATEGORY_CSV, dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]   # 🔹 força maiúsculo
    return df

def load_brand_map() -> pd.DataFrame:
    if not os.path.exists(BRAND_CSV):
        return pd.DataFrame(columns=["MARCA"])
    df = pd.read_csv(BRAND_CSV, dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]   # 🔹 força maiúsculo
    return df


def normalize_product(descricao: str) -> dict:
    """
    Normaliza a descrição de um produto e identifica sua Categoria e Marca
    usando os dicionários auxiliares.

    Regras:
    - Descrição limpa (maiúscula, sem acentos, sem caracteres especiais, sem espaços extras)
    - Categoria: detectada no texto usando category_map
    - Marca: detectada no texto usando brand_map
    - Se não encontrar correspondência → "DESCONHECIDO"
    """
    if pd.isna(descricao):
        descricao = ""
    desc_clean = loader.normalize_text(descricao)

    # Carrega dicionários
    cat_map = load_category_map()
    brand_map = load_brand_map()

    categoria = "DESCONHECIDO"
    marca = "DESCONHECIDO"

    # 🔹 Procura categoria pela CHAVE_CATEGORIA no texto
    if not cat_map.empty and "CHAVE_CATEGORIA" in cat_map.columns and "CATEGORIA" in cat_map.columns:
        for _, row in cat_map.iterrows():
            chave = loader.normalize_text(row["CHAVE_CATEGORIA"])
            if chave and chave in desc_clean:
                categoria = loader.normalize_text(row["CATEGORIA"])
                break

    # 🔹 Procura marca pela PALAVRA no texto
    if not brand_map.empty and "PALAVRA" in brand_map.columns and "MARCA" in brand_map.columns:
        for _, row in brand_map.iterrows():
            palavra = loader.normalize_text(row["PALAVRA"])
            if palavra and palavra in desc_clean:
                marca = loader.normalize_text(row["MARCA"])
                break

    return {
        "Categoria": categoria,
        "Marca": marca,
        "Descricao": desc_clean,
    }
