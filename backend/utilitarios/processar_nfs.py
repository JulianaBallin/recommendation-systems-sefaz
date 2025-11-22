import pandas as pd
import unicodedata
import re

def limpar_texto(txt: str) -> str:
    if not isinstance(txt, str):
        return ""
    # remove acentos
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    # remove caracteres inúteis
    txt = re.sub(r"[^a-zA-Z0-9\s.,-]", " ", txt)
    # padroniza espaços
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip().lower()


from backend.utilitarios.limpeza_dados import limpar_descricao
from backend.utilitarios.utilitarios_dicionarios import detectar_marca

def processar_csv_nfs(df: pd.DataFrame, nfs_existentes: set):
    erros = []
    validos = []

    # verificar se tem as colunas certas
    if "descricao" not in df.columns:
        raise ValueError("CSV deve conter a coluna: descricao")

    for _, row in df.iterrows():
        raw_desc = row["descricao"]

        # 1. Limpeza
        desc = limpar_descricao(str(raw_desc))

        # 2. Detectar marca
        marca = detectar_marca(desc)

        linha_erros = []

        if len(desc) < 3:
            linha_erros.append("Descrição inválida (muito curta)")

        # chave única simples para evitar duplicatas exatas
        chave_ident = desc

        if chave_ident in nfs_existentes:
            linha_erros.append("Linha já existe no banco")

        if linha_erros:
            erros.append({
                "descricao": raw_desc,
                "erros": "; ".join(linha_erros)
            })
        else:
            validos.append({
                "descricao": desc,
                "marca": marca
            })

    return pd.DataFrame(validos), pd.DataFrame(erros)
