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
│
├── data/
│   ├── raw/                
│   │   ├── receipt_nf.csv
│   │   ├── clients.csv
│   │
│   ├── derived/            
│   │   ├── products.csv
│   │   ├── supermarkets_dataset.csv
│   │   ├── ratings.csv
│   │
│   ├── dictionaries/        
│   │    ├── bairros_zonas.csv
│   │    ├── brand_map.csv
│   │    └── category_map.csv
│   │
│   └── models/               # Modelos treinados e artefatos
│       └── best_svd_params.json
│
├── backend/
│   ├── dataset/             
│   │   ├── loader.py #        
│   │   ├── generator.py  
│   │   ├── simulator.py  # simular novas avaliações de clientes
│   │   └── __init__.py
│   │
│   ├── utils/
│   │   ├── product_loader.py       # regras de limpeza + validação products
│   │   ├── client_loader.py        # regras de limpeza + validação clients
│   │   ├── supermarket_loader.py   # geração e normalização de supermercados
│   │   ├── preprocessing.py        # funções auxiliares genéricas
│   │   ├── dictionaries.py         # dicionários internos
│   │   ├── ui_messages.py          # feedback frontend
│   │   └── similarity.py
│   │
│   ├── recommender/         # Algoritmos de recomendação
│   │   ├── collaborative.py # Algoritmo de filtragem colaborativa
│   │   ├── content.py
│   │   ├── hybrid.py
│   │   ├── metrics.py      # métrica de avaliação de acurácia
│   │   └── __init__.py
│   │
│   └── __init__.py
│   └── main.py # gerencia a API do backend
│
├── frontend/
│   └── streamlit_app/
│       ├── main.py
│       ├── modules/
│       │   ├── app_products.py # página de produtos
│       │   ├── app_clients.py # página de clientes
│       │   ├── app_ratings.py # página de avaliações
│       │   ├── app_home.py    # página inicial
│       │   └── __init__.py
│       └── __init__.py
│
├── README.md
├── requirements.txt
└── .gitignore


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
- **FastAPI** – Backend API  
- **Streamlit** – Frontend interface  
- **Matplotlib / Seaborn** – Visualization  

---

# Sistema de Recomendação de Produtos para Supermercado

Este projeto implementa um sistema completo de recomendação de produtos para um cenário de varejo local, utilizando como base dados de notas fiscais de compras. O sistema usa técnicas avançadas de filtragem colaborativa para fornecer sugestões personalizadas aos clientes, sendo composto por um backend em FastAPI, responsável pela lógica de recomendação, e um frontend em Streamlit para interação do usuário.

---

## ○ Objetivo do Sistema

O objetivo principal é aumentar o engajamento e a satisfação do cliente, oferecendo recomendações de produtos relevantes e personalizadas. O sistema analisa o histórico de avaliações de cada cliente para prever quais outros produtos ele provavelmente gostaria de comprar, auxiliando na decisão de compra e na descoberta de novos itens.

---

## ○ Como Executar o Sistema

Para executar o projeto, você precisará de dois terminais: um para o backend e outro para o frontend.

### 1. Executar o Backend (FastAPI)

O backend é o cérebro do sistema, responsável por treinar o modelo e servir as recomendações.

```bash
# 1. Navegue até a pasta raiz do projeto
cd /caminho/para/recommendation-systems-sefaz

# 2. Instale as dependências do serviço de recomendação
pip install -r backend/recommendation_service/requirements.txt

# 3. Inicie o servidor FastAPI
uvicorn backend.main:app --reload
```

O servidor estará disponível em `http://127.0.0.1:8000`. A primeira inicialização pode demorar alguns minutos, pois o sistema está otimizando os hiperparâmetros do modelo. Nas inicializações seguintes, o processo será quase instantâneo.

### 2. Executar o Frontend (Streamlit)

O frontend é a interface interativa onde os usuários podem avaliar produtos e receber recomendações.

```bash
# 1. Em um novo terminal, navegue até a pasta raiz do projeto
cd /caminho/para/recommendation-systems-sefaz

# 2. Instale as dependências principais (se ainda não o fez)
pip install -r requirements.txt

# 3. Inicie a aplicação Streamlit
streamlit run frontend/streamlit_app/main.py
```

A aplicação web será aberta no seu navegador.

---

## ○ Explicação da Lógica de Recomendação

