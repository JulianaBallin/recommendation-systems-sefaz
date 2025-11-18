# 🛒 Sistema de Recomendação de Compras Locais (Manaus-AM)

Repositório dedicado ao **desenvolvimento e treinamento** de um sistema de recomendação baseado em **notas fiscais eletrônicas (NF-e)** da região de Manaus-AM. O projeto aplica **Filtragem Híbrida** (Colaborativa + Baseada em Conteúdo) para explorar comportamento de consumo e gerar recomendações relevantes de produtos.

---

## 📌 Sumário
1. [Objetivos](#-objetivos)
2. [Cenário de Uso](#cenário-de-uso)
3. [Arquitetura & Estrutura de Pastas](#arquitetura--estrutura-de-pastas)
4. [Dados do Projeto](#dados-do-projeto)
5. [Tecnologias](#tecnologias)
6. [Como Executar](#como-executar)
7. [Lógica de Recomendação](#lógica-de-recomendação)
8. [Métricas de Avaliação](#métricas-de-avaliação)
9. [Equipe](#equipe)
10. [Próximos Passos](#próximos-passos)
11. [Licença](#licença)

---

## 🎯 Objetivos
- Extrair padrões de compra a partir de **NF-e**.
- Desenvolver e treinar um **sistema de recomendação híbrido**.
- Avaliar desempenho com **Precision, Recall, RMSE/MAE e NDCG**.
- Entregar uma solução ajustada ao **contexto local de Manaus-AM**.

---

## 🏙️ Cenário de Uso
Simulação do comportamento de **clientes locais** comprando em supermercados de Manaus. O motor de recomendação aprende com históricos para:
- Sugerir **produtos similares** aos já adquiridos.
- Encontrar **clientes semelhantes** com interesses próximos.
- Gerar **insights** por **bairro** e **categoria**.

---

## 🗂️ Arquitetura & Estrutura de Pastas
```
recommendation-systems-sefaz/
│
├── data/
│ ├── raw/
│ │ ├── receipt_nf.csv
│ │ └── clients.csv
│ ├── derived/
│ │ ├── products.csv
│ │ ├── supermarkets_dataset.csv
│ │ └── ratings.csv
│ ├── dictionaries/
│ │ ├── bairros_zonas.csv
│ │ ├── brand_map.csv
│ │ └── category_map.csv
│ └── models/
│ └── best_svd_params.json
│
├── backend/
│ ├── dataset/
│ │ ├── loader.py
│ │ ├── generator.py
│ │ ├── simulator.py
│ │ └── init.py
│ ├── utils/
│ │ ├── product_loader.py
│ │ ├── client_loader.py
│ │ ├── supermarket_loader.py
│ │ ├── preprocessing.py
│ │ ├── dictionaries.py
│ │ ├── ui_messages.py
│ │ └── similarity.py
│ ├── recommender/
│ │ ├── collaborative.py
│ │ ├── content.py
│ │ ├── hybrid.py
│ │ ├── metrics.py
│ │ └── init.py
│ ├── init.py
│ └── main.py # API (FastAPI)
│
├── frontend/
│ └── streamlit_app/
│ ├── main.py
│ └── modules/
│ ├── app_products.py
│ ├── app_clients.py
│ ├── app_ratings.py
│ ├── app_home.py
│ └── init.py
│
├── requirements.txt
├── README.md
└── .gitignore
```
---

## 📊 Dados do Projeto
- **receipt_nf.csv** → notas fiscais brutas  
- **clients.csv** → cadastro de clientes  
- **products.csv** → produtos processados a partir das NF-e  
- **ratings.csv** → avaliações de produtos (feedback explícito)

---

## 🛠️ Tecnologias
- **Python 3.10+**
- **Pandas / NumPy** (pré-processamento)
- **scikit-learn** (modelagem/avaliação)
- **FastAPI** (API do backend)
- **Streamlit** (interface web)
- **Matplotlib / Seaborn** (visualização)

---

## ▶️ Como Executar
> **Pré-requisitos**: Python 3.10+, `pip` (ou **Poetry**, se preferir), e os arquivos em `data/`.

### 1) Backend (FastAPI)
```bash
# Na raiz do projeto
pip install -r requirements.txt

# Iniciar a API
uvicorn backend.main:app --reload
# Servidor disponível em http://127.0.0.1:8000
```

### 2) Frontend (Streamlit)
```bash
# Em um segundo terminal, na raiz do projeto
pip install -r requirements.txt

# Iniciar a interface
streamlit run frontend/streamlit_app/main.py
```
> A primeira execução pode levar mais tempo se houver busca/ajuste de hiperparâmetros. Nas próximas, o carregamento usa artefatos salvos em `data/models/`.
---

## 🧠 Lógica de Recomendação

Abordagem **Híbrida** com ênfase em **Filtragem Colaborativa** por Fatoração de Matrizes (**SVD++**):  
- **Fatores latentes** capturam “gostos” ocultos de usuários e itens.  
- Considera **feedback explícito** (notas 1–5) e implícito (interações/consumo).  
- Gera predições combinando **vetores latentes** de usuário × item.  
- **Vantagens**: lida bem com esparsidade, generaliza para pares sem histórico direto e captura padrões complexos além de similaridades simples (cosseno/Pearson).
---

## 📏 Métricas de Avaliação

- **Precision & Recall** → relevância das recomendações.  
- **RMSE & MAE** → precisão das notas previstas.  
- **NDCG** → qualidade do ranqueamento.  
- **Acc@K (ex.: @10)** → proporção de acertos no top-K.

**Metodologia (exemplo Acc@10):**  
- **Hold-out** por usuário (treino/teste do histórico).  
- Recomenda-se **K=10** itens usando apenas o conjunto de treino.  
- **Acurácia@10** = acertos / 10, comparando com itens relevantes do gabarito (notas ≥ 3).
---
## 👩‍🎓 Equipe

- **Juliana Ballin Lima** – Universidade do Estado do Amazonas (UEA-EST)  
- **Lucas Carvalho dos Santos** – Universidade do Estado do Amazonas (UEA-EST)
---
## 🗺️ Próximos Passos

- Ajuste fino de hiperparâmetros e validação cruzada.  
- Expansão de features de conteúdo (marca, categoria, preço, sazonalidade).  
- Métricas online (CTR/conversão) e testes A/B.  
- Dashboard de insights por bairro/categoria.

---
## 📄 Licença

Este projeto é distribuído sob a **MIT License**.  
Consulte o arquivo [LICENSE](./LICENSE) para o texto completo da licença.

© 2025 Juliana Ballin Lima · Lucas Carvalho dos Santos
