#!/usr/bin/env python3
import pandas as pd
import random
import string
import os
from backend.pipeline.rodar_pipeline import executar_pipeline_completa

USERS_FILE = "dataset/processado/usuarios.csv"

def gerar_cpf_unico(existing_cpfs):
    while True:
        cpf = "".join([str(random.randint(0, 9)) for _ in range(11)])
        if cpf not in existing_cpfs:
            return cpf

def gerar_nome_falso():
    first = ["Ana", "João", "Carlos", "Marcos", "Julia", "Beatriz", "Pedro", "Luana", "Gabriel", "Leticia"]
    last = ["Silva", "Souza", "Moraes", "Ferreira", "Oliveira", "Santos", "Mendes", "Costa"]
    return random.choice(first) + " " + random.choice(last)

def adicionar_usuarios(qtd=20):
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
    else:
        df = pd.DataFrame(columns=["cpf", "nome"])

    existing_cpfs = set(df["cpf"].astype(str))

    novos = []
    for _ in range(qtd):
        cpf = gerar_cpf_unico(existing_cpfs)
        nome = gerar_nome_falso()
        novos.append({"cpf": cpf, "nome": nome})
        existing_cpfs.add(cpf)

    df_novo = pd.DataFrame(novos)
    df = pd.concat([df, df_novo], ignore_index=True)

    df.to_csv(USERS_FILE, index=False)
    print(f"✔ {qtd} novos usuários adicionados a {USERS_FILE}")

    print("✔ Executando pipeline após atualização...")
    executar_pipeline_completa()

if __name__ == "__main__":
    adicionar_usuarios(30)
