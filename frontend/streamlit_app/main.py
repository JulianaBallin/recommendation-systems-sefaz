# frontend/streamlit_app/main.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from modules import app_home, app_products, app_clients, app_ratings, app_recomendation, app_accuracy

# === Função para carregar CSS global ===
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Arquivo style.css não encontrado. Verifique o caminho.")

# === Configuração inicial do app ===
st.set_page_config(
    page_title="Sistema de Recomendação de Compras Locais",
    page_icon="📊",
    layout="wide"
)

# 🔹 Carregar CSS global
load_css()

# Inicializa página se não existir
if "page" not in st.session_state:
    st.session_state["page"] = "menu"

# Dicionário de páginas
pages = {
    "menu": app_home,
    "produtos": app_products,
    "clientes": app_clients,
    "avaliação": app_ratings,
    "recomendação": app_recomendation,
    "acurácia": app_accuracy,
}

# Sidebar estilizada
st.sidebar.markdown(
    """
    <div style="background-color:#2e453b; padding:15px; border-radius:8px; text-align:center;">
        <h2 style="color:white; font-size:20px; margin:0;"> Navegação </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

choice = st.sidebar.radio(
    "",
    ["Menu", "Produtos", "Clientes", "Avaliação", "Recomendação", "Acurácia"],
    label_visibility="collapsed"  # esconde label padrão feio
)

# Atualiza estado da página
st.session_state["page"] = choice.lower() if choice != "Menu" else "menu"

# Carrega a página atual
current_page = st.session_state["page"]
pages[current_page].run()
