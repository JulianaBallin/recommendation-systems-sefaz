from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import os
import time

from backend.utilitarios.processar_nfs import processar_csv_nfs
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf
from backend.utilitarios.validadores import (
    validate_file_size,
    validate_file_type,
    validate_required_columns,
    validate_dataframe_not_empty,
    validate_nfs_data
)
from backend.utilitarios.response_formatter import upload_response, error_response
from backend.utilitarios.constants import ERROR_CODES

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
    
    try:
        # Validações de arquivo
        validate_file_type(file.filename)
        validate_file_size(file)
        
        # Ler CSV
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.lower()
        
        # Validar DataFrame
        validate_dataframe_not_empty(df)
        validate_required_columns(df, "nfs")
        
        total_recebidas = len(df)
        
        # Validar dados específicos de NFS
        df_pre_validados, validation_errors = validate_nfs_data(df)
        
        # Processar com lógica de negócio
        nfs_existentes = obter_nfs_existentes()
        df_validos, df_erros = processar_csv_nfs(df_pre_validados, nfs_existentes)
        
        # Combinar erros de validação e processamento
        all_errors = validation_errors + df_erros.to_dict(orient="records") if not df_erros.empty else validation_errors
        
        # Inserir válidos no banco
        if not df_validos.empty:
            inserir_nfs_banco(df_validos)
            processar_comparacao_tf_idf(df_validos)
        
        # Contar total armazenado
        total_stored = 0
        if os.path.exists(NFS_CSV):
            total_stored = len(pd.read_csv(NFS_CSV))
        
        tempo = time.time() - inicio
        
        return upload_response(
            total_received=total_recebidas,
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

