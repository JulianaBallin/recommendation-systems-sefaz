import re
import unicodedata
import pandas as pd
from datetime import datetime, date

def normalize_text(value: str) -> str:
    """Normaliza texto: remove acentos, caracteres especiais e espaços extras."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    # converte para maiúsculas
    text = text.upper()
    # remove acentos, mas mantém letras (ex.: Á -> A, ç -> C)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # mantém apenas letras, números e espaços
    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    # normaliza múltiplos espaços
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def validate_numeric(value, field: str):
    """Garante que seja número válido."""
    try:
        val = float(value)
        return val
    except Exception:
        raise ValueError(f"Formato inválido: {field} deve ser numérico.")


def validate_datetime(value, field: str) -> str:
    """
    Valida data e hora no formato DD/MM/YYYY HH:MM:SS.
    Aceita string ou datetime, mas sempre retorna string no formato brasileiro.
    """
    if value is None or str(value).strip() == "":
        raise ValueError(f"O campo '{field}' não pode estar vazio.")

    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.strptime(str(value), "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise ValueError(
                f"Formato inválido: {field} deve estar no formato DD/MM/AAAA HH:MM:SS (ex: 28/08/2025 22:32:40)."
            )

    ano_atual = datetime.today().year
    if dt.year < 2000 or dt.year > ano_atual:
        raise ValueError(
            f"O campo '{field}' deve estar entre o ano 2000 e {ano_atual}."
        )

    return dt.strftime("%d/%m/%Y %H:%M:%S")


def validate_date(value, field: str) -> str:
    """
    Valida string de data no formato DD/MM/YYYY, apenas entre 1950 e ano atual.
    Sempre retorna string no formato DD/MM/YYYY.
    """
    if value is None or str(value).strip() == "":
        raise ValueError(f"O campo '{field}' não pode estar vazio.")

    try:
        dt = datetime.strptime(str(value), "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(
            f"Formato inválido: {field} deve estar no formato DD/MM/AAAA (ex: 11/11/2011)."
        )

    ano_atual = datetime.today().year
    if dt.year < 1950 or dt.year > ano_atual:
        raise ValueError(
            f"O campo '{field}' deve estar entre 01/01/1950 e {ano_atual}."
        )

    return dt.strftime("%d/%m/%Y")

    
def validate_cpf(cpf: str) -> str:
    """Valida CPF: deve ter 11 dígitos numéricos."""
    digits = re.sub(r"\D", "", str(cpf))
    if len(digits) != 11:
        raise ValueError("Formato inválido: CPF deve ter 11 dígitos.")
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

def validate_cnpj(cnpj: str) -> str:
    """Valida CNPJ: deve ter 14 dígitos numéricos."""
    digits = re.sub(r"\D", "", str(cnpj))
    if len(digits) != 14:
        raise ValueError("Formato inválido: CNPJ deve ter 14 dígitos.")
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def remove_accents(text: str) -> str:
    """Remove acentos e normaliza string."""
    if not isinstance(text, str):
        return ""
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )


def validate_cpf(value: str) -> str:
    """
    Valida e normaliza CPF.
    Retorna apenas números se válido, senão levanta ValueError.
    """
    if not isinstance(value, str):
        value = str(value)

    # Remove caracteres não numéricos
    cpf = re.sub(r"\D", "", value)

    # Deve ter 11 dígitos
    if len(cpf) != 11 or not cpf.isdigit():
        raise ValueError(f"CPF inválido: {value}")

    # Rejeita CPFs com todos dígitos iguais
    if cpf == cpf[0] * 11:
        raise ValueError(f"CPF inválido: {value}")

    # Validação dos dígitos verificadores
    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[i]):
            raise ValueError(f"CPF inválido: {value}")

    return cpf


def validate_name(value: str) -> str:
    """
    Valida e normaliza nome próprio.
    - Remove acentos.
    - Só permite letras e espaços.
    - Converte para formato título.
    """
    if not isinstance(value, str):
        raise ValueError("Nome inválido: não é string.")

    nome = remove_accents(value).strip()

    # Só letras e espaços
    if not re.match(r"^[A-Za-z\s]+$", nome):
        raise ValueError(f"Nome inválido: {value}")

    # Converte para título (ex.: "joao silva" -> "Joao Silva")
    return " ".join([p.capitalize() for p in nome.split()])


def normalize_name(name: str) -> str:
    """Remove acentos, espaços extras e deixa maiúsculo para comparar nomes."""
    return normalize_text(name).upper().strip()