from .etapa_limpeza import executar_etapa_limpeza
from .etapa_padronizacao import executar_etapa_padronizacao
from .etapa_tfidf_clustering import executar_etapa_tfidf_clustering
from .etapa_standardizacao import executar_etapa_standardizacao


def executar_pipeline_completa():
    print("\nINICIANDO PIPELINE COMPLETA...\n")

    print("Etapa 1: Limpeza")
    df_limpo = executar_etapa_limpeza()
    print(f"✅ Descrições limpas: {len(df_limpo)}")

    print("\nEtapa 2: Padronização (marca)")
    df_padronizado = executar_etapa_padronizacao(df_limpo)
    print(f"✅ Produtos padronizados: {len(df_padronizado)}")

    print("\nEtapa 3: Clusterização TF-IDF (produtos_base/)")
    executar_etapa_tfidf_clustering(df_padronizado)
    print("✅ Clusterização concluída.")

    print("\nEtapa 4: Standardização final (IDs únicos)")
    df_standardizado = executar_etapa_standardizacao()
    total = len(df_standardizado) if df_standardizado is not None else 0
    print(f"✅ Produtos finalizados em standardized/: {total}")

    print("\nPIPELINE COMPLETA FINALIZADA!\n")
    return df_standardizado


if __name__ == "__main__":
    executar_pipeline_completa()
