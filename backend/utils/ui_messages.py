# backend/utils/ui_messages.py
import streamlit as st
import pandas as pd

def show_success(msg: str):
    """Mostra mensagem de sucesso estilizada via CSS global."""
    st.markdown(
        f'<div class="success-box">✅ {msg}</div>',
        unsafe_allow_html=True
    )

def show_error(msg: str):
    """Mostra mensagem de erro estilizada via CSS global."""
    st.markdown(
        f'<div class="error-box">❌ {msg}</div>',
        unsafe_allow_html=True
    )

def show_info(msg: str):
    """Mostra mensagem de informação estilizada via CSS global."""
    st.markdown(
        f'<div class="info-box">ℹ️ {msg}</div>',
        unsafe_allow_html=True
    )

def show_table(df: pd.DataFrame):
    """
    Exibe tabelas no padrão visual do Streamlit,
    com scroll habilitado automaticamente.
    - Se <= 10 registros: mostra todos
    - Se > 10 registros: mostra 5 primeiros e 5 últimos
    """
    if df is None or df.empty:
        st.info("Nenhum dado disponível.")
        return

    # regra de truncar
    if len(df) <= 10:
        data_to_show = df
    else:
        data_to_show = pd.concat([df.head(5), df.tail(5)])

    # usa st.dataframe (mantém estilo nativo e scroll)
    st.dataframe(data_to_show)


def styled_button(label: str, key: str = None) -> bool:
    """
    Renderiza um botão estilizado manualmente com HTML/CSS inline.
    Retorna True se o botão for clicado.
    """
    button_id = key or label.replace(" ", "_")

    clicked = st.markdown(
        f"""
        <style>
        div.stButton > button#{button_id} {{
            background-color: #2e453b;
            color: #ffffff;
            font-weight: 600;
            font-size: 16px;
            border-radius: 8px;
            padding: 10px 18px;
            margin: 6px auto;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            display: block;
            text-align: center;
        }}
        div.stButton > button#{button_id}:hover {{
            background-color: #5c913b;
            color: #ffffff;
            transform: scale(1.02);
        }}
        </style>
        <button id="{button_id}">{label}</button>
        """,
        unsafe_allow_html=True,
    )

    # Detecta clique via JS hack → Streamlit não expõe clique de botão HTML puro
    return st.button(label, key=f"btn_{button_id}")

