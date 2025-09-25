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
from backend.utils.ui_messages import show_success, show_error, show_info
from backend.utils.ui_messages import show_table


def run():
    # Título da página
    st.markdown('<h1 class="title">🛒 Gerenciar Produtos</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="paragraph">'
        'Gerencie seus produtos de supermercado utilizando duas formas eficientes de cadastro: '
        '1 - Registrar itens pontuais com o <strong>Cadastro Manual</strong>, ideal para ajustes rápidos ou produtos avulsos. '
        '2 - Para inserir grandes volumes de uma vez, use a <strong>Importação em Lote</strong> via arquivo CSV. '
        'Este método exige um formato específico contendo: '
        '<strong>CÓDIGO, DESCRIÇÃO, QTD, UN, VALOR_UNITÁRIO, VALOR_TOTAL, NOME_SUPERMERCADO, CNPJ, ENDEREÇO, NÚMERO_NFCE, SÉRIE e a DATA_HORA_COMPRA</strong>.'
        '</div>',
        unsafe_allow_html=True
    )

    # Carrega dicionários
    cat_map = dictionaries.load_category_map()
    brand_map = dictionaries.load_brand_map()

    # ======================================================
    # 1. Adicionar Produto Manualmente
    # ======================================================
    st.markdown('<h2 class="subtitle">➕ Adicionar Produto Manualmente</h2>', unsafe_allow_html=True)

    with st.form("form_produto_unitario", clear_on_submit=True):
        descricao = st.text_input("Descrição do produto* (ex.: 'Arroz Tio João 5kg')")

        categoria = st.selectbox(
            "Selecione a Categoria*",
            options=["-"] + (
                sorted([c for c in cat_map["CATEGORIA"].dropna().unique().tolist() if c.strip() != ""])
                if not cat_map.empty else []
            ),
            index=0
        )

        marca = st.selectbox(
            "Selecione a Marca*",
            options=["-"] + (
                sorted([m for m in brand_map["MARCA"].dropna().unique().tolist() if m.strip() != ""])
                if not brand_map.empty else []
            ),
            index=0
        )

        submitted = st.form_submit_button("Adicionar Produto")

        if submitted:
            if descricao.strip() == "":
                show_error(" A descrição não pode estar vazia.")
            elif categoria == "-" or not categoria.strip():
                show_error(" A categoria é obrigatória. Selecione uma opção.")
            elif marca == "-" or not marca.strip():
                show_error(" A marca é obrigatória. Selecione uma opção.")
            else:
                produto = {
                    "CATEGORIA": categoria.strip().upper(),
                    "MARCA": marca.strip().upper(),
                    "DESCRICAO": descricao.strip().upper()
                }
                novo_id = product_loader.append_product(produto)
                show_success(f"✅ Produto adicionado com ID {novo_id} ao dataset derivado!")


    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ======================================================
    # 2. Adicionar Produtos em Lote
    # ======================================================
    st.markdown('<h2 class="subtitle">📂 Adicionar Produtos em Lote (CSV)</h2>', unsafe_allow_html=True)

    file = st.file_uploader("Carregar arquivo CSV de nota fiscal", type=["csv"])
    if file:
        try:
            df_raw = pd.read_csv(file)
            df_raw.columns = [c.strip().upper() for c in df_raw.columns]

            if "DESCRICAO" not in df_raw.columns:
                show_error("CSV inválido: precisa ter a coluna DESCRICAO")
            else:
                show_info("📋 Pré-visualização dos dados carregados (3 primeiras + 3 últimas linhas):")

                if len(df_raw) > 6:
                    preview_df = pd.concat([df_raw.head(3), df_raw.tail(3)])
                else:
                    preview_df = df_raw

                st.dataframe(preview_df)
                st.markdown(f'<div class="paragraph"><b>Total de registros no arquivo:</b> {len(df_raw)}</div>',
                            unsafe_allow_html=True)

                if st.button("Confirmar e adicionar ao sistema"):
                    qtd, df_sucesso, df_erros = product_loader.append_batch(df_raw)

                    # =======================
                    # ✅ Produtos válidos
                    # =======================
                    if qtd > 0:
                        show_success(f"{qtd} produtos válidos foram adicionados ao sistema (RAW + Products).")
                        st.markdown("### ✅ Registros Válidos Salvos")
                        st.dataframe(df_sucesso[["ID", "DESCRICAO", "CATEGORIA", "MARCA"]])

                    # =======================
                    # ❌ Produtos inválidos
                    # =======================
                    if not df_erros.empty:
                        show_error("Alguns produtos não foram adicionados por erro de validação:")
                        st.markdown("### ❌ Registros Inválidos (não salvos)")
                        st.dataframe(df_erros[["Linha", "Descricao", "Erro"]])

        except Exception as e:
            show_error(f"Erro ao processar CSV: {e}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ======================================================
    # 3. Visualizar Produtos Raw
    # ======================================================
    st.markdown('<h2 class="subtitle">📑 Visualizar Registros Notas Fiscais (RAW)</h2>', unsafe_allow_html=True)
    preview_raw = loader.preview_raw_receipts()
    if preview_raw["total"] > 0:
        df_preview = preview_raw["preview"]   # já vem head+tail ou tudo
        show_table(df_preview)
        st.markdown(
            f'<div class="paragraph"><b>Total de registros de NF:</b> {preview_raw["total"]}</div>',
            unsafe_allow_html=True
        )
    else:
        show_info("Nenhum produto raw encontrado.")


    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ======================================================
    # 4. Visualizar Produtos Derivados
    # ======================================================
    st.markdown('<h2 class="subtitle">✅ Visualizar Produtos Derivados NF</h2>', unsafe_allow_html=True)
    preview_derived = loader.preview_clean_products(n=10)
    if preview_derived["total"] > 0:
        show_table(preview_derived["preview"])
        st.markdown(f'<div class="paragraph"><b>Total de produtos derivados (NF):</b> {preview_derived["total"]}</div>',
                    unsafe_allow_html=True)
    else:
        show_info("Nenhum produto normalizado ainda.")
