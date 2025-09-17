# Local Purchases Recommendation System

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
3. Evaluate performance using metrics such as **Precision, Recall, and RMSE/MAE**.  
4. Provide a solution tailored to the **local context of Manaus-AM**.  

---

## 🏙️ Usage Scenario
The system simulates the behavior of **local customers purchasing products** in Manaus.  
The recommendation engine learns from purchase histories to:  
- Suggest **similar products** to those already bought.  
- Suggest **similar clients** with overlapping interests.  
- Provide insights into **consumer behavior by neighborhood and category**.  

---

## 🗂️ Project Architecture
```
recommendation-systems-sefaz/
│── README.md
│── requirements.txt
│
├── frontend/
│ └── streamlit_app/
│ └── main.py
│
├── backend/
│ ├── dataset/
│ │ ├── loader.py # Load raw and processed data
│ │ ├── simulator.py # Generate/simulate client-product ratings
│ │ └── updater.py # Update datasets with new entries
│ │
│ ├── recommender/
│ │ ├── collaborative.py # User-based and item-based collaborative filtering
│ │ ├── content.py # Content-based filtering using product attributes
│ │ ├── hybrid.py # Hybrid recommendation (collaborative + content)
│ │ └── metrics.py # Evaluation metrics (RMSE, MAE, Precision, Recall)
│ │
│ ├── utils/
│ │ ├── preprocessing.py # Data cleaning, normalization, feature extraction
│ │ ├── similarity.py # Helper functions for cosine, Pearson, etc.
│ │ └── helpers.py # General utility functions (logging, configs, etc.)
│
├── data/
│ ├── raw/
│ │ ├── products.csv # Products (raw NF-e data)
│ │ ├── clients.csv # Clients (registry)
│ │ └── ratings.csv # Raw client-product ratings
│ ├── processed/
│ │ ├── products_clean.csv # Products enriched with category + neighborhood
│ │ ├── clients_clean.csv # Normalized clients data
│ │ └── ratings_clean.csv # Normalized ratings
│
└── tests/
├── test_loader.py
├── test_collaborative.py
└── test_metrics.py

```
---

## 📊 Datasets

- **products.csv** → Raw data from invoices (id, description, value, etc.).  
- **products_clean.csv** → Enriched with **category** + **neighborhood** (processed).  
- **clients.csv** → Customer registry (name, CPF, birthdate, gender, CEP).  
- **clients_clean.csv** → Processed clients with normalized fields.  
- **ratings.csv** → Raw classifications (client × product).  
- **ratings_clean.csv** → Normalized ratings (used for recommendation training).  

---

## 🤝 Recommendation Approaches

- **Collaborative Filtering** (User-based and Item-based)  
- **Content-Based Filtering** (product features)  
- **Hybrid Model** (combination of both approaches)  

---

## 📐 Similarity Metrics

We tested two approaches:  
- **Cosine Similarity** → good for sparse vectors and when importance lies in direction, not magnitude.  
- **Pearson Correlation** → measures linear correlation between ratings, reducing user bias.  

➡️ **Chosen Metric:** *Cosine Similarity* (more stable with sparse product-client matrices).  

---

## 📏 Accuracy Evaluation
The system is evaluated with:  
- **Precision & Recall** → relevance of recommendations.  
- **RMSE & MAE** → accuracy of predicted ratings.  
- **NDCG** → ranking quality of recommended products.  

---

## 🛠️ Technologies
- **Python 3.10+**  
- **Pandas / NumPy** – Data preprocessing  
- **Scikit-learn** – Modeling and evaluation  
- **Streamlit** – Frontend interface  
- **Matplotlib / Seaborn** – Visualization  
