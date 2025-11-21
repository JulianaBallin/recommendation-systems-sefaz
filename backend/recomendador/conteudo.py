import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from backend.dataset import loader
from backend.recomendador.feedback_manager import FeedbackManager
from backend.recomendador.metricas import calculate_metrics
import numpy as np

class ContentBasedRecommender:
    def __init__(self):
        self.products_df = loader.load_derived_products()
        self.ratings_df = loader.load_ratings()
        self.tfidf_matrix = None
        self.vectorizer = None
        self._prepare_tfidf()

    def _prepare_tfidf(self):
        """Prepara a matriz TF-IDF das descrições dos produtos."""
        if self.products_df.empty:
            return
        
        # Preencher valores nulos
        self.products_df["descricao"] = self.products_df["descricao"].fillna("")
        
        self.vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.products_df["descricao"])

    def recommend(self, user_cpf: str, n_recommendations: int = 5):
        """
        Recomenda itens baseados no perfil de conteúdo do usuário.
        O perfil é construído a partir dos itens que o usuário avaliou bem (>3).
        """
        if self.products_df.empty or self.ratings_df.empty:
            return []

        # 1. Obter itens que o usuário gostou
        user_ratings = self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]
        liked_items = user_ratings[user_ratings["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
        
        if not liked_items:
            return []

        # 2. Criar perfil do usuário (média dos vetores dos itens que gostou)
        # Mapear descrições para índices
        product_indices = []
        for item_desc in liked_items:
            indices = self.products_df[self.products_df["descricao"] == item_desc].index.tolist()
            product_indices.extend(indices)
        
        if not product_indices:
            return []
            
        user_profile = np.asarray(self.tfidf_matrix[product_indices].mean(axis=0))

        # 3. Calcular similaridade com todos os itens
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix).flatten()

        # 4. Filtrar itens já vistos e blacklisted
        seen_items = user_ratings["descricao_produto"].unique()
        
        feedback_manager = FeedbackManager()
        # Nota: get_blacklisted_items retorna IDs, mas aqui estamos trabalhando com descrições/índices
        # Idealmente deveríamos trabalhar sempre com IDs. Vamos converter.
        blacklisted_ids = feedback_manager.get_blacklisted_items(user_cpf)
        blacklisted_descs = self.products_df[self.products_df["id"].isin(blacklisted_ids)]["descricao"].unique()
        
        # Criar lista de tuplas (índice, score)
        sim_scores = list(enumerate(cosine_sim))
        
        # Ordenar por similaridade
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        added_descriptions = set()
        
        for idx, score in sim_scores:
            item_desc = self.products_df.iloc[idx]["descricao"]
            item_id = self.products_df.iloc[idx]["id"]
            
            if item_desc in seen_items or item_desc in blacklisted_descs or item_desc in added_descriptions:
                continue
                
            recommendations.append({
                "id": item_id,
                "descricao": item_desc,
                "marca": self.products_df.iloc[idx]["marca"],
                "score": score
            })
            
            added_descriptions.add(item_desc)
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from backend.dataset import loader
from backend.recomendador.feedback_manager import FeedbackManager
import numpy as np

class ContentBasedRecommender:
    def __init__(self):
        self.products_df = loader.load_derived_products()
        self.ratings_df = loader.load_ratings()
        self.tfidf_matrix = None
        self.vectorizer = None
        self._prepare_tfidf()

    def _prepare_tfidf(self):
        """Prepara a matriz TF-IDF das descrições dos produtos."""
        if self.products_df.empty:
            return
        
        # Preencher valores nulos
        self.products_df["descricao"] = self.products_df["descricao"].fillna("")
        
        self.vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.products_df["descricao"])

    def recommend(self, user_cpf: str, n_recommendations: int = 5):
        """
        Recomenda itens baseados no perfil de conteúdo do usuário.
        O perfil é construído a partir dos itens que o usuário avaliou bem (>3).
        """
        if self.products_df.empty or self.ratings_df.empty:
            return []

        # 1. Obter itens que o usuário gostou
        user_ratings = self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]
        liked_items = user_ratings[user_ratings["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
        
        if not liked_items:
            return []

        # 2. Criar perfil do usuário (média dos vetores dos itens que gostou)
        # Mapear descrições para índices
        product_indices = []
        for item_desc in liked_items:
            indices = self.products_df[self.products_df["descricao"] == item_desc].index.tolist()
            product_indices.extend(indices)
        
        if not product_indices:
            return []
            
        user_profile = np.asarray(self.tfidf_matrix[product_indices].mean(axis=0))

        # 3. Calcular similaridade com todos os itens
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix).flatten()

        # 4. Filtrar itens já vistos e blacklisted
        seen_items = user_ratings["descricao_produto"].unique()
        
        feedback_manager = FeedbackManager()
        # Nota: get_blacklisted_items retorna IDs, mas aqui estamos trabalhando com descrições/índices
        # Idealmente deveríamos trabalhar sempre com IDs. Vamos converter.
        blacklisted_ids = feedback_manager.get_blacklisted_items(user_cpf)
        blacklisted_descs = self.products_df[self.products_df["id"].isin(blacklisted_ids)]["descricao"].unique()
        
        # Criar lista de tuplas (índice, score)
        sim_scores = list(enumerate(cosine_sim))
        
        # Ordenar por similaridade
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        added_descriptions = set()
        
        for idx, score in sim_scores:
            item_desc = self.products_df.iloc[idx]["descricao"]
            item_id = self.products_df.iloc[idx]["id"]
            
            if item_desc in seen_items or item_desc in blacklisted_descs or item_desc in added_descriptions:
                continue
                
            recommendations.append({
                "id": item_id,
                "descricao": item_desc,
                "marca": self.products_df.iloc[idx]["marca"],
                "score": score
            })
            
            added_descriptions.add(item_desc)
            
            if len(recommendations) >= n_recommendations:
                break
                
        return recommendations

    def evaluate_metrics(self, user_cpf: str):
        """
        Avalia as métricas das recomendações para um usuário.
        """
        
        user_ratings = self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]
        if len(user_ratings) < 4:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": 10, "total_relevant": 0,
                "message": "Poucas avaliações."
            }
        train_data, test_data = train_test_split(user_ratings, test_size=0.5, random_state=42)
        train_liked_items = train_data[train_data["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
        
        if not train_liked_items:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": 10, "total_relevant": 0,
                "message": "Sem itens bem avaliados no treino."
            }
        product_indices = []
        for item_desc in train_liked_items:
            indices = self.products_df[self.products_df["descricao"] == item_desc].index.tolist()
            product_indices.extend(indices)
        
        if not product_indices:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": 10, "total_relevant": 0,
                "message": "Produtos não encontrados."
            }
            
        user_profile = np.asarray(self.tfidf_matrix[product_indices].mean(axis=0))
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix).flatten()
        train_items = train_data["descricao_produto"].unique()
        sim_scores = sorted(list(enumerate(cosine_sim)), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for idx, score in sim_scores:
            item_desc = self.products_df.iloc[idx]["descricao"]
            if item_desc in train_items:
                continue
            recommendations.append(item_desc)
            if len(recommendations) >= 10:
                break
        
        relevant_items = test_data[test_data["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
        return calculate_metrics(recommendations, relevant_items)