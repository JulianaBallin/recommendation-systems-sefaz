import streamlit as st
import pandas as pd
import os

from frontend.streamlit_app.modules.ui_messages import show_error

st.set_page_config(layout="wide", page_icon="👥", page_title="Gerenciar Clientes")

st.title("👥 Gestão de Clientes")
st.markdown("Visualize a lista de clientes cadastrados no sistema.")

@st.cache_data
def load_clients():
    """Carrega os clientes do dataset raw."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    clients_path = os.path.join(BASE_DIR, "data", "raw", "clients.csv")
    if os.path.exists(clients_path):
        return pd.read_csv(clients_path)
    return pd.DataFrame()

clients_df = load_clients()

if not clients_df.empty:
    st.dataframe(clients_df, use_container_width=True)
else:
    show_error("Arquivo `clients.csv` não encontrado em `data/raw/`. Não foi possível carregar a lista de clientes.")