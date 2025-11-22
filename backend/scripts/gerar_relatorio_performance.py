import pandas as pd
import os
import time
from backend.recomendador.conteudo import ContentBasedRecommender
from backend.recomendador.colaborativo import CollaborativeFilteringRecommender
from backend.dataset import loader

REPORT_DIR = "dataset/reports"
REPORT_FILE = os.path.join(REPORT_DIR, "performance_report.csv")

def gerar_relatorio():
    print("📊 Iniciando geração de relatório de performance...\n")
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Carregar dados
    ratings = loader.load_ratings()
    if ratings.empty:
        print("❌ Sem avaliações para processar.")
        return

    # Filtrar usuários com pelo menos 5 avaliações (para ter split de treino/teste)
    user_counts = ratings["cpf"].value_counts()
    valid_users = user_counts[user_counts >= 5].index.tolist()
    
    print(f"👥 Usuários elegíveis (>= 5 avaliações): {len(valid_users)}")
    
    results = []
    
    # Instanciar recomendadores
    print("⚙️ Inicializando recomendadores...")
    content_rec = ContentBasedRecommender()
    
    collab_rec = CollaborativeFilteringRecommender(ratings)
    # Treinar SVD uma vez (pode demorar um pouco)
    print("   - Treinando SVD++...")
    collab_rec.train(algo_type="svd")
    
    total = len(valid_users)
    
    for i, cpf in enumerate(valid_users):
        cpf = str(cpf)
        print(f"[{i+1}/{total}] Processando CPF: {cpf}...", end="\r")
        
        # 1. Content-Based
        try:
            m_content = content_rec.evaluate_metrics(cpf, k=10)
            results.append({
                "cpf": cpf,
                "algorithm": "Content-Based",
                "precision": m_content.get("precision_at_k", 0),
                "recall": m_content.get("recall_at_k", 0),
                "f1": m_content.get("f1_score", 0),
                "hits": m_content.get("hits", 0)
            })
        except Exception as e:
            print(f"\n❌ Erro Content-Based para {cpf}: {e}")

        # 2. Collaborative (SVD++)
        try:
            m_collab = collab_rec.evaluate_metrics(cpf, k=10)
            results.append({
                "cpf": cpf,
                "algorithm": "SVD++",
                "precision": m_collab.get("precision_at_k", 0),
                "recall": m_collab.get("recall_at_k", 0),
                "f1": m_collab.get("f1_score", 0),
                "hits": m_collab.get("hits", 0)
            })
        except Exception as e:
            print(f"\n❌ Erro Collaborative para {cpf}: {e}")

    print("\n\n✅ Processamento concluído.")
    
    # Criar DataFrame
    df_results = pd.DataFrame(results)
    
    if df_results.empty:
        print("⚠️ Nenhum resultado gerado.")
        return

    # Salvar CSV detalhado
    df_results.to_csv(REPORT_FILE, index=False)
    print(f"💾 Relatório detalhado salvo em: {REPORT_FILE}")
    
    # Exibir resumo
    print("\n📈 RESUMO DE PERFORMANCE (Média Geral):")
    summary = df_results.groupby("algorithm")[["precision", "recall", "f1", "hits"]].mean()
    print(summary)
    
    # Salvar resumo
    summary.to_csv(os.path.join(REPORT_DIR, "performance_summary.csv"))

if __name__ == "__main__":
    gerar_relatorio()
