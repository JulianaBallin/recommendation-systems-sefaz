import streamlit as st
import os
import pandas as pd
import tempfile
import sys

# Adiciona a pasta raiz do projeto ao sys.path para resolver imports do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.utils.product_loader import add_product, add_products_from_csv
from frontend.streamlit_app.modules.ui_messages import show_success, show_error

EXPECTED_COLUMNS = [
    "CODIGO","DESCRICAO","QTD","UN","VALOR_UNITARIO","VALOR_TOTAL",
    "NOME_SUPERMERCADO","CNPJ","ENDERECO","NUMERO_NFCE","SERIE","DATA_HORA_COMPRA"
]

st.set_page_config(layout="wide", page_icon="📦", page_title="Gerenciar Produtos")

st.title("📦 Gerenciar Produtos")

# -------------------
# FORMULÁRIO INDIVIDUAL
# -------------------
st.subheader("➕ Adicionar Produto Individual")

with st.form("form_add_product"):
    col1, col2, col3 = st.columns(3)

    with col1:
        codigo = st.text_input("Código *", placeholder="823004165003")
        descricao = st.text_input("Descrição *", placeholder="BISCOITO RECHEADO 140G")
        qtd = st.text_input("Quantidade *", placeholder="10")
        un = st.text_input("Unidade *", placeholder="UN, CX, KG")

    with col2:
        valor_unitario = st.text_input("Valor Unitário *", placeholder="4.89")
        valor_total = st.text_input("Valor Total *", placeholder="39.12")
        supermercado = st.text_input("Supermercado *", placeholder="SUPERMERCADO DB LTDA")
        cnpj = st.text_input("CNPJ *", placeholder="22.999.939/0041-95")

    with col3:
        endereco = st.text_area("Endereço *", placeholder="RUA BARAO DO RIO BRANCO, 974, FLORES MANAUS -AM")
        numero_nfce = st.text_input("Número NFCE *", placeholder="193064")
        serie = st.text_input("Série *", placeholder="004")
        data_compra = st.text_input("Data/Hora Compra *", placeholder="17/08/2025 12:34:06")

    submitted = st.form_submit_button("Adicionar Produto")

    if submitted:
        try:
            # validação extra para código
            if not codigo.isdigit() or len(codigo) < 13:
                raise ValueError("Código deve conter ao menos 13 caracteres numéricos.")

            add_product(
                codigo, descricao, qtd, un, valor_unitario, valor_total,
                supermercado, cnpj, endereco, numero_nfce, serie, data_compra
            )
            show_success(f"Produto '{descricao}' adicionado com sucesso ao dataset RAW!")
        except Exception as e:
            show_error(f"Erro ao adicionar produto: {e}")

# -------------------
# UPLOAD CSV
# -------------------
st.subheader("📂 Adicionar Produtos em Lote via CSV")
uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    st.markdown(f"**Arquivo selecionado:** `{uploaded_file.name}`")

    try:
        # Tenta ler o CSV para preview
        df_preview = pd.read_csv(uploaded_file, nrows=5)
        st.write("### 🔎 Prévia dos dados")
        st.dataframe(df_preview, use_container_width=True)

        # Detecta automaticamente se tem cabeçalho
        has_header_guess = set(df_preview.columns).issubset(set(EXPECTED_COLUMNS))
        has_header = st.checkbox("Arquivo contém cabeçalho?", value=has_header_guess)

        if st.button("Cadastrar Produtos do CSV"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            try:
                # Se o arquivo não tiver cabeçalho, precisamos prepará-lo
                if not has_header:
                    df = pd.read_csv(tmp_path, header=None)
                    if df.shape[1] != len(EXPECTED_COLUMNS):
                        raise ValueError(f"O arquivo tem {df.shape[1]} colunas, mas {len(EXPECTED_COLUMNS)} eram esperadas.")
                    df.columns = EXPECTED_COLUMNS
                    df.to_csv(tmp_path, index=False) # Salva o arquivo temporário com os cabeçalhos corretos

                add_products_from_csv(tmp_path)
                show_success("Produtos adicionados com sucesso a partir do arquivo CSV!")

            except Exception as e:
                show_error(f"Erro ao processar o arquivo CSV: {e}")
                st.write("### ✅ Estrutura de colunas esperada:")
                st.code(",".join(EXPECTED_COLUMNS))

    except Exception as e:
        show_error(f"Erro ao ler o arquivo CSV: {e}")
        st.write("### ✅ Estrutura de colunas esperada:")
        st.code(",".join(EXPECTED_COLUMNS))

# -------------------
# VISUALIZAR DATASET
# -------------------
st.subheader("📊 Visualizar Dataset de Produtos")
st.markdown("Visualize os dados brutos, processados ou as interações de compra simuladas (`ratings`).")
 
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
datasets_options = {
    "Raw": os.path.join(BASE_DIR, "data", "raw", "products.csv"),
    "Processed": os.path.join(BASE_DIR, "data", "processed", "products_clean.csv")
}

dataset_choice = st.selectbox("Selecione o dataset", list(datasets_options.keys()))
dataset_path = datasets_options[dataset_choice]

if os.path.exists(dataset_path):
    df = pd.read_csv(dataset_path)
    st.write("### 📝 Cabeçalho")
    st.dataframe(df.head(), use_container_width=True)
    st.write("### 🔽 Últimas 10 linhas")
    st.dataframe(df.tail(10), use_container_width=True)
elif dataset_choice != "Raw": # Não mostra erro para o Raw, que pode não existir inicialmente
    show_error(f"Dataset '{dataset_choice}' não encontrado. Execute os scripts de preparação de dados (`data_cleaner.py`, `product_deduplicator.py`, `simulator.py`) para gerá-lo.")