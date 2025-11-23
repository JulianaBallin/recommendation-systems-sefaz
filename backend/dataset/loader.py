import pandas as pd
import os

DATASET_DIR = "dataset"
PROCESSADO_DIR = os.path.join(DATASET_DIR, "processado")
RATINGS_DIR = os.path.join(DATASET_DIR, "ratings")
RAW_DIR = os.path.join(DATASET_DIR, "raw")
STANDARDIZED_DIR = os.path.join(DATASET_DIR, "standardized")

CLIENTS_PATH = os.path.join(PROCESSADO_DIR, "usuarios.csv")
RATINGS_PATH = os.path.join(RATINGS_DIR, "avaliacoes.csv")
FEEDBACK_PATH = os.path.join(RATINGS_DIR, "feedback.csv")
PRODUCTS_PATH = os.path.join(STANDARDIZED_DIR, "produtos_padronizados.csv")

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
        df = pd.read_csv(RATINGS_PATH)

        # mapear product_id → id padronizado
        if "product_id" in df.columns:
            df_products = load_derived_products()  # id, descricao, marca

            # Mapa da descrição do CSV rating → id padronizado
            mapping = dict(zip(df_products["descricao"], df_products["id"]))

            if "descricao_produto" in df.columns:
                df["id"] = df["descricao_produto"].map(mapping)

        return df

    return pd.DataFrame(columns=["nome_usuario", "cpf", "descricao_produto",
                                 "avaliacao_descricao", "marca_produto",
                                 "avaliacao_marca", "product_id"])


def save_ratings(df):
    os.makedirs(os.path.dirname(RATINGS_PATH), exist_ok=True)
    df.to_csv(RATINGS_PATH, index=False)

def load_feedback():
    if os.path.exists(FEEDBACK_PATH):
        return pd.read_csv(FEEDBACK_PATH)
    return pd.DataFrame(columns=["cpf", "item_id", "feedback", "timestamp"])

def save_feedback(df):
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    df.to_csv(FEEDBACK_PATH, index=False)
