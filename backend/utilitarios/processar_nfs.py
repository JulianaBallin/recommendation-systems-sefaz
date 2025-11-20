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


def processar_csv_nfs(df: pd.DataFrame, nfs_existentes: set):
    erros = []
    validos = []

    # verificar se tem as colunas certas
    if "DESCRICAO" not in df.columns or "SUPERMERCADO" not in df.columns:
        raise ValueError("CSV deve conter as colunas: DESCRICAO e SUPERMERCADO")

    for _, row in df.iterrows():
        raw_desc = row["DESCRICAO"]
        raw_super = row["SUPERMERCADO"]

        desc = limpar_texto(str(raw_desc))
        superm = limpar_texto(str(raw_super))

        linha_erros = []

        if len(desc) < 3:
            linha_erros.append("Descrição inválida")

        if len(superm) < 3:
            linha_erros.append("Supermercado inválido")

        chave_ident = desc + "|" + superm

        if chave_ident in nfs_existentes:
            linha_erros.append("Linha já existe no banco")

        if linha_erros:
            erros.append({
                "descricao": raw_desc,
                "supermercado": raw_super,
                "erros": "; ".join(linha_erros)
            })
        else:
            validos.append({
                "descricao": desc,
                "supermercado": superm
            })

    return pd.DataFrame(validos), pd.DataFrame(erros)
