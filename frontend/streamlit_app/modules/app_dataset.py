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
    st.subheader("👤 Upload de Usuários (Cpf e Nome)")
    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
    if file:
        df_preview = pd.read_csv(file)
        st.write("Prévia:")
        st.dataframe(df_preview.head())

        if st.button("Enviar"):
            file.seek(0)
            resp = requests.post(
                f"{API_URL}/usuarios/upload",
                files={"file": file}
            )
            mostrar_retorno(resp)


def upload_nfs():
    st.subheader("🧾 Upload de Notas Fiscais (descricao)")

    file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

    if file:
        df_preview = pd.read_csv(file)
        st.write("Prévia:")
        st.dataframe(df_preview.head())

        if st.button("Enviar para API"):
            file.seek(0)
            resp = requests.post(
                f"{API_URL}/nfs/upload",
                files={"file": file}
            )
            mostrar_retorno(resp)


def mostrar_retorno(resp):
    resultado = resp.json()

    # Verificar se é a nova estrutura de resposta ou antiga
    if "data" in resultado:
        # Nova estrutura padronizada
        data = resultado["data"]
        lines_valid = data.get("lines_valid", 0)
        lines_invalid = data.get("lines_invalid", 0)
        lines_received = data.get("lines_received", 0)
        invalid_records = data.get("invalid_records", [])
        total_stored = data.get("total_records_stored", "N/A")
        
        # Mostrar resumo do processamento
        if lines_valid > 0:
            st.success(f"✔ {lines_valid} linhas válidas inseridas!")
            st.info(f"📊 Total de registros no banco: {total_stored}")
        else:
            st.warning(f"⚠️ Nenhuma linha nova para inserir")
        
        # Sempre mostrar linhas rejeitadas se houver
        if lines_invalid > 0:
            # Contar quantas são duplicatas
            duplicates_count = sum(1 for rec in invalid_records if 'já existe' in str(rec.get('errors', [])).lower())
            invalid_count = lines_invalid - duplicates_count
            
            if duplicates_count > 0:
                st.info(f"ℹ️ {duplicates_count} de {lines_received} linhas já existem no banco (duplicadas)")
            
            if invalid_count > 0:
                st.error(f"❌ {invalid_count} de {lines_received} linhas foram rejeitadas (inválidas)")
            
            if invalid_records:
                with st.expander("Ver detalhes das linhas rejeitadas/duplicadas"):
                    st.dataframe(pd.DataFrame(invalid_records))
    else:
        # Estrutura antiga (fallback)
        validos = resultado.get('validos', 0)
        invalidos = resultado.get("invalidos", [])
        
        if validos > 0:
            st.success(f"✔ {validos} linhas válidas inseridas!")
        else:
            st.warning(f"⚠️ Nenhuma linha válida para inserir")
            
        if invalidos:
            st.error(f"❌ {len(invalidos)} linhas foram rejeitadas")
            with st.expander("Ver detalhes das linhas rejeitadas"):
                st.dataframe(pd.DataFrame(invalidos))

