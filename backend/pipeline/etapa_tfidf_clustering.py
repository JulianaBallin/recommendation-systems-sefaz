import pandas as pd
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf


def executar_etapa_tfidf_clustering(df_padronizado: pd.DataFrame) -> None:
    processar_comparacao_tf_idf(df_padronizado)
