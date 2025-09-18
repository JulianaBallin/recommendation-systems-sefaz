from backend.utils.preprocessing import update_products
import pandas as pd

if __name__ == "__main__":
    raw_file = "data/raw/products.csv"
    clean_file = "data/processed/products_clean.csv"

    # Debug: mostrar cabeçalho e primeiras linhas
    df_debug = pd.read_csv(raw_file, nrows=5)
    print(df_debug.columns.tolist())
    print("\n=== DEBUG SAMPLE ===")
    print(df_debug.head())
    print("====================\n")

    update_products(raw_file, clean_file)
