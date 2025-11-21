#!/usr/bin/env python3
import pandas as pd
import random
import os

USERS_FILE = "dataset/processado/usuarios.csv"
PRODUTOS_FILE = "dataset/standardized/produtos_padronizados.csv"
AVALIACOES_FILE = "dataset/ratings/avaliacoes.csv"

NOMES_FAKE = [
    "Ana Oliveira", "Lucas Souza", "Maria Santos", "Rafael Barros",
    "João Almeida", "Juliana Freitas", "Paula Figueiredo", "Pedro Carvalho",
    "Fernanda Costa", "Beatriz Lima"
]

def adicionar_avaliacoes(qtd=30):
    if not os.path.exists(USERS_FILE) or not os.path.exists(PRODUTOS_FILE):
        print("❌ Usuários e produtos padronizados são necessários antes.")
        return

    df_users = pd.read_csv(USERS_FILE)
    df_prod = pd.read_csv(PRODUTOS_FILE)

    # criar arquivo se não existir
    if os.path.exists(AVALIACOES_FILE):
        df = pd.read_csv(AVALIACOES_FILE)
    else:
        df = pd.DataFrame(columns=[
            "nome_usuario", "cpf", "descricao_produto", 
            "avaliacao_descricao", "marca_produto",
            "avaliacao_marca", "product_id", "gostou"
        ])

    novas_linhas = []

    for _ in range(qtd):
        user = df_users.sample(1).iloc[0]
        prod = df_prod.sample(1).iloc[0]

        nome_usuario = random.choice(NOMES_FAKE)
        cpf = str(user["cpf"])
        descricao_produto = prod["descricao"]
        marca = prod["marca"]

        aval_descr = random.randint(1, 5)
        aval_marca = random.randint(1, 5)

        gostou = 1 if aval_descr >= 3 else 0

        novas_linhas.append({
            "nome_usuario": nome_usuario,
            "cpf": cpf,
            "descricao_produto": descricao_produto,
            "avaliacao_descricao": aval_descr,
            "marca_produto": marca,
            "avaliacao_marca": aval_marca,
            "product_id": prod["id"],
            "gostou": gostou
        })

    df_new = pd.DataFrame(novas_linhas)
    df = pd.concat([df, df_new], ignore_index=True)

    df.to_csv(AVALIACOES_FILE, index=False)
    print(f"✔ {qtd} novas avaliações adicionadas!")
    print(f"📄 Arquivo atualizado em: {AVALIACOES_FILE}")

if __name__ == "__main__":
    adicionar_avaliacoes(40)
