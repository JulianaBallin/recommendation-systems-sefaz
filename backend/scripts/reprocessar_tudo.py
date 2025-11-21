import os
import shutil
import pandas as pd
from backend.pipeline.rodar_pipeline import executar_pipeline_completa

STANDARD = "dataset/standardized/produtos_padronizados.csv"
RATINGS = "dataset/ratings/avaliacoes.csv"


def limpar_produtos():
    print("\n🧹 Limpando arquivos antigos de produtos...")

    pastas = [
        "dataset/produtos_base",
        "dataset/standardized",
        "dataset/processado/nfs_processadas.csv",
    ]

    for p in pastas:
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)

    os.makedirs("dataset/produtos_base", exist_ok=True)
    os.makedirs("dataset/standardized", exist_ok=True)
    print("✔ Produtos resetados.")


def atualizar_avaliacoes(df_antigo, df_novo):
    """
    Atualiza avaliacoes.csv com novos product_ids.
    Se não tiver product_id, cria a coluna.
    """

    if not os.path.exists(RATINGS):
        print("⚠️ Nenhum avaliacoes.csv encontrado. Ignorando atualização.")
        return

    print("🔄 Atualizando IDs de produtos em avaliacoes.csv...")

    df_ratings = pd.read_csv(RATINGS)

    # ============================================================
    # 1. Verificar se arquivo possui coluna product_id
    # ============================================================
    possui_id = "product_id" in df_ratings.columns

    # Criar mapa: descricao → novo_id
    mapa_novo = dict(zip(df_novo["descricao"], df_novo["id"]))

    if not possui_id:
        print("⚠️ avaliacoes.csv não possui coluna product_id — criando...")

        novos_ids = []
        nao_encontrados = 0

        for _, row in df_ratings.iterrows():
            desc = str(row.get("descricao_produto", "")).strip()

            # Tenta encontrar ID correspondente
            id_novo = mapa_novo.get(desc)

            if id_novo is None:
                nao_encontrados += 1
                novos_ids.append("NOT_FOUND")
            else:
                novos_ids.append(id_novo)

        df_ratings["product_id"] = novos_ids

        print(f"✔ IDs atribuídos. Não encontrados: {nao_encontrados}")

    else:
        # ============================================================
        # 2. Já existe product_id → fazer replace
        # ============================================================

        # criar mapa antigo_descricao -> novo_id
        mapa_antigo_para_novo = {}

        for _, row in df_antigo.iterrows():
            old_desc = row["descricao"]
            old_id = row["id"]

            # novo ID correspondente à mesma descrição atual
            if row["descricao"] in mapa_novo:
                mapa_antigo_para_novo[old_id] = mapa_novo[row["descricao"]]

        # replace
        df_ratings["product_id"] = df_ratings["product_id"].replace(mapa_antigo_para_novo)

        print("✔ IDs antigos substituídos pelos novos.")

    # Salvar
    df_ratings.to_csv(RATINGS, index=False)
    print("✔ avaliacoes.csv atualizado.")


def reprocessar_tudo():
    print("\n🚨 REPROCESSAMENTO COMPLETO INICIADO 🚨")

    # Carregar standardized antigo para mapear IDs
    df_antigo = pd.DataFrame()
    if os.path.exists(STANDARD):
        df_antigo = pd.read_csv(STANDARD)

    # 1. Limpeza
    limpar_produtos()

    # 2. Rodar pipeline completa
    df_novo = executar_pipeline_completa()

    # 3. Atualizar ratings
    if isinstance(df_novo, pd.DataFrame) and not df_novo.empty:
        atualizar_avaliacoes(df_antigo, df_novo)

    print("\n🎉 REPROCESSAMENTO FINALIZADO!")


if __name__ == "__main__":
    reprocessar_tudo()
