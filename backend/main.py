import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from backend.recommender.collaborative import CollaborativeRecommender

# --- Configuração Inicial ---

# Dicionário para armazenar objetos carregados (recommender, dataframes)
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Função executada na inicialização da API para carregar os modelos e dados.
    """
    print("Carregando recursos da API...")
    # Define os caminhos para os datasets
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    ratings_path = os.path.join(PROCESSED_DATA_PATH, 'ratings.csv')
    products_path = os.path.join(PROCESSED_DATA_PATH, 'products_unique.csv')

    # Verifica se os arquivos de dados existem e não estão vazios antes de carregar
    ratings_ok = os.path.exists(ratings_path) and os.path.getsize(ratings_path) > 0
    products_ok = os.path.exists(products_path) and os.path.getsize(products_path) > 0

    if not ratings_ok or not products_ok:
        print("\n" + "="*80)
        print("ERRO: Arquivos de dados não encontrados!")
        print(f"Verifique se '{os.path.basename(ratings_path)}' e '{os.path.basename(products_path)}' existem em 'data/processed/'.")
        print("Para gerar os dados necessários, execute o seguinte comando no terminal:")
        print("python backend/dataset/simulator.py")
        print("="*80 + "\n")
        # Impede a API de iniciar se os dados não estiverem prontos
        raise FileNotFoundError("Arquivos de dados essenciais ausentes. Execute o simulador.")

    # Carrega os dataframes com tratamento de erro para arquivos vazios
    ratings_df = pd.read_csv(ratings_path, on_bad_lines='skip')
    products_df = pd.read_csv(products_path, on_bad_lines='skip')
    
    # Instancia e prepara o recomendador
    recommender = CollaborativeRecommender(ratings_df, products_df)
    recommender.train() # "Treina" o modelo com os dados completos
    ml_models["recommender"] = recommender
    print("Recursos carregados com sucesso!")
    
    yield
    
    # Limpa os recursos ao finalizar a API (opcional)
    ml_models.clear()
    print("Recursos da API liberados.")


app = FastAPI(lifespan=lifespan)

# --- Endpoints da API ---

@app.get("/")
def read_root():
    return {"message": "API do Sistema de Recomendação no ar!"}

@app.get("/recommend/products/{user_cpf}")
def get_product_recommendations(user_cpf: str, n: int = 10):
    """
    Endpoint para obter recomendações de produtos para um usuário.
    """
    recommender = ml_models.get("recommender")
    if not recommender:
        raise HTTPException(status_code=503, detail="Recomendador não está pronto.")
    
    recommendations = recommender.recommend_products_for_user(user_cpf, n)
    
    if recommendations.empty:
        raise HTTPException(status_code=404, detail=f"Usuário com CPF {user_cpf} não encontrado ou sem recomendações possíveis.")
        
    return recommendations.to_dict(orient="records")

@app.get("/recommend/similar-products/{product_id}")
def get_similar_product_recommendations(product_id: str, n: int = 5):
    """
    Endpoint para obter recomendações de produtos similares a um produto específico (Item-Item).
    """
    recommender = ml_models.get("recommender")
    if not recommender:
        raise HTTPException(status_code=503, detail="Recomendador não está pronto.")

    # Converte product_id para o tipo correto se necessário (depende do dataset)
    # No nosso caso, o PRODUCT_ID é numérico.
    recommendations = recommender.recommend_similar_products(product_id, n)

    if recommendations.empty:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado ou sem produtos similares.")

    return recommendations.to_dict(orient="records")