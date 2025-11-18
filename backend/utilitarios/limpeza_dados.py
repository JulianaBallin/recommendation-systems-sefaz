import re
import unicodedata
import pandas as pd
from datetime import datetime


def remover_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto_norm = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in texto_norm if not unicodedata.combining(c)])


def limpar_descricao(descricao: str) -> str:
    """
    Limpa descrições de produtos com base nas regras definidas:
    - Remover tudo após o primeiro número (peso, volume etc.)
    - Remover números restantes (caso fiquem)
    - Remover acentos
    - Remover caracteres especiais
    - Normalizar para minúsculas
    - Remover múltiplos espaços
    """
    if not isinstance(descricao, str):
        return ""

    # 1 — remover tudo após o primeiro número (peso, volume etc.)
    descricao = re.split(r"\d", descricao)[0]

    # 2 — remover acentos
    descricao = remover_acentos(descricao)

    # 3 — manter apenas letras e espaços
    descricao = re.sub(r"[^a-zA-Z\s]", " ", descricao)

    # 4 — caixa baixa
    descricao = descricao.lower()

    # 5 — remover espaços duplicados
    descricao = re.sub(r"\s+", " ", descricao).strip()

    return descricao


def limpar_supermercado(texto: str) -> str:
    """Remove acentos e padroniza o nome+endereço do supermercado."""
    if not isinstance(texto, str):
        return ""
    texto = remover_acentos(texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def descricao_base(descricao: str) -> str:
    """
    Normalização mínima generalizada:
    - Remove tokens irrelevantes (unidades, abreviações, ruído textual).
    - Mantém apenas as palavras que realmente identificam o produto.
    """
    if not isinstance(descricao, str):
        return ""

    palavras = descricao.split()

    # Tokens irrelevantes (geral para QUALQUER produto)
    stopwords = {
        "cx","pct","pc","un","po","bar","tp","lt","ml","kg","g","und","emb",
        "pack","promo","pct","ref","sab","liq"
    }

    filtrado = [
        p for p in palavras
        if p not in stopwords and len(p) > 1
    ]

    return " ".join(filtrado).strip()


def limpar_cpf(cpf: str) -> str:
    """Remove qualquer coisa que não seja número."""
    if not isinstance(cpf, str):
        return ""
    return re.sub(r"[^0-9]", "", cpf)


def limpar_nome(nome: str) -> str:
    """Remove caracteres inválidos do nome e normaliza espaços."""
    if not isinstance(nome, str):
        return ""

    nome = nome.strip()
    nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", nome)
    nome = re.sub(r"\s+", " ", nome)
    return nome.title()


def limpar_data(data: str) -> str:
    """
    Aceita formatos dd/mm/yyyy ou yyyy-mm-dd.
    Converte tudo para formato ISO: yyyy-mm-dd
    """
    if not isinstance(data, str):
        return ""

    data = data.strip()

    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]

    for fmt in formatos:
        try:
            dt = datetime.strptime(data, fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            pass

    return ""  # inválido
