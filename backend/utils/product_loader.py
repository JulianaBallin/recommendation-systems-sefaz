import pandas as pd
import os

# --- Constantes de Caminho ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "raw", "products.csv")

EXPECTED_COLUMNS = [
    "CODIGO", "DESCRICAO", "QTD", "UN", "VALOR_UNITARIO", "VALOR_TOTAL",
    "NOME_SUPERMERCADO", "CNPJ", "ENDERECO", "NUMERO_NFCE", "SERIE", "DATA_HORA_COMPRA"
]

def _validate_product_data(**kwargs):
    """Valida se todos os campos obrigatórios foram preenchidos."""
    for key, value in kwargs.items():
        if not value:
            raise ValueError(f"O campo '{key}' é obrigatório e não pode estar vazio.")

def add_product(
    codigo, descricao, qtd, un, valor_unitario, valor_total,
    supermercado, cnpj, endereco, numero_nfce, serie, data_compra
):
    """
    Adiciona uma única linha de produto ao arquivo `products.csv`.
    Cria o arquivo com cabeçalho se ele não existir.
    """
    product_data = {
        "CODIGO": [codigo], "DESCRICAO": [descricao], "QTD": [qtd], "UN": [un],
        "VALOR_UNITARIO": [valor_unitario], "VALOR_TOTAL": [valor_total],
        "NOME_SUPERMERCADO": [supermercado], "CNPJ": [cnpj], "ENDERECO": [endereco],
        "NUMERO_NFCE": [numero_nfce], "SERIE": [serie], "DATA_HORA_COMPRA": [data_compra]
    }
    _validate_product_data(**{k: v[0] for k, v in product_data.items()})

    df_new_product = pd.DataFrame(product_data)

    # Adiciona ao CSV, criando o arquivo e o cabeçalho se necessário
    df_new_product.to_csv(
        RAW_PRODUCTS_PATH,
        mode='a',
        header=not os.path.exists(RAW_PRODUCTS_PATH),
        index=False
    )

def add_products_from_csv(csv_path: str):
    """
    Lê um arquivo CSV e adiciona seu conteúdo ao `products.csv`.
    Garante que as colunas estejam na ordem correta.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo CSV não encontrado em: {csv_path}")

    df_from_csv = pd.read_csv(csv_path)

    # Valida se todas as colunas esperadas estão presentes
    if not set(EXPECTED_COLUMNS).issubset(df_from_csv.columns):
        missing_cols = set(EXPECTED_COLUMNS) - set(df_from_csv.columns)
        raise ValueError(f"Colunas faltando no arquivo CSV: {', '.join(missing_cols)}")

    # Reordena para garantir a consistência e adiciona ao arquivo principal
    df_to_append = df_from_csv[EXPECTED_COLUMNS]
    df_to_append.to_csv(RAW_PRODUCTS_PATH, mode='a', header=not os.path.exists(RAW_PRODUCTS_PATH), index=False)