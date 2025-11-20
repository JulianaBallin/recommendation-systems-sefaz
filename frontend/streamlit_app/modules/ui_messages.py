"""
ui_messages.py
Módulo de mensagens padronizadas para o sistema AmazIA.

Responsável por exibir notificações visuais no Streamlit com estilo e ícones
consistentes entre as páginas da aplicação.
"""

import streamlit as st

# =========================================================
# Mensagens padronizadas
# =========================================================

def show_success(message: str):
    """
    Exibe uma mensagem de sucesso (verde).

    Parâmetros:
        message (str): texto da mensagem a ser exibida.
    """
    st.success(message, icon="✅")


def show_error(message: str):
    """
    Exibe uma mensagem de erro (vermelha).

    Parâmetros:
        message (str): texto da mensagem a ser exibida.
    """
    st.error(message, icon="🚨")


def show_warning(message: str):
    """
    Exibe uma mensagem de aviso (amarela).

    Parâmetros:
        message (str): texto da mensagem a ser exibida.
    """
    st.warning(message, icon="⚠️")


def show_info(message: str):
    """
    Exibe uma mensagem informativa (cinza/azulada).

    Parâmetros:
        message (str): texto da mensagem a ser exibida.
    """
    st.info(message, icon="ℹ️")
