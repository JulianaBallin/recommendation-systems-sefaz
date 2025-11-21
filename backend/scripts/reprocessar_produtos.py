import pandas as pd
import os
import shutil
import sys

# Adicionar diretório raiz ao path para importar módulos do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf

def reprocessar():
    print("🔄 Iniciando reprocessamento de produtos...")
    
    # Caminhos
    # Caminhos
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset"))
    nfs_path = os.path.join(dataset_dir, "processado/nfs_processadas.csv")
    standardized_path = os.path.join(dataset_dir, "standardized/produtos_padronizados.csv")
    base_dir = os.path.join(dataset_dir, "produtos_base")
    
    # 1. Limpar dados antigos
    if os.path.exists(standardized_path):
        os.remove(standardized_path)
        print(f"🗑️ Removido: {standardized_path}")
        
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
        print(f"🗑️ Limpo diretório: {base_dir}")
        
    # 2. Carregar NFS processadas
    if not os.path.exists(nfs_path):
        print(f"❌ Erro: Arquivo {nfs_path} não encontrado.")
        return
        
    df_nfs = pd.read_csv(nfs_path)
    print(f"📂 Carregadas {len(df_nfs)} notas fiscais.")
    
    if df_nfs.empty:
        print("⚠️ Aviso: Nenhuma nota fiscal para processar.")
        return
        
    # 3. Executar TF-IDF
    print("🚀 Executando padronização (TF-IDF)...")
    processar_comparacao_tf_idf(df_nfs)
    
    print("✅ Reprocessamento concluído com sucesso!")

if __name__ == "__main__":
    reprocessar()
