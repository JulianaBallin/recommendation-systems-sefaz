import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from surprise import Dataset, Reader, SVDpp, KNNWithMeans
from surprise.model_selection import GridSearchCV
from backend.recomendador.metricas import calculate_metrics
from backend.recomendador.feedback_manager import FeedbackManager
from backend.dataset import loader

class CollaborativeFilteringRecommender:
    """
    Implementa sistema de recomendação com suporte a SVD++ e KNN (User/Item based).
    """
    def __init__(self, ratings_df: pd.DataFrame):
        if ratings_df.empty:
            raise ValueError("O DataFrame de avaliações não pode estar vazio.")
        
        self.ratings_df = ratings_df.copy()
        # Garantir que CPF seja string para consistência
        if 'cpf' in self.ratings_df.columns:
            self.ratings_df['cpf'] = self.ratings_df['cpf'].astype(str)
        
        # Verificar se já tem ID ou precisa fazer merge
        if 'id' not in self.ratings_df.columns:
            # Carregar produtos para obter IDs
            products_df = loader.load_derived_products()
            
            # Normalizar descrições
            self.ratings_df["descricao_produto"] = self.ratings_df["descricao_produto"].astype(str).str.strip()
            products_df["descricao"] = products_df["descricao"].astype(str).str.strip()
            
            # Merge para adicionar ID do produto
            self.ratings_df = self.ratings_df.merge(
                products_df[["id", "descricao"]], 
                left_on="descricao_produto", 
                right_on="descricao", 
                how="left"
            )
            
            # Remover linhas sem ID
            self.ratings_df.dropna(subset=["id"], inplace=True)

        self.model = None
        self.algo_type = "svd"
        self.best_params = {}

    def train(self, algo_type="svd"):
        """
        Treina o modelo escolhido.
        """
        self.algo_type = algo_type
        
        # Garante tipos corretos
        self.ratings_df['avaliacao_descricao'] = pd.to_numeric(self.ratings_df['avaliacao_descricao'], errors='coerce')
        self.ratings_df.dropna(subset=['cpf', 'id', 'avaliacao_descricao'], inplace=True)

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings_df[['cpf', 'id', 'avaliacao_descricao']], reader)
        full_trainset = data.build_full_trainset()

        if algo_type == "svd":
            self._train_svd(data, full_trainset)
        elif algo_type == "user_knn":
            print("Treinando KNN User-Based...")
            sim_options = {'name': 'cosine', 'user_based': True}
            self.model = KNNWithMeans(sim_options=sim_options)
            self.model.fit(full_trainset)
        elif algo_type == "item_knn":
            print("Treinando KNN Item-Based...")
            sim_options = {'name': 'cosine', 'user_based': False}
            self.model = KNNWithMeans(sim_options=sim_options)
            self.model.fit(full_trainset)

    def _train_svd(self, data, full_trainset):
        if not self.best_params:
            print("Otimizando SVD++...")
            param_grid = {
                'n_factors': [50, 100],
                'n_epochs': [20],
                'lr_all': [0.005],
                'reg_all': [0.02]
            }
            gs = GridSearchCV(SVDpp, param_grid, measures=['rmse'], cv=3)
            gs.fit(data)
            self.best_params = gs.best_params['rmse']

        print("Treinando SVD++...")
        self.model = SVDpp(**self.best_params) if self.best_params else SVDpp()
        self.model.fit(full_trainset)

    def _get_popular_items(self, n: int = 10):
        """Retorna os N itens mais populares."""
        item_popularity = self.ratings_df.groupby('id')['avaliacao_descricao'].mean()
        popular_items = item_popularity.sort_values(ascending=False).head(n).index.tolist()
        return popular_items

    def recommend_items(self, user_cpf: str, n_recommendations: int = 5):
        """
        Gera recomendações para um usuário específico.
        """
        if self.model is None:
            return []

        all_item_ids = self.ratings_df['id'].unique()
        seen_items = self.ratings_df[self.ratings_df['cpf'] == user_cpf]['id'].unique()

        feedback_manager = FeedbackManager()
        blacklisted_items = feedback_manager.get_blacklisted_items(user_cpf)
        
        items_to_predict = np.setdiff1d(all_item_ids, np.union1d(seen_items, blacklisted_items))
        predictions = [self.model.predict(user_cpf, item_id) for item_id in items_to_predict]
        predictions.sort(key=lambda x: x.est, reverse=True)
        
        recommended_items = [{'id': pred.iid, 'score': pred.est} for pred in predictions]

        # Fallback para itens populares
        if len(recommended_items) < n_recommendations:
            exclude_items = set(seen_items) | {item['id'] for item in recommended_items} | set(blacklisted_items)
            popular_items = self._get_popular_items(n=n_recommendations * 2)
            fallback_items = [item for item in popular_items if item not in exclude_items]
            needed = n_recommendations - len(recommended_items)
            recommended_items.extend([{'id': item_id, 'score': 0} for item_id in fallback_items[:needed]])
        
        # Fallback para favoritos do usuário
        if len(recommended_items) < n_recommendations:
            user_ratings = self.ratings_df[self.ratings_df['cpf'] == user_cpf]
            user_top_rated = user_ratings.sort_values(by="avaliacao_descricao", ascending=False)
            current_rec_ids = {item['id'] for item in recommended_items}
            fallback_favorites = [item for item in user_top_rated['id'].tolist() if item not in current_rec_ids and item not in blacklisted_items]
            needed = n_recommendations - len(recommended_items)
            recommended_items.extend([{'id': item_id, 'score': 0} for item_id in fallback_favorites[:needed]])
        
        return recommended_items[:n_recommendations]

    def evaluate_metrics(self, user_cpf: str):
        user_ratings = self.ratings_df[self.ratings_df['cpf'] == user_cpf]
        if len(user_ratings) < 4:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": 10, "total_relevant": 0,
                "message": "Poucas avaliações."
            }
        train_data, test_data = train_test_split(user_ratings, test_size=0.5, random_state=42)
        
        other_users = self.ratings_df[self.ratings_df['cpf'] != user_cpf][['cpf', 'id', 'avaliacao_descricao']]
        train_subset = train_data[['cpf', 'id', 'avaliacao_descricao']]
        temp_df = pd.concat([other_users, train_subset])
        
        temp_rec = CollaborativeFilteringRecommender(temp_df)
        temp_rec.best_params = self.best_params
        temp_rec.train(algo_type=self.algo_type)
        
        recs = temp_rec.recommend_items(user_cpf, n_recommendations=10)
        rec_ids = [str(item['id']) for item in recs]  # Converter para string
        rel_ids = [str(id_val) for id_val in test_data[test_data['avaliacao_descricao'] >= 3]['id'].tolist()]  # Converter para string
        
        return calculate_metrics(rec_ids, rel_ids)
