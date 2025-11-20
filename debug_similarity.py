from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re

def preprocess(text):
    # Replace underscores with spaces
    text = text.replace("_", " ")
    return text

def test_similarity():
    products = [
        "cafe pilao",
        "caf pilao",
        "cafe pilao vacuo",
        "cafe_pilao",
        "cafe pilao trad",
        "cafe pilao 500g",
        "arroz tio joao",
        "arroz t joao"
    ]
    
    products_clean = [preprocess(p) for p in products]
    
    print("--- Testing Similarity (Char N-grams) ---")
    # Using char_wb n-grams to capture subword similarities (good for typos and partial matches)
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(products_clean)
    
    # Compare everything to "cafe pilao" (index 0)
    base_idx = 0
    base_vec = tfidf_matrix[base_idx]
    print(f"Base: '{products[base_idx]}'")
    
    for i in range(1, 6): # Compare only cafe pilao variations
        compare_vec = tfidf_matrix[i]
        sim = cosine_similarity(base_vec, compare_vec)[0][0]
        print(f"Comparing with '{products[i]}': {sim:.4f}")

    print("\n--- Testing Arroz ---")
    # Compare "arroz tio joao" (index 6) with "arroz t joao" (index 7)
    base_idx = 6
    base_vec = tfidf_matrix[base_idx]
    compare_vec = tfidf_matrix[7]
    sim = cosine_similarity(base_vec, compare_vec)[0][0]
    print(f"Base: '{products[6]}'")
    print(f"Comparing with '{products[7]}': {sim:.4f}")

if __name__ == "__main__":
    test_similarity()
