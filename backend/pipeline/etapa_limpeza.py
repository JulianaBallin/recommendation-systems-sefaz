import os
import pandas as pd
from backend.utilitarios.limpeza_dados import limpar_descricao

RAW_PATH = "dataset/raw/nfs.csv"

def executar_etapa_limpeza():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {RAW_PATH}")

    df = pd.read_csv(RAW_PATH)

    if "descricao" not in df.columns:
        raise ValueError("CSV deve conter a coluna: descricao")

    df["descricao_limpa"] = df["descricao"].astype(str).apply(limpar_descricao)
    df = df[df["descricao_limpa"].str.len() > 1]

    return df.reset_index(drop=True)
