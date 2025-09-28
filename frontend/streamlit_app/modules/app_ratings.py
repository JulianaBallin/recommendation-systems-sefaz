import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime
from backend.dataset import loader
from backend.utils.preprocessing import validate_cpf, normalize_text, normalize_name
from backend.utils.ui_messages import show_table 


def calculate_age(birthdate_str):
    """Calcula a idade a partir de uma data de nascimento no formato 'dd/mm/yyyy'."""
    try:
        # Tenta múltiplos formatos: com barras e com espaços
        try:
            birthdate = datetime.strptime(birthdate_str, "%d/%m/%Y")
        except ValueError:
            birthdate = datetime.strptime(birthdate_str, "%d %m %Y")

        today = datetime.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    except (ValueError, TypeError):
        return "N/A"

def run():
    st.title("⭐ Avaliação e Recomendação")
    st.markdown("---")
    st.markdown(
        """
        <p style="text-align: center; margin-bottom: 25px;">
            Ajude-nos a melhorar suas recomendações de compras!  
            <strong>Avalie os produtos</strong> cadastrados informando a <strong>marca</strong> ou a <strong>categoria</strong>.  
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

    # Padronizar colunas esperadas
    rename_map = {
        "descricao": "DESCRICAO",
        "description": "DESCRICAO",
        "codigo": "CODIGO",
        "categoria": "CATEGORIA",
        "marca": "MARCA",
    }
    products.columns = [c.upper() for c in products.columns]
    products = products.rename(columns=rename_map)

    # =======================
    # SEÇÃO 1: AVALIAÇÃO POR PRODUTO
    # =======================
    st.subheader("👤 Selecionar Usuário")

    selected_client = None
    if not clients.empty:
        # Cria uma lista de opções formatadas para o selectbox
        client_options = ["Selecione um cliente..."] + [
            f"{row['NOME']} ({row['CPF']})" for index, row in clients.iterrows()
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
            match = clients[clients["CPF"] == selected_cpf]
            if not match.empty:
                selected_client = match.iloc[0].to_dict()
                st.success(f"Cliente encontrado: **{selected_client['NOME']}** (CPF: {selected_client['CPF']})")
    else:
        st.warning("Nenhum cliente cadastrado. Por favor, adicione clientes na página 'Clientes'.")

    # Seleção de Produto
    st.markdown("### 🛍️ Selecionar Produto")
    options = ["----"] + (
        products["DESCRICAO"].dropna().unique().tolist()
        if not products.empty and "DESCRICAO" in products.columns
        else []
    )
    produto_desc = st.selectbox(
        "Digite ou escolha um produto*",
        options=options,
        index=0,
        key="produto_select",
    )

    if produto_desc != "----" and selected_client is not None:
        produto_row = products[products["DESCRICAO"] == produto_desc].iloc[0]

        # Produto
        st.markdown("### ⭐ Avaliação do Produto*")
        st.markdown(f"**{produto_row['DESCRICAO']}**")
        rating_desc = st.slider("Nota", 1, 5, 3)

        # Categoria
        rating_cat = None
        if produto_row.get("CATEGORIA"):
            st.markdown("### 🏷️ Avaliação da Categoria")
            st.markdown(f"**{produto_row['CATEGORIA']}**")
            rating_cat = st.select_slider(
                "Nota", options=[None, 1, 2, 3, 4, 5], value=None, key="rating_cat"
            )

        # Marca
        rating_brand = None
        if produto_row.get("MARCA"):
            st.markdown("### 🏭 Avaliação da Marca")
            st.markdown(f"**{produto_row['MARCA']}**")
            rating_brand = st.select_slider(
                "Nota", options=[None, 1, 2, 3, 4, 5], value=None, key="rating_brand"
            )

        if st.button("Salvar Avaliação"):
            if not selected_client.get("CPF"):
                st.error("CPF não pode ser nulo para salvar avaliação.")
            else:
                # Cria nova linha com a avaliação
                new_entry = pd.DataFrame([{
                    "CPF_CLIENTE": selected_client["CPF"],
                    "ID_PRODUTO": produto_row["ID"],   # ✅ corrigido
                    "RATING_DESCRICAO": rating_desc,   # obrigatório
                    "RATING_CATEGORIA": rating_cat if rating_cat else None,
                    "RATING_MARCA": rating_brand if rating_brand else None,
                }])

                # Remove qualquer registro antigo do mesmo CPF+ID_PRODUTO
                mask = (
                    (ratings["CPF_CLIENTE"].astype(str) == str(selected_client["CPF"])) &
                    (ratings["ID_PRODUTO"].astype(str) == str(produto_row["ID"]))
                )
                ratings = ratings[~mask]

                # Adiciona a nova avaliação
                ratings = pd.concat([ratings, new_entry], ignore_index=True)

                # Salva no CSV
                loader.save_ratings(ratings)
                st.success("✅ Avaliação salva com sucesso!")

                # Força refresh da tela
                if hasattr(st, "rerun"):
                    st.rerun()
                else:
                    st.experimental_rerun()

    # Mostrar avaliações
    if not ratings.empty:
        st.markdown("### 📊 Visualizar Registros de Avaliações")
        show_table(ratings)
        st.markdown(f"**Total de avaliações:** {len(ratings)}")

    # =======================
    # SEÇÃO 3: OVERVIEW DO USUÁRIO
    # =======================
    if selected_client:
        st.markdown("---")

        # --- LÓGICA DE CONTROLE DE ESTADO ---
        # Reseta a exibição do overview se o cliente mudar
        if 'last_cpf' not in st.session_state or st.session_state.last_cpf != selected_client.get("CPF"):
            st.session_state.show_overview = False
            st.session_state.last_cpf = selected_client.get("CPF")

        if st.button("Consultar Usuário"):
            st.session_state.show_overview = True

        # --- BLOCO DE EXIBIÇÃO PERSISTENTE ---
        if st.session_state.get('show_overview', False):
            with st.container():
                st.subheader(f"👤 Overview do Usuário Consultado")

                # 1. Filtrar avaliações do usuário
                user_ratings = ratings[ratings["CPF_CLIENTE"].astype(str) == str(selected_client["CPF"])]
                total_avaliacoes = len(user_ratings)

                # 2. Calcular idade
                idade = calculate_age(selected_client.get("DATA_NASC"))

                # 3. Obter produtos favoritos
                top_produtos = pd.DataFrame()
                if not user_ratings.empty:
                    user_ratings_local = user_ratings.copy()
                    user_ratings_local["ID_PRODUTO"] = user_ratings_local["ID_PRODUTO"].astype(str)
                    products["ID"] = products["ID"].astype(str)
                    user_ratings_details = pd.merge(user_ratings_local, products, left_on="ID_PRODUTO", right_on="ID", how="left")
                    if not user_ratings_details.empty:
                        user_ratings_details['RATING_DESCRICAO'] = pd.to_numeric(user_ratings_details['RATING_DESCRICAO'], errors='coerce')
                        favorite_products = user_ratings_details[user_ratings_details['RATING_DESCRICAO'] >= 4]
                        top_produtos = favorite_products.sort_values(by="RATING_DESCRICAO", ascending=False)

                # 4. Exibir informações
                col1, col2, col3 = st.columns([2, 4, 1])
                full_name_parts = selected_client.get("NOME", "N/A").split()
                display_name = f"{full_name_parts[0]} {full_name_parts[-1]}" if len(full_name_parts) > 1 else full_name_parts[0]
                col1.metric("Totais de Avaliação", total_avaliacoes)
                col2.metric("Nome do Usuário", display_name)
                col3.metric("Idade", idade)
                
                st.markdown("---")
                st.markdown("##### 💖 Produtos Favoritos")
                if top_produtos is not None and not top_produtos.empty:
                    for index, row in top_produtos.iterrows():
                        descricao = row.get('DESCRICAO', 'Produto sem descrição')
                        rating = row.get('RATING_DESCRICAO', 'N/A')
                        st.markdown(f"- **{descricao}** (Nota: {int(rating)})")
                else:
                    st.info("Este usuário não possui produtos favoritos (avaliados com nota 4 ou superior).")

                st.markdown("---")
                st.markdown("#####  Histórico de Avaliações do Usuário")
                if not user_ratings.empty:
                    user_ratings_with_desc = pd.merge(user_ratings, products, left_on="ID_PRODUTO", right_on="ID", how="left")
                    cols_to_show = ["DESCRICAO", "RATING_DESCRICAO", "RATING_CATEGORIA", "RATING_MARCA"]
                    st.dataframe(user_ratings_with_desc[cols_to_show], use_container_width=True)
                else:
                    st.warning("Este usuário ainda não possui avaliações. Para ver o histórico, avalie um produto.")

                # =======================
                # SEÇÃO 4: GERAR RECOMENDAÇÕES
                # =======================
                st.markdown("---")
                st.markdown("##### 🚀 Gerar Recomendações para o Usuário")
                
                n_recs = st.slider("Número de recomendações a gerar:", min_value=1, max_value=10, value=5, key="n_recs_slider")

                if st.button("Gerar Recomendações"):
                    API_URL = "http://127.0.0.1:8000/recommend"
                    cpf = selected_client["CPF"]

                    with st.spinner("Buscando recomendações personalizadas..."):
                        try:
                            response = requests.get(f"{API_URL}/{cpf}?n_items={n_recs}")

                            if response.status_code == 200:
                                data = response.json()
                                recommended_items_data = data.get("recommendations", [])
                                accuracy_report = data.get("accuracy_report", {})

                                # Extrai IDs e scores
                                recommended_ids = [item['id'] for item in recommended_items_data]
                                recommended_scores = {str(item['id']): item['score'] for item in recommended_items_data}

                                st.subheader("🎁 Produtos Recomendados para o Usuário")
                                if recommended_ids:
                                    # Filtra os produtos recomendados
                                    recommended_products_df = products[products["ID"].isin([str(i) for i in recommended_ids])].copy()
                                    # Adiciona o score ao DataFrame para poder ordenar
                                    recommended_products_df['SCORE'] = recommended_products_df['ID'].apply(lambda x: recommended_scores.get(str(x), 0))
                                    # Ordena o DataFrame pelo score em ordem decrescente
                                    sorted_recommended_products = recommended_products_df.sort_values(by='SCORE', ascending=False)

                                    for index, row in sorted_recommended_products.iterrows():
                                        score = row['SCORE']
                                        # Formata o score para exibir com 2 casas decimais
                                        st.markdown(f"- **{row['DESCRICAO']}** (Score: {score:.2f})")
                                else:
                                    st.info("Não foi possível gerar novas recomendações no momento.")

                                st.markdown("---")
                                st.subheader("🎯 Relatório de Acurácia do Modelo")
                                st.markdown(
                                    "<p style='font-size: 14px;'>A acurácia é calculada através de uma simulação. O sistema esconde metade do histórico de avaliações do usuário (o gabarito) e tenta prever esses itens usando a outra metade. A métrica representa a porcentagem de acertos dentro das 10 previsões feitas durante este teste.</p>",
                                    unsafe_allow_html=True
                                )
                                
                                if accuracy_report.get("message") != "Acurácia calculada com sucesso.":
                                    st.warning(accuracy_report.get("message", "Não foi possível calcular a acurácia."))
                                else:
                                    hits = accuracy_report.get("hits", 0)
                                    total = accuracy_report.get("total_recommended", 0)
                                    accuracy = accuracy_report.get("precision_at_k", 0.0)
                                    misses = total - hits

                                    col1_acc, col2_acc, _ = st.columns([1, 1, 2])
                                    col1_acc.metric("Acertos", f"{hits}/{total}")
                                    col2_acc.metric("Acurácia", f"{accuracy:.0%}", help="Dos 10 itens recomendados na simulação, quantos foram acertos? Mede a eficiência do espaço.")
                                    
                                    chart_data = pd.DataFrame({
                                        'Tipo': ['Acertos', 'Erros'],
                                        'Quantidade': [hits, misses],
                                        'Cor': ['#3e721d', '#a69076']
                                    })

                                    chart = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
                                        theta=alt.Theta(field="Quantidade", type="quantitative"),
                                        color=alt.Color(field="Cor", type="nominal", scale=None),
                                        tooltip=['Tipo', 'Quantidade']
                                    ).properties(title='Distribuição de Acertos vs. Erros')
                                    st.altair_chart(chart, use_container_width=True)

                                # --- SEÇÃO DE RECOMENDAÇÕES DA SIMULAÇÃO ---
                                st.markdown("---")
                                st.subheader("🔬 Recomendações da Simulação (para Acurácia)")
                                st.markdown("Esta é a lista de itens que o modelo previu durante a simulação de acurácia. É comparando esta lista com o 'Gabarito' que obtemos a métrica.")

                                simulated_rec_ids = accuracy_report.get("simulated_recommendations", [])
                                hit_item_ids = accuracy_report.get("hit_items", [])

                                if simulated_rec_ids:
                                    simulated_rec_products = products[products["ID"].isin([str(i) for i in simulated_rec_ids])]
                                    for index, row in simulated_rec_products.iterrows():
                                        if row["ID"] in [str(i) for i in hit_item_ids]:
                                            st.markdown(f"- ✅ **{row['DESCRICAO']}**: <span style='color:green;'>**Acerto!**</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"- ❌ **{row['DESCRICAO']}**: <span style='color:red;'>**Erro** (Recomendado, mas não estava no gabarito)</span>", unsafe_allow_html=True)
                                else:
                                    st.info("Não foi possível gerar recomendações na simulação.")


                                # --- SEÇÃO DE GABARITO ---
                                st.markdown("---")
                                st.subheader("🔍 Detalhes do Gabarito")
                                st.markdown("Itens que o usuário gostou (com nota ≥ 3) no conjunto de teste e que foram usados para medir a acurácia.")

                                ground_truth_ids = accuracy_report.get("ground_truth_liked_items", [])
                                if ground_truth_ids:
                                    ground_truth_products = products[products["ID"].isin([str(i) for i in ground_truth_ids])]

                                    # A comparação deve ser com as recomendações da SIMULAÇÃO
                                    simulated_rec_ids_str = [str(i) for i in accuracy_report.get("simulated_recommendations", [])]

                                    for index, row in ground_truth_products.iterrows():
                                        if row["ID"] in simulated_rec_ids_str:
                                            st.markdown(f"- ✅ **{row['DESCRICAO']}**: <span style='color:green;'>**Acerto!** (Recomendado corretamente)</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"- ❌ **{row['DESCRICAO']}**: <span style='color:orange;'>**Não recomendado** (Era uma boa sugestão, mas não foi prevista)</span>", unsafe_allow_html=True)
                                else:
                                    st.info("Não havia itens com nota positiva no conjunto de teste para compor o gabarito.")

                                # --- SEÇÃO DE DADOS DE TREINO ---
                                st.markdown("---")
                                st.subheader("📚 Itens Usados para Treino (na Simulação)")
                                st.markdown("Itens do histórico do usuário que foram usados para treinar o modelo temporário que gerou as recomendações para o cálculo de acurácia.")

                                training_ids = accuracy_report.get("training_items", [])
                                if training_ids:
                                    training_products = products[products["ID"].isin([str(i) for i in training_ids])]
                                    for index, row in training_products.iterrows():
                                        st.markdown(f"- {row['DESCRICAO']}")
                                else:
                                    st.info("Não foi possível identificar os itens de treino.")


                            else:
                                st.error(f"Erro ao contatar o serviço de recomendação: {response.text}")

                        except requests.exceptions.ConnectionError:
                            st.error("Não foi possível conectar ao serviço de recomendação. Verifique se o backend está em execução.")
