# YaraRec — Sistema Híbrido de Recomendação Baseado em Dados Fiscais  
## Incentivo ao Consumo Local em Supermercados de Manaus-AM  

---

## 🧭 Estrutura do Projeto

```
amazia/
│
├── backend/
│   ├── banco_dados/
│   │   ├── conexao.py                 # Cria e gerencia a engine SQLite
│   │   └── init_db.py                 # Cria tabelas (DDL) e garante integridade inicial
│   │
│   ├── dados/
│   │   ├── carregador_dados.py        # Lê CSVs validados e insere registros válidos no banco
│   │   └── __init__.py
│   │
│   ├── utilitarios/
│   │   ├── validacao_dados.py         # Funções de validação de CPF, CNPJ, CEP, datas, texto etc.
│   │   ├── limpeza_dados.py           # Padroniza campos e remove registros inválidos
│   │   ├── mensagens_ui.py            # Mostra mensagens de sucesso/erro no Streamlit
│   │   └── __init__.py
│   │
│   ├── recomendador/
│   │   ├── colaborativo.py            # (mantido) modelo de filtragem colaborativa
│   │   ├── conteudo.py                # (mantido) modelo baseado em conteúdo
│   │   ├── hibrido.py                 # (mantido) modelo híbrido
│   │   ├── metricas.py                # (mantido) métricas (precision, recall, RMSE, MAE)
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py                        # (opcional) FastAPI para expor endpoints
│
├── dados/
│   ├── derivados/                     # CSVs limpos e prontos para inserção no banco
│   │   ├── produtos.csv
│   │   ├── categorias.csv
│   │   ├── marcas.csv
│   │   ├── clientes.csv
│   │   ├── supermercados.csv
│   │   ├── nfs.csv
│   │   └── avaliacoes_busca.csv
│   │
│   ├── modelos/                       # Modelos e parâmetros de recomendação treinados
│   │   └── melhores_parametros_svd.json
│   │
│   └── amazia.db                      # Banco SQLite principal (será criado automaticamente)
│
├── frontend/
│   └── streamlit_app/
│       ├── main.py                    # Controla as 3 páginas (Home, Dataset, Recs)
│       ├── style.css                  # Estilos visuais da aplicação
│       └── modules/
│           ├── app_home.py            # Página 1 – Objetivo, autores, ferramentas
│           ├── app_dataset.py         # Página 2 – Upload CSV, validação e inserção no banco
│           ├── app_avaliacoes_recomendacoes.py  # Página 3 – Avaliações, Recs e Métricas
│           ├── ui_messages.py         # Mensagens padronizadas da interface
│           └── __init__.py
│
├── tests/
│   ├── test_validacao_dados.py        # Testes para validações de CPF, CNPJ, CEP, datas, etc.
│   ├── test_banco_dados.py            # Testes de conexão e integridade das tabelas SQLite
│   └── __init__.py
│
├── README.md
├── CHECKLIST.md
├── requirements.txt
└── .gitignore

```


---

## 🧩 Estrutura das Páginas (Streamlit / WebApp)

### **Página 1 — Home**
- [ ] Exibir título: “YaraRec: Sistema Híbrido de Recomendação Baseado em Dados Fiscais”
- [ ] Descrever objetivo do projeto  
- [ ] Mostrar autores e afiliações  
- [ ] Listar ferramentas e bibliotecas utilizadas (Python, Pandas, Scikit-Learn, Streamlit, BigQuery, Docker)  
- [ ] Exibir fluxograma simples do sistema  

---

### **Página 2 — Dataset**
- [ ] Permitir upload em lote de arquivos `.csv`
- [ ] Importar tabelas: `PRODUTOS`, `CLIENTES`, `NFS`, `AVALIACOES_BUSCA`
- [ ] Validar e limpar dados conforme regras abaixo  
- [ ] Exibir amostra dos dados (preview 10 linhas)  
- [ ] Mostrar alertas de inconsistências detectadas  
- [ ] Salvar dataset tratado em `/data/clean/`  

---

### **Página 3 — Avaliações e Recomendações**
- [ ] Selecionar usuário (CPF)  
- [ ] Exibir seções:
  - [ ] 🔹 Recomendações  
  - [ ] 🔹 Busca personalizada (filtros por categoria, marca, supermercado)  
  - [ ] 🔹 Avaliações de produtos  
  - [ ] 🔹 Acurácia (comparativo entre recomendação e histórico real)  

---

## 🗂️ Estrutura das Tabelas

### **PRODUTOS**
| Campo | Tipo | Regras |
|--------|------|--------|
| Id_Categoria | int | Deve existir em `CATEGORIA` |
| Id_Marca | int | Deve existir em `MARCA` |
| Id_Produto | int | Autogerado e único |
| Descricao_Produto | str | Até 150 caracteres, texto livre |

### **CATEGORIA**
| Campo | Tipo | Regras |
|--------|------|--------|
| Id_Categoria | int | Autogerado e único |
| Descricao_Categoria | str | Sem números ou caracteres especiais |

### **MARCA**
| Campo | Tipo | Regras |
|--------|------|--------|
| Id_Marca | int | Autogerado e único |
| Descricao_Marca | str | Sem números ou caracteres especiais |

### **CLIENTES**
| Campo | Tipo | Regras |
|--------|------|--------|
| Cpf | str | Válido e único |
| Nome | str | Sem números ou caracteres especiais |
| DataNasc | date | Formato DD/MM/AAAA |
| Genero | char | F, M ou O |
| Cep | str | Válido para Manaus-AM |

