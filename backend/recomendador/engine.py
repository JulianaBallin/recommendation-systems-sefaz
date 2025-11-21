import pandas as pd
from rapidfuzz import fuzz

def calcular_similaridade(descricao_ref, df_produtos, threshold=70):
    resultados = []

    for _, row in df_produtos.iterrows():
        score = fuzz.partial_ratio(descricao_ref, row["descricao"])

        if score >= threshold:
            resultados.append({
                "id": row["id"],
                "descricao": row["descricao"],
                "marca": row["marca"],
                "score": score
            })

    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)
    return resultados


def recomendar_por_cpf(cpf: str, top_k=5):
    # Carregar dados
    df_ratings = pd.read_csv("dataset/ratings/avaliacoes.csv")
    df_produtos = pd.read_csv("dataset/standardized/produtos_padronizados.csv")

    # Normalizar CPF
    df_ratings["cpf"] = df_ratings["cpf"].astype(str)

    # Criar coluna 'gostou' se não existir
    if "gostou" not in df_ratings.columns:
        df_ratings["gostou"] = df_ratings["avaliacao_descricao"].apply(lambda x: 1 if x >= 3 else 0)

    # Histórico do usuário
    historico = df_ratings[df_ratings["cpf"] == cpf]

    if historico.empty:
        return []

    # Produtos que ele gostou
    produtos_usuario = historico[historico["gostou"] == 1]["product_id"].unique()

    recomendacoes = []

    for pid in produtos_usuario:
        produto_ref = df_produtos[df_produtos["id"] == pid]

        if produto_ref.empty:
            continue

        descricao_ref = produto_ref.iloc[0]["descricao"]

        similares = calcular_similaridade(descricao_ref, df_produtos)

        recomendacoes.extend(similares)

    # Remover produtos que o usuário já consumiu
    recomendacoes = [r for r in recomendacoes if r["id"] not in produtos_usuario]

    # Remover duplicatas
    unique = {}
    for item in recomendacoes:
        unique[item["id"]] = item
    recomendacoes = list(unique.values())

    # Ordenar por score final
    recomendacoes = sorted(recomendacoes, key=lambda x: x["score"], reverse=True)

    return recomendacoes[:top_k]
