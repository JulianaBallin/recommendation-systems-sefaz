import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.dataset import loader
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.feedback_manager import FeedbackManager

def verify_recommendations():
    print("=== Verificação do Sistema de Recomendação ===")
    
    # 1. Setup
    clients = loader.load_raw_clients()
    if clients.empty:
        print("ERRO: Sem clientes.")
        return
    
    user_cpf = clients.iloc[0]["cpf"]
    print(f"Usuário de teste: {clients.iloc[0]['nome']} ({user_cpf})")
    
    ratings = loader.load_ratings()
    
    # 2. Teste Colaborativo (Item-based)
    print("\n--- Teste Colaborativo (Item-based) ---")
    recommender = CollaborativeFilteringRecommender(ratings)
    recommender.train(algo_type="item_knn")
    recs = recommender.recommend_items(user_cpf, n_recommendations=5)
    
    if not recs:
        print("Nenhuma recomendação gerada.")
    else:
        print(f"Geradas {len(recs)} recomendações.")
        first_rec_id = recs[0]['id']
        print(f"Primeira recomendação: {first_rec_id}")
        
        # 3. Teste de Feedback Negativo
        print("\n--- Teste de Feedback Negativo ---")
        feedback_manager = FeedbackManager()
        print(f"Adicionando dislike para o item {first_rec_id}...")
        feedback_manager.add_feedback(user_cpf, first_rec_id, "dislike")
        
        # Verificar blacklist
        blacklist = feedback_manager.get_blacklisted_items(user_cpf)
        print(f"Itens na blacklist: {len(blacklist)}")
        if first_rec_id in blacklist:
            print("SUCESSO: Item negativado está na blacklist.")
        else:
            print("FALHA: Item negativado NÃO está na blacklist.")
            
        # 4. Gerar recomendações novamente e verificar se o item sumiu
        print("\n--- Regenerando Recomendações ---")
        recs_new = recommender.recommend_items(user_cpf, n_recommendations=5)
        rec_ids_new = [r['id'] for r in recs_new]
        
        if first_rec_id not in rec_ids_new:
            print("SUCESSO: Item negativado foi removido das recomendações.")
        else:
            print("FALHA: Item negativado AINDA aparece nas recomendações.")

    # 5. Teste Baseado em Conteúdo
    print("\n--- Teste Baseado em Conteúdo ---")
    content_rec = ContentBasedRecommender()
    c_recs = content_rec.recommend(user_cpf, n_recommendations=5)
    print(f"Geradas {len(c_recs)} recomendações baseadas em conteúdo.")
    
    # Limpar feedback de teste
    # (Opcional, mas bom para não sujar o banco se for persistente)
    
if __name__ == "__main__":
    verify_recommendations()
