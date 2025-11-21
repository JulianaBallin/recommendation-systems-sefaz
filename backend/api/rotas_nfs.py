from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os
import time

from backend.utilitarios.processar_nfs import processar_csv_nfs
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf

router = APIRouter(prefix="/nfs", tags=["Notas Fiscais"])

NFS_CSV = "dataset/processado/nfs_processadas.csv"

def obter_nfs_existentes():
    if not os.path.exists(NFS_CSV):
        return set()
    
    try:
        df = pd.read_csv(NFS_CSV)
        if "descricao" in df.columns:
            return set(df["descricao"])
    except Exception:
        pass
        
    return set()


def inserir_nfs_banco(df):
    if df.empty:
        return

    os.makedirs(os.path.dirname(NFS_CSV), exist_ok=True)
    
    if not os.path.exists(NFS_CSV):
        df.to_csv(NFS_CSV, index=False)
    else:
        df.to_csv(NFS_CSV, mode="a", header=False, index=False)


@router.post("/upload")
async def upload_nfs(file: UploadFile = File(...)):
    inicio = time.time()

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.lower()

    if df.empty:
        return {"status": "erro", "mensagem": "CSV vazio!"}

    COLUNAS_OBRIGATORIAS = {"descricao"}
    if not COLUNAS_OBRIGATORIAS.issubset(df.columns.str.lower()):
        return {
            "status": "erro",
            "mensagem": f"Colunas obrigatórias ausentes. Esperado: {COLUNAS_OBRIGATORIAS}"
        }

    nfs_existentes = obter_nfs_existentes()

    df_validos, df_erros = processar_csv_nfs(df, nfs_existentes)

    if not df_validos.empty:
        inserir_nfs_banco(df_validos)
        processar_comparacao_tf_idf(df_validos)

    tempo = round(time.time() - inicio, 3)

    return {
        "status": "ok",
        "linhas_recebidas": len(df),
        "linhas_validas": len(df_validos),
        "linhas_invalidas": len(df_erros),
        "tempo_processamento": f"{tempo}s",
        "total_nfs_armazenadas": len(pd.read_csv(NFS_CSV)),
        "invalidos": df_erros.to_dict(orient="records")
    }
