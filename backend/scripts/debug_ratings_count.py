import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.dataset import loader

ratings = loader.load_ratings()
print(f"Total ratings: {len(ratings)}")
print(f"Columns: {ratings.columns}")
print(f"CPF type: {ratings['cpf'].dtype}")

counts = ratings['cpf'].value_counts()
print("\nRatings per user distribution:")
print(counts.describe())

print(f"\nUsers with < 4 ratings: {len(counts[counts < 4])}")
print(f"Users with >= 4 ratings: {len(counts[counts >= 4])}")

print("\nSample CPFs from ratings:")
print(ratings['cpf'].head().tolist())
