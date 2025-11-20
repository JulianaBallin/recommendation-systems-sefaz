import streamlit as st
import pandas as pd
import requests
import altair as alt
from backend.dataset import loader

def load_and_preprocess_data():
    """Carrega clientes e produtos, e padroniza colunas."""
    clients = loader.load_raw_clients()
    products = loader.load_derived_products()

    rename_map = {
        "descricao": "DESCRICAO",
        "description": "DESCRICAO",
        "codigo": "CODIGO",
        "categoria": "CATEGORIA",
        "marca": "MARCA",
    }
    products.columns = [c.upper() for c in products.columns]
    products = products.rename(columns=rename_map)
    
    # Garantir que o ID seja string para comparações
    if "ID" in products.columns:
        products["ID"] = products["ID"].astype(str)
        
    return clients, products

def select_client(clients):
    """Exibe o seletor de clientes e retorna o cliente selecionado."""
    st.subheader("👤 Selecionar Usuário")

    if not clients.empty:
        client_options = ["Selecione um cliente..."] + [
            f"{row['NOME']} ({row['CPF']})" for index, row in clients.iterrows()
        ]
        
        client_choice = st.selectbox(
            "Escolha um cliente na lista para gerar recomendações:",
            options=client_options,
            index=0
        )

        if client_choice != "Selecione um cliente...":
            selected_cpf = client_choice.split('(')[-1].replace(')', '')
            match = clients[clients["CPF"] == selected_cpf]
            if not match.empty:
                selected_client = match.iloc[0].to_dict()
                st.success(f"Cliente selecionado: **{selected_client['NOME']}** (CPF: {selected_client['CPF']})")
                return selected_client
    else:
        st.warning("Nenhum cliente cadastrado.")
    
    return None

def get_recommendations(cpf, n_recs):
    """Faz a requisição para a API de recomendação."""
    API_URL = "http://127.0.0.1:8000/recommend"
    try:
        response = requests.get(f"{API_URL}/{cpf}?n_items={n_recs}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao contatar o serviço de recomendação: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao serviço de recomendação. Verifique se o backend está em execução.")
        return None

def display_recommendations(products, recommended_items_data):
    """Exibe a lista de produtos recomendados."""
    # Extrai IDs e scores
    recommended_ids = [item['id'] for item in recommended_items_data]
    recommended_scores = {str(item['id']): item['score'] for item in recommended_items_data}

    st.subheader("🎁 Produtos Recomendados")
    if recommended_ids:
        # Filtra os produtos recomendados
        recommended_products_df = products[products["ID"].isin([str(i) for i in recommended_ids])].copy()
        # Adiciona o score ao DataFrame para poder ordenar
        recommended_products_df['SCORE'] = recommended_products_df['ID'].apply(lambda x: recommended_scores.get(str(x), 0))
        # Ordena o DataFrame pelo score em ordem decrescente
        sorted_recommended_products = recommended_products_df.sort_values(by='SCORE', ascending=False)

        for index, row in sorted_recommended_products.iterrows():
            score = row['SCORE']
            st.markdown(f"- **{row['DESCRICAO']}** (Score: {score:.2f})")
    else:
        st.info("Não foi possível gerar novas recomendações no momento.")

def display_accuracy_report(accuracy_report):
    """Exibe o relatório de acurácia e gráfico."""
    st.markdown("---")
    st.subheader("🎯 Relatório de Acurácia do Modelo")
    st.markdown(
        "<p style='font-size: 14px;'>A acurácia é calculada através de uma simulação. O sistema esconde metade do histórico de avaliações do usuário (o gabarito) e tenta prever esses itens usando a outra metade. A métrica representa a porcentagem de acertos dentro das 10 previsões feitas durante este teste.</p>",
        unsafe_allow_html=True
    )
    
    if accuracy_report.get("message") != "Acurácia calculada com sucesso.":
        st.warning(accuracy_report.get("message", "Não foi possível calcular a acurácia."))
        return

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

def display_simulation_details(products, accuracy_report):
    """Exibe os detalhes da simulação (acertos/erros)."""
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

def display_ground_truth(products, accuracy_report):
    """Exibe o gabarito (itens que o usuário gostou)."""
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

def display_training_items(products, accuracy_report):
    """Exibe os itens usados para treino."""
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

def run():
    st.title("🧠 Geração de Recomendações")
    st.markdown("---")
    st.markdown(
        """
        <p style="text-align: center; margin-bottom: 25px;">
            Obtenha recomendações personalizadas para os clientes baseadas no histórico de avaliações.
        </p>
        """,
        unsafe_allow_html=True
    )

    # 1. Carregar dados
    clients, products = load_and_preprocess_data()

    # 2. Selecionar usuário
    selected_client = select_client(clients)

    # 3. Gerar recomendações
    if selected_client:
        st.markdown("---")
        st.subheader("⚙️ Configuração da Recomendação")
        
        n_recs = st.slider("Número de recomendações a gerar:", min_value=1, max_value=10, value=5, key="n_recs_slider_rec_page")

        if st.button("Gerar Recomendações"):
            cpf = selected_client["CPF"]
            
            with st.spinner("Buscando recomendações personalizadas..."):
                data = get_recommendations(cpf, n_recs)
                
                if data:
                    recommended_items_data = data.get("recommendations", [])
                    accuracy_report = data.get("accuracy_report", {})

                    # 4. Exibir resultados
                    display_recommendations(products, recommended_items_data)
                    display_accuracy_report(accuracy_report)
                    display_simulation_details(products, accuracy_report)
                    display_ground_truth(products, accuracy_report)
                    display_training_items(products, accuracy_report)
