import pandas as pd
from backend.dataset import loader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FeedbackManager:
    def __init__(self):
        self.feedback_df = loader.load_feedback()
        self.products_df = loader.load_derived_products()

    def add_feedback(self, user_cpf, item_id, feedback_type):
        """
        Adiciona um feedback (like/dislike) para um usuário e item.
        feedback_type: 'like' ou 'dislike'
        """
        new_feedback = {
            "cpf": user_cpf,
            "item_id": item_id,
            "feedback": feedback_type,
            "timestamp": pd.Timestamp.now()
        }
        
        # 🔒 Validar ID: só aceitar produtos existentes
        valid_ids = self.products_df["id"].astype(str).tolist()

        if str(item_id) not in valid_ids:
            raise ValueError(f"ID inválido recebido no feedback: {item_id}")

        
        # Remove feedback anterior se existir
        self.feedback_df = self.feedback_df[
            ~((self.feedback_df["cpf"] == user_cpf) & (self.feedback_df["item_id"] == item_id))
        ]
        
        self.feedback_df = pd.concat([self.feedback_df, pd.DataFrame([new_feedback])], ignore_index=True)
        loader.save_feedback(self.feedback_df)

    def get_user_dislikes(self, user_cpf):
        """Retorna lista de IDs de produtos que o usuário deu dislike."""
        if self.feedback_df.empty:
            return []
        
        user_feedback = self.feedback_df[self.feedback_df["cpf"] == user_cpf]
        dislikes = user_feedback[user_feedback["feedback"] == "dislike"]["item_id"].tolist()
        return dislikes

    def get_blacklisted_items(self, user_cpf, similarity_threshold=0.7):
        """
        Retorna uma lista de itens que devem ser excluídos das recomendações
        com base nos dislikes do usuário e similaridade de conteúdo.
        """
        disliked_ids = self.get_user_dislikes(user_cpf)
        if not disliked_ids:
            return []

        # Filtrar produtos válidos
        valid_disliked_ids = [pid for pid in disliked_ids if pid in self.products_df["id"].values]
        if not valid_disliked_ids:
            return []

        # Preparar TF-IDF
        corpus = self.products_df["descricao"].fillna("").tolist()
        ids = self.products_df["id"].tolist()
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        blacklisted_ids = set(disliked_ids)
        
        # Para cada item negativado, encontrar similares
        for disliked_id in valid_disliked_ids:
            try:
                idx = ids.index(disliked_id)
                disliked_vec = tfidf_matrix[idx]
                
                # Calcular similaridade com todos os outros
                similarities = cosine_similarity(disliked_vec, tfidf_matrix).flatten()
                
                # Pegar índices com alta similaridade
                similar_indices = [i for i, sim in enumerate(similarities) if sim >= similarity_threshold]
                
                for i in similar_indices:
                    blacklisted_ids.add(ids[i])
            except ValueError:
                continue
                
        return list(blacklisted_ids)
