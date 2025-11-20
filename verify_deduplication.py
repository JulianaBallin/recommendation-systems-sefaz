import pandas as pd
import os
import shutil
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf

DATASET_DIR = "dataset"
STANDARDIZED_PATH = os.path.join(DATASET_DIR, "standardized", "produtos_padronizados.csv")

def setup():
    # Clear standardized file
    if os.path.exists(STANDARDIZED_PATH):
        os.remove(STANDARDIZED_PATH)
    # Ensure directory exists
    os.makedirs(os.path.dirname(STANDARDIZED_PATH), exist_ok=True)

def test_deduplication():
    print("Testing Product Deduplication...")
    
    # Create a DataFrame with duplicate products
    data = [
        {"descricao": "coca cola 2l", "marca": "coca cola"},
        {"descricao": "coca cola 2l", "marca": "coca cola"}, # Same product
        {"descricao": "pepsi 2l", "marca": "pepsi"}          # Different product
    ]
    df = pd.DataFrame(data)
    
    print("Processing DataFrame...")
    processar_comparacao_tf_idf(df)
    
    # Check results
    if os.path.exists(STANDARDIZED_PATH):
        df_std = pd.read_csv(STANDARDIZED_PATH)
        print(f"Standardized rows: {len(df_std)}")
        print(df_std)
        
        # Verify IDs
        coca_rows = df_std[df_std["descricao"].str.contains("coca cola")]
        pepsi_rows = df_std[df_std["descricao"].str.contains("pepsi")]
        
        unique_coca_ids = coca_rows["id"].unique()
        unique_pepsi_ids = pepsi_rows["id"].unique()
        
        print(f"Unique Coke IDs: {len(unique_coca_ids)} (Expected: 1)")
        print(f"Unique Pepsi IDs: {len(unique_pepsi_ids)} (Expected: 1)")
        
        if len(unique_coca_ids) == 1 and len(unique_pepsi_ids) == 1 and unique_coca_ids[0] != unique_pepsi_ids[0]:
            print("✅ Deduplication Verified: Identical products share the same ID.")
        else:
            print("❌ Deduplication FAILED.")
            
    else:
        print("❌ Verification FAILED: File not found.")

if __name__ == "__main__":
    setup()
    test_deduplication()
