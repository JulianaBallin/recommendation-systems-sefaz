#!/usr/bin/env python3
import pandas as pd
import random
import os
from backend.pipeline.rodar_pipeline import executar_pipeline_completa

NFS_FILE = "dataset/raw/nfs.csv"

produtos_exemplo = [
    "SABONETE DOVE 90G",
    "CAFÉ PILÃO 500G",
    "NESCAU ACHOCOLATADO",
    "ARROZ TIO JOAO 5KG",
    "MAC RENATA ESPAGUETE 500G",
    "CREME DENTAL COLGATE",
    "FEIJ CARIOCA TP1KG",
    "LEITE CONDENSADO MOCOCA",
    "BATATA PALHA SCRUSH",
    "SALCHICHA SEARA HOT DOG",
    "QUEIJO MUSSARELA FATIADO",
    "LEITE INTEGRAL TIROL",
]

def adicionar_nfs(qtd=30):
    if os.path.exists(NFS_FILE):
        df = pd.read_csv(NFS_FILE)
    else:
        df = pd.DataFrame(columns=["descricao"])

    novos = []
    for _ in range(qtd):
        novos.append({"descricao": random.choice(produtos_exemplo)})

    df_novo = pd.DataFrame(novos)
    df = pd.concat([df, df_novo], ignore_index=True)

    df.to_csv(NFS_FILE, index=False)
    print(f"✔ {qtd} novas linhas adicionadas a NFs")

    print("✔ Executando pipeline após atualização NFs...")
    executar_pipeline_completa()

if __name__ == "__main__":
    adicionar_nfs(40)
