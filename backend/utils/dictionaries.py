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


def load_category_map(path: str = CATEGORY_CSV) -> pd.DataFrame:
    """
    Carrega mapa de categorias a partir do CSV.
    - Usa a coluna 'categoria'
    - Remove duplicatas e valores vazios
    - Padroniza o texto sem acentuação
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    if "categoria" not in df.columns:
        raise ValueError(f"Coluna 'categoria' não encontrada em {path}")

    df = df.dropna(subset=["categoria"])
    df["categoria"] = df["categoria"].apply(_normalize_text)
    df = df[df["categoria"] != ""]
    df = df.drop_duplicates(subset=["categoria"])

    return df.reset_index(drop=True)


def load_brand_map(path: str = BRAND_CSV) -> pd.DataFrame:
    """
    Carrega mapa de marcas a partir do CSV.
    - Usa a coluna 'marca'
    - Remove duplicatas e valores vazios
    - Padroniza o texto sem acentuação
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    if "marca" not in df.columns:
        raise ValueError(f"Coluna 'marca' não encontrada em {path}")

    df = df.dropna(subset=["marca"])
    df["marca"] = df["marca"].apply(_normalize_text)
    df = df[df["marca"] != ""]
    df = df.drop_duplicates(subset=["marca"])

    return df.reset_index(drop=True)


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

    # Procura categoria pela chave_categoria no texto
    if not cat_map.empty and "chave_categoria" in cat_map.columns and "categoria" in cat_map.columns:
        for _, row in cat_map.iterrows():
            chave = loader.normalize_text(row["chave_categoria"])
            if chave and chave in desc_clean:
                categoria = loader.normalize_text(row["categoria"])
                break

    # Procura marca pela palavra no texto
    if not brand_map.empty and "palavra" in brand_map.columns and "marca" in brand_map.columns:
        for _, row in brand_map.iterrows():
            palavra = loader.normalize_text(row["palavra"])
            if palavra and palavra in desc_clean:
                marca = loader.normalize_text(row["marca"])
                break

    return {
        "Categoria": categoria,
        "Marca": marca,
        "Descricao": desc_clean,
    }
