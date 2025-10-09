"""
main.py
Ponto de entrada do frontend do sistema AmazIA (Streamlit).

Versão simplificada para exibir apenas a página inicial (Home).
Utiliza o CSS global e o módulo app_home para renderização da interface principal.
"""

import sys, os
import streamlit as st

# === Configuração de caminho para importar backend e módulos ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from modules import app_home  # apenas a Home ativa


# === Função para carregar CSS global ===
def load_css():
    """Carrega o arquivo CSS principal do sistema."""
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Arquivo style.css não encontrado. Verifique o caminho.")


# === Configuração inicial do app ===
st.set_page_config(
    page_title="AmazIA — Sistema de Recomendação Local",
    page_icon="frontend/assets/logo_verde.png",
    layout="wide"
)

# === Carregar CSS global ===
load_css()

# === Renderizar Home diretamente ===
app_home.run()
