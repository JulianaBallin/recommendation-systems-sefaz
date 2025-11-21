import re
from datetime import datetime

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r"[^0-9]", "", cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito

        if digito != int(cpf[i]):
            return False

    return True


def limpar_cpf(cpf: str) -> str:
    return re.sub(r"[^0-9]", "", str(cpf))


def limpar_nome(nome: str) -> str:
    nome = str(nome)
    nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", nome).strip()
    nome = re.sub(r"\s+", " ", nome)
    return nome.title()


def limpar_data(data: str) -> str:
    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]

    data = str(data).strip()

    for fmt in formatos:
        try:
            return datetime.strptime(data, fmt).strftime("%Y-%m-%d")
        except:
            pass

    return ""
