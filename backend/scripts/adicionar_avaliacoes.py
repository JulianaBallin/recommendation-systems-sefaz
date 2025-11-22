#!/usr/bin/env python3
import pandas as pd
import random
import os

USERS_FILE = "dataset/processado/usuarios.csv"
PRODUTOS_FILE = "dataset/standardized/produtos_padronizados.csv"
AVALIACOES_FILE = "dataset/ratings/avaliacoes.csv"

def adicionar_avaliacoes(qtd=40):
    if not os.path.exists(USERS_FILE) or not os.path.exists(PRODUTOS_FILE):
        print("❌ Necessário ter usuários e produtos padronizados antes.")
        return

    df_users = pd.read_csv(USERS_FILE)
    df_prod = pd.read_csv(PRODUTOS_FILE)

    if os.path.exists(AVALIACOES_FILE):
        df = pd.read_csv(AVALIACOES_FILE)
    else:
        df = pd.DataFrame(columns=[
            "nome_usuario",
            "cpf",
            "descricao_produto",
            "avaliacao_descricao",
            "marca_produto",
            "avaliacao_marca",
            "product_id"
        ])

    novos = []

    for _ in range(qtd):
        user = df_users.sample(1).iloc[0]
        prod = df_prod.sample(1).iloc[0]

        novos.append({
            "nome_usuario": user["nome"],
            "cpf": user["cpf"],
            "descricao_produto": prod["descricao"],
            "avaliacao_descricao": random.randint(1, 5),
            "marca_produto": prod["marca"],
            "avaliacao_marca": random.randint(1, 5),
            "product_id": prod["id"]
        })

    df_new = pd.DataFrame(novos)
    df = pd.concat([df, df_new], ignore_index=True)

    os.makedirs(os.path.dirname(AVALIACOES_FILE), exist_ok=True)
    df.to_csv(AVALIACOES_FILE, index=False)

    print(f"✔ {qtd} novas avaliações COMPLETAS adicionadas.")

if __name__ == "__main__":
    adicionar_avaliacoes(50)
