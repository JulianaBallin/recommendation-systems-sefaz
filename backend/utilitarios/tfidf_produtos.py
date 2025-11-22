import os
import hashlib
import pandas as pd

from backend.service.produtos_base_service import garantir_produto_base_para_descricao

STANDARDIZED_PATH = "dataset/standardized/produtos_padronizados.csv"


def gerar_id_deterministic(descricao_padronizada: str, marca: str) -> str:
    """
    Gera ID determinístico baseado em hash SHA-256 da descrição + marca.
    
    Args:
        descricao_padronizada: Descrição limpa e padronizada
        marca: Marca do produto
        
    Returns:
        ID de 16 caracteres hexadecimais
    """
    chave = f"{descricao_padronizada}|{marca}".lower()
    hash_obj = hashlib.sha256(chave.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def registrar_standardized(id_produto: str, descricao_pad: str, marca: str) -> None:
    """
    Registra produto em produtos_padronizados.csv, evitando duplicatas.
    
    Args:
        id_produto: ID determinístico do produto
        descricao_pad: Descrição padronizada
        marca: Marca do produto
    """
    os.makedirs(os.path.dirname(STANDARDIZED_PATH), exist_ok=True)

    if os.path.exists(STANDARDIZED_PATH):
        df_existing = pd.read_csv(STANDARDIZED_PATH)
        
        # Verificar se já existe por ID (evita duplicatas)
        if id_produto in df_existing['id'].values:
            return  # Já registrado, não adicionar
        
        # Adicionar novo registro
        df_existing.loc[len(df_existing)] = [id_produto, descricao_pad, marca]
        df_existing.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")
    else:
        # Criar novo arquivo
        df = pd.DataFrame([[id_produto, descricao_pad, marca]], 
                          columns=["id", "descricao", "marca"])
        df.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")


def filtrar_nfs_novas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna apenas produtos que ainda não foram processados.
    Compara com descrições em produtos_padronizados.csv.
    
    Args:
        df: DataFrame com coluna 'descricao'
        
    Returns:
        DataFrame apenas com novas descrições
    """
    if not os.path.exists(STANDARDIZED_PATH):
        return df
    
    try:
        df_std = pd.read_csv(STANDARDIZED_PATH)
        if 'descricao' not in df_std.columns:
            return df
            
        # Criar conjunto de descrições existentes (lowercase para comparação)
        descricoes_existentes = set(df_std['descricao'].str.lower())
        
        # Filtrar apenas novas (case-insensitive)
        mask = ~df['descricao'].str.lower().isin(descricoes_existentes)
        df_novas = df[mask].copy()
        
        return df_novas
    except Exception:
        # Em caso de erro, processar tudo
        return df


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
    Processa produtos com clustering TF-IDF, gerando IDs determinísticos.
    
    Args:
        df: DataFrame com colunas 'descricao' e 'marca'
    """
    mapa_ids = carregar_mapa_ids()

    for _, row in df.iterrows():
        descricao_original = row.get("descricao", "")
        marca = row.get("marca", "generico")

        # Obter descrição padronizada via clustering
        descricao_padronizada = garantir_produto_base_para_descricao(
            descricao=descricao_original,
            marca=marca
        )

        # Gerar ID determinístico (hash da descrição + marca)
        id_produto = gerar_id_deterministic(descricao_padronizada, marca)
        
        # Registrar (com deduplicação automática)
        registrar_standardized(
            id_produto=id_produto,
            descricao_pad=descricao_padronizada,
            marca=marca
        )