### **SUPERMERCADOS**
| Campo | Tipo | Regras |
|--------|------|--------|
| Id_Supermercado | str | CNPJ+CEP (chave primária) |
| Cnpj | str | Válido e único |
| Nome | str | Nome da loja |
| Cep | str | Válido para Manaus-AM |
| Bairro | str | Texto simples |
| Rua | str | Texto simples |
| Num | str/int | Endereço físico |

### **NFS**
| Campo | Tipo | Regras |
|--------|------|--------|
| Id_Supermercado | str | Deve existir em `SUPERMERCADOS` |
| Id_Produto | int | Deve existir em `PRODUTOS` |
| Preco | float | Valor positivo |
| TimeStamp_Registro | datetime | Data e hora da compra |

### **AVALIACOES_BUSCA**
| Campo | Tipo | Regras |
|--------|------|--------|
| Cpf_Cliente | str | Deve existir em `CLIENTES` |
| Id_Categoria | int | Avaliação 0–5 ou None |
| Qtd_Busca_Categoria | int | ≥ 0 |
| Id_Marca | int | Avaliação 0–5 ou None |
| Qtd_Busca_Marca | int | ≥ 0 |
| Id_Produto | int | Avaliação 0–5 ou None |
| Qtd_Busca_Produto | int | ≥ 0 |
| Cnpj_Supermercado | str | Deve existir em `SUPERMERCADOS` |
| Avaliacao_Supermercado | int | 0–5 ou None |
| Qtd_Busca_Supermercado | int | ≥ 0 |

---

## 🧼 Funções de Validação e Limpeza

### 🔹 `validate_produtos(df_produtos)`
- Verifica se `Id_Categoria` e `Id_Marca` existem  
- Gera `Id_Produto` único  
- Limita `Descricao_Produto` a 150 caracteres  

### 🔹 `validate_categoria(df_categoria)`
- Remove caracteres numéricos e especiais  
- Gera `Id_Categoria` único  

### 🔹 `validate_marca(df_marca)`
- Remove caracteres numéricos e especiais  
- Gera `Id_Marca` único  

### 🔹 `validate_clientes(df_clientes)`
- Valida CPF, data, gênero e CEP  
- Remove nomes com caracteres inválidos  
- Garante unicidade de CPF  

### 🔹 `validate_supermercados(df_super)`
- Valida CNPJ e CEP (somente Manaus-AM)  
- Cria chave primária combinada `Id_Supermercado = CNPJ + CEP`  

### 🔹 `validate_nfs(df_nfs)`
- Verifica integridade referencial (`Id_Produto`, `Id_Supermercado`)  
- Valida preço e timestamp  

### 🔹 `validate_avaliacoes_busca(df_av)`
- Garante notas entre 0 e 5  
- Preenche None com 0 ou média ponderada  
- Verifica existência de CPF e chaves externas  

---

## 🤖 Inteligência de Recomendação (Módulo `recommender_engine.py`)

### 🔸 Base inicial
- [ ] Utilizar dados de `AVALIACOES_BUSCA` como vetor de preferências  
- [ ] Considerar **avaliações explícitas (0–5)** e **frequência de busca (interesse implícito)**  
- [ ] Normalizar colunas para pesos equilibrados  

### 🔸 Modelo híbrido proposto
- [ ] **Filtragem colaborativa:** similaridade entre usuários (cosine similarity, KNN ou LightFM)  
- [ ] **Baseado em conteúdo:** características do produto (categoria, marca, preço médio)  
- [ ] **Recomendação final:** média ponderada entre ambos  

### 🔸 Estratégias contra *cold start*
- [ ] Produtos mais comprados (via `NFS`)  
- [ ] Itens mais buscados globalmente  
- [ ] Categorias populares na mesma região (via CEP)  

### 🔸 Ajustes de peso (exemplo)
| Fator | Peso sugerido |
|--------|----------------|
| Avaliação explícita | 0.6 |
| Qtd_Busca | 0.3 |
| Popularidade (NFS) | 0.1 |

### 🔸 Métricas de avaliação
- [ ] Precision@K  
- [ ] Recall@K  
- [ ] RMSE / MAE  
- [ ] F1-score opcional  

---

## 🧪 Testes e Validação
- [ ] Testes unitários para funções de validação  
- [ ] Teste de integridade entre tabelas (chaves cruzadas)  
- [ ] Teste de desempenho do modelo de recomendação  
- [ ] Verificação de acurácia geral (>80% de precisão mínima esperada)  

---

## ⚙️ Ferramentas e Stack Técnica

| Categoria | Ferramentas |
|------------|-------------|
| Linguagem | Python 3.12 |
| WebApp/UI | Streamlit |
| Dados | Pandas, BigQuery, CSV |
| IA / ML | Scikit-Learn, LightFM |
| Banco Local | SQLite ou BigQuery |
| Container | Docker |
| Controle de Versão | Git + GitHub/GitLab |
| Formatação / Lint | Black, Ruff, Pylint |

---

## 🚀 Próximos Passos

- [ ] Implementar funções de validação e limpeza (`data_validation.py`)  
- [ ] Criar fluxo de upload e preview na Página 2  
- [ ] Conectar a base limpa ao módulo de recomendação  
- [ ] Ajustar pesos e testar diferentes métricas de avaliação  
- [ ] Gerar relatório de desempenho (acurácia, precision@k, recall@k)  
- [ ] Documentar resultados e preparar artigo técnico  

---

📝 **Autor(es):**  
Juliana B. Lima, Lucas C. dos Santos, Osvaldo T. Viana Junior  
**Instituição:** Escola Superior de Tecnologia – Universidade do Estado do Amazonas (UEA)  
**Projeto:** *YaraRec – Sistema Híbrido de Recomendação Baseado em Dados Fiscais*  
