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
    st.title("⭐ Avaliação")
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
    # =======================
    # SEÇÃO 3: OVERVIEW DO USUÁRIO
    # =======================
    st.markdown("---")
    st.subheader("👤 Overview do Usuário Consultado")

    if selected_client:
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

        # 4. Exibir informações básicas
        full_name_parts = selected_client.get("NOME", "N/A").split()
        display_name = f"{full_name_parts[0]} {full_name_parts[-1]}" if len(full_name_parts) > 1 else full_name_parts[0]
        st.metric("Nome do Usuário", display_name)
        
        st.markdown("---")
        st.markdown("#### 💖 Produtos Favoritos")
        if top_produtos is not None and not top_produtos.empty:
            # Exibir como tabela (DataFrame)
            fav_cols = ["DESCRICAO", "RATING_DESCRICAO"]
            df_display = top_produtos[fav_cols].rename(columns={"DESCRICAO": "Produto", "RATING_DESCRICAO": "Nota"})
            # Converter para string para alinhar à esquerda
            df_display["Nota"] = df_display["Nota"].astype(str)
            
            st.dataframe(
                df_display,
                hide_index=True
            )
        else:
            st.info("Este usuário não possui produtos favoritos (avaliados com nota 4 ou superior).")

        st.markdown("---")
        st.markdown("#### 📜 Histórico de Avaliações")
        if not user_ratings.empty:
            user_ratings_with_desc = pd.merge(user_ratings, products, left_on="ID_PRODUTO", right_on="ID", how="left")
            cols_to_show = ["DESCRICAO", "RATING_DESCRICAO", "RATING_CATEGORIA", "RATING_MARCA"]
            st.dataframe(
                user_ratings_with_desc[cols_to_show],
                hide_index=True
            )
            st.markdown(f"**Total de avaliações:** {total_avaliacoes}")
        else:
            st.warning("Este usuário ainda não possui avaliações. Para ver o histórico, avalie um produto.")

    else:
        st.info("Selecione um usuário acima para visualizar o overview.")

