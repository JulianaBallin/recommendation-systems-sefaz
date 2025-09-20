import streamlit as st
import requests
import pandas as pd
import os
import sys

# Adiciona a pasta raiz do projeto ao sys.path para resolver imports do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from frontend.streamlit_app.modules.ui_messages import show_error, show_success

# URL da API do backend (ajuste se necessário)
API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide", page_icon="👤", page_title="Recomendação por Cliente")

st.title("👤 Recomendação por Similaridade de Cliente")
st.markdown("""
Esta página demonstra a **Filtragem Colaborativa Baseada em Usuário**. 
Selecione um cliente (CPF) e o sistema irá:
1. Encontrar clientes com histórico de compras similar (usando Correlação de Pearson).
2. Recomendar produtos que esses clientes similares compraram, mas que o cliente selecionado ainda não comprou.
""")

# --- Carregar CPFs para seleção ---
@st.cache_data
def load_clients_cpfs():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    clients_path = os.path.join(BASE_DIR, "data", "raw", "clients.csv")
    if os.path.exists(clients_path):
        df_clients = pd.read_csv(clients_path)
        return df_clients['CPF'].unique()
    return []

cpfs = load_clients_cpfs()

if not cpfs.any():
    show_error("Não foi possível carregar a lista de clientes. Verifique o arquivo `data/raw/clients.csv`.")
else:
    # --- Formulário de Seleção ---
    selected_cpf = st.selectbox(
        "Selecione o CPF de um cliente para gerar recomendações:",
        options=cpfs,
        index=0,
        placeholder="Selecione um CPF..."
    )

    if st.button("Gerar Recomendações", use_container_width=True):
        if selected_cpf:
            with st.spinner(f"Buscando recomendações para o CPF: {selected_cpf}..."):
                try:
                    response = requests.get(f"{API_URL}/recommend/products/{selected_cpf}")
                    response.raise_for_status()  # Lança um erro para códigos de status HTTP 4xx/5xx
                    
                    recommendations = response.json()
                    st.success(f"✨ Top {len(recommendations)} recomendações de produtos encontradas!")
                    st.dataframe(pd.DataFrame(recommendations), use_container_width=True)

                except requests.exceptions.HTTPError as e:
                    error_detail = "Erro desconhecido do servidor."
                    try:
                        error_detail = e.response.json().get('detail', e.response.text)
                    except requests.exceptions.JSONDecodeError:
                        error_detail = e.response.text
                    show_error(f"Erro ao buscar recomendações: {e.response.status_code} - {error_detail}")
                except requests.exceptions.RequestException as e:
                    show_error(f"Não foi possível conectar à API em {API_URL}. Verifique se o backend está em execução. Detalhe: {e}")