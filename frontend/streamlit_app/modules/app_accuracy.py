import streamlit as st
import requests

def run():
    st.title("⚙️ Avaliação Geral da Acurácia")
    st.markdown("---")
    st.markdown("Calcule a acurácia média do sistema de recomendação, considerando todos os usuários com um número mínimo de avaliações.")

    if st.button("Calcular Acurácia"):
        API_URL = "http://127.0.0.1:8000/evaluate_system"
        with st.spinner("Calculando a acurácia média para todos os usuários elegíveis... Isso pode levar alguns minutos."):
            try:
                response = requests.get(API_URL)
                if response.status_code == 200:
                    report = response.json()
                    avg_precision = report.get("average_precision", 0)
                    user_count = report.get("evaluated_users_count", 0)
                    st.success(f"Avaliação concluída baseada nos **{user_count}** usuários elegíveis e disponíveis na base de dados.")
                    st.metric("Acurácia Média do Sistema", f"{avg_precision:.2%}")
                else:
                    st.error(f"Erro ao avaliar o sistema: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao serviço de recomendação. Verifique se o backend está em execução.")
