import re
import unicodedata

def remover_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto_norm = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in texto_norm if not unicodedata.combining(c)])


def limpar_descricao(descricao: str) -> str:
    if not isinstance(descricao, str):
        return ""

    descricao = descricao.lower()
    descricao = remover_acentos(descricao)
    descricao = descricao.replace("_", " ").replace("-", " ")

    descricao = re.sub(r'\b\d+\s*(g|kg|ml|l|gr|un|rl)\b', '', descricao)

    noise_words = [
        "vacuo","trad","pet","cx","un","bar","original","tp","emb","promo","pct",
        "ref","liq","rl","rolos","embal","gr","g","ml","l","kg","un"
    ]

    for w in noise_words:
        descricao = re.sub(rf'\b{w}\b', '', descricao)

    descricao = re.sub(r"[^a-z0-9\s]", " ", descricao)
    descricao = re.sub(r"\s+", " ", descricao).strip()
    descricao = expandir_abreviacoes(descricao)

    return descricao


def expandir_abreviacoes(texto: str) -> str:
    if not isinstance(texto, str):
        return ""

    abrevs = {
        "t": "tio",
        "tio": "tio",
        "tjoao": "tio joao",
        "joao": "joao",
        "carc": "carioca",
        "far": "farinha",
        "lac": "lactea",
        "lact": "lactea",
        "frang": "frango",
        "perd": "perdigao",
        "cong": "congelado",
        "iog": "iogurte",
        "nestl": "nestle",
        "mor": "morango",
        "mac": "macarrao",
        "rnt": "renata",
        "esp": "espaguete",
        "ph": "papel higienico",
        "hig": "higienico",
        "sab": "sabonete",
        "dov": "dove",
        "achoc": "achocolatado",
        "qjo": "queijo",
        "mus": "mussarela",
        "muss": "mussarela",
        "fat": "fatiado",
        "int": "integral",
        "rosq": "rosquinha",
        "lim": "limao",
        "ref": "refrigerante",
        "refrig": "refrigerante",
        "calab": "calabresa",
        "acuc": "acucar",
        "h": "higienico",
        "dent": "dental",
    }

    palavras = texto.split()
    palavras_exp = [abrevs.get(p, p) for p in palavras]
    return " ".join(palavras_exp)



def limpar_supermercado(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto = remover_acentos(texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto
