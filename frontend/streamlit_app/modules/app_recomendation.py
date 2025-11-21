import streamlit as st
import pandas as pd
from backend.dataset import loader
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.feedback_manager import FeedbackManager

def run():
    st.title("🎯 Recomendações")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # === Carregar dados ===
    clients = loader.load_raw_clients()
    products = loader.load_derived_products()
    ratings = loader.load_ratings()

    # =======================
    # SEÇÃO 1: CONFIGURAÇÃO
    # =======================
    
    # Seleção de Usuário
    selected_client = None
    if not clients.empty:
        client_options = ["Selecione um cliente..."] + [
            f"{row['nome']} ({row['cpf']})" for index, row in clients.iterrows()
        ]
        client_choice = st.selectbox("👤 Usuário:", options=client_options, index=0)
        
        if client_choice != "Selecione um cliente...":
            selected_cpf = client_choice.split('(')[-1].replace(')', '')
            match = clients[clients["cpf"].astype(str) == str(selected_cpf)]
            if not match.empty:
                selected_client = match.iloc[0].to_dict()
    
    # Configurações de Recomendação
    n_recs = st.slider("Número de recomendações:", 1, 20, 5)
    
    algo_type = st.selectbox(
        "Tipo de Filtragem:",
        [
            "SVD++",
            "Colaborativa (Baseada em Item)",
            "Colaborativa (Baseada em Usuário)",
            "Baseada em Conteúdo"
        ]
    )
    
    algo_map = {
        "SVD++": "svd",
        "Colaborativa (Baseada em Item)": "item_knn",
        "Colaborativa (Baseada em Usuário)": "user_knn",
        "Baseada em Conteúdo": "content"
    }

    # =======================
    # SEÇÃO 2: GERAR RECOMENDAÇÕES
    # =======================
    if selected_client:
        if st.button("🚀 Gerar Recomendações", type="primary"):
            with st.spinner("Gerando recomendações personalizadas..."):
                recommendations = []
                
                try:
                    if algo_map[algo_type] == "content":
                        recommender = ContentBasedRecommender()
                        recommendations = recommender.recommend(selected_client["cpf"], n_recs)
                    else:
                        # Colaborativo
                        recommender = CollaborativeFilteringRecommender(ratings)
                        # Treinar com o algoritmo selecionado
                        recommender.train(algo_type=algo_map[algo_type])
                        recommendations = recommender.recommend_items(selected_client["cpf"], n_recs)
                    
                    # Salvar no session state para persistir após feedback
                    st.session_state["last_recommendations"] = recommendations
                    st.session_state["last_algo"] = algo_type
                    st.session_state["last_user"] = selected_client["cpf"]
                    
                except Exception as e:
                    st.error(f"Erro ao gerar recomendações: {str(e)}")

    # =======================
    # SEÇÃO 3: EXIBIÇÃO E FEEDBACK
    # =======================
    # Recuperar recomendações do estado se o usuário for o mesmo
    if selected_client and st.session_state.get("last_user") == selected_client["cpf"]:
        recommendations = st.session_state.get("last_recommendations", [])
        
        if recommendations:
            st.subheader(f"Recomendações para {selected_client['nome']}")
            st.caption(f"Algoritmo: {st.session_state.get('last_algo')}")
            
            feedback_manager = FeedbackManager()
            
            for i, rec in enumerate(recommendations):
                # Tentar obter detalhes do produto se não vierem (caso do colaborativo)
                rec_id = rec.get("id")
                if "descricao" not in rec:
                    prod_details = products[products["id"] == rec_id]
                    if not prod_details.empty:
                        rec["descricao"] = prod_details.iloc[0]["descricao"]
                        rec["marca"] = prod_details.iloc[0]["marca"]
                    else:
                        rec["descricao"] = f"Produto {rec_id}"
                        rec["marca"] = "Desconhecida"

                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{rec['descricao']}**")
                        st.caption(f"Marca: {rec['marca']} | Score: {rec.get('score', 0):.2f}")
                    
                    with col2:
                        # Adicionando índice 'i' à chave para garantir unicidade mesmo se o produto aparecer duplicado
                        if st.button("👍 Gostei", key=f"like_{rec_id}_{i}"):
                            feedback_manager.add_feedback(selected_client["cpf"], rec_id, "like")
                            st.toast(f"Você gostou de {rec['descricao']}!", icon="👍")
                    
                    with col3:
                        if st.button("👎 Não Gostei", key=f"dislike_{rec_id}_{i}"):
                            feedback_manager.add_feedback(selected_client["cpf"], rec_id, "dislike")
                            st.toast(f"Você não gostou de {rec['descricao']}. Ajustaremos as recomendações.", icon="👎")
                    
                    st.divider()
        else:
            if st.session_state.get("last_algo"): # Se já tentou gerar
                st.info("Nenhuma recomendação encontrada com os critérios atuais.")
    elif not selected_client:
        st.info("Selecione um usuário para começar.")
