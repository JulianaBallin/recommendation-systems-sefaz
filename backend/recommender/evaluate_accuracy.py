import pandas as pd
import numpy as np
import os
import sys

# Adiciona o diretório raiz ao path para permitir imports do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.recommender.collaborative import CollaborativeRecommender

def evaluate_item_item_accuracy(ratings_df: pd.DataFrame, products_df: pd.DataFrame, user_cpf: str, n_recommendations: int = 5):
    """
    Avalia a acurácia do modelo Item-Item para um único usuário.

    Args:
        ratings_df (pd.DataFrame): O dataset completo de ratings.
        products_df (pd.DataFrame): O dataset de produtos.
        user_cpf (str): O CPF do usuário a ser avaliado.
        n_recommendations (int): O número de recomendações a serem geradas.

    Returns:
        dict: Um dicionário com os resultados da avaliação.
    """
    # 1. DIVIDIR OS DADOS DO USUÁRIO
    user_data = ratings_df[ratings_df['CPF'] == user_cpf].copy()
    
    if len(user_data) < 4: # Precisa de pelo menos 2 para treino e 2 para teste
        return {"error": "Usuário com dados insuficientes para avaliação."}

    # Embaralha os dados do usuário para garantir uma divisão aleatória
    user_data = user_data.sample(frac=1, random_state=42).reset_index(drop=True)

    # Divide os dados: 50% para treino, 50% para teste (gabarito)
    split_point = int(len(user_data) * 0.5)
    train_data = user_data.iloc[:split_point]
    test_data = user_data.iloc[split_point:]

    # O restante dos dados (de outros usuários) também faz parte do treino
    other_users_data = ratings_df[ratings_df['CPF'] != user_cpf]
    full_train_set = pd.concat([train_data, other_users_data])

    # Pega o produto mais comprado pelo usuário no conjunto de TREINO para gerar recomendações
    if train_data.empty:
        return {"error": "Conjunto de treino vazio para o usuário."}
    
    # Ordena por RATING (quantidade) e pega o ID do produto
    reference_product_id = train_data.sort_values(by='RATING', ascending=False).iloc[0]['PRODUCT_ID']
    reference_product_desc = products_df.loc[products_df['PRODUCT_ID'] == reference_product_id, 'DESCRICAO'].iloc[0]

    # 2. GERAR RECOMENDAÇÕES COM BASE APENAS NA PARTE 1 (TREINO)
    # Instancia o recomendador com o conjunto de treino
    recommender = CollaborativeRecommender(full_train_set, products_df)
    recommender.train()

    # Gera as recomendações
    recommendations_df = recommender.recommend_similar_products(reference_product_id, n=n_recommendations)
    recommended_product_ids = set(recommendations_df['PRODUCT_ID'].astype(str))    

    # 3. COMPARAR COM A PARTE 2 (GABARITO)
    # Itens que o usuário realmente comprou no conjunto de teste
    test_product_ids = set(test_data['PRODUCT_ID'].astype(str))

    # Função auxiliar para buscar descrições
    def get_product_details(product_ids_set):
        details = products_df[products_df['PRODUCT_ID'].isin(product_ids_set)]
        return (details['PRODUCT_ID'] + " - " + details['DESCRICAO']).tolist()

    recommended_items_with_names = get_product_details(recommended_product_ids)
    test_items_with_names = get_product_details(test_product_ids)

    # 4. CALCULAR A ACURÁCIA
    hits = recommended_product_ids.intersection(test_product_ids)
    num_hits = len(hits)
    
    if n_recommendations == 0:
        accuracy = 0.0
    else:
        accuracy = num_hits / n_recommendations

    hits_with_names = get_product_details(hits)

    return {
        "user_cpf": user_cpf,
        "reference_product": f"{reference_product_id} - {reference_product_desc}",
        "train_items": train_data['PRODUCT_ID'].tolist(),
        "test_items_ground_truth": test_items_with_names,
        "recommended_items": recommended_items_with_names,
        "hits": hits_with_names,
        "num_hits": num_hits,
        "num_recommendations": n_recommendations,
        "accuracy": accuracy
    }

if __name__ == "__main__":
    # --- Carregar os dados ---
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
    
    ratings_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'ratings.csv'))
    products_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'products_unique.csv'))

    # Converte IDs para string para consistência
    ratings_df['PRODUCT_ID'] = ratings_df['PRODUCT_ID'].astype(str)
    products_df['PRODUCT_ID'] = products_df['PRODUCT_ID'].astype(str)

    # --- Executar a avaliação ---
    # Escolhe um cliente aleatório que tenha comprado pelo menos 4 itens
    user_counts = ratings_df['CPF'].value_counts()
    eligible_users = user_counts[user_counts >= 4].index
    target_user = np.random.choice(eligible_users)

    results = evaluate_item_item_accuracy(ratings_df, products_df, user_cpf=target_user, n_recommendations=5)

    # --- Exibir o relatório ---
    print("\n" + "="*80)
    print("Relatório de Acurácia - Filtragem Colaborativa (Item-Item)")
    print("="*80)
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title():<30}: {value}")
    print("="*80)
    print(f"\nAnálise: O sistema recomendou {results['num_recommendations']} produtos e acertou {results['num_hits']}, resultando em uma acurácia de {results['accuracy']:.2%}.")
    print("="*80 + "\n")