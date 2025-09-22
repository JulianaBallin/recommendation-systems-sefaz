import csv
import os
import unicodedata
import re
from datetime import datetime

# sobe apenas até a raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

DATASET_PATH = os.path.join(BASE_DIR, "data", "raw", "products.csv")


def normalize_text(text: str) -> str:
    """Remove acentos, caracteres especiais e converte para maiúsculas."""
    if not isinstance(text, str):
        return text
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c) and (c.isalnum() or c.isspace())]).upper().strip()


def validate_product(codigo, descricao, qtd, un, valor_unitario, valor_total,
                     supermercado, cnpj, endereco, numero_nfce, serie, data_compra):
    """Valida todos os campos do produto antes de salvar."""

    # Campos obrigatórios
    fields = {
        "Código": codigo,
        "Descrição": descricao,
        "Quantidade": qtd,
        "Unidade": un,
        "Valor Unitário": valor_unitario,
        "Valor Total": valor_total,
        "Supermercado": supermercado,
        "CNPJ": cnpj,
        "Endereço": endereco,
        "Número NFCE": numero_nfce,
        "Série": serie,
        "Data/Hora Compra": data_compra
    }
    for name, value in fields.items():
        if value is None or str(value).strip() == "":
            raise ValueError(f"O campo '{name}' é obrigatório e não pode estar vazio.")

    # Código, NFCE e Série devem ser numéricos
    if not str(codigo).isdigit():
        raise ValueError("Código deve conter apenas números.")
    if not str(numero_nfce).isdigit():
        raise ValueError("Número NFCE deve conter apenas números.")
    if not str(serie).isdigit():
        raise ValueError("Série deve conter apenas números.")

    # Quantidade
    try:
        qtd_int = int(qtd)
        if qtd_int <= 0:
            raise ValueError("Quantidade deve ser um número inteiro positivo.")
    except ValueError:
        raise ValueError("Quantidade inválida. Informe um número inteiro.")

    # Valores
    try:
        vu = float(valor_unitario)
        vt = float(valor_total)
        if vu <= 0 or vt <= 0:
            raise ValueError("Valores devem ser maiores que zero.")
    except ValueError:
        raise ValueError("Valor Unitário e Valor Total devem ser numéricos válidos.")

    # CNPJ no formato 99.999.999/9999-99
    if not re.match(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$", cnpj):
        raise ValueError("CNPJ inválido. Formato esperado: 99.999.999/9999-99")

    # Data no formato dd/mm/yyyy HH:MM:SS
    try:
        datetime.strptime(data_compra, "%d/%m/%Y %H:%M:%S")
    except ValueError:
        raise ValueError("Data/Hora inválida. Formato esperado: dd/mm/yyyy HH:MM:SS")

    return True


def add_product(codigo: str, descricao: str, qtd: int, un: str,
                valor_unitario: float, valor_total: float,
                supermercado: str, cnpj: str, endereco: str,
                numero_nfce: str, serie: str, data_compra: str) -> None:
    """Adiciona um único produto ao dataset products.csv, validando antes."""
    
    # Validação
    validate_product(codigo, descricao, qtd, un, valor_unitario, valor_total,
                     supermercado, cnpj, endereco, numero_nfce, serie, data_compra)

    row = [
        normalize_text(str(codigo)),
        normalize_text(descricao),
        int(qtd),
        normalize_text(un),
        float(valor_unitario),
        float(valor_total),
        normalize_text(supermercado),
        normalize_text(cnpj),
        normalize_text(endereco),
        normalize_text(str(numero_nfce)),
        normalize_text(str(serie)),
        normalize_text(data_compra)  # já validada
    ]

    file_exists = os.path.isfile(DATASET_PATH)
    with open(DATASET_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:  # primeira vez, escrever cabeçalho
            writer.writerow([
                "CODIGO","DESCRICAO","QTD","UN","VALOR_UNITARIO","VALOR_TOTAL",
                "NOME_SUPERMERCADO","CNPJ","ENDERECO","NUMERO_NFCE","SERIE","DATA_HORA_COMPRA"
            ])
        writer.writerow(row)


def add_products_from_csv(csv_path: str) -> None:
    """Adiciona vários produtos a partir de um CSV externo, validando cada linha."""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            add_product(
                codigo=row["CODIGO"],
                descricao=row["DESCRICAO"],
                qtd=row["QTD"],
                un=row["UN"],
                valor_unitario=row["VALOR_UNITARIO"],
                valor_total=row["VALOR_TOTAL"],
                supermercado=row["NOME_SUPERMERCADO"],
                cnpj=row["CNPJ"],
                endereco=row["ENDERECO"],
                numero_nfce=row["NUMERO_NFCE"],
                serie=row["SERIE"],
                data_compra=row["DATA_HORA_COMPRA"]
            )
