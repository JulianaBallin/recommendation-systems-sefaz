import pandas as pd
import os

DATASET_DIR = "dataset"
RAW_DIR = os.path.join(DATASET_DIR, "raw")
STANDARDIZED_DIR = os.path.join(DATASET_DIR, "standardized")

CLIENTS_PATH = os.path.join(RAW_DIR, "usuarios_simulados.csv")
PRODUCTS_PATH = os.path.join(STANDARDIZED_DIR, "produtos_padronizados.csv")
RATINGS_PATH = os.path.join(RAW_DIR, "avaliacoes.csv")

def load_raw_clients():
    if os.path.exists(CLIENTS_PATH):
        return pd.read_csv(CLIENTS_PATH)
    return pd.DataFrame(columns=["cpf", "nome"])

def load_derived_products():
    if os.path.exists(PRODUCTS_PATH):
        return pd.read_csv(PRODUCTS_PATH)
    return pd.DataFrame(columns=["id", "descricao", "marca"])

def load_ratings():
    if os.path.exists(RATINGS_PATH):
        return pd.read_csv(RATINGS_PATH)
    return pd.DataFrame(columns=["nome_usuario", "cpf", "descricao_produto", "avaliacao_descricao", "marca_produto", "avaliacao_marca"])

def save_ratings(df):
    os.makedirs(os.path.dirname(RATINGS_PATH), exist_ok=True)
    df.to_csv(RATINGS_PATH, index=False)
