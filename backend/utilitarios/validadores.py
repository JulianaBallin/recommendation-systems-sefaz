"""
Funções de validação para uploads e dados.
"""

import re
import pandas as pd
from datetime import datetime
from fastapi import UploadFile, HTTPException
from typing import Set, List, Tuple
from backend.utilitarios.constants import (
    MAX_FILE_SIZE_BYTES,
    ALLOWED_FILE_TYPES,
    ERROR_MESSAGES,
    ERROR_CODES,
    REQUIRED_COLUMNS
)


# ==================== VALIDAÇÕES DE ARQUIVO ====================

def validate_file_size(file: UploadFile) -> None:
    """
    Valida o tamanho do arquivo.
    
    Args:
        file: Arquivo enviado
        
    Raises:
        HTTPException: Se arquivo for muito grande
    """
    # Ler o conteúdo para verificar tamanho
    file.file.seek(0, 2)  # Ir para o final do arquivo
    file_size = file.file.tell()
    file.file.seek(0)  # Voltar ao início
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": ERROR_CODES["FILE_ERROR"],
                "message": ERROR_MESSAGES["FILE_TOO_LARGE"],
                "file_size_mb": round(file_size / (1024 * 1024), 2)
            }
        )


def validate_file_type(filename: str) -> None:
    """
    Valida o tipo do arquivo pela extensão.
    
    Args:
        filename: Nome do arquivo
        
    Raises:
        HTTPException: Se tipo de arquivo não for permitido
    """
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=415,
            detail={
                "code": ERROR_CODES["FILE_ERROR"],
                "message": ERROR_MESSAGES["INVALID_FILE_TYPE"],
                "received": filename.split(".")[-1] if "." in filename else "unknown"
            }
        )


def validate_dataframe_not_empty(df: pd.DataFrame) -> None:
    """
    Valida se o DataFrame não está vazio.
    
    Args:
        df: DataFrame para validar
        
    Raises:
        HTTPException: Se DataFrame estiver vazio
    """
    if df.empty:
        raise HTTPException(
            status_code=400,
            detail={
                "code": ERROR_CODES["VALIDATION_ERROR"],
                "message": ERROR_MESSAGES["EMPTY_FILE"]
            }
        )


def validate_required_columns(df: pd.DataFrame, entity_type: str) -> None:
    """
    Valida se o DataFrame possui as colunas obrigatórias.
    
    Args:
        df: DataFrame para validar
        entity_type: Tipo da entidade ("nfs" ou "usuarios")
        
    Raises:
        HTTPException: Se colunas obrigatórias estiverem ausentes
    """
    required = set(REQUIRED_COLUMNS.get(entity_type, []))
    existing = set(df.columns.str.lower())
    missing = required - existing
    
    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "code": ERROR_CODES["VALIDATION_ERROR"],
                "message": ERROR_MESSAGES["MISSING_COLUMNS"].format(missing=", ".join(missing)),
                "missing_columns": list(missing),
                "required_columns": list(required)
            }
        )


# ==================== VALIDAÇÕES DE DADOS ====================

def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF com verificação de dígitos verificadores.
    
    Args:
        cpf: CPF para validar
        
    Returns:
        True se válido, False caso contrário
    """
    cpf = re.sub(r"[^0-9]", "", str(cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    # Validar dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito

        if digito != int(cpf[i]):
            return False

    return True


def validate_usuarios_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[dict]]:
    """
    Valida dados específicos de usuários.
    
    Args:
        df: DataFrame com dados de usuários
        
    Returns:
        Tupla (dados_validos, erros)
    """
    errors = []
    valid_indices = []
    
    for idx, row in df.iterrows():
        row_errors = []
        
        # Validar CPF
        cpf_valor = row.get('cpf')
        if pd.isna(cpf_valor) or not validar_cpf(cpf_valor):
            row_errors.append(f"CPF inválido: {cpf_valor}")
        
        # Validar nome não-vazio
        if pd.isna(row.get('nome')) or str(row.get('nome')).strip() == '':
            row_errors.append("Nome não pode ser vazio")
        
        if row_errors:
            errors.append({
                "row": int(idx),
                "data": row.to_dict(),
                "errors": row_errors
            })
        else:
            valid_indices.append(idx)
    
    df_valid = df.loc[valid_indices].copy() if valid_indices else pd.DataFrame()
    
    return df_valid, errors


def validate_nfs_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[dict]]:
    """
    Valida dados específicos de NFS.
    
    Args:
        df: DataFrame com dados de NFS
        
    Returns:
        Tupla (dados_validos, erros)
    """
    errors = []
    valid_indices = []
    
    for idx, row in df.iterrows():
        row_errors = []
        
        # Validar descrição não-vazia
        if pd.isna(row.get('descricao')) or str(row.get('descricao')).strip() == '':
            row_errors.append("Descrição não pode ser vazia")
        
        if row_errors:
            errors.append({
                "row": int(idx),
                "data": row.to_dict(),
                "errors": row_errors
            })
        else:
            valid_indices.append(idx)
    
    df_valid = df.loc[valid_indices].copy() if valid_indices else pd.DataFrame()
    
    return df_valid, errors


# ==================== FUNÇÕES DE LIMPEZA ====================

def limpar_cpf(cpf: str) -> str:
    """Remove caracteres não numéricos do CPF."""
    return re.sub(r"[^0-9]", "", str(cpf))


def limpar_nome(nome: str) -> str:
    """Limpa e formata nome."""
    nome = str(nome)
    nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", nome).strip()
    nome = re.sub(r"\s+", " ", nome)
    return nome.title()


def limpar_data(data: str) -> str:
    """Padroniza formato de data para YYYY-MM-DD."""
    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]

    data = str(data).strip()

    for fmt in formatos:
        try:
            return datetime.strptime(data, fmt).strftime("%Y-%m-%d")
        except:
            pass

    return ""
