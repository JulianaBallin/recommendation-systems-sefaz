import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from surprise import Dataset, Reader, SVDpp, KNNWithMeans
from surprise.model_selection import GridSearchCV
from backend.recomendador.metricas import evaluate_precision_at_k
from backend.recomendador.feedback_manager import FeedbackManager
from backend.dataset import loader

PARAMS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models', 'best_svd_params.json')

class CollaborativeFilteringRecommender:
    """
    Implementa sistema de recomendação com suporte a SVD++ e KNN (User/Item based).
    """
    def __init__(self, ratings_df: pd.DataFrame):
        if ratings_df.empty:
            raise ValueError("O DataFrame de avaliações não pode estar vazio.")
        
        self.ratings_df = ratings_df.copy()
        
        # Carregar produtos para obter IDs reais
        products_df = loader.load_derived_products()
        
        # Normalizar descrições para garantir o merge
        self.ratings_df["descricao_produto"] = self.ratings_df["descricao_produto"].astype(str).str.strip()
        products_df["descricao"] = products_df["descricao"].astype(str).str.strip()
        
        # Merge para adicionar o ID do produto
        self.ratings_df = self.ratings_df.merge(
            products_df[["id", "descricao"]], 
            left_on="descricao_produto", 
            right_on="descricao", 
            how="left"
        )
        
        # Mapear colunas
        col_map = {
            "cpf": "CPF_CLIENTE",
            "id": "ID_PRODUTO",
            "avaliacao_descricao": "RATING_DESCRICAO"
        }
        self.ratings_df.rename(columns=col_map, inplace=True)
        
        # Remover linhas sem ID (produtos não padronizados ou não encontrados)
        self.ratings_df.dropna(subset=["ID_PRODUTO"], inplace=True)

        self.model = None
        self.algo_type = "svd" # svd, user_knn, item_knn
        self.best_params = {}

    def train(self, algo_type="svd"):
        """
        Treina o modelo escolhido.
        algo_type: 'svd', 'user_knn', 'item_knn'
        """
        self.algo_type = algo_type
        
        # Garante tipos corretos
        self.ratings_df['RATING_DESCRICAO'] = pd.to_numeric(self.ratings_df['RATING_DESCRICAO'], errors='coerce')
        self.ratings_df.dropna(subset=['CPF_CLIENTE', 'ID_PRODUTO', 'RATING_DESCRICAO'], inplace=True)

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings_df[['CPF_CLIENTE', 'ID_PRODUTO', 'RATING_DESCRICAO']], reader)
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
        # Lógica original do SVD (simplificada para caber aqui, mantendo otimização se existir)
        if not self.best_params and not os.path.exists(PARAMS_FILE):
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
            # Salvar params... (omitido para brevidade, mas ideal manter)
        
        if not self.best_params and os.path.exists(PARAMS_FILE):
             with open(PARAMS_FILE, 'r') as f:
                self.best_params = json.load(f)

        print("Treinando SVD++...")
        self.model = SVDpp(**self.best_params) if self.best_params else SVDpp()
        self.model.fit(full_trainset)

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
        if self.model is None:
            return []

        # Pega todos os IDs de produtos
        all_item_ids = self.ratings_df['ID_PRODUTO'].unique()

        # Itens que o usuário já viu (para não recomendar de novo)
        seen_items = self.ratings_df[self.ratings_df['CPF_CLIENTE'] == user_cpf]['ID_PRODUTO'].unique()

        # Filtrar itens "blacklisted" (dislikes e similares)
        feedback_manager = FeedbackManager()
        blacklisted_items = feedback_manager.get_blacklisted_items(user_cpf)
        
        # Itens a serem previstos (todos - vistos - blacklisted)
        items_to_predict = np.setdiff1d(all_item_ids, np.union1d(seen_items, blacklisted_items))

        # Prevê a nota para cada item não visto
        predictions = [self.model.predict(user_cpf, item_id) for item_id in items_to_predict]

        # Ordena as recomendações pela pontuação ponderada
        predictions.sort(key=lambda x: x.est, reverse=True)
        
        recommended_items = [{'id': pred.iid, 'score': pred.est} for pred in predictions]

        # --- MELHORIA: Fallback para itens populares ---
        # Se não geramos recomendações suficientes, completamos com os mais populares
        if len(recommended_items) < n_recommendations:
            # Itens que o usuário já viu ou que já foram recomendados ou blacklisted
            exclude_items = set(seen_items) | {item['id'] for item in recommended_items} | set(blacklisted_items)
            
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
            # Excluir também os blacklisted aqui, embora teoricamente ele já tenha avaliado bem, mas se deu dislike depois...
            # Assumimos que se ele avaliou bem, não está na blacklist (blacklist vem de feedback explícito negativo)
            fallback_favorites = [item for item in user_top_rated['ID_PRODUTO'].tolist() if item not in current_rec_ids and item not in blacklisted_items]
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
        temp_recommender.train(algo_type=self.algo_type) # Treina o modelo temporário com o mesmo algoritmo

        # 2. Chama a função de avaliação modularizada
        return evaluate_precision_at_k(
            recommender=temp_recommender,
            user_cpf=user_cpf,
            test_data=test_data,
            training_item_ids=training_item_ids,
            n_evaluation_recs=10
        )

    def evaluate_system_accuracy(self, min_ratings_for_eval: int = 4):
        """
        Avalia a acurácia média do sistema (Precision@k) para todos os usuários elegíveis.

        Args:
            min_ratings_for_eval (int): O número mínimo de avaliações que um usuário
                                        deve ter para ser incluído na avaliação.

        Returns:
            Um dicionário com a acurácia média e o número de usuários avaliados.
        """
        user_counts = self.ratings_df['CPF_CLIENTE'].value_counts()
        eligible_users = user_counts[user_counts >= min_ratings_for_eval].index.tolist()

        if not eligible_users:
            return {"average_precision": 0, "evaluated_users_count": 0, "message": "Nenhum usuário elegível para avaliação."}

        total_precision = 0
        evaluated_count = 0

        for i, user_cpf in enumerate(eligible_users):
            print(f"Avaliando usuário {i+1}/{len(eligible_users)}: {user_cpf}")
            report = self.evaluate_accuracy(user_cpf)
            total_precision += report.get("precision_at_k", 0)
            evaluated_count += 1
        
        average_precision = (total_precision / evaluated_count) if evaluated_count > 0 else 0
        return {"average_precision": average_precision, "evaluated_users_count": evaluated_count}
