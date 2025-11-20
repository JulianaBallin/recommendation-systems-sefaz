from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.utilitarios.processar_nfs import processar_csv_nfs

router = APIRouter(prefix="/nfs", tags=["Notas Fiscais"])

import os
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf

NFS_CSV = "dataset/processado/nfs_processadas.csv"

def obter_nfs_existentes():
    if not os.path.exists(NFS_CSV):
        return set()
    
    try:
        df = pd.read_csv(NFS_CSV)
        # Cria chave composta para verificação
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
    df = pd.read_csv(file.file)

    nfs_existentes = obter_nfs_existentes()

    df_validos, df_erros = processar_csv_nfs(df, nfs_existentes)

    # inserir válidos no banco
    if not df_validos.empty:
        inserir_nfs_banco(df_validos)
        
        # Trigger TF-IDF
        processar_comparacao_tf_idf(df_validos)

    return {
        "status": "ok",
        "validos": len(df_validos),
        "invalidos": df_erros.to_dict(orient="records")
    }
