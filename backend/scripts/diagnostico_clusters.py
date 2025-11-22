import os
import glob
from collections import defaultdict

BASE_DIR = "dataset/produtos_base"

def diagnostico_clusters():
    print("🔍 Iniciando diagnóstico de clusters...\n")
    
    if not os.path.exists(BASE_DIR):
        print(f"❌ Diretório {BASE_DIR} não encontrado.")
        return

    files = glob.glob(os.path.join(BASE_DIR, "*.txt"))
    
    if not files:
        print("⚠️ Nenhum arquivo de cluster encontrado.")
        return

    # Mapeamento: descricao -> lista de arquivos onde aparece
    global_map = defaultdict(list)
    
    # Contadores
    total_files = 0
    total_products = 0
    files_with_internal_dups = 0
    
    print(f"📂 Analisando {len(files)} arquivos de cluster...\n")

    for file_path in files:
        filename = os.path.basename(file_path)
        total_files += 1
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        total_products += len(lines)
        
        # 1. Verificar duplicatas internas
        seen = set()
        duplicates = set()
        for line in lines:
            if line in seen:
                duplicates.add(line)
            seen.add(line)
            
            # Adicionar ao mapa global
            global_map[line].append(filename)
            
        if duplicates:
            files_with_internal_dups += 1
            print(f"⚠️  Cluster '{filename}' tem duplicatas internas:")
            for d in duplicates:
                print(f"   - {d}")

    print("\n" + "="*50 + "\n")

    # 2. Verificar produtos espalhados (cross-cluster)
    scattered_products = {k: v for k, v in global_map.items() if len(set(v)) > 1}
    
    if scattered_products:
        print("🚨 ALERTA: Produtos espalhados em múltiplos clusters:\n")
        for prod, file_list in scattered_products.items():
            print(f"🔴 '{prod}' aparece em: {', '.join(set(file_list))}")
    else:
        print("✅ Nenhum produto espalhado entre clusters diferentes.")

    print("\n" + "="*50 + "\n")
    
    # Resumo
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print(f"   - Total de Clusters: {total_files}")
    print(f"   - Total de Produtos (descrições): {total_products}")
    print(f"   - Clusters com duplicatas internas: {files_with_internal_dups}")
    print(f"   - Produtos em múltiplos clusters: {len(scattered_products)}")
    
    if files_with_internal_dups == 0 and len(scattered_products) == 0:
        print("\n✅ DIAGNÓSTICO APROVADO: Clusters consistentes.")
    else:
        print("\n❌ DIAGNÓSTICO REPROVADO: Inconsistências encontradas.")

if __name__ == "__main__":
    diagnostico_clusters()
