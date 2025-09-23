"""
app_clients.py
---------------
Interface Streamlit para gerenciar clientes:
1. Cadastrar cliente manualmente
2. Adicionar clientes em lote via upload CSV
3. Visualizar clientes brutos (raw)
4. Visualizar clientes derivados (limpos e normalizados)
"""

import streamlit as st
import pandas as pd

from backend.dataset import loader
from backend.utils import client_loader


def run():
    # Reset do formulário se flag estiver ativa
    if "reset_client_form" in st.session_state and st.session_state.reset_client_form:
        st.session_state.reset_client_form = False
        st.session_state.cpf_input = ""
        st.session_state.nome_input = ""
        st.session_state.nasc_input = ""
        st.session_state.cep_input = ""
        st.session_state.genero_input = "-"


    st.title("👥 Clientes")
    st.markdown("Gerencie clientes cadastrados manualmente ou via upload de CSV.")

    # ======================================================
    # 1. Cadastrar Cliente Manualmente
    # ======================================================
    st.subheader("Cadastrar Cliente Manualmente")

    with st.form("form_cliente_unitario", clear_on_submit=False):
        cpf = st.text_input("CPF (apenas números)", key="cpf_input")
        nome = st.text_input("Nome completo", key="nome_input")
        nascimento = st.text_input("Data de nascimento (dd/mm/yyyy)", key="nasc_input")
        cep = st.text_input("CEP (somente Manaus-AM, ex.: 69075000)", key="cep_input")
        genero = st.selectbox("Gênero", ["-", "Feminino", "Masculino", "Outro"], key="genero_input")

        submitted = st.form_submit_button("Cadastrar Cliente")

        if submitted:
            if genero == "-":
                st.error("❌ Você deve selecionar o gênero.")
            else:
                cliente = {
                    "Cpf": cpf.strip(),
                    "Name": nome.strip(),
                    "Birthdate": nascimento.strip(),
                    "Cep": cep.strip(),
                    "Gender": genero,
                }
                ok, msg = client_loader.append_client(cliente)

                if ok:
                    st.success("✅ Cliente cadastrado com sucesso!")
                    st.session_state.reset_client_form = True
                    st.rerun()

                else:
                    st.error(f"❌ Não foi possível cadastrar: {msg}")


    st.markdown("---")

    # ======================================================
    # 2. Adicionar Clientes em Lote
    # ======================================================
    st.subheader("Adicionar Clientes em Lote (CSV)")

    file = st.file_uploader("Carregar arquivo CSV de clientes", type=["csv"])
    if file:
        try:
            df_raw = pd.read_csv(file)
            df_raw.columns = [c.strip().upper() for c in df_raw.columns]

            required_cols = {"CPF", "NOME", "DATA_NASCIMENTO", "CEP", "GENERO"}
            if not required_cols.issubset(set(df_raw.columns)):
                st.error(
                    f"CSV inválido. Colunas esperadas: {', '.join(required_cols)}"
                )
            else:
                st.info("Pré-visualização dos dados carregados:")
                st.dataframe(df_raw.head(3))
                st.dataframe(df_raw.tail(3))

                if st.button("Confirmar e adicionar ao sistema"):
                    qtd, invalids = client_loader.append_batch_clients(df_raw)

                    if qtd > 0:
                        st.success(f"✅ {qtd} clientes válidos adicionados à base.")

                    if invalids:
                        st.warning("⚠️ Algumas linhas não foram adicionadas:")
                        for line, reason in invalids:
                            st.text(f"Linha {line}: {reason}")
                            
        except Exception as e:
            st.error(f"Erro ao processar CSV: {e}")

    st.markdown("---")

    # ======================================================
    # 3. Visualizar Clientes Brutos (Raw)
    # ======================================================
    st.subheader("Visualizar Clientes Cadastrados")
    preview = client_loader.preview_clients()
    if preview["total"] > 0:
        st.dataframe(preview["preview"])
        st.write(f"**Total de clientes cadastrados:** {preview['total']}")
    else:
        st.info("Nenhum cliente encontrado.")

    st.markdown("---")
