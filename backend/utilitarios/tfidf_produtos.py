import os
import uuid
import pandas as pd

from backend.service.produtos_base_service import garantir_produto_base_para_descricao

STANDARDIZED_PATH = "dataset/standardized/produtos_padronizados.csv"


def registrar_standardized(id_produto: str, descricao_pad: str, marca: str) -> None:
    os.makedirs(os.path.dirname(STANDARDIZED_PATH), exist_ok=True)

    if not os.path.exists(STANDARDIZED_PATH):
        df = pd.DataFrame(columns=["id", "descricao", "marca"])
        df.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")

    df = pd.read_csv(STANDARDIZED_PATH)

    df.loc[len(df)] = [id_produto, descricao_pad, marca]
    df.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")


def carregar_mapa_ids() -> dict:
    if not os.path.exists(STANDARDIZED_PATH):
        return {}
    try:
        df = pd.read_csv(STANDARDIZED_PATH)
        if "descricao" in df.columns and "id" in df.columns:
            return dict(zip(df["descricao"], df["id"]))
    except Exception:
        return {}
    return {}


def processar_comparacao_tf_idf(df: pd.DataFrame) -> None:
    """
    df com colunas: descricao, marca
    Faz a comparação incremental, atribui/gera IDs e registra em standardized.
    """
    mapa_ids = carregar_mapa_ids()

    for _, row in df.iterrows():
        descricao_original = row.get("descricao", "")
        marca = row.get("marca", "generico")

        descricao_padronizada = garantir_produto_base_para_descricao(
            descricao=descricao_original,
            marca=marca
        )

        if descricao_padronizada in mapa_ids:
            id_produto = mapa_ids[descricao_padronizada]
        else:
            id_produto = str(uuid.uuid4())
            mapa_ids[descricao_padronizada] = id_produto

        registrar_standardized(
            id_produto=id_produto,
            descricao_pad=descricao_padronizada,
            marca=marca
        )
