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
📁 Estrutura limpa do projeto:

recommendation-systems-sefaz/
.
├── backend
│   ├── api
│   │   ├── __init__.py
│   │   ├── rotas_nfs.py
│   │   └── rotas_usuarios.py
│   ├── __init__.py
│   ├── main.py
│   ├── recomendador
│   │   ├── base.py
│   │   ├── colaborativo.py
│   │   ├── conteudo.py
│   │   ├── hibrido.py
│   │   ├── __init__.py
│   │   └── metricas.py
│   └── utilitarios
│       ├── limpeza_dados.py
│       ├── processamento.py
│       ├── processar_nfs.py
│       ├── processar_usuarios.py
│       ├── tfidf_produtos.py
│       ├── utilitarios_dicionarios.py
│       └── validadores.py
├── dataset
│   ├── processado
│   │   └── nfs_processadas.csv
│   ├── produtos_base
│   ├── raw
│   │   └── nfs.csv
│   └── standardized
│       └── produtos_padronizados.csv
├── frontend
│   ├── assets
│   └── streamlit_app
│       ├── __init__.py
│       ├── main.py
│       ├── modules
│       │   ├── app_dataset.py
│       │   ├── app_home.py
│       │   ├── app_ratings.py
│       │   ├── __init__.py
│       │   └── ui_messages.py
│       └── style.css
├── __init__.py
├── LICENSE
├── Makefile
├── README.md
├── requirements.txt
└── run_simulator.py

```

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
> **Pré-requisitos**: Python 3.10+, `pip` e os arquivos em `data/`.

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
