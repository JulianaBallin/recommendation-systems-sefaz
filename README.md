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
📦 recommendation-system
├── data/ # Dataset (local purchase invoices)
├── notebooks/ # Jupyter Notebooks for analysis and prototyping
├── src/ # Main source code
│ ├── preprocessing/ # Data cleaning and transformation scripts
│ ├── models/ # Recommendation model implementations
│ ├── evaluation/ # Evaluation metrics and validation functions
│ └── utils/ # Helper functions
├── tests/ # Unit tests
├── requirements.txt # Project dependencies
└── README.md # Documentation


---

## 📊 Methodology

- **Collaborative Filtering:**  
  Based on user–item interactions, using matrix factorization and embeddings.  

- **Content-Based Filtering:**  
  Uses product attributes such as categories, brands, and average values.  

- **Hybrid Filtering:**  
  Combines both approaches for higher precision and broader coverage.  

---

## 🚀 How to Run

1. Clone this repository:  
   ```bash
   git clone https://github.com/your-username/recommendation-system.git
   cd recommendation-system



