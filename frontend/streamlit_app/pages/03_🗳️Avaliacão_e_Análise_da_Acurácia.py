import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Adiciona o diretório raiz ao path para permitir imports do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.recommender.evaluate_accuracy import evaluate_item_item_accuracy
from frontend.streamlit_app.modules.ui_messages import show_error

st.set_page_config(layout="wide", page_icon="🗳️", page_title="Avaliação do Sistema")

st.title("📈 Avaliação e Análise de Acurácia")
st.markdown("""
Esta página executa uma avaliação da acurácia do modelo de recomendação **Item-Item**. 
A metodologia segue os passos abaixo:
1.  **Escolha de um Usuário**: Um cliente com um histórico de compras suficiente é selecionado aleatoriamente.
2.  **Divisão dos Dados**: O histórico de compras do cliente é dividido em um conjunto de **treino** (para gerar as recomendações) e um conjunto de **teste** (para servir como gabarito).
3.  **Geração e Comparação**: O sistema gera recomendações com base nos dados de treino e as compara com os itens do conjunto de teste.
4.  **Cálculo da Acurácia**: A acurácia é medida pela proporção de recomendações corretas.
""")

@st.cache_data
def load_data_for_evaluation():
    """Carrega os datasets necessários para a avaliação."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    try:
        ratings_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'ratings.csv'))
        products_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'products_unique.csv'))

        # Converte IDs para string para consistência
        ratings_df['PRODUCT_ID'] = ratings_df['PRODUCT_ID'].astype(str)
        products_df['PRODUCT_ID'] = products_df['PRODUCT_ID'].astype(str)
        
        return ratings_df, products_df
    except FileNotFoundError:
        return None, None

ratings_df, products_df = load_data_for_evaluation()

if ratings_df is None or products_df is None:
    show_error("Arquivos `ratings.csv` ou `products_unique.csv` não encontrados. Execute os scripts de preparação de dados primeiro.")
else:
    if st.button("Executar Avaliação de Acurácia", use_container_width=True):
        with st.spinner("Executando avaliação... Isso pode levar alguns segundos."):
            # Escolhe um cliente aleatório que tenha comprado pelo menos 4 itens
            user_counts = ratings_df['CPF'].value_counts()
            eligible_users = user_counts[user_counts >= 4].index

            if len(eligible_users) == 0:
                show_error("Não há usuários com dados suficientes para realizar a avaliação (mínimo de 4 compras).")
            else:
                target_user = np.random.choice(eligible_users)
                
                results = evaluate_item_item_accuracy(ratings_df, products_df, user_cpf=target_user, n_recommendations=5)

                if "error" in results:
                    show_error(f"Erro ao avaliar o usuário {target_user}: {results['error']}")
                else:
                    st.subheader("📊 Relatório de Acurácia")

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label="Acurácia do Modelo",
                            value=f"{results['accuracy']:.2%}"
                        )
                        st.metric(
                            label="Total de Acertos",
                            value=f"{results['num_hits']}",
                            help="Número de itens recomendados que estavam no conjunto de teste (gabarito)."
                        )
                        st.metric(
                            label="Total de Recomendações",
                            value=f"{results['num_recommendations']}"
                        )

                    with col2:
                        st.info(f"**Usuário Testado:** `{results['user_cpf']}`")
                        st.info(f"**Produto de Referência:** `{results['reference_product']}`")

                    st.write("---")
                    st.write("#### Detalhes da Execução")
                    
                    st.write("**Itens Recomendados:**")
                    st.json(results['recommended_items'])
                    
                    st.write("**Itens do Gabarito (Conjunto de Teste):**")
                    st.json(results['test_items_ground_truth'])

                    st.write("**Acertos (Itens em comum):**")
                    st.success(f"{results['hits'] if results['hits'] else 'Nenhum acerto.'}")