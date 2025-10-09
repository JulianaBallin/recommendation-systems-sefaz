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
yararec/
│
├── dados/
│   ├── derivados/                          # CSVs validados e prontos para inserção no banco
│   │   ├── produtos.csv                    # Produtos (Id_Categoria, Id_Marca, Descricao_Produto)
│   │   ├── categorias.csv                  # Categorias de produtos
│   │   ├── marcas.csv                      # Marcas de produtos
│   │   ├── clientes.csv                    # Clientes (Cpf, Nome, DataNasc, Genero, Cep)
│   │   ├── supermercados.csv               # Supermercados (Cnpj, Nome, Endereço)
│   │   ├── nfs.csv                         # Notas fiscais (Id_Produto, Id_Supermercado, Preco, DataHora)
│   │   └── avaliacoes_busca.csv            # Avaliações e histórico de busca dos usuários
│   │
│   ├── modelos/                            # Modelos e parâmetros de recomendação treinados
│   │   └── melhores_parametros_svd.json    # Parâmetros otimizados do modelo híbrido/SVD
│   │
│   └── yararec.db                          # Banco de dados SQLite (persistência final)
│
├── backend/
│   ├── banco_dados/                        # Controle do banco e inicialização
│   │   ├── conexao.py                      # Cria e gerencia a engine de conexão SQLite
│   │   └── init_db.py                      # Criação das tabelas do sistema YaraRec
│   │
│   ├── dados/                              # Ingestão e persistência de dados validados
│   │   ├── carregador_dados.py             # Lê CSVs, aplica validação e insere linhas válidas
│   │   └── __init__.py
│   │
│   ├── utilitarios/                        # Funções auxiliares de validação e limpeza
│   │   ├── validacao_dados.py              # Valida formato de CPF, CNPJ, CEP, datas, texto, etc.
│   │   ├── limpeza_dados.py                # Remove registros inconsistentes e padroniza campos
│   │   ├── mensagens_ui.py                 # Mensagens padronizadas (sucesso, erro, alerta)
│   │   └── similaridade.py                 # Funções de cálculo de similaridade entre usuários/produtos
│   │
│   ├── recomendador/                       # Implementação do motor de recomendação
│   │   ├── colaborativo.py                 # Filtragem colaborativa
│   │   ├── conteudo.py                     # Recomendação baseada em conteúdo
│   │   ├── hibrido.py                      # Combinação híbrida (colab + conteúdo)
│   │   ├── metricas.py                     # Avaliação de desempenho (precision, recall, RMSE, MAE)
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py                             # API FastAPI opcional (se desejar expor endpoints)
│
├── frontend/
│   └── aplicacao_streamlit/                # Interface interativa (3 páginas)
│       ├── main.py                         # Menu lateral e roteamento das páginas
│       └── modulos/
│           ├── app_home.py                 # Página 1 — Objetivo, autores, ferramentas
│           ├── app_dataset.py              # Página 2 — Upload de CSVs, validação e persistência
│           ├── app_avaliacoes_recomendacoes.py  # Página 3 — Avaliações, Recomendações, Acurácia
│           └── __init__.py
│
├── tests/                                  # Testes automatizados (unitários e integração)
│   ├── test_validacao_dados.py             # Testes para funções de validação e limpeza
│   ├── test_recomendador_hibrido.py        # Testes para o modelo híbrido de recomendação
│   └── __init__.py
│
├── README.md                               # Descrição geral do projeto
├── CHECKLIST.md                            # Roteiro de implementação (etapas)
├── requirements.txt                        # Dependências do Python
└── .gitignore                              # Arquivos e pastas ignorados pelo Git

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
