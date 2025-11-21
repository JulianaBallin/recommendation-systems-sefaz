import pandas as pd

df = pd.read_csv("dataset/standardized/produtos_padronizados.csv")
dups = df[df["descricao"].duplicated(keep=False)]
print(dups)
