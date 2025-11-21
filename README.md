# 🛒 AmazIA - Sistema de Recomendação de Compras (Manaus-AM)

Sistema completo para **processamento de notas fiscais**, **padronização de produtos**, **agrupamento inteligente (TF-IDF + Fuzzy)** e **recomendação híbrida** de itens comprados em supermercados.  
O projeto foi desenvolvido para refletir o contexto real de consumo da cidade de **Manaus-AM**.

---

## 📌 Sumário
1. Objetivos  
2. Cenário de Uso  
3. Pipeline Completa (TF-IDF + Fuzzy + Standardização)  
4. Arquitetura & Estrutura de Pastas  
5. Dados do Projeto  
6. Tecnologias  
7. Como Executar  
8. Lógica de Recomendação  
9. Métricas  
10. Equipe  
11. Licença  

---

## 🎯 Objetivos

- Extrair padrões de compra a partir de **notas fiscais reais**.  
- Criar um processo confiável para **padronizar e identificar produtos iguais**, mesmo quando descritos de formas diferentes.  
- Unificar produtos em pastas `produtos_base/` e em `produtos_padronizados.csv`.  
- Treinar um **sistema híbrido de recomendação** (Colaborativo + Conteúdo).  
- Avaliar desempenho usando métricas clássicas de Recommender Systems.  

---

## 🏙️ Cenário de Uso

No ambiente real de Manaus, supermercados escrevem produtos de formas diferentes:

- “CAFÉ PILÃO 500G”  
- “CAF PILAO”  
- “CAFE PILAO TP 500G”

O objetivo do sistema é:  
**descobrir automaticamente que todas essas linhas são o MESMO produto**.

A partir disso:

- gerar recomendações mais corretas,  
- manter histórico limpo,  
- permitir dashboard confiável,  
- e organizar produtos de forma incremental conforme novas NFs chegam.

---

## 🔗 Pipeline Completa (do RAW → Standardizado)

A pipeline automática executada é composta por **4 etapas principais**:

### **1) Etapa de Limpeza (dataset/raw → dataset/processado)**
- Remove números de peso/volumetria (g, kg, ml etc.).  
- Expande abreviações (“caf” → “cafe”, “pil” → “pilao”).  
- Remove ruído e normaliza acentos.  
- Extrai marca usando `utilitarios_dicionarios.py`.  
- Remove duplicatas.  
- Salva em:  
  `dataset/processado/nfs_processadas.csv`

---

### **2) Etapa de Padronização de Marcas**
A limpeza gera a coluna `marca`, que permite:

- agrupar produtos de forma mais precisa,  
- priorizar combinações TF-IDF entre itens da mesma marca,  
- melhorar similaridade sem depender apenas do texto.

---

### **3) Etapa TF-IDF + Fuzzy (agrupamento incremental)**

A etapa mais importante do sistema.

#### **Por que TF-IDF?**
TF-IDF transforma cada descrição em um vetor que considera:
- frequência de caracteres relevantes  
- desambiguação entre palavras  
- comparação via **cosine similarity**

Melhora muito a identificação entre:
- “nescau po”  
- “achocolatado po nescau”  
- “nescau achoc”  

#### **Por que RapidFuzz/Fuzzy?**
Algumas descrições curtas perdem poder discriminante no TF-IDF.  
Exemplo: “sab dove”, “sab dov”, “sab”.  

O Fuzzy Matching calcula similaridade textual pura via:
- token_sort_ratio  
- partial_ratio  

E garante que descrições muito pequenas ou abreviadas não se percam.

#### **Como funciona o agrupamento?**
Para cada descrição nova:

1. Compara com **todas as linhas de todos os arquivos** em `produtos_base/`.  
2. Usa **TF-IDF + Cosine Similarity** como filtro principal.  
3. Usa **RapidFuzz** como desempate quando a similaridade é ambígua.  
4. Se achar linha com similaridade acima do limiar (ex.: 65%),  
   → adiciona essa nova descrição no mesmo arquivo `.txt`.  
5. Senão:  
   → cria um novo arquivo `.txt` com o nome da descrição base.

Esse mecanismo é **incremental**: cada nova NF melhora a base sem recriar tudo.

---

