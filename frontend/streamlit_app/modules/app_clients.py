import sys, os
import streamlit as st
import pandas as pd
import datetime
from backend.utils.client_loader import clean_clients

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

RAW_PATH = os.path.join(BASE_DIR,"data/raw/clients.csv")

def run():
    st.title("👤 Clientes")
    st.write("Página de Clientes em desenvolvimento...")

def save_client(data: dict):
    df_new = pd.DataFrame([data])

    try:
        df_existing = pd.read_csv(RAW_PATH)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_all = df_new

    df_clean = clean_clients(df_all)
    df_clean.to_csv(RAW_PATH, index=False)

    return df_clean

def render_clients_form():
    st.header("Cadastro de Cliente 🧑")

    nome = st.text_input(
        "Nome*",
        placeholder="João da Silva"
    )
    cpf = st.text_input(
        "CPF * (formato: 000.000.000-00)",
        placeholder="000.000.000-00"
    )

    # limite de datas: 01/01/1950 até hoje
    min_date = datetime.date(1950, 1, 1)
    max_date = datetime.date.today()
    nascimento = st.date_input(
        "Data de Nascimento * (DD/MM/AAAA)",
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(2000, 1, 1),
        format="DD/MM/YYYY"
    )


    genero_label = st.selectbox(
        "Gênero *",
        ["Feminino", "Masculino", "Outros"]
    )

    # converte label para inicial
    genero_map = {"Feminino": "F", "Masculino": "M", "Outros": "O"}
    genero = genero_map[genero_label]

    cep = st.text_input(
        "CEP * (formato: 00000-000)",
        placeholder="00000-000"
    )

    if st.button("Salvar Cliente"):
        if not nome or not cpf or not nascimento or not genero or not cep:
            st.error("⚠️ Todos os campos marcados com * são obrigatórios.")
            return

        data = {
            "NAME": nome,
            "CPF": cpf,
            "BIRTHDATE": nascimento.strftime("%d/%m/%Y"),  # formato DD/MM/AAAA
            "GENDER": genero,
            "CEP": cep
        }

        try:
            df_clean = save_client(data)
            st.success("✅ Cliente salvo com sucesso!")
            st.dataframe(df_clean.tail())
        except ValueError as e:
            st.error(f"Erro de validação: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
