import pandas as pd
import os

def deduplicate_products():
    """
    Lê o arquivo products_clean.csv, remove produtos com descrições duplicadas, mantendo
    as colunas PRODUCT_ID, DESCRICAO e CATEGORIA, e salva o resultado em um novo
    arquivo 'products_unique.csv'.
    """
    print("Iniciando a remoção de duplicatas do dataset de produtos...")

    # --- 1. Definir caminhos ---
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
    products_clean_path = os.path.join(PROCESSED_DATA_PATH, 'products_clean.csv')
    output_path = os.path.join(PROCESSED_DATA_PATH, 'products_unique.csv')

    # --- 2. Carregar o dataset ---
    try:
        products_df = pd.read_csv(products_clean_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{os.path.basename(products_clean_path)}' não encontrado em '{PROCESSED_DATA_PATH}'.")
        print("Execute o script 'data_cleaner.py' primeiro.")
        return

    # --- 3. Processar os dados ---
    print(f"Produtos antes da remoção de duplicatas: {len(products_df)}")
    
    # Seleciona apenas as colunas de interesse
    unique_products_df = products_df[['PRODUCT_ID', 'DESCRICAO', 'CATEGORIA']].copy()
    
    # Remove duplicatas com base na DESCRICAO, mantendo a primeira ocorrência
    unique_products_df.drop_duplicates(subset=['DESCRICAO'], keep='first', inplace=True)
    
    print(f"Produtos após a remoção de duplicatas: {len(unique_products_df)}")

    # --- 4. Salvar o resultado ---
    unique_products_df.to_csv(output_path, index=False)
    print(f"Arquivo '{os.path.basename(output_path)}' criado com sucesso com produtos únicos.")

if __name__ == "__main__":
    deduplicate_products()
