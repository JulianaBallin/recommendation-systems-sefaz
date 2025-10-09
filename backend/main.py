from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from backend.dataset import loader
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
import pandas as pd

# --- Carregamento e Preparação do Modelo ---
recommender_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega os dados e inicializa o recomendador na inicialização da API."""
    global recommender_instance
    print("🚀 Iniciando o serviço de recomendação...")
    try:
        ratings_df = loader.load_ratings()
        if not ratings_df.empty:
            recommender_instance = CollaborativeFilteringRecommender(ratings_df)
            recommender_instance.train() # Chama o treinamento explicitamente
            print("✅ Serviço de recomendação iniciado e modelo treinado.")
        else:
            print("⚠️ Aviso: Nenhum dado de avaliação encontrado. O serviço de recomendação está inativo.")
    except Exception as e:
        print(f"❌ Erro ao iniciar o serviço de recomendação: {e}")
    
    yield
    # Código para limpeza ao desligar a API (se necessário)
    print("🛑 Serviço de recomendação finalizado.")

app = FastAPI(
    title="Recommendation Service API",
    description="API para gerar recomendações de produtos com base em Filtragem Colaborativa.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/recommend/{cpf_cliente}", tags=["Recommendations"])
def get_recommendations(cpf_cliente: str, n_items: int = 5):
    """
    Gera recomendações de produtos para um cliente específico e avalia a acurácia.
    """
    if recommender_instance is None:
        raise HTTPException(status_code=503, detail="Serviço de recomendação indisponível (sem dados).")

    try:
        # Gera recomendações
        recommended_ids = recommender_instance.recommend_items(cpf_cliente, n_items)
        
        # Avalia a acurácia
        accuracy_report = recommender_instance.evaluate_accuracy(cpf_cliente)

        return {
            "cpf_cliente": cpf_cliente,
            "recommendations": recommended_ids,
            "accuracy_report": accuracy_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a recomendação: {str(e)}")