import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"

def run():
    st.title("🎯 Recomendações")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # === Carregar dados via API ===
    try:
        resp_clients = requests.get(f"{API_URL}/recomendacao/usuarios")
        if resp_clients.status_code == 200:
            clients = pd.DataFrame(resp_clients.json())
        else:
            st.error("Erro ao carregar usuários da API.")
            clients = pd.DataFrame()

        resp_products = requests.get(f"{API_URL}/recomendacao/itens")
        if resp_products.status_code == 200:
            products = pd.DataFrame(resp_products.json())
        else:
            st.error("Erro ao carregar produtos da API.")
            products = pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro de conexão com a API: {e}")
        clients = pd.DataFrame()
        products = pd.DataFrame()

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
            # Garantir tipo string para comparação
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
            "Baseada em Conteúdo",
            "Híbrida (Conteúdo + CF)"
        ]
    )
    
    algo_map = {
        "SVD++": "svd",
        "Colaborativa (Baseada em Item)": "item_knn",
        "Colaborativa (Baseada em Usuário)": "user_knn",
        "Baseada em Conteúdo": "content",
        "Híbrida (Conteúdo + CF)": "hybrid"
    }

    # =======================
    # SEÇÃO 2: GERAR RECOMENDAÇÕES
    # =======================
    if selected_client:
        if st.button("🚀 Gerar Recomendações", type="primary"):
            with st.spinner("Gerando recomendações personalizadas via API..."):
                recommendations = []
                
                try:
                    payload = {
                        "user_cpf": str(selected_client["cpf"]),
                        "n_recs": n_recs,
                        "algo_type": algo_map[algo_type]
                    }
                    
                    response = requests.post(f"{API_URL}/recomendacao/recomendar", json=payload)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        
                        # Extrair recomendações da nova estrutura de resposta
                        if "data" in response_data and "recommendations" in response_data["data"]:
                            recommendations = response_data["data"]["recommendations"]
                        else:
                            # Fallback para estrutura antiga
                            recommendations = response_data
                        
                        # Salvar no session state
                        st.session_state["last_recommendations"] = recommendations
                        st.session_state["last_algo"] = algo_type
                        st.session_state["last_user"] = selected_client["cpf"]
                        st.session_state["last_n_recs"] = n_recs
                    else:
                        st.error(f"Erro na API: {response.text}")
                    
                except Exception as e:
                    st.error(f"Erro ao gerar recomendações: {str(e)}")

    # =======================
    # SEÇÃO 3: EXIBIÇÃO E FEEDBACK
    # =======================
    # Recuperar recomendações do estado se o usuário for o mesmo
    if selected_client and st.session_state.get("last_user") == selected_client["cpf"]:
        recommendations = st.session_state.get("last_recommendations", [])
        # --- NORMALIZAÇÃO DE RECOMENDAÇÕES ---
        normalized = []
        for item in recommendations:

            # ⛔ Se vier string, significa que a resposta da API está incorreta
            if isinstance(item, str):
                st.error(f"⚠️ Resposta inválida recebida da API: {item}")
                continue

            # Somente aceitar recomendações em formato dict
            if isinstance(item, dict):
                normalized.append(item)
            else:
                st.error(f"⚠️ Formato inesperado de recomendação: {item}")

        recommendations = normalized
        st.session_state["last_recommendations"] = normalized

        if recommendations:
            st.subheader(f"Recomendações para {selected_client['nome']}")
            st.caption(f"Algoritmo: {st.session_state.get('last_algo')}")
            
            for i, rec in enumerate(recommendations):
                # Tentar obter detalhes do produto se não vierem (caso do colaborativo)
                rec_id = rec.get("id")
                
                # Se vier do colaborativo, pode não ter descrição/marca
                if "descricao" not in rec:
                    if not products.empty:
                        # Converter IDs para string para garantir match
                        # O ID na recomendação pode ser int ou str, no products também
                        # Vamos tentar converter ambos para string
                        prod_details = products[products["id"].astype(str) == str(rec_id)]
                        if not prod_details.empty:
                            rec["descricao"] = prod_details.iloc[0]["descricao"]
                            rec["marca"] = prod_details.iloc[0]["marca"]
                        else:
                            rec["descricao"] = f"Produto {rec_id}"
                            rec["marca"] = "Desconhecida"
                    else:
                        rec["descricao"] = f"Produto {rec_id}"
                        rec["marca"] = "Desconhecida"

                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{rec.get('descricao', 'Sem descrição')}**")
                        st.caption(f"Marca: {rec.get('marca', 'N/A')} | Score: {rec.get('score', 0):.2f}")
                        if "explanation" in rec:
                            st.write(f"🟢 *{rec['explanation']}*")

                    with col2:
                        if st.button("👍 Gostei", key=f"like_{rec_id}_{i}"):
                            try:
                                requests.post(f"{API_URL}/recomendacao/feedback", json={
                                    "user_cpf": str(selected_client["cpf"]),
                                    "item_id": rec_id,
                                    "feedback_type": "like"
                                })
                                st.toast(f"Você gostou de {rec.get('descricao')}!", icon="👍")

                                st.session_state["last_recommendations"] = [
                                    r for r in st.session_state["last_recommendations"]
                                    if r.get("id") != rec_id
                                ]
                                st.rerun()

                            except Exception as e:
                                st.error(f"Erro ao enviar feedback: {e}")
                    
                    with col3:
                        if st.button("👎 Não Gostei", key=f"dislike_{rec_id}_{i}"):
                            try:
                                requests.post(f"{API_URL}/recomendacao/feedback", json={
                                    "user_cpf": str(selected_client["cpf"]),
                                    "item_id": rec_id,
                                    "feedback_type": "dislike"
                                })
                                st.toast(f"Você não gostou de {rec.get('descricao')}.", icon="👎")
                                            
                                st.session_state["last_recommendations"] = [
                                    r for r in st.session_state["last_recommendations"]
                                    if r.get("id") != rec_id
                                ]
                               
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Erro ao enviar feedback: {e}")
                    
                    st.divider()
            
            # =======================
            # SEÇÃO 4: MÉTRICAS DE AVALIAÇÃO
            # =======================
            st.markdown("---")
            st.subheader("📊 Métricas de Avaliação")
            
            if st.button("🔍 Avaliar Acurácia", key="evaluate_metrics"):
                with st.spinner("Calculando métricas via API..."):
                    try:
                        last_algo = st.session_state.get('last_algo')
                        if not last_algo:
                            st.warning("Gere recomendações primeiro antes de avaliar a acurácia.")
                        else:
                            algo_key = algo_map.get(last_algo)
                            k_value = st.session_state.get('last_n_recs', 10)
                            
                            payload = {
                                "user_cpf": str(selected_client["cpf"]),
                                "algo_type": algo_key,
                                "k": k_value
                            }
                            
                            response = requests.post(f"{API_URL}/recomendacao/metricas", json=payload)
                            
                            if response.status_code == 200:
                                response_data = response.json()
                                
                                # Extrair métricas da nova estrutura de resposta
                                if "data" in response_data:
                                    metrics = response_data["data"]
                                else:
                                    # Fallback para estrutura antiga
                                    metrics = response_data
                                
                                # Exibir métricas
                                if "message" in metrics:
                                    st.warning(metrics["message"])
                                else:
                                    k_value = metrics.get('total_recommended', 10)
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric(
                                            label=f"Precision@{k_value}",
                                            value=f"{metrics['precision_at_k']:.2%}",
                                            help="Proporção de itens recomendados que são relevantes"
                                        )
                                    
                                    with col2:
                                        st.metric(
                                            label=f"Recall@{k_value}",
                                            value=f"{metrics.get('recall_at_k', 0):.2%}",
                                            help="Proporção de itens relevantes que foram recomendados"
                                        )
                                    
                                    with col3:
                                        st.metric(
                                            label="F1-Score",
                                            value=f"{metrics.get('f1_score', 0):.2%}",
                                            help="Média harmônica entre Precision e Recall"
                                        )
                                    
                                    st.caption(f"**Hits:** {metrics['hits']} de {metrics['total_recommended']} recomendações | **Relevantes:** {metrics.get('total_relevant', 'N/A')}")
                            else:
                                st.error(f"Erro na API de métricas: {response.text}")
                    
                    except Exception as e:
                        import traceback
                        st.error(f"Erro ao calcular métricas: {str(e)}")
                        st.code(traceback.format_exc())
        else:
            if st.session_state.get("last_algo"):
                st.info("Nenhuma recomendação encontrada com os critérios atuais.")
    elif not selected_client:
        st.info("Selecione um usuário para começar.")
