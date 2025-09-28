import streamlit as st
import os

def run():
    # === Título principal ===
    st.markdown('<h1 class="title">Sistema de Recomendação de Compras Locais</h1>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # === Contexto ===
    st.markdown(
        """
        <div class="paragraph">
        Este sistema foi desenvolvido para analisar notas fiscais eletrônicas (NF-e) da região de Manaus-AM 
        e gerar recomendações personalizadas de produtos com base em <b>Filtragem Colaborativa</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="paragraph">
        O sistema recomenda produtos baseado nas avaliações dos clientes nas dimensões de 
        <b>categoria, marca e descrição</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<h2 class="subtitle">Navegação</h2>', unsafe_allow_html=True)

    # === CSS para cartões ===
    st.markdown(
        """
        <style>
        .card {
            text-align: center;
            border: 1px solid #a69076;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            width: 160px;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: auto;
            color: #fff;
            background-color: #2e453b;
        }
        .card:hover {
            transform: scale(1.05);
            cursor: pointer;
            background-color: #3e721d;
        }
        .card-icon {
            font-size: 45px;
            margin-bottom: 15px;
        }
        .card-title {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
        }
        /* botão transparente em cima do cartão */
        div.stButton > button {
            position: absolute;
            width: 160px;
            height: 160px;
            opacity: 0;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # === Função auxiliar: renderiza cartão + botão invisível ===
    def nav_card(label, icon, key, page_name):
        col = st.container()
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(" ", key=key):  # botão invisível
                st.session_state["page"] = page_name
                st.rerun()

    # === Layout de cartões de navegação ===
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1: nav_card("Menu", "🏠", "nav_menu", "menu")
    with col2: nav_card("Produtos", "🛒", "nav_produtos", "produtos")
    with col3: nav_card("Clientes", "👨‍👨‍👦", "nav_clientes", "clientes")
    with col4: nav_card("Avaliação", "⭐", "nav_avaliacao", "avaliacao")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<h2 class="subtitle">Ferramentas Utilizadas</h2>', unsafe_allow_html=True)

    # === Cartões de ferramentas ===
    tools_col1, tools_col2, tools_col3, tools_col4 = st.columns(4, gap="large")

    with tools_col1:
        st.markdown(
            """
            <a href="https://github.com" target="_blank">
                <div class="card">
                    <img src="https://img.icons8.com/ios11/512/FFFFFF/github.png" width="50">
                    <div class="card-title">GitHub</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    with tools_col2:
        st.markdown(
            """
            <a href="https://streamlit.io" target="_blank">
                <div class="card">
                    <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="50">
                    <div class="card-title">Streamlit</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    with tools_col3:
        st.markdown(
            """
            <a href="https://www.python.org" target="_blank">
                <div class="card">
                    <img src="https://images.icon-icons.com/112/PNG/512/python_18894.png" width="80">
                    <div class="card-title">Python</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    with tools_col4:
        st.markdown(
            """
            <a href="https://en.wikipedia.org/wiki/Comma-separated_values" target="_blank">
                <div class="card">
                    <img src="https://cdn-icons-png.flaticon.com/256/8242/8242984.png" width="50">
                    <div class="card-title">CSV</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
