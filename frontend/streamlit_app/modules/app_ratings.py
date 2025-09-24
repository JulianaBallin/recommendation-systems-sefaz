import streamlit as st
import pandas as pd
from backend.dataset import loader
from backend.utils.preprocessing import validate_cpf, normalize_text, normalize_name

def run():
    st.title("Avaliação e Recomendação")
    st.markdown("---")

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
    st.subheader("Avaliar Produto")

    cpf_val = st.session_state.get("cpf_val", "")
    nome_val = st.session_state.get("nome_val", "")
    selected_client = None

    cpf_input = st.text_input("CPF", value=cpf_val, key="cpf_input")
    nome_input = st.text_input("Nome", value=nome_val, key="nome_input")

    # CPF → Nome
    if cpf_input:
        try:
            cpf_norm = validate_cpf(cpf_input)
            match = clients[clients["CPF"].astype(str) == cpf_norm]
            if not match.empty:
                selected_client = match.iloc[0].to_dict()
                st.session_state["cpf_val"] = selected_client["CPF"]
                st.session_state["nome_val"] = selected_client["NOME"]
                st.success(f"Cliente encontrado: **{selected_client['NOME']}** (CPF: {selected_client['CPF']})")
            else:
                st.error("❌ CPF não encontrado na base de clientes.")
        except Exception as e:
            st.error(f"CPF inválido: {e}")

    # Nome → CPF
    elif nome_input:
        try:
            nome_norm = normalize_name(nome_input)
            clients["NOME_NORM"] = clients["NOME"].apply(normalize_name)
            sugestoes = clients[clients["NOME_NORM"].str.contains(nome_norm)]
            if not sugestoes.empty:
                escolha = st.selectbox("Selecione o cliente", sugestoes["NOME"].tolist())
                if escolha:
                    selected_client = sugestoes[sugestoes["NOME"] == escolha].iloc[0].to_dict()
                    st.session_state["cpf_val"] = selected_client["CPF"]
                    st.session_state["nome_val"] = selected_client["NOME"]
                    st.success(f"Cliente encontrado: **{selected_client['NOME']}** (CPF: {selected_client['CPF']})")
            else:
                st.error("❌ Nome não encontrado na base de clientes.")
        except Exception as e:
            st.error(f"Erro ao validar nome: {e}")

    # Seleção de Produto
    st.markdown("### Selecione um Produto")
    options = ["----"] + (
        products["DESCRICAO"].dropna().unique().tolist()
        if not products.empty and "DESCRICAO" in products.columns
        else []
    )
    produto_desc = st.selectbox(
        "Digite ou escolha um produto",
        options=options,
        index=0,
        key="produto_select",
    )

    if produto_desc != "----" and selected_client is not None:
        produto_row = products[products["DESCRICAO"] == produto_desc].iloc[0]

        # Produto
        st.markdown("### ⭐ Avaliação do Produto")
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
        st.markdown("### Tabela de Avaliações")
        st.dataframe(ratings.tail(10))
