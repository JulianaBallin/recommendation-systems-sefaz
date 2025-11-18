import pandas as pd

from backend.utilitarios.validadores import (
    limpar_cpf,
    limpar_nome,
    limpar_data,
    validar_cpf,
)


def processar_csv_usuarios(df: pd.DataFrame, cpfs_existentes: set):
    erros = []
    validos = []
    cpfs_arquivo = set()

    for _, row in df.iterrows():
        cpf_raw = row.get("cpf", "")
        nome_raw = row.get("nome", "")
        data_raw = row.get("datanasc", "")

        cpf = limpar_cpf(cpf_raw)
        nome = limpar_nome(nome_raw)
        data = limpar_data(data_raw)

        linha_erros = []

        if not validar_cpf(cpf):
            linha_erros.append("CPF inválido")

        if cpf in cpfs_existentes:
            linha_erros.append("CPF já existe no banco")

        if cpf in cpfs_arquivo:
            linha_erros.append("CPF duplicado no arquivo")

        if len(nome) < 2:
            linha_erros.append("Nome inválido")

        if data == "":
            linha_erros.append("Data inválida")

        if linha_erros:
            erros.append({
                "cpf": cpf_raw,
                "nome": nome_raw,
                "datanasc": data_raw,
                "erros": "; ".join(linha_erros)
            })
        else:
            validos.append({
                "cpf": cpf,
                "nome": nome,
                "datanasc": data
            })
            cpfs_arquivo.add(cpf)

    return pd.DataFrame(validos), pd.DataFrame(erros)
