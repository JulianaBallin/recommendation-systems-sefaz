import streamlit as st

def show_success(msg: str):
    st.markdown(
        f"""
        <div style="
            background-color:#28a745;  /* verde forte */
            color:#ffffff;             /* texto branco */
            padding:14px;
            border-radius:6px;
            font-size:16px;
            font-weight:600;">
            ✅ {msg}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_error(msg: str):
    st.markdown(
        f"""
        <div style="
            background-color:#dc3545;  /* vermelho forte */
            color:#ffffff;             /* texto branco */
            padding:14px;
            border-radius:6px;
            font-size:16px;
            font-weight:600;">
            ❌ {msg}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_info(msg: str):
    st.markdown(
        f"""
        <div style="
            background-color:#007bff;  /* azul forte */
            color:#ffffff;             /* texto branco */
            padding:14px;
            border-radius:6px;
            font-size:16px;
            font-weight:600;">
            ℹ️ {msg}
        </div>
        """,
        unsafe_allow_html=True
    )
