from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean_text(text):
    text = text.lower()
    text = text.replace("_", " ")
    text = re.sub(r'\b\d+\s*(g|kg|ml|l|gr)\b', '', text)
    noise_words = ["vacuo", "trad", "pet", "cx", "un", "bar", "original"]
    for word in noise_words:
        text = re.sub(r'\b' + word + r'\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def test_similarity():
    products = [
        "cafe pilao",
        "cafe 3 coracoes",
        "cafe santa clara",
        "arroz tio joao",
        "arroz prato fino"
    ]
    
    products_clean = [clean_text(p) for p in products]
    
    print("--- Cleaned Texts ---")
    for orig, clean in zip(products, products_clean):
        print(f"'{orig}' -> '{clean}'")
    
    print("\n--- Testing Similarity (Char N-grams) ---")
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(products_clean)
    
    base_idx = 0
    base_vec = tfidf_matrix[base_idx]
    print(f"Base: '{products_clean[base_idx]}'")
    
    for i in range(1, 3):
        compare_vec = tfidf_matrix[i]
        sim = cosine_similarity(base_vec, compare_vec)[0][0]
        print(f"Comparing with '{products_clean[i]}': {sim:.4f}")

    print("\n--- Testing Arroz ---")
    base_idx = 3
    base_vec = tfidf_matrix[base_idx]
    print(f"Base: '{products_clean[base_idx]}'")
    compare_vec = tfidf_matrix[4]
    sim = cosine_similarity(base_vec, compare_vec)[0][0]
    print(f"Comparing with '{products_clean[4]}': {sim:.4f}")

if __name__ == "__main__":
    test_similarity()
