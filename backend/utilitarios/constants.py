"""
Constantes para validações e configurações do sistema.
"""

# Limites de arquivo
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Formatos permitidos
ALLOWED_FILE_TYPES = [".csv"]

# Colunas obrigatórias por tipo
REQUIRED_COLUMNS = {
    "nfs": ["descricao"],
    "usuarios": ["cpf", "nome"]
}

# Mensagens de erro
ERROR_MESSAGES = {
    "FILE_TOO_LARGE": f"Arquivo muito grande. Tamanho máximo permitido: {MAX_FILE_SIZE_MB}MB",
    "INVALID_FILE_TYPE": f"Tipo de arquivo inválido. Formatos permitidos: {', '.join(ALLOWED_FILE_TYPES)}",
    "EMPTY_FILE": "Arquivo vazio ou sem dados válidos",
    "MISSING_COLUMNS": "Colunas obrigatórias ausentes: {missing}",
    "INVALID_CPF": "CPF inválido: {cpf}",
    "EMPTY_REQUIRED_FIELD": "Campo obrigatório vazio: {field}",
    "INVALID_DATA_TYPE": "Tipo de dado inválido na coluna {column}",
    "PROCESSING_ERROR": "Erro ao processar arquivo: {error}"
}

# Códigos de erro
ERROR_CODES = {
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "FILE_ERROR": "FILE_ERROR",
    "PROCESSING_ERROR": "PROCESSING_ERROR",
    "SERVER_ERROR": "SERVER_ERROR"
}
