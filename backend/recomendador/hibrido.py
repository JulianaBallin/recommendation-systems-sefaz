import numpy as np
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.recomendador.feedback_manager import FeedbackManager
from backend.dataset import loader

class HybridRecommender:
    """
    Combina recomendação colaborativa e baseada em conteúdo.
    - Usa SVD++ como CF
    - Usa TF-IDF como Content
    - Produz explicações automáticas para cada item
    """

    def __init__(self, weight_cf: float = 0.6, weight_content: float = 0.4):
        self.weight_cf = weight_cf
        self.weight_content = weight_content

        # Dados base
        self.products_df = loader.load_derived_products()
        ratings_df = loader.load_ratings()

        # Ajustar id
        if "product_id" in ratings_df.columns:
            ratings_df = ratings_df.rename(columns={"product_id": "id"})

        self.ratings_df = ratings_df

        # Inicializar componentes
        self.content = ContentBasedRecommender()
        self.cf = CollaborativeFilteringRecommender(self.ratings_df)
        self.cf.train("svd")

        self.feedback = FeedbackManager()


    def recommend(self, user_cpf: str, n_recs: int = 5):
        """
        Retorna recomendações híbridas com explicações.
        """
        # 1) Content-based
        content_recs = self.content.recommend(user_cpf, n_recs * 3)
        content_scores = {r["id"]: float(r["score"]) for r in content_recs}

        # 2) Colaborativo
        cf_recs = self.cf.recommend_items(user_cpf, n_recs * 3)
        cf_scores = {r["id"]: float(r["score"]) for r in cf_recs}

        # 3) Blacklist + vistos
        seen_items = set(self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]["id"])
        blacklisted = set(self.feedback.get_blacklisted_items(user_cpf))

        # 4) Combinação de scores
        all_ids = set(content_scores.keys()) | set(cf_scores.keys())

        final = []

        for pid in all_ids:

            # Não recomendar itens vistos ou bloqueados
            if pid in seen_items or pid in blacklisted:
                continue

            score_ct = content_scores.get(pid, 0)
            score_cf = cf_scores.get(pid, 0)

            final_score = self.weight_cf * score_cf + self.weight_content * score_ct

            # Criar explicação automática
            if score_cf > 0 and score_ct > 0:
                explanation = "Recomendado por similaridade de conteúdo e por usuários semelhantes."
            elif score_cf > 0:
                explanation = "Recomendado com base no comportamento de usuários semelhantes (CF)."
            else:
                explanation = "Recomendado por similaridade com itens que você avaliou bem (conteúdo)."

            # Detalhes do produto
            row = self.products_df[self.products_df["id"] == pid]
            if not row.empty:
                descricao = row.iloc[0]["descricao"]
                marca = row.iloc[0]["marca"]
            else:
                descricao = str(pid)
                marca = "Desconhecida"

            final.append({
                "id": pid,
                "descricao": descricao,
                "marca": marca,
                "score": round(float(final_score), 4),
                "explanation": explanation,
            })

        # Ordenar e limitar
        final = sorted(final, key=lambda r: r["score"], reverse=True)

        return final[:n_recs]
