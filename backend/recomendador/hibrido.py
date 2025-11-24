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

        # Validar pesos
        if abs(weight_cf + weight_content - 1.0) > 0.01:
            raise ValueError("Pesos devem somar 1.0")

        # Dados base
        self.products_df = loader.load_derived_products()
        ratings_df = loader.load_ratings()

        # Ajustar id
        if "product_id" in ratings_df.columns:
            ratings_df = ratings_df.rename(columns={"product_id": "id"})

        self.ratings_df = ratings_df

        # Otimização: criar lookup dictionary
        self._build_product_lookup()

        # Inicializar componentes
        self.content = ContentBasedRecommender()
        self.cf = CollaborativeFilteringRecommender(self.ratings_df)
        self.cf.train("svd")

        self.feedback = FeedbackManager()

        # Calibrar escala do CF
        self.cf_score_range = self._get_cf_score_range()

    def _build_product_lookup(self):
        """Cria dicionário para busca eficiente de produtos"""
        self.product_lookup = {}
        for _, row in self.products_df.iterrows():
            self.product_lookup[row["id"]] = {
                "descricao": row.get("descricao", ""),
                "marca": row.get("marca", "Desconhecida")
            }

    def _get_cf_score_range(self):
        """Determina a escala real dos scores do CF"""
        try:
            # Amostrar alguns usuários para descobrir a escala
            sample_users = self.ratings_df["cpf"].astype(str).unique()[:10]
            all_scores = []
            
            for user in sample_users:
                try:
                    recs = self.cf.recommend_items(user, 10)
                    all_scores.extend([r["score"] for r in recs if r["score"] is not None])
                except:
                    continue
            
            if not all_scores:
                return (1, 5)  # fallback para escala esperada
                
            return min(all_scores), max(all_scores)
        except:
            return (1, 5)  # fallback conservador

    def _normalize_cf_score(self, score):
        """Normaliza score do CF para 0-1 de forma robusta"""
        if score is None or score == 0:
            return 0
        
        # Se o score já estiver entre 0-1, retorna como está
        if 0 <= score <= 1:
            return score
        
        # Se estiver entre 1-5, normaliza
        if 1 <= score <= 5:
            return (score - 1) / 4
        
        # Para outros casos, usa clamp
        return max(0, min(1, score))

    def recommend(self, user_cpf: str, n_recs: int = 5):
        """
        Retorna recomendações híbridas com explicações.
        """
        user_cpf = str(user_cpf)
        
        try:
            # 1) Content-based
            content_recs = self.content.recommend(user_cpf, n_recs * 3)
            content_scores = {r["id"]: float(r["score"]) for r in content_recs}
        except Exception as e:
            print(f"Content-based failed: {e}")
            content_scores = {}

        try:
            # 2) Colaborativo
            cf_recs = self.cf.recommend_items(user_cpf, n_recs * 3)
            cf_scores = {r["id"]: float(r["score"]) for r in cf_recs}
        except Exception as e:
            print(f"CF failed: {e}")
            cf_scores = {}

        # Fallback se ambos falharem
        if not content_scores and not cf_scores:
            return self._get_fallback_recommendations(user_cpf, n_recs)

        # 3) Blacklist + vistos
        seen_items = set(self.ratings_df[self.ratings_df["cpf"].astype(str) == user_cpf]["id"])
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

            # Normalização
            score_cf_norm = self._normalize_cf_score(score_cf)
            score_ct_norm = max(0, min(1, score_ct))

            final_score = (
                self.weight_cf * score_cf_norm +
                self.weight_content * score_ct_norm
            )

            # Criar explicação automática usando scores NORMALIZADOS
            if score_cf_norm > 0.1 and score_ct_norm > 0.1:
                explanation = "Recomendado por similaridade de conteúdo e usuários semelhantes."
            elif score_cf_norm > 0.1:
                explanation = "Recomendado com base em padrões de compra de usuários com gostos parecidos com o seu."
            elif score_ct_norm > 0.1:
                explanation = "Recomendado por similaridade com itens que você avaliou bem."
            else:
                explanation = "Recomendação baseada em popularidade."

            # Detalhes do produto
            product_info = self.product_lookup.get(pid, {
                "descricao": str(pid),
                "marca": "Desconhecida"
            })

            final.append({
                "id": pid,
                "descricao": product_info["descricao"],
                "marca": product_info["marca"],
                "score": round(float(final_score), 4),
                "explanation": explanation,
                "components": {  # Debug info
                    "cf_score": round(score_cf_norm, 4),
                    "content_score": round(score_ct_norm, 4)
                }
            })

        # Ordenar e limitar
        final = sorted(final, key=lambda r: r["score"], reverse=True)

        return final[:n_recs]

    def _get_fallback_recommendations(self, user_cpf: str, n_recs: int):
        """Fallback: produtos populares não vistos"""
        user_cpf = str(user_cpf)
        
        # Calcular popularidade (média de avaliações)
        product_ratings = self.ratings_df.groupby("id")["avaliacao_descricao"].mean()
        popular_products = product_ratings.sort_values(ascending=False).head(n_recs * 2)
        
        seen_items = set(self.ratings_df[
            self.ratings_df["cpf"].astype(str) == user_cpf
        ]["id"])
        
        blacklisted = set(self.feedback.get_blacklisted_items(user_cpf))
        
        recommendations = []
        for pid, score in popular_products.items():
            if pid in seen_items or pid in blacklisted:
                continue
                
            product_info = self.product_lookup.get(pid, {
                "descricao": str(pid),
                "marca": "Desconhecida"
            })
            
            # Normalizar score de popularidade para 0-1
            pop_score_norm = (score - 1) / 4 if score > 1 else 0
            
            recommendations.append({
                "id": pid,
                "descricao": product_info["descricao"],
                "marca": product_info["marca"],
                "score": round(float(pop_score_norm), 4),
                "explanation": "Produto popular entre todos os usuários.",
                "fallback": True
            })
            
            if len(recommendations) >= n_recs:
                break
                
        return recommendations

    def evaluate_metrics(self, user_cpf: str, k: int = 10):
        """
        Avalia métricas para o recomendador híbrido.
        
        Args:
            user_cpf: CPF do usuário
            k: Número de recomendações a gerar para avaliação
        """
        try:
            # Gerar recomendações híbridas
            recommendations = self.recommend(user_cpf, k)
            rec_ids = [str(rec["id"]) for rec in recommendations]
            
            # Obter itens relevantes (avaliações >= 3)
            user_ratings = self.ratings_df[self.ratings_df["cpf"].astype(str) == str(user_cpf)]
            if user_ratings.empty:
                return {
                    "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                    "hits": 0, "total_recommended": k, "total_relevant": 0,
                    "message": "Usuário sem avaliações para cálculo de métricas."
                }
            
            relevant_items = user_ratings[user_ratings["avaliacao_descricao"] >= 3]["id"].tolist()
            relevant_items = [str(item) for item in relevant_items]
            
            # Calcular métricas
            from backend.recomendador.metricas import calculate_metrics
            metrics = calculate_metrics(rec_ids, relevant_items)
            
            return metrics
            
        except Exception as e:
            return {
                "precision_at_k": 0, "recall_at_k": 0, "f1_score": 0,
                "hits": 0, "total_recommended": k, "total_relevant": 0,
                "message": f"Erro na avaliação híbrida: {str(e)}"
            }