O sistema utiliza uma abordagem de **Filtragem Colaborativa** baseada em **Fatoração de Matrizes**, especificamente o algoritmo **SVD++**.

1.  **O que é SVD++?**: É uma evolução do popular algoritmo SVD. Ele decompõe a grande matriz de avaliações (usuários vs. produtos) em matrizes menores que representam **fatores latentes** (características ou "gostos" ocultos).

2.  **Feedback Explícito e Implícito**: A grande vantagem do SVD++ é que ele considera dois tipos de informação:
    *   **Feedback Explícito**: As notas de 1 a 5 que os usuários dão aos produtos.
    *   **Feedback Implícito**: O simples fato de um usuário ter interagido com um produto (independentemente da nota). Isso enriquece o perfil do usuário, permitindo que o modelo aprenda com todo o seu histórico de interações.

3.  **Previsão**: Para recomendar um produto, o modelo combina os fatores latentes de um usuário com os de um item para prever qual seria a nota. As recomendações são os itens com as maiores notas previstas.

4.  **Otimização**: Na primeira inicialização, o sistema usa `GridSearchCV` para testar dezenas de combinações de hiperparâmetros e encontrar a "receita" ideal para o modelo, garantindo a máxima acurácia possível para o dataset atual.

---

## ○ Justificativa da Métrica de Similaridade Usada

O sistema não utiliza uma métrica de similaridade direta como "Cosseno" ou "Pearson". Em vez disso, ele adota a abordagem mais moderna e poderosa da **Fatoração de Matrizes (SVD++)**.

A justificativa para essa escolha é que a Fatoração de Matrizes é superior aos métodos baseados em vizinhança (que usam similaridade de cosseno) por várias razões:

*   **Captura de Padrões Complexos**: Em vez de apenas encontrar usuários ou itens "parecidos", o SVD++ aprende as **razões subjacentes** pelas quais um usuário gosta de um item. Ele modela gostos complexos e não-lineares (ex: um usuário que gosta de produtos de limpeza e de padaria pode ter um perfil "dono de casa").
*   **Melhor Desempenho com Dados Esparsos**: Lida muito melhor com a esparsidade (muitos valores em branco na matriz de avaliações), que é o cenário comum em sistemas reais.
*   **Generalização**: Consegue prever notas para pares usuário-item que não têm sobreposição direta no histórico, com base nos fatores latentes aprendidos com todo o conjunto de dados.

A "similaridade" no SVD++ é, portanto, o resultado da interação entre os vetores de fatores latentes do usuário e do item, uma medida muito mais rica e precisa do que as métricas de distância tradicionais.

---

## ○ Cálculo e Análise da Acurácia

A acurácia do modelo é avaliada usando a métrica **Acurácia @10**, que é um padrão da indústria para sistemas de recomendação.

### Metodologia de Cálculo

Para cada usuário, o sistema realiza uma simulação para testar sua capacidade de previsão:

1.  **Divisão dos Dados (Hold-Out)**: O histórico de avaliações de um usuário é dividido em duas partes:
    *   **Parte 1: Treino (50%)**: Usada para treinar um modelo de recomendação temporário.
    *   **Parte 2: Gabarito (50%)**: Fica "escondida" do modelo. Apenas os itens com nota positiva (≥ 3) desta parte são considerados como o conjunto de respostas corretas.

2.  **Geração de Recomendações na Simulação**: O modelo temporário gera uma lista de **10 recomendações** (`K=10`) para o usuário, com base apenas nos dados da "Parte 1".

3.  **Comparação e Cálculo**: O sistema compara as 10 recomendações da simulação com os itens do "Gabarito".
    *   **Acertos**: O número de itens que aparecem em ambas as listas.
    *   **Fórmula**: `Acurácia @10 = (Número de Acertos) / 10`

### Análise

*   **O que a métrica significa?**: Uma acurácia de 30% significa que, a cada 10 itens recomendados na simulação, 3 foram acertos relevantes para o usuário. Isso mede a **eficiência do espaço de recomendação**.
*   **Diferença para a Recomendação Final**: É crucial entender que a lista de recomendações gerada na simulação **não é a mesma** que é mostrada ao usuário. A recomendação final utiliza 100% dos dados para dar a melhor sugestão possível, enquanto a acurácia é calculada em um cenário de teste controlado para avaliar o poder preditivo do modelo.
