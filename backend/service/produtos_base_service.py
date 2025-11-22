import os
import unicodedata
from typing import List, Tuple, Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

from backend.utilitarios.limpeza_dados import limpar_descricao

PRODUTOS_BASE_DIR = "dataset/produtos_base"
STANDARDIZED_PATH = "dataset/standardized/produtos_padronizados.csv"


def _normalizar_nome_arquivo(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = "".join(c if c.isalnum() or c == " " else " " for c in texto)
    texto = "_".join(texto.lower().split())
    return texto + ".txt"


def _carregar_linhas_produtos() -> Tuple[List[str], List[str]]:
    arquivos: List[str] = []
    linhas: List[str] = []

    if not os.path.exists(PRODUTOS_BASE_DIR):
        os.makedirs(PRODUTOS_BASE_DIR)
        return arquivos, linhas

    for arquivo in os.listdir(PRODUTOS_BASE_DIR):
        if not arquivo.endswith(".txt"):
            continue

        caminho = os.path.join(PRODUTOS_BASE_DIR, arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                arquivos.append(arquivo)
                linhas.append(linha)

    return arquivos, linhas


def _append_linha(caminho: str, descricao: str) -> None:
    with open(caminho, "a", encoding="utf-8") as f:
        f.write("\n" + descricao)


def _criar_novo_arquivo(descricao: str) -> str:
    nome = _normalizar_nome_arquivo(descricao)
    caminho = os.path.join(PRODUTOS_BASE_DIR, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(descricao)
    return nome


def _obter_primeira_linha(caminho: str) -> str:
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                return linha
    return ""


def _extrair_root_key(texto: str) -> str:
    """
    Extrai uma 'chave raiz' conservadora:
    - mantém a ordem original
    - usa no máximo as 2 primeiras palavras
    """
    if not isinstance(texto, str):
        return ""
    tokens = texto.split()
    if len(tokens) <= 2:
        return " ".join(tokens)
    return " ".join(tokens[:2])


def _carregar_mapa_descricao_para_marca() -> Dict[str, str]:
    if not os.path.exists(STANDARDIZED_PATH):
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(STANDARDIZED_PATH)
        if "descricao" in df.columns and "marca" in df.columns:
            return dict(zip(df["descricao"], df["marca"]))
    except Exception:
        return {}
    return {}


def _calcular_score_hibrido(
    descricao_limpa: str,
    corpus: List[str],
    marca_nova: Optional[str],
    mapa_descr_marca: Dict[str, str]
) -> Tuple[int, float]:
    """
    Score híbrido:
      - 0.5 * cosine(TF-IDF)
      - 0.3 * fuzzy token_set_ratio
      - 0.2 * fuzzy da root_key
      - bônus se marca_nova == marca_existente (+0.12)
    """
    if not corpus:
        return -1, 0.0

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(corpus + [descricao_limpa])

    nova_repr = tfidf_matrix[-1]
    base_repr = tfidf_matrix[:-1]

    cosine_scores = cosine_similarity(nova_repr, base_repr)[0]

    fuzzy_scores = [fuzz.token_set_ratio(descricao_limpa, txt) / 100 for txt in corpus]

    root_nova = _extrair_root_key(descricao_limpa)
    root_scores = [
        fuzz.token_set_ratio(root_nova, _extrair_root_key(txt)) / 100
        for txt in corpus
    ]

    combined: List[float] = []
    for i in range(len(corpus)):
        base_score = (
            0.5 * float(cosine_scores[i])
            + 0.3 * float(fuzzy_scores[i])
            + 0.2 * float(root_scores[i])
        )

        marca_existente = mapa_descr_marca.get(corpus[i])
        bonus_marca = 0.0
        if marca_nova and marca_existente and marca_nova == marca_existente:
            bonus_marca = 0.12

        score_final = base_score + bonus_marca
        if score_final > 1.0:
            score_final = 1.0

        combined.append(score_final)

    idx = max(range(len(combined)), key=lambda j: combined[j])
    return idx, combined[idx]


def garantir_produto_base_para_descricao(
    descricao: str,
    marca: Optional[str] = None,
    threshold: float = 0.85  # Aumentado de 0.80 para 0.85 (mais rigoroso)
) -> str:
    """
    Retorna a 'descricao canônica' (linha base) do cluster ao qual a descrição pertence.
    Se não pertencer a nenhum cluster existente, cria um novo arquivo .txt.
    """
    descricao_limpa = limpar_descricao(descricao or "")

    arquivos, linhas = _carregar_linhas_produtos()

    if not linhas:
        nome = _criar_novo_arquivo(descricao_limpa)
        caminho = os.path.join(PRODUTOS_BASE_DIR, nome)
        return _obter_primeira_linha(caminho)

    mapa_descr_marca = _carregar_mapa_descricao_para_marca()

    idx, score = _calcular_score_hibrido(
        descricao_limpa=descricao_limpa,
        corpus=linhas,
        marca_nova=marca,
        mapa_descr_marca=mapa_descr_marca
    )

    if idx >= 0 and score >= threshold:
        arquivo_match = arquivos[idx]
        linha_base = linhas[idx]
        caminho = os.path.join(PRODUTOS_BASE_DIR, arquivo_match)

        if descricao_limpa != linha_base:
            _append_linha(caminho, descricao_limpa)

        return linha_base

    nome = _criar_novo_arquivo(descricao_limpa)
    caminho = os.path.join(PRODUTOS_BASE_DIR, nome)
    return _obter_primeira_linha(caminho)
