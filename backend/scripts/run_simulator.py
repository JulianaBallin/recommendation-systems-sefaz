import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.utilitarios.processamento import processar_nfs
from backend.utilitarios.tfidf_produtos import processar_comparacao_tf_idf
import pandas as pd


if __name__ == "__main__":
    # Passo 1: limpeza
    processar_nfs()

    # Passo 2: carrega processado
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset/processado/nfs_processadas.csv"))
    df = pd.read_csv(dataset_path)

    # Passo 3: TF-IDF
    processar_comparacao_tf_idf(df)
