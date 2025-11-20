"""
main.py – Frontend Streamlit do sistema AmazIA.
"""

import sys, os
import streamlit as st

# === Ajuste de PATH para importar os módulos ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from modules import app_home, app_dataset


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Configurações gerais
st.set_page_config(
    page_title="AmazIA - Sistema de Recomendação",
    page_icon="frontend/assets/logo_verde.png",
    layout="wide"
)

load_css()

# Sidebar com páginas
pagina = st.sidebar.selectbox(
    "📌 Navegação",
    ["🏠 Home", "📂 Upload de Dados"]
)

if pagina == "🏠 Home":
    app_home.run()

elif pagina == "📂 Upload de Dados":
    app_dataset.run()
