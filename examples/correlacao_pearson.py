from math import sqrt
import streamlit as st
import pandas as pd

def pearson_correlation(rating1: dict, rating2: dict) -> float:

    sum_x= 0.00 # soma das notas do primeiro avaliador
    sum_y = 0.00 # somas das notas do segundo avaliador
    sum_xy = 0.00 # soma dos produtos x e y (x*y) 
    sum_x2 = 0.00 # soma das notas ao quadrado primeiro avaliador
    sum_y2 = 0.00 # soma das notas ao quadrado segundo avaliador
    n = 0.00 # quantidade de itens avaliados (em comum)

    for key in rating1:
        if key in rating2:
            n += 1
            x = rating1[key]
            y = rating2[key]
            sum_xy += x * y
            sum_x += x
            sum_y += y
            sum_x2 += x ** 2
            sum_y2 += y ** 2

    if n == 0:
        return 0.00
    
    denominador = sqrt(sum_x2 - (sum_x ** 2)/n) * sqrt(sum_y2 - (sum_y ** 2)/n)

    if denominador ==0:
        return 0.00
    
    return (sum_xy - (sum_x * sum_y) / n) / denominador

def read_file(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    dataset = {}
    for _, row in df.iterrows():
        user = row["Username"]
        item = row["Game"]
        rating = row["Rating"]

        if user not in dataset:
            dataset[user] = {}
        dataset[user][item] = rating
    return dataset


def correlacao_app():
    st.title("Sistema de Correlação de Pearson")

    dataset = read_file("./dataset.csv")

    username1 = st.text_input("Digite o nome de usuário 1:")
    username2 = st.text_input("Digite o nome de usuário 2:")

    if st.button("Calcular"):
        if username1 in dataset and username2 in dataset:
            correlacao = pearson_correlation(dataset[username1], dataset[username2])
            st.write(f"Correlação para {username1} e {username2}:")
            st.write(f"Pontuação: {correlacao:.4f}")
        else:
            st.error("Nome de usuário não encontrado. Por favor, insira nomes válidos.")


def main():
    correlacao_app()


if __name__ == "__main__":
    main()