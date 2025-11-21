"""
Formatadores de resposta padronizados para a API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


def get_timestamp() -> str:
    """Retorna timestamp atual no formato ISO."""
    return datetime.now().isoformat()


def success_response(
    data: Any,
    metadata: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Formata resposta de sucesso padronizada.
    
    Args:
        data: Dados da resposta
        metadata: Metadados opcionais
        message: Mensagem opcional
        
    Returns:
        Dict com resposta formatada
    """
    response = {
        "status": "success",
        "timestamp": get_timestamp(),
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
    
    if message:
        response["message"] = message
    
    return response


def error_response(
    message: str,
    code: str = "ERROR",
    details: Optional[Any] = None,
    status_code: int = 500
) -> Dict[str, Any]:
    """
    Formata resposta de erro padronizada.
    
    Args:
        message: Mensagem de erro
        code: Código do erro
        details: Detalhes adicionais
        status_code: Código HTTP
        
    Returns:
        Dict com resposta formatada
    """
    response = {
        "status": "error",
        "timestamp": get_timestamp(),
        "error": {
            "code": code,
            "message": message,
            "http_status": status_code
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def upload_response(
    total_received: int,
    total_valid: int,
    total_invalid: int,
    processing_time: float,
    total_stored: Optional[int] = None,
    invalid_records: Optional[List[Dict]] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Formata resposta específica para uploads.
    
    Args:
        total_received: Total de linhas recebidas
        total_valid: Total de linhas válidas
        total_invalid: Total de linhas inválidas
        processing_time: Tempo de processamento em segundos
        total_stored: Total de registros armazenados
        invalid_records: Lista de registros inválidos
        additional_info: Informações adicionais
        
    Returns:
        Dict com resposta formatada
    """
    data = {
        "lines_received": total_received,
        "lines_valid": total_valid,
        "lines_invalid": total_invalid,
        "success_rate": round((total_valid / total_received * 100) if total_received > 0 else 0, 2)
    }
    
    metadata = {
        "processing_time_seconds": round(processing_time, 3),
        "processing_time_formatted": f"{processing_time:.3f}s"
    }
    
    if total_stored is not None:
        data["total_records_stored"] = total_stored
    
    if invalid_records:
        data["invalid_records"] = invalid_records[:10]  # Limitar a 10 para não sobrecarregar
        if total_invalid > 10:
            data["invalid_records_shown"] = 10
            data["invalid_records_total"] = total_invalid
    
    if additional_info:
        metadata.update(additional_info)
    
    return success_response(data=data, metadata=metadata)


def recommendation_response(
    recommendations: List[Dict[str, Any]],
    user_cpf: str,
    algorithm: str,
    processing_time: Optional[float] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Formata resposta específica para recomendações.
    
    Args:
        recommendations: Lista de recomendações
        user_cpf: CPF do usuário
        algorithm: Algoritmo utilizado
        processing_time: Tempo de processamento
        additional_metadata: Metadados adicionais
        
    Returns:
        Dict com resposta formatada
    """
    data = {
        "recommendations": recommendations,
        "total_recommendations": len(recommendations)
    }
    
    metadata = {
        "user_cpf": user_cpf,
        "algorithm": algorithm
    }
    
    if processing_time is not None:
        metadata["processing_time_seconds"] = round(processing_time, 3)
    
    if additional_metadata:
        metadata.update(additional_metadata)
    
    return success_response(data=data, metadata=metadata)


def metrics_response(
    metrics: Dict[str, Any],
    user_cpf: str,
    algorithm: str,
    k_value: int,
    processing_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Formata resposta específica para métricas.
    
    Args:
        metrics: Dicionário com métricas calculadas
        user_cpf: CPF do usuário
        algorithm: Algoritmo utilizado
        k_value: Valor de K usado
        processing_time: Tempo de processamento
        
    Returns:
        Dict com resposta formatada
    """
    metadata = {
        "user_cpf": user_cpf,
        "algorithm": algorithm,
        "k_value": k_value
    }
    
    if processing_time is not None:
        metadata["processing_time_seconds"] = round(processing_time, 3)
    
    return success_response(data=metrics, metadata=metadata)
