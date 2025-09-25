import pandas as pd

path = "data/derived/products.csv"
df = pd.read_csv(path)

# Força maiúsculo e remove duplicadas
df.columns = [c.strip().upper() for c in df.columns]
df = df.loc[:, ~df.columns.duplicated()]

# Mantém só as colunas corretas
cols = ["ID", "CATEGORIA", "MARCA", "DESCRICAO"]
df = df[[c for c in df.columns if c in cols]]

# Salva limpo
df.to_csv(path, index=False, columns=cols)

print("✅ Arquivo corrigido:", path)
