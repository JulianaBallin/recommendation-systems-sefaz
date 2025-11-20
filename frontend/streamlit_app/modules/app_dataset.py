import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

def run():
    st.title("📂 Upload de Dados – AmazIA")

    opcao = st.selectbox(
        "Escolha o tipo de upload:",
        ["Usuários (CLIENTES)", "Notas Fiscais (NFS)"]
    )

    if opcao.startswith("Usuários"):
        return upload_usuarios()

    if opcao.startswith("Notas Fiscais"):
        return upload_nfs()


def upload_usuarios():
    st.subheader("👤 Upload de Usuários (cpf, nome, datanasc)")
    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
    if file:
        df_preview = pd.read_csv(file)
        st.write("Prévia:")
        st.dataframe(df_preview.head())

        if st.button("Enviar"):
            resp = requests.post(
                f"{API_URL}/usuarios/upload",
                files={"file": file}
            )
            mostrar_retorno(resp)


def upload_nfs():
    st.subheader("🧾 Upload de Notas Fiscais (DESCRICAO, SUPERMERCADO)")

    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

    if file:
        df_preview = pd.read_csv(file)
        st.write("Prévia:")
        st.dataframe(df_preview.head())

        if st.button("Enviar para API"):
            resp = requests.post(
                f"{API_URL}/nfs/upload",
                files={"file": file}
            )
            mostrar_retorno(resp)


def mostrar_retorno(resp):
    resultado = resp.json()

    st.success(f"✔ {resultado['validos']} linhas válidas inseridas!")
    if resultado["invalidos"]:
        st.error("⚠ Linhas rejeitadas:")
        st.dataframe(pd.DataFrame(resultado["invalidos"]))
