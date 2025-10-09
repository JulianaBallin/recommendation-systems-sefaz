import pandas as pd

def evaluate_precision_at_k(recommender, user_cpf: str, test_data: pd.DataFrame, training_item_ids: list, n_evaluation_recs: int = 10):
    """
    Calcula a Precisão@K (Acurácia) para um determinado usuário e modelo.

    Args:
        recommender: A instância do modelo de recomendação treinado (temporário).
        user_cpf: O CPF do usuário a ser avaliado.
        test_data: O DataFrame contendo os dados de teste (gabarito).
        training_item_ids: Lista de IDs de itens usados no treino.
        n_evaluation_recs: O número de recomendações a serem geradas (K).

    Returns:
        Um dicionário contendo o relatório completo de acurácia.
    """
    # 1. Gera recomendações com base no modelo de simulação
    recommended_items_with_scores = recommender.recommend_items(user_cpf, n_recommendations=n_evaluation_recs)
    recommended_item_ids = [item['id'] for item in recommended_items_with_scores]

    # 2. Identifica os itens que o usuário gostou no gabarito
    liked_items_in_test = test_data[test_data['RATING_DESCRICAO'] >= 3]['ID_PRODUTO'].tolist()

    # 3. Calcula os acertos e a precisão
    hit_items = set(recommended_item_ids) & set(liked_items_in_test)
    hits = len(hit_items)
    total_recommended = len(recommended_item_ids)
    precision_at_k = (hits / total_recommended) if total_recommended > 0 else 0

    # 4. Monta o relatório final
    return {
        "precision_at_k": precision_at_k,
        "hits": hits,
        "total_recommended": total_recommended,
        "message": "Acurácia calculada com sucesso.",
        "ground_truth_liked_items": liked_items_in_test,
        "training_items": training_item_ids,
        "simulated_recommendations": recommended_item_ids,
        "hit_items": list(hit_items)
    }