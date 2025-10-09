import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from surprise import Dataset, Reader, SVDpp
from surprise.model_selection import GridSearchCV
from backend.recomendador.metricas import evaluate_precision_at_k

PARAMS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models', 'best_svd_params.json')

class CollaborativeFilteringRecommender:
    """
    Implementa um sistema de recomendação com SVD++, uma evolução do SVD
    que considera feedback implícito para maior acurácia.
    """
    def __init__(self, ratings_df: pd.DataFrame):
        if ratings_df.empty:
            raise ValueError("O DataFrame de avaliações não pode estar vazio.")
        
        self.ratings_df = ratings_df.copy() # Armazena os dados brutos
        self.svd_model = None
        self.best_params = {}

    def train(self):
        """
        Otimiza hiperparâmetros (se necessário) e treina o modelo SVD++ com os dados fornecidos.
        """
        # Garante que os tipos de dados estão corretos
        self.ratings_df['RATING_DESCRICAO'] = pd.to_numeric(self.ratings_df['RATING_DESCRICAO'], errors='coerce')
        self.ratings_df.dropna(subset=['CPF_CLIENTE', 'ID_PRODUTO', 'RATING_DESCRICAO'], inplace=True)

        # Prepara os dados para o formato da biblioteca Surprise
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings_df[['CPF_CLIENTE', 'ID_PRODUTO', 'RATING_DESCRICAO']], reader)
        
        # 1. Otimiza os hiperparâmetros apenas se não estiverem em memória
        if not self.best_params and not os.path.exists(PARAMS_FILE):
            print("Otimizando hiperparâmetros do modelo SVD++ (pode demorar)...")
            param_grid = {
                'n_factors': [50, 80, 100],      # Testar mais fatores latentes
                'n_epochs': [20, 30],           # Mais iterações para convergência
                'lr_all': [0.005, 0.01],      # Taxas de aprendizado variadas
                'reg_all': [0.02, 0.05, 0.1]  # Termos de regularização para evitar overfitting
            }
            gs = GridSearchCV(SVDpp, param_grid, measures=['rmse', 'mae'], cv=3, joblib_verbose=2)
            gs.fit(data)

            self.best_params = gs.best_params['rmse']
            
            # Salva os melhores parâmetros em um arquivo JSON
            models_dir = os.path.dirname(PARAMS_FILE)
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            with open(PARAMS_FILE, 'w') as f:
                json.dump(self.best_params, f)

            print(f"Melhores parâmetros encontrados e salvos (RMSE: {gs.best_score['rmse']:.4f}):", self.best_params)
        
        elif not self.best_params:
            print("Carregando hiperparâmetros otimizados de arquivo...")
            with open(PARAMS_FILE, 'r') as f:
                self.best_params = json.load(f)
            print("Parâmetros carregados:", self.best_params)

        # 2. Treina o modelo final com os melhores parâmetros
        print("Treinando o modelo com os melhores parâmetros...")
        self.svd_model = SVDpp(**self.best_params, random_state=42)
        
        # Constrói o conjunto de treino com todos os dados
        full_trainset = data.build_full_trainset()
        self.svd_model.fit(full_trainset)

    def _get_popular_items(self, n: int = 10):
        """Retorna os N itens mais populares com base na média de avaliação."""
        item_popularity = self.ratings_df.groupby('ID_PRODUTO')['RATING_DESCRICAO'].mean()
        # Ordena pela nota média e pega os N melhores
        popular_items = item_popularity.sort_values(ascending=False).head(n).index.tolist()
        return popular_items

    def recommend_items(self, user_cpf: str, n_recommendations: int = 5):
        """
        Gera recomendações para um usuário específico.
        """
        if self.svd_model is None:
            return []

        # Pega todos os IDs de produtos
        all_item_ids = self.ratings_df['ID_PRODUTO'].unique()

        # Itens que o usuário já viu (para não recomendar de novo)
        seen_items = self.ratings_df[self.ratings_df['CPF_CLIENTE'] == user_cpf]['ID_PRODUTO'].unique()

        # Itens a serem previstos (todos menos os que o usuário já viu)
        items_to_predict = np.setdiff1d(all_item_ids, seen_items)

        # Prevê a nota para cada item não visto
        predictions = [self.svd_model.predict(user_cpf, item_id) for item_id in items_to_predict]

        # Ordena as recomendações pela pontuação ponderada
        predictions.sort(key=lambda x: x.est, reverse=True)
        
        recommended_items = [{'id': pred.iid, 'score': pred.est} for pred in predictions]

        # --- MELHORIA: Fallback para itens populares ---
        # Se não geramos recomendações suficientes, completamos com os mais populares
        if len(recommended_items) < n_recommendations:
            # Itens que o usuário já viu ou que já foram recomendados
            exclude_items = set(seen_items) | {item['id'] for item in recommended_items}
            
            popular_items = self._get_popular_items(n=n_recommendations * 2) # Pega mais para ter margem
            fallback_items = [item for item in popular_items if item not in exclude_items]
            
            needed = n_recommendations - len(recommended_items)
            recommended_items.extend([{'id': item_id, 'score': 0} for item_id in fallback_items[:needed]]) # Score 0 para fallback
        
        # --- MELHORIA 2: Fallback para os itens favoritos do próprio usuário (Recompra) ---
        # Se, mesmo após os fallbacks, não houver recomendações suficientes (cenário de saturação),
        # preenchemos com os itens mais bem avaliados pelo próprio usuário.
        if len(recommended_items) < n_recommendations:
            user_ratings = self.ratings_df[self.ratings_df['CPF_CLIENTE'] == user_cpf]
            user_top_rated = user_ratings.sort_values(by="RATING_DESCRICAO", ascending=False)
            
            current_rec_ids = {item['id'] for item in recommended_items}
            fallback_favorites = [item for item in user_top_rated['ID_PRODUTO'].tolist() if item not in current_rec_ids]
            needed = n_recommendations - len(recommended_items)
            recommended_items.extend([{'id': item_id, 'score': 0} for item_id in fallback_favorites[:needed]])
        
        return recommended_items[:n_recommendations]

    def evaluate_accuracy(self, user_cpf: str):
        """
        Avalia a acurácia das recomendações para um usuário, conforme a metodologia solicitada.
        """
        user_ratings = self.ratings_df[self.ratings_df['CPF_CLIENTE'] == user_cpf]

        # Requer um número mínimo de avaliações para uma avaliação significativa
        if len(user_ratings) < 4:
            return {
                "precision_at_k": 0, "hits": 0, "total_recommended": 10,
                "message": "Avaliação de acurácia não disponível (poucas avaliações)."
            }

        # 1. Divide os dados do usuário em treino e teste (gabarito)
        train_data, test_data = train_test_split(user_ratings, test_size=0.5, random_state=42)

        # Extrai os IDs dos itens usados no conjunto de treino da simulação
        training_item_ids = train_data['ID_PRODUTO'].tolist()

        # Cria e treina um modelo temporário isolado, usando os melhores parâmetros já encontrados.
        temp_ratings_df = pd.concat([self.ratings_df[self.ratings_df['CPF_CLIENTE'] != user_cpf], train_data])
        temp_recommender = CollaborativeFilteringRecommender(temp_ratings_df)
        temp_recommender.best_params = self.best_params # Garante que use os mesmos parâmetros
        temp_recommender.train() # Treina o modelo temporário

        # 2. Chama a função de avaliação modularizada
        return evaluate_precision_at_k(
            recommender=temp_recommender,
            user_cpf=user_cpf,
            test_data=test_data,
            training_item_ids=training_item_ids,
            n_evaluation_recs=10
        )
