"""
product_loader.py
-----------------
Funções auxiliares para:
- Limpeza e validação de produtos
- Geração de IDs únicos
- Inserção unitária ou em lote nos datasets
- Contagem de registros
"""

import os
import pandas as pd
from datetime import datetime
from backend.utils.preprocessing import (
    normalize_text,
    validate_numeric,
    validate_datetime,
    validate_cnpj,
)
from backend.utils import dictionaries
from backend.dataset import loader

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Caminhos padrões
DATA_RAW = os.path.join(BASE_DIR,"data/raw/receipts_nf.csv")
DATA_DERIVED = os.path.join(BASE_DIR,"data/derived/products.csv")

REQUIRED_COLUMNS = [
    "CODIGO","DESCRICAO","QTD","UN","VALOR_UNITARIO","VALOR_TOTAL",
    "NOME_SUPERMERCADO","CNPJ","ENDERECO","NUMERO_NFCE","SERIE","DATA_HORA_COMPRA"
]

def validate_cnpj(cnpj: str) -> bool:
    """Valida CNPJ brasileiro (14 dígitos com DV)."""
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    def calc_digit(base: str, multipliers: list[int]) -> int:
        soma = sum(int(base[i]) * multipliers[i] for i in range(len(multipliers)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    m1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    m2 = [6] + m1
    d1 = calc_digit(cnpj[:12], m1)
    d2 = calc_digit(cnpj[:12] + str(d1), m2)
    return cnpj[-2:] == f"{d1}{d2}"


def validate_receipts(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Valida DataFrame de NF antes de salvar.
    Retorna (True, "") se válido, ou (False, motivo) se inválido.
    """
    # Colunas obrigatórias
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            return False, f"Coluna obrigatória ausente: {col}. Exemplo esperado: {','.join(REQUIRED_COLUMNS)}"

    # Linha a linha
    for idx, row in df.iterrows():
        # Campos vazios
        for col in REQUIRED_COLUMNS:
            if pd.isna(row[col]) or str(row[col]).strip() == "":
                return False, f"Linha {idx+1}: campo {col} vazio. Exemplo esperado para {col}: 'VALOR_TOTAL=326.72', 'CNPJ=06.710.613/0009-56'"

        # Inteiros
        for col in ["CODIGO", "NUMERO_NFCE", "SERIE"]:
            try:
                int(str(row[col]).replace(".0", ""))
            except Exception:
                return False, f"Linha {idx+1}: {col} inválido ({row[col]}). Exemplo esperado: CODIGO=136269016710, SERIE=017"

        # QTD
        try:
            qtd = int(row["QTD"])
            if qtd < 1:
                return False, f"Linha {idx+1}: QTD inválido ({row['QTD']}). Exemplo esperado: QTD=8"
        except Exception:
            return False, f"Linha {idx+1}: QTD inválido ({row['QTD']}). Exemplo esperado: QTD=8"

        # Valores numéricos
        try:
            float(row["VALOR_UNITARIO"])
            float(row["VALOR_TOTAL"])
        except Exception:
            return False, f"Linha {idx+1}: VALOR_UNITARIO/VALOR_TOTAL inválidos ({row['VALOR_UNITARIO']}/{row['VALOR_TOTAL']}). Exemplo esperado: VALOR_UNITARIO=40.84, VALOR_TOTAL=326.72"

        # Data
        try:
            datetime.strptime(str(row["DATA_HORA_COMPRA"]).strip(), "%d/%m/%Y %H:%M:%S")
        except Exception:
            return False, f"Linha {idx+1}: DATA_HORA_COMPRA inválida ({row['DATA_HORA_COMPRA']}). Exemplo esperado: 28/08/2025 22:32:40"

        # CNPJ
        if not validate_cnpj(row["CNPJ"]):
            return False, f"Linha {idx+1}: CNPJ inválido ({row['CNPJ']}). Exemplo válido: 06.710.613/0009-56"

    return True, ""

# ======================================================
# 🔹 Funções de limpeza de DataFrames de produtos
# ======================================================

def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida e limpa o DataFrame de produtos brutos.
    - Checa campos obrigatórios
    - Normaliza textos
    - Valida CNPJs, numéricos e datas
    - Remove duplicados
    """
    required_cols = [
        "CODIGO", "DESCRICAO", "QTD", "UN", "VALOR_UNITARIO",
        "VALOR_TOTAL", "NOME_SUPERMERCADO", "CNPJ", "ENDERECO",
        "NUMERO_NFCE", "SERIE", "DATA_HORA_COMPRA",
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")
        if df[col].isnull().any() or (df[col].astype(str).str.strip() == "").any():
            raise ValueError(f"O campo '{col}' não pode estar vazio.")

    # Normalizações
    df["DESCRICAO"] = df["DESCRICAO"].apply(normalize_text)
    df["NOME_SUPERMERCADO"] = df["NOME_SUPERMERCADO"].apply(normalize_text)
    df["ENDERECO"] = df["ENDERECO"].apply(normalize_text)

    # CNPJ
    df["CNPJ"] = df["CNPJ"].apply(validate_cnpj)

    # Numéricos
    for col in ["CODIGO", "QTD", "VALOR_UNITARIO", "VALOR_TOTAL", "NUMERO_NFCE", "SERIE"]:
        df[col] = df[col].apply(lambda x: validate_numeric(x, col))

    # Datas
    df["DATA_HORA_COMPRA"] = df["DATA_HORA_COMPRA"].apply(
        lambda x: validate_datetime(x, "DATA_HORA_COMPRA")
    )

    # Deduplicação
    df = df.drop_duplicates(subset=["CODIGO", "NUMERO_NFCE"], keep="first")

    return df.reset_index(drop=True)


# ======================================================
# 🔹 Funções de validação individual
# ======================================================

def validate_categoria(categoria: str, cat_map: pd.DataFrame) -> tuple[bool, str]:
    """Valida categoria contra o mapa de categorias."""
    if categoria in cat_map["chave_categoria"].unique():
        return True, ""
    return False, f"Categoria inválida: {categoria}"


def validate_marca(marca: str, brand_map: pd.DataFrame) -> tuple[bool, str]:
    """Valida marca contra o mapa de marcas."""
    if marca == "Genérica" or marca in brand_map["marca"].unique():
        return True, ""
    return False, f"Marca inválida: {marca}"


def validate_descricao(descricao: str) -> tuple[bool, str]:
    """Valida se a descrição é não vazia e suficientemente longa."""
    if not descricao.strip():
        return False, "Descrição não pode estar vazia"
    if len(descricao.strip()) < 3:
        return False, "Descrição muito curta"
    return True, ""


def validate_produto(
    categoria: str, marca: str, descricao: str,
    cat_map: pd.DataFrame, brand_map: pd.DataFrame
) -> tuple[bool, str]:
    """Valida os três campos principais de um produto (categoria, marca, descrição)."""
    ok, msg = validate_categoria(categoria, cat_map)
    if not ok:
        return False, msg
    ok, msg = validate_marca(marca, brand_map)
    if not ok:
        return False, msg
    ok, msg = validate_descricao(descricao)
    if not ok:
        return False, msg
    return True, ""


def normalize_and_validate(
    description: str, cat_map: pd.DataFrame = None, brand_map: pd.DataFrame = None
) -> dict:
    """
    Normaliza e valida um produto a partir da descrição:
    - Extrai Categoria e Marca usando dictionaries
    - Valida com os mapas
    - Retorna dict pronto para salvar
    """
    if cat_map is None:
        cat_map = dictionaries.load_category_map()
    if brand_map is None:
        brand_map = dictionaries.load_brand_map()

    produto = dictionaries.normalize_product(description)
    ok, msg = validate_produto(
        produto["Categoria"], produto["Marca"], produto["Descricao"], cat_map, brand_map
    )
    if not ok:
        raise ValueError(f"Produto inválido: {msg} | {description}")

    return produto


# ======================================================
# 🔹 Funções de persistência (ID, Append, Contagem)
# ======================================================

def generate_unique_id(df: pd.DataFrame, id_col: str = "ID") -> int:
    """
    Gera ID único incremental com base no maior já existente.
    Retorna 1 se não houver registros.
    """
    if df.empty or id_col not in df.columns:
        return 1
    return int(df[id_col].max()) + 1


def append_product(record: dict, derived_path: str = DATA_DERIVED) -> int:
    """
    Adiciona um único produto ao dataset derivado.
    Retorna o ID gerado.
    """
    os.makedirs(os.path.dirname(derived_path), exist_ok=True)

    if os.path.exists(derived_path) and os.stat(derived_path).st_size > 0:
        df = pd.read_csv(derived_path)
    else:
        # cria DataFrame vazio com as colunas corretas
        df = pd.DataFrame(columns=["ID", "Categoria", "Marca", "Descricao"])

    # Gera ID
    new_id = generate_unique_id(df)
    record["ID"] = new_id
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(derived_path, index=False)

    return new_id


def generate_unique_id(df: pd.DataFrame) -> int:
    """Gera novo ID único incremental para produto derivado."""
    if df.empty or "ID" not in df.columns:
        return 1
    return int(df["ID"].max()) + 1


# ======================================================
# 🔹 Função principal de inserção em lote
# ======================================================
def append_batch(
    df_new: pd.DataFrame,
    raw_path: str = loader.RAW_RECEIPTS,
    derived_path: str = loader.DERIVED_PRODUCTS,
) -> int:
    """
    Adiciona lote de produtos (NF → raw + derived).
    - Valida todos os registros
    - Salva raw (completo)
    - Gera derived (ID, Categoria, Marca, Descricao)
    Retorna a quantidade de novos produtos adicionados.
    """
    # ==============================
    # 1. Validação
    # ==============================
    is_valid, msg = validate_receipts(df_new)
    if not is_valid:
        raise ValueError(f"Erro de validação no CSV: {msg}")

    # ==============================
    # 2. RAW (Notas fiscais completas)
    # ==============================
    if os.path.exists(raw_path) and os.stat(raw_path).st_size > 0:
        raw = pd.read_csv(raw_path)
    else:
        raw = pd.DataFrame(columns=df_new.columns)

    raw = pd.concat([raw, df_new], ignore_index=True)
    raw.to_csv(raw_path, index=False)

    # ==============================
    # 3. DERIVED (Produtos normalizados)
    # ==============================
    if os.path.exists(derived_path) and os.stat(derived_path).st_size > 0:
        derived = pd.read_csv(derived_path)
    else:
        derived = pd.DataFrame(columns=["ID", "Categoria", "Marca", "Descricao"])

    novos = []
    for _, row in df_new.iterrows():
        # Normaliza produto pela descrição
        produto = dictionaries.normalize_product(str(row["DESCRICAO"]))

        # Gera ID único
        produto["ID"] = generate_unique_id(derived)

        novos.append(produto)
        derived = pd.concat([derived, pd.DataFrame([produto])], ignore_index=True)

    derived.to_csv(derived_path, index=False)

    return len(novos)


def count_records(path: str) -> int:
    """Conta registros de um CSV. Retorna 0 se não existir."""
    if not os.path.exists(path):
        return 0
    return len(pd.read_csv(path))
