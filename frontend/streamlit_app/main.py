# frontend/streamlit_app/main.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from modules import app_home
from modules import app_products, app_clients, app_ratings

st.set_page_config(
    page_title="Local Purchases Recommender",
    page_icon="📊",
    layout="wide"
)

# Inicializa página se não existir
if "page" not in st.session_state:
    st.session_state["page"] = "menu"

pages = {
    "menu": app_home,
    "produtos": app_products,
    "clientes": app_clients,
    "avaliacao": app_ratings,
}

# Sidebar para navegação (opcional, pode remover depois se quiser só os cartões)
choice = st.sidebar.radio("Navegação:", ["Menu", "Produtos", "Clientes", "Avaliação"])

if choice == "Menu":
    st.session_state["page"] = "menu"
elif choice == "Produtos":
    st.session_state["page"] = "produtos"
elif choice == "Clientes":
    st.session_state["page"] = "clientes"
elif choice == "Avaliação":
    st.session_state["page"] = "avaliacao"

# Carrega a página atual
current_page = st.session_state["page"]
pages[current_page].run()
