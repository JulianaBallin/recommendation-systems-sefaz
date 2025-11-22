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
        
        # Usar product_id se disponível, senão fallback para descricao (mas agora deve ter product_id)
        if "product_id" in user_ratings.columns:
            liked_items = user_ratings[user_ratings["avaliacao_descricao"] >= 4]["product_id"].tolist()
            seen_items = user_ratings["product_id"].unique()
        else:
            # Fallback legado (caso o loader não tenha atualizado ou arquivo antigo)
            liked_items = user_ratings[user_ratings["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
            seen_items = user_ratings["descricao_produto"].unique()
        
        if not liked_items:
            return []

        # 2. Criar perfil do usuário (média dos vetores dos itens que gostou)
        # Mapear IDs para índices
        product_indices = []
        
        if "product_id" in user_ratings.columns:
            # Filtrar produtos que estão no dataframe de produtos
            valid_liked_items = [pid for pid in liked_items if pid in self.products_df["id"].values]
            for pid in valid_liked_items:
                indices = self.products_df[self.products_df["id"] == pid].index.tolist()
                product_indices.extend(indices)
        else:
            for item_desc in liked_items:
                indices = self.products_df[self.products_df["descricao"] == item_desc].index.tolist()
                product_indices.extend(indices)
        
        if not product_indices:
            return []
            
        user_profile = np.asarray(self.tfidf_matrix[product_indices].mean(axis=0))

        # 3. Calcular similaridade com todos os itens
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix).flatten()

        # 4. Filtrar itens já vistos e blacklisted
        feedback_manager = FeedbackManager()
        blacklisted_ids = feedback_manager.get_blacklisted_items(user_cpf)
        
        # Criar lista de tuplas (índice, score)
        sim_scores = list(enumerate(cosine_sim))
        
        # Ordenar por similaridade
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        added_ids = set()
        
        for idx, score in sim_scores:
            item_id = self.products_df.iloc[idx]["id"]
            item_desc = self.products_df.iloc[idx]["descricao"]
            
            # Verificar se já viu (pelo ID ou descrição se legado)
            if "product_id" in user_ratings.columns:
                if item_id in seen_items or item_id in blacklisted_ids or item_id in added_ids:
                    continue
            else:
                if item_desc in seen_items or item_id in blacklisted_ids or item_id in added_ids:
                    continue
                
            recommendations.append({
                "id": item_id,
                "descricao": item_desc,
                "marca": self.products_df.iloc[idx]["marca"],
                "score": score
            })
            
            added_ids.add(item_id)
            
            if len(recommendations) >= n_recommendations:
                break
                
        return recommendations

    def evaluate_metrics(self, user_cpf: str, k: int = 10):
        """
        Avalia as métricas das recomendações para um usuário.
        
        Args:
            user_cpf: CPF do usuário
            k: Número de recomendações a gerar para avaliação (padrão: 10)
        """
        
        user_ratings = self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]
        if len(user_ratings) < 4:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": k, "total_relevant": 0,
                "message": "Poucas avaliações."
            }
        train_data, test_data = train_test_split(user_ratings, test_size=0.5, random_state=42)
        
        # Usar IDs para treino e teste
        if "product_id" in user_ratings.columns:
            train_liked_items = train_data[train_data["avaliacao_descricao"] >= 4]["product_id"].tolist()
            relevant_items = test_data[test_data["avaliacao_descricao"] >= 4]["product_id"].tolist()
        else:
            train_liked_items = train_data[train_data["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
            relevant_items = test_data[test_data["avaliacao_descricao"] >= 4]["descricao_produto"].tolist()
        
        if not train_liked_items:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": k, "total_relevant": 0,
                "message": "Sem itens bem avaliados no treino."
            }
            
        product_indices = []
        if "product_id" in user_ratings.columns:
            for pid in train_liked_items:
                indices = self.products_df[self.products_df["id"] == pid].index.tolist()
                product_indices.extend(indices)
        else:
            for item_desc in train_liked_items:
                indices = self.products_df[self.products_df["descricao"] == item_desc].index.tolist()
                product_indices.extend(indices)
        
        if not product_indices:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": k, "total_relevant": 0,
                "message": "Produtos não encontrados."
            }
            
        user_profile = np.asarray(self.tfidf_matrix[product_indices].mean(axis=0))
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix).flatten()
        
        # Itens de treino para excluir
        if "product_id" in user_ratings.columns:
            train_items = set(train_data["product_id"].unique())
        else:
            train_items = set(train_data["descricao_produto"].unique())
            
        sim_scores = sorted(list(enumerate(cosine_sim)), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for idx, score in sim_scores:
            if "product_id" in user_ratings.columns:
                item_val = self.products_df.iloc[idx]["id"]
            else:
                item_val = self.products_df.iloc[idx]["descricao"]
                
            if item_val in train_items:
                continue
            recommendations.append(str(item_val)) # Converter para string para comparação
            if len(recommendations) >= k:
                break
        
        relevant_items = [str(r) for r in relevant_items] # Converter para string
        return calculate_metrics(recommendations, relevant_items)