# 📊 Local Purchases Recommendation System

This repository is dedicated to the **development and training of a recommendation system** based on **local purchase invoices (NF-e)** from the Manaus-AM region.  
The project applies **Hybrid Filtering techniques** (Collaborative Filtering + Content-Based Filtering) to explore consumer behavior and generate relevant product recommendations.

---

## 👩‍🎓 Team

- **Juliana Ballin Lima** – Universidade do Estado do Amazonas (UEA - EST)  
- **Lucas Carvalho dos Santos** – Universidade do Estado do Amazonas (UEA - EST)  

---

## 🎯 Project Goals

1. Extract purchasing patterns from **electronic invoices (NF-e)**.  
2. Develop and train a **hybrid recommendation system**.  
3. Evaluate performance using metrics such as **Precision, Recall, and NDCG**.  
4. Provide a solution tailored to the **local context of Manaus-AM**.  

---

## 🛠️ Technologies

- **Python 3.10+**  
- **Pandas / NumPy** – Data preprocessing  
- **Scikit-learn** – Modeling and metrics  
- **Surprise / LightFM** – Recommendation algorithms  
- **Jupyter Notebook** – Exploratory analysis and experiments  
- **Matplotlib / Seaborn** – Data visualization  

---

## 📂 Repository Structure

```bash
Recommendation-Systems-Sefaz/
│
├── data/
│   ├── raw/               # original datasets (unmodified)
│   │   ├── products.csv   # simulated product data
│   │   └── ratings.csv    # simulated user ratings
│   │
│   ├── processed/         # datasets ready for ML training
│   │   ├── products_clean.csv
│   │   └── ratings_clean.csv
│   │
│   └── external/          # optional external datasets (e.g., Instacart, Dunnhumby)
│
├── src/
│   ├── dataset/           # data manipulation and updates
│   │   ├── loader.py
│   │   ├── simulator.py
│   │   └── updater.py
│   │
│   ├── recommender/       # recommendation algorithms
│   │   ├── collaborative.py
│   │   ├── content.py
│   │   └── hybrid.py
│   │
│   └── utils/             # preprocessing helpers, logging, etc.
│
├── streamlit_app/         # interactive interface
│   └── main.py
│
├── notebooks/             # exploratory analyses
├── tests/                 # unit tests
└── README.md
```

## 📐 Project Architecture

This project follows a **Modular Architecture for Recommender Systems**, inspired by **Cookiecutter Data Science** and **Clean Architecture principles**.  

- **data/**  
  - Keeps raw, processed, and external datasets well separated.  
  - Ensures reproducibility by never overwriting the original data (`raw/`).  

- **src/**  
  - Encapsulates all the system’s logic.  
  - `dataset/` handles dataset loading, simulation, and updates.  
  - `recommender/` implements Collaborative Filtering, Content-Based Filtering, and Hybrid approaches.  
  - `utils/` centralizes preprocessing and logging functions.  

- **streamlit_app/**  
  - Provides a friendly user interface to **simulate new data entries** (products and ratings) and visualize recommendations.  

- **notebooks/**  
  - Dedicated to exploratory analysis and model evaluation during development.  

- **tests/**  
  - Unit tests ensure maintainability and reliability of each module.  

👉 This separation of concerns guarantees clarity, scalability, and makes it easy to later migrate from **simulated CSV data** to **real SEFAZ-AM data** when available.  

---

## 📊 Methodology

- **Collaborative Filtering:**  
  Based on user–item interactions, using matrix factorization and embeddings.  

- **Content-Based Filtering:**  
  Uses product attributes such as categories, brands, and average values.  

- **Hybrid Filtering:**  
  Combines both approaches for higher precision and broader coverage.  
