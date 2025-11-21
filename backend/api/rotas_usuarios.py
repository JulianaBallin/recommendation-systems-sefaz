from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os

from backend.utilitarios.processar_usuarios import processar_csv_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

CLIENTES_CSV = "dataset/processado/usuarios.csv"

def obter_cpfs_existentes():
    if not os.path.exists(CLIENTES_CSV):
        return set()
    
    try:
        df = pd.read_csv(CLIENTES_CSV)
        if "cpf" in df.columns:
            return set(df["cpf"].astype(str))
    except Exception:
        pass
        
    return set()


def inserir_usuarios_banco(df):
    if df.empty:
        return

    os.makedirs(os.path.dirname(CLIENTES_CSV), exist_ok=True)
    
    if not os.path.exists(CLIENTES_CSV):
        df.to_csv(CLIENTES_CSV, index=False)
    else:
        df.to_csv(CLIENTES_CSV, mode="a", header=False, index=False)


@router.post("/upload")
async def upload_usuarios(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    
    COLUNAS_OBRIGATORIAS = {"cpf", "nome"}

    if not COLUNAS_OBRIGATORIAS.issubset(df.columns.str.lower()):
        return {
            "status": "erro",
            "mensagem": f"Colunas obrigatórias ausentes. Esperado: {COLUNAS_OBRIGATORIAS}"
        }

    cpfs_existentes = obter_cpfs_existentes()

    df_validos, df_erros = processar_csv_usuarios(df, cpfs_existentes)

    inserir_usuarios_banco(df_validos)

    return {
        "status": "ok",
        "validos": len(df_validos),
        "invalidos": df_erros.to_dict(orient="records")
    }
