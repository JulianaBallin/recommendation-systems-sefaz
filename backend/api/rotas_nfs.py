from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import os
import time

from backend.utilitarios.validadores import (
    validate_file_size,
    validate_file_type,
    validate_required_columns,
    validate_dataframe_not_empty,
    validate_nfs_data
)
from backend.utilitarios.processar_nfs import processar_csv_nfs
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf, filtrar_nfs_novas
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


def obter_total_nfs():
    if not os.path.exists(NFS_CSV):
        return 0
    try:
        return len(pd.read_csv(NFS_CSV))
    except Exception:
        return 0


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
        
        print(f"[DEBUG] Colunas lidas: {df.columns.tolist()}")
        print(f"[DEBUG] Total de linhas após leitura: {len(df)}")
        
        # Remover linhas vazias (comum em CSVs com linhas intercaladas)
        df = df.dropna(subset=['descricao'])
        df = df[df['descricao'].str.strip() != '']
        
        print(f"[DEBUG] Total de linhas após remover vazias: {len(df)}")
        
        # Validar DataFrame
        validate_dataframe_not_empty(df)
        validate_required_columns(df, "nfs")
        
        total_recebidas = len(df)
        
        # Validar dados específicos de NFS
        df_pre_validados, validation_errors = validate_nfs_data(df)
        
        print(f"[DEBUG] Linhas pré-validadas: {len(df_pre_validados)}")
        print(f"[DEBUG] Erros de validação: {len(validation_errors)}")
        
        # Processar com lógica de negócio
        nfs_existentes = obter_nfs_existentes()
        print(f"[DEBUG] NFs existentes no banco: {len(nfs_existentes)}")
        
        df_validos, df_erros = processar_csv_nfs(df_pre_validados, nfs_existentes)
        
        print(f"[DEBUG] Linhas válidas após processar: {len(df_validos)}")
        print(f"[DEBUG] Linhas com erro após processar: {len(df_erros)}")
        
        # Combinar erros de validação e processamento
        all_errors = validation_errors + df_erros.to_dict(orient="records") if not df_erros.empty else validation_errors
        
        # Inserir válidos no banco
        if not df_validos.empty:
            inserir_nfs_banco(df_validos)
            
            # Pipeline incremental: processar apenas novas descrições
            df_novas = filtrar_nfs_novas(df_validos)
            produtos_novos = len(df_novas)
            produtos_duplicados = len(df_validos) - produtos_novos
            
            # Processar TF-IDF apenas para produtos novos
            if not df_novas.empty:
                processar_comparacao_tf_idf(df_novas)
        else:
            produtos_novos = 0
            produtos_duplicados = 0
        
        tempo_decorrido = time.time() - inicio
        total_no_banco = obter_total_nfs()
        
        # Preparar resposta com estatísticas incrementais
        response = upload_response(
            total_received=total_recebidas,
            total_valid=len(df_validos),
            total_invalid=len(all_errors),
            total_stored=total_no_banco,
            processing_time=tempo_decorrido,
            invalid_records=all_errors,
            additional_info={
                "produtos_novos_processados": produtos_novos,
                "produtos_duplicados_ignorados": produtos_duplicados
            }
        )
        
        print(f"[DEBUG] Resposta sendo retornada:")
        print(f"[DEBUG] lines_valid={len(df_validos)}, lines_invalid={len(all_errors)}")
        print(f"[DEBUG] Response data: {response}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Erro ao processar arquivo: {str(e)}",
            code=ERROR_CODES["PROCESSING_ERROR"],
            details={"error_type": type(e).__name__},
            status_code=500
        )
