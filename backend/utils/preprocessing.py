"""
Preprocessing utilities for cleaning and enriching product datasets.
"""

import pandas as pd
from backend.utils.dictionaries import CATEGORY_MAP, BRAND_MAP, BAIRRO_ZONA_MAP


def extract_category(description: str) -> str:
    """Return category from product description using CATEGORY_MAP keywords."""
    for keyword, category in CATEGORY_MAP.items():
        if keyword in str(description).upper():
            return category
    return "Indefinido"


def extract_brand(description: str) -> str:
    """Return brand from product description using BRAND_MAP list."""
    for brand in BRAND_MAP:
        if brand in str(description).upper():
            return brand.capitalize()
    return "Genérico"


def extract_bairro(address: str) -> str:
    """
    Return bairro found in address using BAIRRO_ZONA_MAP keys.
    Prioritizes longest matches to avoid substring errors.
    """
    addr_upper = str(address).upper()

    # Ordenar bairros por tamanho (maior primeiro)
    for bairro in sorted(BAIRRO_ZONA_MAP.keys(), key=len, reverse=True):
        if bairro in addr_upper:
            return bairro.title()

    return "Desconhecido"


def map_zone(bairro: str) -> str:
    """Return zone based on bairro using BAIRRO_ZONA_MAP dict."""
    return BAIRRO_ZONA_MAP.get(str(bairro).upper(), "Zona Desconhecida")


def update_products(raw_file: str, clean_file: str):
    """
    Process raw products.csv and update products_clean.csv incrementally.
    - On first run: process all rows from raw_file.
    - On subsequent runs: only append new rows not already in clean_file.
    """

    # Load raw data
    df_raw = pd.read_csv(raw_file)

    # Normalize column names
    df_raw.columns = df_raw.columns.str.strip().str.upper()

    try:
        # Try loading existing processed file
        df_clean = pd.read_csv(clean_file)
        df_clean.columns = df_clean.columns.str.strip().str.upper()
        existing_codes = set(df_clean["CODIGO"].astype(str))
        last_id = df_clean["PRODUCT_ID"].max()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If file doesn't exist or is empty → start fresh
        df_clean = pd.DataFrame()
        existing_codes = set()
        last_id = 0

    # Keep only new products
    df_new = df_raw[~df_raw["CODIGO"].astype(str).isin(existing_codes)].copy()

    if df_new.empty:
        print("✅ Nenhum produto novo encontrado.")
        return

    # Assign incremental IDs
    df_new["PRODUCT_ID"] = range(last_id + 1, last_id + 1 + len(df_new))

    # Add processed columns
    df_new["CATEGORIA"] = df_new["DESCRICAO"].apply(extract_category)
    df_new["MARCA"] = df_new["DESCRICAO"].apply(extract_brand)
    df_new["BAIRRO"] = df_new["ENDERECO"].apply(extract_bairro)
    df_new["ZONA"] = df_new["BAIRRO"].apply(map_zone)

    # Merge with old data
    df_final = pd.concat([df_clean, df_new], ignore_index=True)

    # Save updated file
    df_final.to_csv(clean_file, index=False, encoding="utf-8")
    print(f"✅ {len(df_new)} novos produtos adicionados em {clean_file}")
