"""
limpeza_dados.py
Responsável por aplicar regras de validação e limpeza aos arquivos CSV
antes da inserção no banco de dados SQLite do sistema AmazIA.

Cada função de limpeza recebe um DataFrame e retorna uma versão validada
com apenas os registros aceitos.
"""

import pandas as pd
import unicodedata

from backend.utilitarios.validacao_dados import (
    validar_cpf,
    validar_nome,
    validar_data_nascimento,
    validar_genero,
    validar_cep_manaus,
    validar_cnpj,
    validar_texto_simples,
    validar_descricao,
    validar_preco,
    validar_timestamp,
    validar_nota_avaliacao
)
from frontend.streamlit_app.modules.ui_messages import (
    show_success,
    show_error,
    show_warning,
)

# ============================================================
# 🔹 Funções auxiliares gerais
# ============================================================

def _normalizar_texto(texto: str) -> str:
    """
    Remove acentuação, converte para minúsculas e remove espaços extras.
    Exemplo: 'Ypê' -> 'ype'
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def _limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas totalmente vazias e espaços extras nas colunas.
    """
    df = df.dropna(how="all")
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def _contar_invalidos(total: int, validos: int, nome_tabela: str):
    """Exibe resumo visual no Streamlit após validação."""
    if total == 0:
        show_warning(f"Nenhum registro encontrado em {nome_tabela}.")
    elif validos == total:
        show_success(f"Todos os {total} registros de {nome_tabela} são válidos ✅")
    elif validos == 0:
        show_error(f"Nenhum registro válido encontrado em {nome_tabela}. 🚨")
    else:
        show_warning(
            f"{validos}/{total} registros válidos em {nome_tabela}. "
            f"As linhas inválidas foram descartadas ⚠️"
        )

# ============================================================
# 🔸 Limpeza e validação por tabela
# ============================================================

def limpar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela CLIENTES:
    - CPF válido e único
    - Nome sem caracteres inválidos
    - Data de nascimento válida
    - Gênero (F, M ou O)
    - CEP pertencente a Manaus-AM
    """
    df = _limpar_dataframe(df)
    total = len(df)

    df_validos = df[
        df["Cpf"].apply(validar_cpf)
        & df["Nome"].apply(validar_nome)
        & df["DataNasc"].apply(validar_data_nascimento)
        & df["Genero"].apply(validar_genero)
        & df["Cep"].apply(validar_cep_manaus)
    ]

    validos = len(df_validos)
    _contar_invalidos(total, validos, "CLIENTES")
    return df_validos


def limpar_supermercados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela SUPERMERCADOS:
    - CNPJ válido
    - CEP válido para Manaus
    - Nome não vazio
    """
    df = _limpar_dataframe(df)
    total = len(df)

    df_validos = df[
        df["Cnpj"].apply(validar_cnpj)
        & df["Cep"].apply(validar_cep_manaus)
        & df["Nome"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0)
    ]

    validos = len(df_validos)
    _contar_invalidos(total, validos, "SUPERMERCADOS")
    return df_validos


def limpar_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela CATEGORIA:
    - Descricao_Categoria apenas texto
    - Remove duplicatas ignorando acentos e capitalização
    """
    df = _limpar_dataframe(df)
    total = len(df)

    # Normaliza texto
    df["Descricao_Categoria_Normalizada"] = df["Descricao_Categoria"].apply(_normalizar_texto)

    df_validos = (
        df[df["Descricao_Categoria_Normalizada"].apply(validar_texto_simples)]
        .drop_duplicates(subset=["Descricao_Categoria_Normalizada"], keep="first")
        .drop(columns=["Descricao_Categoria_Normalizada"])
    )

    validos = len(df_validos)
    _contar_invalidos(total, validos, "CATEGORIA")
    return df_validos


def limpar_marcas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela MARCA:
    - Descricao_Marca apenas texto
    - Remove duplicatas ignorando acentos e capitalização
    """
    df = _limpar_dataframe(df)
    total = len(df)

    df["Descricao_Marca_Normalizada"] = df["Descricao_Marca"].apply(_normalizar_texto)

    df_validos = (
        df[df["Descricao_Marca_Normalizada"].apply(validar_texto_simples)]
        .drop_duplicates(subset=["Descricao_Marca_Normalizada"], keep="first")
        .drop(columns=["Descricao_Marca_Normalizada"])
    )

    validos = len(df_validos)
    _contar_invalidos(total, validos, "MARCA")
    return df_validos



def limpar_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela PRODUTOS:
    - Descricao_Produto válida (<= 150 caracteres)
    - Remove duplicatas de descrição ignorando acentuação e capitalização
    """
    df = _limpar_dataframe(df)
    total = len(df)

    # Normaliza texto
    df["Descricao_Normalizada"] = df["Descricao_Produto"].apply(_normalizar_texto)

    df_validos = (
        df[df["Descricao_Normalizada"].apply(validar_descricao)]
        .drop_duplicates(subset=["Descricao_Normalizada"], keep="first")
        .drop(columns=["Descricao_Normalizada"])
    )

    validos = len(df_validos)
    _contar_invalidos(total, validos, "PRODUTOS")
    return df_validos


def limpar_nfs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela NFS:
    - Id_Supermercado e Id_Produto não nulos
    - Preço real positivo
    - Timestamp válido
    """
    df = _limpar_dataframe(df)
    total = len(df)

    df_validos = df[
        df["Id_Supermercado"].notna()
        & df["Id_Produto"].apply(lambda x: str(x).isdigit())
        & df["Preco"].apply(validar_preco)
        & df["TimeStamp_Registro"].apply(validar_timestamp)
    ]

    validos = len(df_validos)
    _contar_invalidos(total, validos, "NFS")
    return df_validos


def limpar_avaliacoes_busca(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida os dados da tabela AVALIACOES_BUSCA:
    - CPF do cliente válido
    - Notas entre 0 e 5 ou None
    """
    df = _limpar_dataframe(df)
    total = len(df)

    colunas_nota = [
        "Avaliacao_Categoria",
        "Avaliacao_Marca",
        "Avaliacao_Produto",
        "Avaliacao_Supermercado",
    ]

    condicoes = df["Cpf_Cliente"].apply(validar_cpf)
    for col in colunas_nota:
        condicoes &= df[col].apply(validar_nota_avaliacao)

    df_validos = df[condicoes]
    validos = len(df_validos)
    _contar_invalidos(total, validos, "AVALIACOES_BUSCA")
    return df_validos
