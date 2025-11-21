from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import os
import time

from backend.utilitarios.processar_usuarios import processar_csv_usuarios
from backend.utilitarios.validadores import (
    validate_file_size,
    validate_file_type,
    validate_required_columns,
    validate_dataframe_not_empty,
    validate_usuarios_data
)
from backend.utilitarios.response_formatter import upload_response, error_response
from backend.utilitarios.constants import ERROR_CODES

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
    inicio = time.time()
    
    try:
        # Validações de arquivo
        validate_file_type(file.filename)
        validate_file_size(file)
        
        # Ler CSV
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.lower()
        
        # Validar DataFrame
        validate_dataframe_not_empty(df)
        validate_required_columns(df, "usuarios")
        
        total_recebidos = len(df)
        
        # Validar dados específicos de usuários (CPF, nome, etc.)
        df_pre_validados, validation_errors = validate_usuarios_data(df)
        
        # Processar com lógica de negócio (duplicações, etc.)
        cpfs_existentes = obter_cpfs_existentes()
        df_validos, df_erros = processar_csv_usuarios(df_pre_validados, cpfs_existentes)
        
        # Combinar erros de validação e processamento
        all_errors = validation_errors + df_erros.to_dict(orient="records") if not df_erros.empty else validation_errors
        
        # Inserir válidos no banco
        if not df_validos.empty:
            inserir_usuarios_banco(df_validos)
        
        # Contar total armazenado
        total_stored = 0
        if os.path.exists(CLIENTES_CSV):
            total_stored = len(pd.read_csv(CLIENTES_CSV))
        
        tempo = time.time() - inicio
        
        return upload_response(
            total_received=total_recebidos,
            total_valid=len(df_validos),
            total_invalid=len(all_errors),
            processing_time=tempo,
            total_stored=total_stored,
            invalid_records=all_errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Erro ao processar arquivo: {str(e)}",
            code=ERROR_CODES["PROCESSING_ERROR"],
            details={"error_type": type(e).__name__},
            status_code=500
        )

