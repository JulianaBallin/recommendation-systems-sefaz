"""
app_products.py
---------------
Interface Streamlit para gerenciar produtos:
1. Adicionar produto manualmente
2. Adicionar produtos em lote via upload CSV
3. Visualizar produtos raw
4. Visualizar produtos derivados
"""

import streamlit as st
import pandas as pd

from backend.dataset import loader
from backend.utils import dictionaries, product_loader


def run():
    st.title("📦 Produtos")
    st.markdown("Gerencie produtos cadastrados a partir das notas fiscais ou manualmente.")

    # Carrega dicionários
    cat_map = dictionaries.load_category_map()
    brand_map = dictionaries.load_brand_map()

    # ======================================================
    # 1. Adicionar Produto Manualmente
    # ======================================================
    st.subheader("Adicionar Produto Manualmente")

    with st.form("form_produto_unitario", clear_on_submit=True):
        descricao = st.text_input("Descrição do produto (ex.: 'Arroz Tio João 5kg')")

        categoria = st.selectbox(
            "Selecione a Categoria*",
            options=["-"] + (
                sorted([c for c in cat_map["categoria"].dropna().unique().tolist() if c.strip() != ""])
                if not cat_map.empty else []
            ),
            index=0
        )

        marca = st.selectbox(
            "Selecione a Marca*",
            options=["-"] + (
                sorted([m for m in brand_map["marca"].dropna().unique().tolist() if m.strip() != ""])
                if not brand_map.empty else []
            ),
            index=0
        )

        submitted = st.form_submit_button("Adicionar Produto")

        if submitted:
            if descricao.strip() == "":
                st.error("❌ A descrição não pode estar vazia.")
            else:
                produto = {
                    "Categoria": categoria,
                    "Marca": marca,
                    "Descricao": descricao.strip().upper()
                }
                novo_id = product_loader.append_product(produto)
                st.success(f"✅ Produto adicionado com ID {novo_id} ao dataset derivado!")

    st.markdown("---")

    # ======================================================
    # 2. Adicionar Produtos em Lote
    # ======================================================
    st.subheader("Adicionar Produtos em Lote (NF → Raw + Derived)")

    file = st.file_uploader("Carregar arquivo CSV de nota fiscal", type=["csv"])
    if file:
        try:
            df_raw = pd.read_csv(file)
            df_raw.columns = [c.strip().upper() for c in df_raw.columns]

            if "DESCRICAO" not in df_raw.columns:
                st.error("CSV inválido: precisa ter a coluna DESCRICAO")
            else:
                # Preview antes de salvar
                st.info("📋 Pré-visualização dos dados carregados (3 primeiras + 3 últimas linhas):")

                if len(df_raw) > 6:
                    preview_df = pd.concat([df_raw.head(3), df_raw.tail(3)])
                else:
                    preview_df = df_raw

                st.dataframe(preview_df)
                st.write(f"**Total de registros no arquivo:** {len(df_raw)}")

                if st.button("Confirmar e adicionar ao sistema"):
                    try:
                        qtd = product_loader.append_batch(df_raw)
                        st.success(f"✅ {qtd} produtos válidos adicionados ao sistema.")
                    except ValueError as e:
                        st.error(str(e))

        except Exception as e:
            st.error(f"Erro ao processar CSV: {e}")

    st.markdown("---")

    # ======================================================
    # 3. Visualizar Produtos Raw
    # ======================================================
    st.subheader("Visualizar Produtos Raw (NF)")
    preview_raw = loader.preview_raw_receipts()
    if preview_raw["total"] > 0:
        st.dataframe(pd.concat([preview_raw["head"], preview_raw["tail"]]))
        st.write(f"**Total de registros de NF:** {preview_raw['total']}")
    else:
        st.info("Nenhum produto raw encontrado.")

    st.markdown("---")

    # ======================================================
    # 4. Visualizar Produtos Derivados
    # ======================================================
    st.subheader("Visualizar Produtos Normalizados")
    preview_derived = loader.preview_clean_products(n=10)
    if preview_derived["total"] > 0:
        st.dataframe(preview_derived["preview"])
        st.write(f"**Total de produtos derivados:** {preview_derived['total']}")
    else:
        st.info("Nenhum produto normalizado ainda.")
