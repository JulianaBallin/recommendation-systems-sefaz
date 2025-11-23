import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime
import time
from backend.dataset import loader


def run():
    st.title("⭐ Avaliação")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style="text-align: center; margin-bottom: 25px;">
            Ajude-nos a melhorar suas recomendações de compras!  
            <strong>Avalie os produtos</strong> cadastrados atribuindo uma nota para a <strong>descrição</strong> e a <strong>marca</strong>.  
            Esse passo é opcional, mas quanto mais detalhes você fornecer, mais precisas serão as sugestões futuras.  
            Assim, você ganha recomendações relevantes e apoio na hora de decidir suas próximas compras.
        </p>
        """,
        unsafe_allow_html=True
    )

    # === Carregar dados ===
    clients = loader.load_raw_clients()
    products = loader.load_derived_products()
    ratings = loader.load_ratings()

    # =======================
    # SEÇÃO 1: SELEÇÃO DE USUÁRIO
    # =======================
    st.subheader("👤 Selecionar Usuário")

    selected_client = None
    if not clients.empty:
        # Cria uma lista de opções formatadas para o selectbox
        client_options = ["Selecione um cliente..."] + [
            f"{row['nome']} ({row['cpf']})" for index, row in clients.iterrows()
        ]
        
        client_choice = st.selectbox(
            "Escolha um cliente na lista:",
            options=client_options,
            index=0
        )

        # Se um cliente for escolhido, extrai o CPF e busca os dados
        if client_choice != "Selecione um cliente...":
            # Extrai o CPF da string (ex: "JOAO SILVA (12345678909)" -> "12345678909")
            selected_cpf = client_choice.split('(')[-1].replace(')', '')
            # Converter para int ou str dependendo do tipo no dataframe, aqui assumimos str para comparação segura
            match = clients[clients["cpf"].astype(str) == str(selected_cpf)]
            if not match.empty:
                selected_client = match.iloc[0].to_dict()
                st.success(f"Cliente encontrado: **{selected_client['nome']}** (CPF: {selected_client['cpf']})")
    else:
        st.warning("Nenhum cliente cadastrado. Por favor, gere clientes simulados.")

    # =======================
    # SEÇÃO 2: AVALIAÇÃO DE PRODUTO
    # =======================
    if selected_client:
        st.markdown("### 🛍️ Avaliar Novo Produto")
        
        # Mostrar mensagem de sucesso se acabou de salvar
        if st.session_state.get("show_success"):
            st.success("✅ Avaliação salva com sucesso!")
            # A mensagem desaparecerá na próxima interação do usuário
            st.session_state["show_success"] = False
        
        # Filtrar produtos já avaliados pelo usuário
        user_ratings = ratings[ratings["cpf"].astype(str) == str(selected_client["cpf"])]
        rated_products = user_ratings["descricao_produto"].unique()
        
        available_products = products[~products["descricao"].isin(rated_products)]
        
        if not available_products.empty:
            product_options = ["Selecione um produto..."] + available_products["descricao"].unique().tolist()
            
            selected_product_desc = st.selectbox(
                "Escolha um produto para avaliar:",
                options=product_options,
                index=0
            )
            
            if selected_product_desc != "Selecione um produto...":
                # Obter dados do produto selecionado
                product_row = products[products["descricao"] == selected_product_desc].iloc[0]
                
                st.markdown(f"**Produto:** {product_row['descricao']}")
                st.markdown(f"**Marca:** {product_row['marca']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    rating_desc = st.slider("Avaliação da Descrição (1-5)", 1, 5, 3, key="rating_desc")
                
                with col2:
                    rating_brand = st.slider("Avaliação da Marca (1-5)", 1, 5, 3, key="rating_brand")
                    
                if st.button("Salvar Avaliação"):
                    new_rating = {
                        "nome_usuario": selected_client["nome"],
                        "cpf": selected_client["cpf"],
                        "descricao_produto": product_row["descricao"],
                        "avaliacao_descricao": rating_desc,
                        "marca_produto": product_row["marca"],
                        "avaliacao_marca": rating_brand,
                        "id": product_row["id"]
                    }
                    
                    # Adicionar ao dataframe
                    ratings = pd.concat([ratings, pd.DataFrame([new_rating])], ignore_index=True)
                    
                    # Salvar
                    loader.save_ratings(ratings)
                    
                    # Marcar que acabou de salvar para mostrar mensagem após rerun
                    st.session_state["show_success"] = True
                    
                    # Refresh para atualizar a lista de produtos disponíveis
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
        else:
            st.info("Este usuário já avaliou todos os produtos disponíveis!")

        # =======================
        # SEÇÃO 3: HISTÓRICO
        # =======================
        st.markdown("---")
        st.subheader("📜 Histórico de Avaliações")
        
        if not user_ratings.empty:
            # Mostrar colunas relevantes
            cols_to_show = ["descricao_produto", "avaliacao_descricao", "marca_produto", "avaliacao_marca"]
            st.dataframe(user_ratings[cols_to_show], hide_index=True, use_container_width=True)
            st.markdown(f"**Total de avaliações:** {len(user_ratings)}")
        else:
            st.info("Nenhuma avaliação registrada para este usuário.")

