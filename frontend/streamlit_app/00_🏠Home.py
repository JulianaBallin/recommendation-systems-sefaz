import streamlit as st
import sys, os

# Ajuste do path para enxergar backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# depois você pode criar pages.app_clients, pages.app_reviews, pages.app_analises
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

# 🎨 CSS GLOBAL
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
    }
    input, textarea {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border-radius: 8px !important;
        border: 1px solid #ccd6dd !important;
    }
    label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    .stButton>button {
        background-color: #a3c4f3;
        color: #000000;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #779ecb;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
        font-weight: 700;
    }
    /* Caixa de info customizada */
    .custom-info {
        background-color: #ecf0f1;
        color: #2c3e50;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #d0d7de;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- PÁGINA PRINCIPAL (HOME) ---
st.title("🏠 Bem-vindo ao Sistema de Recomendação")

st.markdown(
    "<div class='custom-info'>Use o menu de navegação à esquerda para explorar as funcionalidades do sistema.</div>",
    unsafe_allow_html=True
)