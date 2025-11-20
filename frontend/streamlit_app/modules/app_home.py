"""
app_home.py — Página inicial com margens fixas
"""

import os
from pathlib import Path
import streamlit as st
import base64


def image_to_base64(image_path):
    """Converte imagem para base64 para garantir carregamento"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Erro ao converter imagem {image_path}: {e}")
        return None


def run():
    """Renderiza a página inicial com margens fixas"""

    # === Caminhos absolutos dos assets ===
    assets_dir = Path(__file__).resolve().parents[2] / "assets"
    banner_path = assets_dir / "banner_titulo.png"
    foto_juliana = assets_dir / "foto_juliana.png"
    foto_lucas = assets_dir / "foto_lucas.jpg"

    # === Banner Centralizado ===
    if banner_path.exists():
        try:
            banner_base64 = image_to_base64(banner_path)
            if banner_base64:
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:center; align-items:center; margin-top:-10px; margin-bottom:10px;">
                        <img src="data:image/png;base64,{banner_base64}" class="banner-img">
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Erro ao carregar banner: {e}")

    # === Texto principal - AGORA SEM MARGENS NO HTML ===
    st.markdown(
        """
        <div class="paragraph">
        O <b>AmazIA</b> é um sistema desenvolvido para analisar dados de 
        <b>Notas Fiscais Eletrônicas (NF-e)</b> da região de Manaus-AM, gerando 
        recomendações personalizadas de produtos com base em um modelo híbrido de 
        <b>Filtragem Colaborativa</b> e <b>Filtragem por Conteúdo</b>.
        O objetivo é fortalecer o comércio local, oferecendo sugestões de compra 
        inteligentes que consideram preferências do consumidor, categorias e marcas 
        mais bem avaliadas, além do histórico real de consumo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # === Seção: Ferramentas Utilizadas ===
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<h2 class='subtitle'>Ferramentas Utilizadas</h2>", unsafe_allow_html=True)

    tools = [
        ("GitHub", "https://img.icons8.com/ios11/512/FFFFFF/github.png", "github"),
        ("Streamlit", "https://streamlit.io/images/brand/streamlit-mark-color.png", "streamlit"),
        ("Python", "https://images.icon-icons.com/112/PNG/512/python_18894.png", "python"),
        ("CSV", "https://cdn-icons-png.flaticon.com/256/8242/8242984.png", "csv"),
    ]

    cols = st.columns(4, gap="large")
    for col, (name, icon, css_class) in zip(cols, tools):
        col.markdown(
            f"""
            <div class="card-tool {css_class}">
                <img src="{icon}">
                <p>{name}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # === Seção: Autores ===
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<h2 class='subtitle'>Autores</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")

    autores = [
        ("Juliana Ballin Lima", foto_juliana, "jbl.snf23@uea.edu.br", "https://github.com/JulianaBallin"),
        ("Lucas Carvalho dos Santos", foto_lucas, "lcds.snf23@uea.edu.br", "https://github.com/lucas-carvalho-ds"),
    ]
    
    for col, (nome, foto, email, github) in zip((col1, col2), autores):
        if foto.exists():
            try:
                foto_base64 = image_to_base64(foto)
                if foto_base64:
                    if foto.suffix.lower() in ['.jpg', '.jpeg']:
                        foto_url = f"data:image/jpeg;base64,{foto_base64}"
                    else:
                        foto_url = f"data:image/png;base64,{foto_base64}"
                else:
                    foto_url = foto.as_uri()
            except Exception as e:
                foto_url = "https://cdn-icons-png.flaticon.com/512/1077/1077012.png"
        else:
            foto_url = "https://cdn-icons-png.flaticon.com/512/1077/1077012.png"

        col.markdown(
            f"""
            <div class="author-card">
                <img src="{foto_url}" class="author-photo">
                <div class="author-info">
                    <p class="author-name">{nome}</p>
                    <div class="author-link">
                        <a href="mailto:{email}">{email}</a>
                        <a href="{github}" target="_blank">{github}</a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)