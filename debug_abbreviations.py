from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import unicodedata

def remover_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto_norm = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in texto_norm if not unicodedata.combining(c)])

def expandir_abreviacoes(texto: str) -> str:
    # Dicionário de abreviações comuns em supermercados
    abrevs = {
        "far": "farinha",
        "lac": "lactea",
        "lact": "lactea",
        "frang": "frango",
        "perd": "perdigao",
        "cong": "congelado",
        "iog": "iogurte",
        "nestl": "nestle",
        "mor": "morango",
        "morang": "morango",
        "mac": "macarrao",
        "rnt": "renata",
        "esp": "espaguete",
        "ph": "papel higienico",
        "hig": "higienico",
        "sab": "sabonete",
        "dov": "dove",
        "p": "po",
        "po": "po",
        "choc": "chocolate",
        "achoc": "achocolatado",
        "cond": "condensado",
        "qjo": "queijo",
        "mus": "mussarela",
        "muss": "mussarela",
        "fat": "fatiado",
        "int": "integral",
        "bisc": "biscoito",
        "waff": "waffer",
        "rosq": "rosquinha",
        "lar": "laranja",
        "lim": "limao",
        "ref": "refrigerante",
        "refrig": "refrigerante",
        "calab": "calabresa"
    }
    
    palavras = texto.split()
    palavras_expandidas = [abrevs.get(p, p) for p in palavras]
    return " ".join(palavras_expandidas)

def limpar_descricao(descricao: str) -> str:
    if not isinstance(descricao, str):
        return ""

    # 0. Lowercase
    descricao = descricao.lower()

    # 1. Remover acentos
    descricao = remover_acentos(descricao)

    # 2. Substituir underscores e hifens por espaços
    descricao = descricao.replace("_", " ").replace("-", " ")

    # 3. Remover medidas (ex: 500g, 1kg, 2l, 900ml)
    descricao = re.sub(r'\b\d+\s*(g|kg|ml|l|gr)\b', '', descricao)

    # 4. Remover palavras de ruído
    noise_words = ["vacuo", "trad", "pet", "cx", "un", "bar", "original", "tp", "emb", "promo", "pct", "ref", "liq"]
    for word in noise_words:
        descricao = re.sub(r'\b' + word + r'\b', '', descricao)

    # 5. Manter apenas letras, números e espaços
    descricao = re.sub(r"[^a-z0-9\s]", " ", descricao)

    # 6. Remover espaços duplicados
    descricao = re.sub(r"\s+", " ", descricao).strip()
    
    # 7. Expandir abreviações (NOVO)
    descricao = expandir_abreviacoes(descricao)

    return descricao

def test_similarity():
    pairs = [
        ("far_lac_nestle", "farinha_lactea_nestle"),
        ("frango_perd", "frango_perdigao_cong"),
        ("iog_nestl_mor", "iog_nest_morang"),
        ("mac_renata_esp", "macarrao_renata_espaguete"),
        ("macarrao_rnt_esp", "macarrao_renata_espaguete"),
        ("ph_neve", "papel_hig_neve"),
        ("sab_dov", "sabonete_dove")
    ]
    
    print("--- Testing Similarity with Expansion ---")
    
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    
    for p1, p2 in pairs:
        c1 = limpar_descricao(p1)
        c2 = limpar_descricao(p2)
        
        corpus = [c1, c2]
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        
        print(f"'{p1}' -> '{c1}'")
        print(f"'{p2}' -> '{c2}'")
        print(f"Similarity: {sim:.4f}\n")

if __name__ == "__main__":
    test_similarity()
