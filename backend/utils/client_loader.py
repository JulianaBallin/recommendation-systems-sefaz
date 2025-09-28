"""
client_loader.py
----------------
Funções para validação, limpeza e persistência de clientes.

Regras:
- CPF: deve ser válido e único
- Nome: não pode conter pontuação ou números
- Data de nascimento: deve ser válida no formato dd/mm/yyyy
- CEP: deve ser válido e restrito a Manaus-AM (69000-000 até 69099-999)
"""

import os
import re
import pandas as pd
from datetime import datetime
from backend.dataset import loader
from backend.utils.preprocessing import normalize_text
from backend.utils.preprocessing import validate_cpf, validate_name
from backend.dataset.loader import clean_dataframe


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

CLIENTS_RAW = os.path.join(BASE_DIR,"data/raw/clients.csv")


# Funções utilitárias de validação

def validate_cpf(cpf: str, existing_cpfs: list[str]) -> tuple[bool, str]:
    """
    Valida CPF brasileiro.
    - Deve ter 11 dígitos
    - Deve passar no cálculo dos dígitos verificadores
    - Não pode já existir no dataset
    """
    cpf = re.sub(r"[^0-9]", "", str(cpf))
    if len(cpf) != 11:
        return False, f"❌ CPF com tamanho inválido: {cpf}"

    if cpf in existing_cpfs:
        return False, f"❌ CPF já existente na base de dados: {cpf}"

    if cpf == cpf[0] * 11:
        return False, f"❌ CPF inválido (sequência repetida): {cpf}"

    def calc_digit(cpf_base: str, factors: list[int]) -> int:
        soma = sum(int(cpf_base[i]) * factors[i] for i in range(len(factors)))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    d1 = calc_digit(cpf[:9], list(range(10, 1, -1)))
    d2 = calc_digit(cpf[:10], list(range(11, 1, -1)))

    if cpf[-2:] != f"{d1}{d2}":
        return False, f"❌ CPF inválido (dígitos verificadores não conferem): {cpf}"

    return True, ""


def validate_name(name: str) -> tuple[bool, str]:
    """
    Valida o nome do cliente.
    - Não pode ser vazio
    - Deve conter apenas letras e espaços
    """
    if not name or str(name).strip() == "":
        return False, "❌ Nome não pode estar vazio"

    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", str(name)):
        return False, f"❌ Nome contém caracteres inválidos: {name}"

    return True, ""


def validate_birthdate(birthdate: str) -> tuple[bool, str]:
    """
    Valida a data de nascimento no formato dd/mm/yyyy.
    """
    try:
        datetime.strptime(str(birthdate).strip(), "%d/%m/%Y")
        return True, ""
    except Exception:
        return False, f"❌ Data de nascimento inválida: {birthdate}. Exemplo válido: 25/12/1990"


def validate_cep(cep: str) -> tuple[bool, str]:
    """
    Valida CEP.
    - Deve ter 8 dígitos
    - Deve estar dentro da faixa de Manaus-AM (69000-000 até 69099-999)
    """
    cep = re.sub(r"[^0-9]", "", str(cep))
    if len(cep) != 8:
        return False, f"❌ CEP inválido: {cep}"

    if not (69000000 <= int(cep) <= 69099999):
        return False, f"❌ CEP não pertence a Manaus-AM: {cep}"

    return True, ""


def validate_gender(gender: str) -> tuple[bool, str]:
    """
    Valida o gênero informado.
    Aceita: Feminino, Masculino ou Outro.
    Armazena somente a inicial no CSV (F, M, O).
    """
    gender = str(gender).strip().upper()
    if gender not in ["FEMININO", "MASCULINO", "OUTRO", "F", "M", "O"]:
        return False, f"❌ Gênero inválido: {gender}. Valores aceitos: Feminino, Masculino, Outro"
    return True, ""


# Funções principais

def load_clients(path: str = CLIENTS_RAW) -> pd.DataFrame:
    """
    Carrega a base de clientes.
    Retorna DataFrame vazio se não existir.
    """
    if os.path.exists(path) and os.stat(path).st_size > 0:
        df = pd.read_csv(path, dtype=str)
        df.columns = [c.strip().upper() for c in df.columns]  # 🔹 garante maiúsculo
        return df
    return pd.DataFrame(columns=["CPF", "NAME", "BIRTHDATE", "CEP", "GENDER"])  # 🔹 já em maiúsculo


def save_clients(df: pd.DataFrame, path: str = CLIENTS_RAW):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.columns = [c.strip().upper() for c in df.columns]   # 🔹 garante maiúsculo
    df = clean_dataframe(df, subset_cols=["CPF"])
    df.to_csv(path, index=False)


def append_client(record: dict, path: str = CLIENTS_RAW) -> tuple[bool, str]:
    """
    Adiciona um cliente individual à base.
    Retorna (True, "") se salvo com sucesso,
    ou (False, motivo) se inválido.
    """
    df = load_clients(path)
    existing_cpfs = df["CPF"].astype(str).tolist()

    # Validações
    ok, msg = validate_cpf(record.get("CPF", ""), existing_cpfs)
    if not ok:
        return False, msg

    ok, msg = validate_name(record.get("NAME", ""))
    if not ok:
        return False, msg

    ok, msg = validate_birthdate(record.get("BIRTHDATE", ""))
    if not ok:
        return False, msg

    ok, msg = validate_cep(record.get("CEP", ""))
    if not ok:
        return False, msg

    ok, msg = validate_gender(record.get("GENDER", ""))
    if not ok:
        return False, msg

    normalized = {
        "CPF": re.sub(r"[^0-9]", "", record["CPF"]),
        "NAME": normalize_text(record["NAME"]),
        "BIRTHDATE": record["BIRTHDATE"].strip(),
        "CEP": re.sub(r"[^0-9]", "", record["CEP"]),
        "GENDER": record["GENDER"].strip().upper()[0],
    }


    df = pd.concat([df, pd.DataFrame([normalized])], ignore_index=True)
    save_clients(df, path)
    return True, ""


def append_batch_clients(df_new: pd.DataFrame, path: str = CLIENTS_RAW) -> tuple[int, list[dict]]:
    """
    Adiciona clientes em lote a partir de um DataFrame.
    - Retorna (quantidade_adicionados, [ {Linha, Erro}, ... ])
    """
    df_existing = load_clients(path)
    existing_cpfs = df_existing["CPF"].astype(str).tolist()

    valid_rows = []
    errors = []

    for idx, row in df_new.iterrows():
        record = {
            "CPF": str(row.get("CPF", "")).strip(),
            "NAME": str(row.get("NAME", "")).strip(),
            "BIRTHDATE": str(row.get("BIRTHDATE", "")).strip(),
            "CEP": str(row.get("CEP", "")).strip(),
            "GENDER": str(row.get("GENDER", "")).strip(),
        }

        # 🔹 CPF
        ok, msg = validate_cpf(record["CPF"], existing_cpfs)
        if not ok:
            errors.append({"Linha": idx + 1, "Erro": msg})
            continue

        # 🔹 Nome
        ok, msg = validate_name(record["NAME"])
        if not ok:
            errors.append({"Linha": idx + 1, "Erro": msg})
            continue

        # 🔹 Data nascimento
        ok, msg = validate_birthdate(record["BIRTHDATE"])
        if not ok:
            errors.append({"Linha": idx + 1, "Erro": msg})
            continue

        # 🔹 CEP
        ok, msg = validate_cep(record["CEP"])
        if not ok:
            errors.append({"Linha": idx + 1, "Erro": msg})
            continue

        # 🔹 Gênero
        ok, msg = validate_gender(record["GENDER"])
        if not ok:
            errors.append({"Linha": idx + 1, "Erro": msg})
            continue

        # ✅ Se passou em tudo, normaliza e adiciona
        normalized = {
            "CPF": re.sub(r"[^0-9]", "", record["CPF"]),
            "NAME": normalize_text(record["NAME"]),
            "BIRTHDATE": record["BIRTHDATE"],
            "CEP": re.sub(r"[^0-9]", "", record["CEP"]),
            "GENDER": record["GENDER"].upper()[0],  # F, M, O
        }

        valid_rows.append(normalized)
        existing_cpfs.append(normalized["CPF"])

    # 🔹 Salva se houver válidos
    if valid_rows:
        df_final = pd.concat([df_existing, pd.DataFrame(valid_rows)], ignore_index=True)
        save_clients(df_final, path)

    return len(valid_rows), errors


def preview_clients(path: str = CLIENTS_RAW, n: int = 10) -> dict:
    """
    Retorna preview da base de clientes:
    - primeiras n linhas
    - últimas n linhas
    - total de registros
    Evita duplicação quando há poucos registros.
    """
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return {"preview": pd.DataFrame(), "total": 0}

    df = pd.read_csv(path)
    total = len(df)

    if total <= 2 * n:
        # 🔹 Se poucos registros, mostra todos
        preview = df
    else:
        # 🔹 Caso contrário, mostra início e fima
        preview = pd.concat([df.head(n), df.tail(n)])

    return {"preview": preview, "total": total}


def clean_clients(df: pd.DataFrame) -> pd.DataFrame:
    """Valida e normaliza clientes (CPF, nome, etc)."""
    required_cols = ["CPF", "NOME", "DATA_NASC", "CEP", "SEXO"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")
        if df[col].isnull().any() or (df[col].astype(str).str.strip() == "").any():
            raise ValueError(f"O campo '{col}' não pode estar vazio.")

    df["CPF"] = df["CPF"].apply(validate_cpf)
    df["NOME"] = df["NOME"].apply(normalize_text)
    df["CEP"] = df["CEP"].apply(lambda x: re.sub(r"\D", "", str(x)))
    df = df.drop_duplicates(subset=["CPF"], keep="first")

    return df.reset_index(drop=True)