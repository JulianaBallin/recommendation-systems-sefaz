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
    - Remover medidas (g, kg, ml, l)
    - Remover palavras de ruído (vacuo, trad, pet, etc)
    - Remover acentos
    - Substituir underscores por espaços
    - Normalizar para minúsculas
    """
    if not isinstance(descricao, str):
        return ""

    # 0. Lowercase
    descricao = descricao.lower()

    # 1. Remover acentos
    descricao = remover_acentos(descricao)

    # 2. Substituir underscores e hifens por espaços
    descricao = descricao.replace("_", " ").replace("-", " ")

    # 3. Remover medidas (ex: 500g, 1kg, 2l, 900ml)
    # \b garante que é palavra inteira ou final de palavra
    descricao = re.sub(r'\b\d+\s*(g|kg|ml|l|gr)\b', '', descricao)

    # 4. Remover palavras de ruído
    noise_words = ["vacuo", "trad", "pet", "cx", "un", "bar", "original", "tp", "emb", "promo", "pct", "ref", "liq"]
    for word in noise_words:
        descricao = re.sub(r'\b' + word + r'\b', '', descricao)

    # 5. Manter apenas letras, números e espaços
    descricao = re.sub(r"[^a-z0-9\s]", " ", descricao)

    # 6. Remover espaços duplicados
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
