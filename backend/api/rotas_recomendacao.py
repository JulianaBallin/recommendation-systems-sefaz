from fastapi import APIRouter, HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.recomendador.feedback_manager import FeedbackManager
from backend.dataset import loader

router = APIRouter(prefix="/recomendacao", tags=["Recomendação"])

class RecommendationRequest(BaseModel):
    user_cpf: str
    n_recs: int = 5
    algo_type: str # "content", "svd", "user_knn", "item_knn"

class MetricsRequest(BaseModel):
    user_cpf: str
    algo_type: str
    k: int = 10  # Número de recomendações para avaliar

class FeedbackRequest(BaseModel):
    user_cpf: str
    item_id: Any
    feedback_type: str

@router.post("/recomendar")
def gerar_recomendacoes(request: RecommendationRequest):
    try:
        if request.algo_type == "content":
            recommender = ContentBasedRecommender()
            recs = recommender.recommend(request.user_cpf, request.n_recs)
        else:
            ratings = loader.load_ratings()
            recommender = CollaborativeFilteringRecommender(ratings)
            recommender.train(algo_type=request.algo_type)
            recs = recommender.recommend_items(request.user_cpf, request.n_recs)
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metricas")
def calcular_metricas(request: MetricsRequest):
    try:
        if request.algo_type == "content":
            recommender = ContentBasedRecommender()
            metrics = recommender.evaluate_metrics(request.user_cpf, k=request.k)
        else:
            ratings = loader.load_ratings()
            recommender = CollaborativeFilteringRecommender(ratings)
            recommender.train(algo_type=request.algo_type)
            metrics = recommender.evaluate_metrics(request.user_cpf, k=request.k)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def enviar_feedback(request: FeedbackRequest):
    try:
        fm = FeedbackManager()
        fm.add_feedback(request.user_cpf, request.item_id, request.feedback_type)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/itens")
def listar_itens():
    products = loader.load_derived_products()
    products = products.where(pd.notnull(products), None)
    return products.to_dict(orient="records")

@router.get("/usuarios")
def listar_usuarios():
    clients = loader.load_raw_clients()
    clients = clients.where(pd.notnull(clients), None)
    return clients.to_dict(orient="records")
