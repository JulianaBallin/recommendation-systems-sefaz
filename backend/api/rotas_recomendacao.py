from fastapi import APIRouter, HTTPException
import pandas as pd
import time
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.recomendador.feedback_manager import FeedbackManager
from backend.recomendador.hibrido import HybridRecommender
from backend.dataset import loader
from backend.utilitarios.response_formatter import (
    recommendation_response,
    metrics_response,
    success_response,
    error_response
)
from backend.utilitarios.constants import ERROR_CODES

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
    inicio = time.time()
    
    try:
        if request.algo_type == "content":
            recommender = ContentBasedRecommender()
            recs = recommender.recommend(request.user_cpf, request.n_recs)
            
        elif request.algo_type == "hybrid":
            recommender = HybridRecommender()
            recs = recommender.recommend(request.user_cpf, request.n_recs)

        else:
            ratings = loader.load_ratings()
            recommender = CollaborativeFilteringRecommender(ratings)
            recommender.train(algo_type=request.algo_type)
            recs = recommender.recommend_items(request.user_cpf, request.n_recs)

        tempo = time.time() - inicio
        
        return recommendation_response(
            recommendations=recs,
            user_cpf=request.user_cpf,
            algorithm=request.algo_type,
            processing_time=tempo,
            additional_metadata={"requested_count": request.n_recs}
        )
    except Exception as e:
        return error_response(
            message=f"Erro ao gerar recomendações: {str(e)}",
            code=ERROR_CODES["PROCESSING_ERROR"],
            details={"error_type": type(e).__name__},
            status_code=500
        )

@router.post("/metricas")
def calcular_metricas(request: MetricsRequest):
    inicio = time.time()
    
    try:
        if request.algo_type == "content":
            recommender = ContentBasedRecommender()
            metrics = recommender.evaluate_metrics(request.user_cpf, k=request.k)
        else:
            ratings = loader.load_ratings()
            recommender = CollaborativeFilteringRecommender(ratings)
            recommender.train(algo_type=request.algo_type)
            metrics = recommender.evaluate_metrics(request.user_cpf, k=request.k)
        
        tempo = time.time() - inicio
        
        return metrics_response(
            metrics=metrics,
            user_cpf=request.user_cpf,
            algorithm=request.algo_type,
            k_value=request.k,
            processing_time=tempo
        )
    except Exception as e:
        return error_response(
            message=f"Erro ao calcular métricas: {str(e)}",
            code=ERROR_CODES["PROCESSING_ERROR"],
            details={"error_type": type(e).__name__},
            status_code=500
        )

@router.post("/feedback")
def enviar_feedback(request: FeedbackRequest):
    try:
        fm = FeedbackManager()
        fm.add_feedback(request.user_cpf, request.item_id, request.feedback_type)
        
        return success_response(
            data={"feedback_registered": True},
            message=f"Feedback '{request.feedback_type}' registrado com sucesso"
        )
    except Exception as e:
        return error_response(
            message=f"Erro ao registrar feedback: {str(e)}",
            code=ERROR_CODES["PROCESSING_ERROR"],
            details={"error_type": type(e).__name__},
            status_code=500
        )

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
