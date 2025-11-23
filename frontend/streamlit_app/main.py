"""
main.py – Frontend Streamlit do sistema AmazIA.
"""

import sys, os
import streamlit as st
import base64

# === Ajuste de PATH para importar os módulos ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from modules import app_home, app_dataset, app_ratings, app_recomendation


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # CSS adicional para melhorias visuais
    st.markdown("""
    <style>
        /* Barra lateral com verde escuro - CORRIGIDO */
        section[data-testid="stSidebar"] {
            background-color: #1a472a !important;
        }
        
        /* Sidebar content - CORRIGIDO */
        .css-1d391kg, .css-1lcbmhc, .stSidebar {
            background-color: #1a472a !important;
        }
        
        /* Texto da sidebar - melhor contraste */
        .stSidebar p, .stSidebar label, .stSidebar div, .stSidebar span {
            color: #ffffff !important;
        }
        
        /* Logo na sidebar */
        .sidebar-logo {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #2d5a3d;
            margin-bottom: 20px;
        }
        
        .sidebar-logo img {
            max-width: 80%;
            height: auto;
            border-radius: 10px;
        }
        
        /* Label "Navegação" com melhor contraste */
        .stSelectbox label {
            color: #ffffff !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        
        /* Seleção de páginas - verde escuro */
        div[data-baseweb="select"] > div {
            background-color: #2d5a3d !important;
            border: 2px solid #3d6b4f !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }
        
        /* Botões de upload - verde escuro */
        .stFileUploader section {
            background-color: #1a472a !important;
            border: 2px solid #2d5a3d !important;
            border-radius: 8px !important;
        }
        
        .stFileUploader section div {
            color: white !important;
        }
        
        .stFileUploader section button {
            background-color: #2d5a3d !important;
            color: white !important;
        }
        
        /* Cards para produtos recomendados */
        .product-card {
            background-color: #f8f9fa;
            border: 2px solid #1a472a;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease-in-out;
        }
        
        .product-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Mensagens com melhor contraste */
        .stSuccess {
            background-color: #d4edda !important;
            border: 1px solid #c3e6cb !important;
            color: #155724 !important;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
        }
        
        .stInfo {
            background-color: #d1ecf1 !important;
            border: 1px solid #bee5eb !important;
            color: #0c5460 !important;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
        }
        
        .stWarning {
            background-color: #fff3cd !important;
            border: 1px solid #ffeaa7 !important;
            color: #856404 !important;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
        }
        
        .stError {
            background-color: #f8d7da !important;
            border: 1px solid #f5c6cb !important;
            color: #721c24 !important;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
        }
        
        /* Botões padrão do Streamlit - verde escuro */
        .stButton button {
            background-color: #1a472a !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            font-weight: bold !important;
        }
        
        .stButton button:hover {
            background-color: #2d5a3d !important;
            color: white !important;
        }
        
        /* Campos de entrada */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            border: 2px solid #1a472a !important;
            border-radius: 6px !important;
        }
        
    </style>
    """, unsafe_allow_html=True)


def get_image_base64(image_path):
    """Converte imagem para base64 para exibição no HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""


def main():
    # Configurações gerais
    st.set_page_config(
        page_title="AmazIA - Sistema de Recomendação",
        page_icon="frontend/assets/logo_amazia.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()

    # Sidebar com logo e navegação
    with st.sidebar:
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_verde.png")
        if os.path.exists(logo_path):
            st.markdown(
                f'<div class="sidebar-logo">'
                f'<img src="data:image/png;base64,{get_image_base64(logo_path)}" alt="AmazIA Logo">'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="sidebar-logo">'
                '<h2 style="color: #ffffff; margin: 0; font-weight: bold;">🌿 AmazIA</h2>'
                '<p style="color: #a8df8e; margin: 0; font-size: 14px;">Sistema de Recomendação</p>'
                '</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Navegação
        pagina = st.selectbox(
            "📌 Navegação",
            [
                "🏠 Home", 
                "📂 Upload de Dados", 
                "⭐ Avaliação",
                "📊 Recomendação"
            ],
            key="nav_selectbox"
        )

    # Páginas
    if pagina == "🏠 Home":
        app_home.run()

    elif pagina == "📂 Upload de Dados":
        app_dataset.run()

    elif pagina == "⭐ Avaliação":
        app_ratings.run()

    elif pagina == "📊 Recomendação":
        app_recomendation.run()


if __name__ == "__main__":
    main()