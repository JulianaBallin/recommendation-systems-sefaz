import pandas as pd


def calculate_metrics(recommended_items: list, relevant_items: list):
    """
    Calcula Precision@K, Recall@K e F1-Score de forma genérica.
    
    Funciona para qualquer tipo de filtragem (colaborativa, conteúdo, híbrida, etc).
    
    Args:
        recommended_items: Lista de itens recomendados (podem ser IDs, descrições, ou qualquer identificador).
        relevant_items: Lista de itens relevantes (mesmo tipo de identificador usado em recommended_items).
    
    Returns:
        Dicionário com precision_at_k, recall_at_k, f1_score, hits, total_recommended e total_relevant.
    
    Exemplo:
        >>> recs = ['A', 'B', 'C', 'D', 'E']
        >>> relevantes = ['B', 'D', 'F', 'G']
        >>> metrics = calculate_metrics(recs, relevantes)
        >>> # Precision = 2/5 = 0.4 (B e D estão nas recomendações)
        >>> # Recall = 2/4 = 0.5 (B e D foram capturados de 4 relevantes)
        >>> # F1 = 2 * 0.4 * 0.5 / (0.4 + 0.5) = 0.444
    """
    # Calcula hits (recomendações que são relevantes)
    hits = len(set(recommended_items) & set(relevant_items))
    total_recommended = len(recommended_items)
    total_relevant = len(relevant_items)
    
    # Calcula métricas
    precision_at_k = (hits / total_recommended) if total_recommended > 0 else 0
    recall_at_k = (hits / total_relevant) if total_relevant > 0 else 0
    f1_score = (2 * precision_at_k * recall_at_k / (precision_at_k + recall_at_k)) if (precision_at_k + recall_at_k) > 0 else 0
    
    return {
        "precision_at_k": precision_at_k,
        "recall_at_k": recall_at_k,
        "f1_score": f1_score,
        "hits": hits,
        "total_recommended": total_recommended,
        "total_relevant": total_relevant
    }