import os
import uuid
import unicodedata
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.utilitarios.limpeza_dados import limpar_descricao

PRODUTOS_BASE_DIR = "dataset/produtos_base"
STANDARDIZED_PATH = "dataset/standardized/produtos_padronizados.csv"


def normalizar_nome_arquivo(texto: str) -> str:
    """
    Remove acentos, caracteres especiais, troca espaços por _.
    """
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = "".join(c if c.isalnum() or c == " " else " " for c in texto)
    texto = "_".join(texto.lower().split())
    return texto + ".txt"


def carregar_documentos_base():
    """
    Lê todos os arquivos da pasta produtos_base e retorna:
    - lista de nomes (sem .txt)
    - lista de conteúdos
    """
    nomes = []
    textos = []

    if not os.path.exists(PRODUTOS_BASE_DIR):
        os.makedirs(PRODUTOS_BASE_DIR)

    for arquivo in os.listdir(PRODUTOS_BASE_DIR):
        if arquivo.endswith(".txt"):
            caminho = os.path.join(PRODUTOS_BASE_DIR, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                textos.append(f.read())
                nomes.append(arquivo.replace(".txt", "").replace("_", " "))

    return nomes, textos


def salvar_documento_base(descricao_padronizada):
    base = limpar_descricao(descricao_padronizada)
    nome_arquivo = normalizar_nome_arquivo(base)
    caminho = os.path.join(PRODUTOS_BASE_DIR, nome_arquivo)

    if os.path.exists(caminho):
        return base

    # sempre escrever APENAS A BASE
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(base)

    return base



def comparar_tf_idf(descricao: str):
    """
    Compara a descrição com os documentos base e retorna:
    - nome do produto mais similar
    - valor da similaridade
    """
    nomes, textos = carregar_documentos_base()

    # Caso ainda não existam documentos base → produto novo
    if len(textos) == 0:
        return None, 0.0

    corpus = textos + [descricao]

    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Último elemento é a descrição nova
    nova_repr = tfidf_matrix[-1]
    base_repr = tfidf_matrix[:-1]

    similaridades = cosine_similarity(nova_repr, base_repr)[0]

    # índice da maior similaridade
    idx = similaridades.argmax()
    sim = similaridades[idx]
    nome_produto = nomes[idx]

    return nome_produto, sim


def registrar_standardized(id_produto, descricao_pad, marca):
    """
    Salva em dataset/standardized/produtos_padronizados.csv
    """
    os.makedirs(os.path.dirname(STANDARDIZED_PATH), exist_ok=True)

    # Se arquivo ainda não existe, cria com cabeçalho
    if not os.path.exists(STANDARDIZED_PATH):
        df = pd.DataFrame(columns=["id", "descricao", "marca"])
        df.to_csv(STANDARDIZED_PATH, index=False)

    df = pd.read_csv(STANDARDIZED_PATH)

    nova_linha = {
        "id": id_produto,
        "descricao": descricao_pad,
        "marca": marca
    }

    df = df._append(nova_linha, ignore_index=True)
    df.to_csv(STANDARDIZED_PATH, index=False, encoding="utf-8")


def carregar_mapa_ids():
    """
    Carrega um dicionário {descricao_padronizada: id_produto}
    do arquivo standardized.
    """
    if not os.path.exists(STANDARDIZED_PATH):
        return {}
    
    try:
        df = pd.read_csv(STANDARDIZED_PATH)
        if "descricao" in df.columns and "id" in df.columns:
            # Cria mapa descricao -> id
            # Se houver duplicatas, pega o primeiro (ou último), tanto faz, desde que seja consistente
            return dict(zip(df["descricao"], df["id"]))
    except Exception:
        pass
        
    return {}


def processar_comparacao_tf_idf(df):
    """
    df é o DataFrame vindo de nfs_processadas.csv
    Colunas esperadas: descricao, marca
    """
    
    # 1. Carregar mapa de IDs existentes para evitar duplicar IDs para o mesmo produto
    mapa_ids = carregar_mapa_ids()
    
    for _, row in df.iterrows():

        descricao = row["descricao"]
        marca = row["marca"]

        # 0. Limpeza avançada antes de comparar
        descricao = limpar_descricao(descricao)

        nome_existente, similaridade = comparar_tf_idf(descricao)

        if similaridade >= 0.6:
            # Produto reconhecido
            descricao_padronizada = nome_existente
        else:
            # Produto novo ➝ criar documento base
            base = limpar_descricao(descricao)
            descricao_padronizada = base
            salvar_documento_base(base)

        # Verificar se já existe ID para essa descrição padronizada
        if descricao_padronizada in mapa_ids:
            id_produto = str(mapa_ids[descricao_padronizada])
        else:
            # Gerar NOVO ID único
            id_produto = str(uuid.uuid4())
            mapa_ids[descricao_padronizada] = id_produto

        # Registrar no standardized
        registrar_standardized(
            id_produto=id_produto,
            descricao_pad=descricao_padronizada,
            marca=marca
        )

    print("✅ TF-IDF concluído. Produtos registrados em standardized/")
