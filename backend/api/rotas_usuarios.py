from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.utilitarios.processar_usuarios import processar_csv_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def obter_cpfs_existentes():
    return set()


def inserir_usuarios_banco(df):
    pass


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
