"""
Script de teste para verificar o parâmetro K dinâmico nas métricas.
"""

import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_dynamic_k():
    print("=" * 60)
    print("Testando Parâmetro K Dinâmico nas Métricas")
    print("=" * 60)
    
    # 1. Obter um usuário
    print("\n1. Obtendo usuários...")
    response = requests.get(f"{API_URL}/recomendacao/usuarios")
    if response.status_code != 200:
        print("❌ Erro ao carregar usuários")
        return
    
    users = response.json()
    if not users:
        print("❌ Nenhum usuário encontrado")
        return
    
    test_user = users[0]
    user_cpf = test_user['cpf']
    print(f"✅ Usuário de teste: {test_user['nome']} ({user_cpf})")
    
    # 2. Testar com diferentes valores de K
    test_cases = [3, 5, 7, 10]
    
    for k_value in test_cases:
        print(f"\n{'='*60}")
        print(f"Testando com K = {k_value}")
        print(f"{'='*60}")
        
        # Testar com filtragem colaborativa (item_knn)
        print(f"\n📊 Avaliando métricas com K={k_value}...")
        
        payload = {
            "user_cpf": str(user_cpf),
            "algo_type": "item_knn",
            "k": k_value
        }
        
        response = requests.post(f"{API_URL}/recomendacao/metricas", json=payload)
        
        if response.status_code == 200:
            metrics = response.json()
            
            if "message" in metrics:
                print(f"⚠️  {metrics['message']}")
            else:
                total_rec = metrics.get('total_recommended', 0)
                print(f"\n✅ Métricas calculadas com sucesso!")
                print(f"   Total Recomendado: {total_rec}")
                print(f"   Precision@{total_rec}: {metrics['precision_at_k']:.2%}")
                print(f"   Recall@{total_rec}: {metrics.get('recall_at_k', 0):.2%}")
                print(f"   F1-Score: {metrics.get('f1_score', 0):.2%}")
                print(f"   Hits: {metrics['hits']}")
                print(f"   Total Relevantes: {metrics.get('total_relevant', 0)}")
                
                # Verificar se K está correto
                if total_rec == k_value:
                    print(f"\n✅ SUCESSO: total_recommended = {k_value} (esperado)")
                else:
                    print(f"\n❌ FALHA: total_recommended = {total_rec}, esperado = {k_value}")
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   {response.text}")
    
    print(f"\n{'='*60}")
    print("Testes concluídos!")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        test_dynamic_k()
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
