from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.utilitarios.processar_nfs import processar_csv_nfs

router = APIRouter(prefix="/nfs", tags=["Notas Fiscais"])

def obter_nfs_existentes():
    # depois: buscar no banco
    return set()

def inserir_nfs_banco(df):
    # depois: salvar no banco
    pass


@router.post("/upload")
async def upload_nfs(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    # aqui futuramente verificaremos duplicatas no banco
    nfs_existentes = obter_nfs_existentes()

    df_validos, df_erros = processar_csv_nfs(df, nfs_existentes)

    # inserir válidos no banco
    inserir_nfs_banco(df_validos)

    return {
        "status": "ok",
        "validos": len(df_validos),
        "invalidos": df_erros.to_dict(orient="records")
    }
