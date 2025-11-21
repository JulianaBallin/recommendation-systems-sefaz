from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.utilitarios.processar_usuarios import processar_csv_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


import os

USUARIOS_CSV = "dataset/processado/usuarios.csv"

def obter_cpfs_existentes():
    if not os.path.exists(USUARIOS_CSV):
        return set()
    
    try:
        df = pd.read_csv(USUARIOS_CSV)
        if "cpf" in df.columns:
            return set(df["cpf"].astype(str))
    except Exception:
        pass
        
    return set()


def inserir_usuarios_banco(df):
    if df.empty:
        return

    os.makedirs(os.path.dirname(USUARIOS_CSV), exist_ok=True)
    
    if not os.path.exists(USUARIOS_CSV):
        df.to_csv(USUARIOS_CSV, index=False)
    else:
        df.to_csv(USUARIOS_CSV, mode="a", header=False, index=False)


@router.post("/upload")
async def upload_usuarios(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    cpfs_existentes = obter_cpfs_existentes()

    df_validos, df_erros = processar_csv_usuarios(df, cpfs_existentes)

    inserir_usuarios_banco(df_validos)

    return {
        "status": "ok",
        "validos": len(df_validos),
        "invalidos": df_erros.to_dict(orient="records")
    }
