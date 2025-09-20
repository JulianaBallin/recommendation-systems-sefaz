import streamlit as st
import requests
import pandas as pd
import os
import sys

# Adiciona a pasta raiz do projeto ao sys.path para resolver imports do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from frontend.streamlit_app.modules.ui_messages import show_error, show_success

# URL da API do backend
API_URL = "http://127.0.0.1:8000"


st.set_page_config(layout="wide", page_icon="🛍️", page_title="Recomendação por Produtos")

st.title("🛍️ Recomendação por Similaridade de Produto")
st.markdown("""
Esta página demonstra a **Filtragem Colaborativa Baseada em Item**.
Selecione um produto e o sistema irá encontrar outros produtos que são frequentemente comprados
juntos ou por clientes com perfis de consumo semelhantes.
""")

# --- Carregar Produtos para seleção ---
@st.cache_data
def load_products():
    """Carrega os produtos do dataset processado para a seleção."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    products_path = os.path.join(BASE_DIR, "data", "processed", "products_unique.csv")
    if os.path.exists(products_path):
        df_products = pd.read_csv(products_path)
        # Criar uma coluna de exibição "ID - Descrição" para o selectbox
        df_products['display'] = df_products['PRODUCT_ID'].astype(str) + " - " + df_products['DESCRICAO']
        return df_products.set_index('PRODUCT_ID')
    return pd.DataFrame()

products_df = load_products()

if products_df.empty:
    show_error("Não foi possível carregar a lista de produtos. Execute o script `product_deduplicator.py` e verifique o arquivo `data/processed/products_unique.csv`.")
else:
    # --- Formulário de Seleção ---
    selected_product_display = st.selectbox(
        "Selecione um produto para encontrar itens similares:",
        options=products_df['display'],
        index=0
    )

    if st.button("Encontrar Produtos Similares", use_container_width=True):
        if selected_product_display:
            # Extrai o ID do produto da string de exibição
            selected_product_id = selected_product_display.split(" - ")[0]
            
            with st.spinner(f"Buscando produtos similares a: {selected_product_display}...") as s:
                try:
                    # Ajusta a chamada para pedir 5 recomendações
                    response = requests.get(f"{API_URL}/recommend/similar-products/{selected_product_id}?n=5")
                    response.raise_for_status()
                    
                    recommendations = response.json()
                    df_recs = pd.DataFrame(recommendations).drop_duplicates(subset=['PRODUCT_ID'])
                    show_success(f"✨ Top {len(df_recs)} produtos similares encontrados!")
                    st.dataframe(df_recs, use_container_width=True)
                except requests.exceptions.HTTPError as e:
                    # Trata especificamente o erro 404 (Não encontrado)
                    if e.response.status_code == 404:
                        st.warning(f"Não foram encontradas recomendações de produtos similares para '{selected_product_display}'.")
                    else:
                        # Para outros erros HTTP, mostra a mensagem genérica
                        show_error(f"Ocorreu um erro na API: {e.response.status_code} - {e.response.text}")
                except requests.exceptions.RequestException as e:
                    show_error(f"Não foi possível conectar à API. Verifique se o backend está em execução. Detalhe: {e}")