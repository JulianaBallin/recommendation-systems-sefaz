import os
import pandas as pd
from backend.utilitarios.limpeza_dados import limpar_descricao, limpar_supermercado
from backend.utilitarios.utilitarios_dicionarios import detectar_marca


RAW_PATH = "dataset/raw/nfs.csv"
PROCESSED_PATH = "dataset/processado/nfs_processadas.csv"


def processar_nfs():
    print("🔄 Iniciando processamento das NFs...")

    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {RAW_PATH}")

    # Carrega o CSV
    df = pd.read_csv(RAW_PATH)

    # Valida colunas
    if "DESCRICAO" not in df.columns or "SUPERMERCADO" not in df.columns:
        raise ValueError("❌ O CSV deve conter as colunas: DESCRICAO e SUPERMERCADO")

    # Limpeza
    df["descricao_limpa"] = df["DESCRICAO"].apply(limpar_descricao)
    df["supermercado_limpo"] = df["SUPERMERCADO"].apply(limpar_supermercado)

    # Detecta marca
    df["marca"] = df["descricao_limpa"].apply(detectar_marca)

    # Remove descrições vazias
    df = df[df["descricao_limpa"].str.len() > 1]

    # Remove duplicatas
    df = df.drop_duplicates(subset=["descricao_limpa", "supermercado_limpo", "marca"])

    # Organiza colunas finais
    df_final = df[["descricao_limpa", "supermercado_limpo", "marca"]]
    df_final.columns = ["descricao", "supermercado", "marca"]

    # Garante diretório
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)

    # Salva
    df_final.to_csv(PROCESSED_PATH, index=False, encoding="utf-8")

    print(f"✅ Processamento concluído! Arquivo salvo em: {PROCESSED_PATH}")
