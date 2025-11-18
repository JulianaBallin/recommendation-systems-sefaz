import streamlit as st

def show_success(message: str):
    """
    Exibe uma mensagem de sucesso padronizada no Streamlit.
    """
    st.success(message, icon="✅")

def show_error(message: str):
    """
    Exibe uma mensagem de erro padronizada no Streamlit.
    """
    st.error(message, icon="🚨")