### **4) Etapa de Standardização Final**
Para cada grupo de `produtos_base/` é criado ou atualizado:

- **um único ID único (UUID)**  
- **uma linha final no CSV**:  
  `dataset/standardized/produtos_padronizados.csv`

Garantias:
- produtos iguais sempre compartilham o **mesmo ID**  
- novos produtos recebem IDs novos  
- nenhum produto é duplicado  

Esse CSV é a base usada pelo motor de recomendação.

---

## 🗂️ Arquitetura & Estrutura de Pastas

recommendation-systems-sefaz/
.
├── backend  
│   ├── api  
│   │   ├── rotas_nfs.py  
│   │   └── rotas_usuarios.py  
│   ├── main.py  
│   ├── pipeline  
│   │   ├── etapa_limpeza.py  
│   │   ├── etapa_padronizacao.py  
│   │   ├── etapa_tfidf_clustering.py  
│   │   ├── etapa_standardizacao.py  
│   │   └── rodar_pipeline.py  
│   ├── recomendador  
│   │   ├── colaborativo.py  
│   │   ├── conteudo.py  
│   │   ├── hibrido.py  
│   └── utilitarios  
│       ├── limpeza_dados.py  
│       ├── tfidf_produtos.py  
│       ├── utilitarios_dicionarios.py  
│       └── validadores.py  
├── dataset  
│   ├── raw  
│   │   └── nfs.csv  
│   ├── processado  
│   │   └── nfs_processadas.csv  
│   ├── produtos_base  
│   └── standardized  
│       └── produtos_padronizados.csv  
├── frontend  
│   ├── assets  
│   └── streamlit_app  
├── scripts  
│   ├── gerar_usuarios.py  
│   ├── gerar_nfs.py  
│   ├── gerar_avaliacoes.py  
│   └── reprocessar_tudo.py  
└── README.md  

---

## 🛠️ Tecnologias

### Backend
- Python 3.10+
- FastAPI
- Pandas / NumPy

### Processamento & Recomendação
- Scikit-learn (TF-IDF, métricas, modelos)
- RapidFuzz (similaridade)
- Cosine Similarity
- SVD++ / Filtragem Colaborativa

### Frontend
- Streamlit  
- CSS customizado  
- Components reutilizáveis  

---

## ▶️ Como Executar

### 1) Backend (FastAPI)
uvicorn backend.main:app --reload --port 8000

A API sobe em:
http://127.0.0.1:8000

### 2) Pipeline manual (opcional)
python -m backend.pipeline.rodar_pipeline

### 3) Reprocessar tudo (reset completo)
python scripts/reprocessar_tudo.py

### 4) Frontend (Streamlit)
streamlit run frontend/streamlit_app/main.py

---

## 🧠 Lógica de Recomendação

O sistema utiliza um modelo **Híbrido**, combinando:

### **1) Filtragem Colaborativa**
- Matriz usuários × produtos  
- SVD++ ou KNN-based filtering  
- Similaridade de preferências entre usuários  

### **2) Conteúdo (TF-IDF de descrições padronizadas)**
- semelhança entre produtos a partir do texto processado  
- funciona mesmo para usuários com pouca interação (Cold Start)

### **3) Abordagem Híbrida**
- Combinação ponderada:  
  recomendação = α * colaborativa + (1 − α) * conteúdo  

---

## 📏 Métricas

- **Precision@K**  
- **Recall@K**  
- **NDCG@K**  
- **RMSE / MAE**  
- **Coverage**  
- **Acurácia@K** principal para avaliação prática.  

---

## 👩‍🎓 Equipe

- **Juliana Ballin Lima** – Universidade do Estado do Amazonas (UEA-EST)  
- **Lucas Carvalho dos Santos** – Universidade do Estado do Amazonas (UEA-EST)

---

## 🗺️ Próximos Passos

- Expandir dicionário de marcas e categorias.  
- Adicionar detecção de categorias automáticas (LLMs).  
- Melhorar clusterização usando embeddings (Sentence-BERT).  
- Integrar fatores de preço, sazonalidade e perfil do usuário.  
- Criar dashboard avançado com ranking de consumo por bairro.

---

## 📄 Licença

Projeto distribuído sob MIT License.  
© 2025 Juliana Ballin Lima · Lucas Carvalho dos Santos
