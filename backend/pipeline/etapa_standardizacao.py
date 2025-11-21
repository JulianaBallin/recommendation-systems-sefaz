import os
import pandas as pd
from backend.utilitarios.tfidf_produtos import STANDARDIZED_PATH

def executar_etapa_standardizacao():
    if not os.path.exists(STANDARDIZED_PATH):
        return None

    df = pd.read_csv(STANDARDIZED_PATH)

    if df.empty:
        return df

    df = df.drop_duplicates(subset=["id", "descricao", "marca"])
    df.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")
    return df
