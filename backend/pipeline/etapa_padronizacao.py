import os
import pandas as pd
from backend.utilitarios.utilitarios_dicionarios import detectar_marca

PROCESSED_PATH = "dataset/processado/nfs_processadas.csv"

def executar_etapa_padronizacao(df):
    df = df.copy()

    df["marca"] = df["descricao_limpa"].apply(detectar_marca)

    df_final = df[["descricao_limpa", "marca"]].rename(
        columns={"descricao_limpa": "descricao"}
    )

    df_final = df_final.drop_duplicates(subset=["descricao", "marca"])

    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    df_final.to_csv(PROCESSED_PATH, index=False)

    return df_final.reset_index(drop=True)
