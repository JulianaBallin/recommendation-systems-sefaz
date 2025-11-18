# ✅ **AmazIA — Checklist Técnico de Desenvolvimento**

## 🎯 Objetivo Geral
Padronizar o fluxo de ingestão, pré-processamento e recomendação de produtos a partir de Notas Fiscais (NFs), garantindo consistência entre bancos, dicionários e validação de dados para o sistema híbrido de recomendação **AmazIA**.

---

## 🧱 **1. Banco de Dados e Estrutura Inicial**

### 🔸 Criação e Simulação
- [✅] Criar banco de dados local (`amazia.db`) ou instância no BigQuery.  
- [✅] Simular IDs de NF com **formato real (NUMERO_NFCE: 196546 SERIE:17 juntos torna-se o ID)**.  
- [✅] **Separar tabelas:**  
  - `NF` → informações gerais da nota fiscal. Campos: ID, Cnpj, endereco, datahoracompra   
  - `PRODUTO_NF` → produtos vinculados à NF (relação N:1).  Campos: Id_produto,Id_nota,valor_unitario
  - `PRODUTO_PROCESSADO_NF` → versão tratada/padronizada doa produtos das NFs, onde o sistema busca e retorna a descrição padronizada de cada produto emitido.

### 🔹 Regras de Criação
- Cada nova NF deve ser validada contra produtos já registrados.  
- Caso o produto já exista, retornar sua forma padronizada.  
- Caso contrário, registrar uma nova entrada com base nos dicionários de referência.

---

## 📚 **2. Dicionários do Sistema**

### 🔸 Dicionários Fixos (usados para povoar o banco)
- [✅] `CATEGORIA`
- [✅] `SUBCATEGORIA`
- [✅] `ESTADOS_FISICOS`
- [✅] `UNIDADE_MEDIDA`
- [✅] `SUPERMERCADOS`
- [✅] `ESTADO_FISICO`
- [✅] `ORIGEM`

> Esses dicionários são independentes da descrição textual dos produtos.  
> Servem como **referências fixas** para validação e integridade relacional.

### 🔸 Dicionários Dinâmicos (para conferência automática)
- [✅] `MARCA` — incluir variações (com/sem acentuação e abreviações).  
- [✅] `NOME_PRODUTO` — verificação cruzada com tabela `PRODUTOS` e também incluir variações (com/sem acentuação e abreviações).  
- [✅] `ESTADO_FISICO` — cruzado com `CARACTERISTICAS`.  
- [✅] `ORIGEM` — também proveniente de `CARACTERISTICAS`.

> Todos os dicionários dinâmicos serão utilizados no **pré-processamento** e na **extração automática de entidades**.

---

## 🧹 **3. Pré-Processamento de Dados**

### 🔸 Normalização de texto
- [ ] Remover pontuação e símbolos.  
- [ ] Converter para **CAIXA ALTA**.  
- [ ] Remover espaços duplicados.  
- [ ] Expandir abreviações conhecidas (usando dicionários).  
- [ ] Corrigir erros comuns de digitação.

### 🔸 Validação
- [ ] Todos os dados devem ser validados antes da persistência.  
- [ ] Apenas registros com formato aceito devem ser inseridos no banco.  
- [ ] Exibir *preview* dos registros rejeitados no frontend.

---

## 💻 **4. Frontend — Página `Dataset` (Streamlit)**

### 🔹 Arquivo: `frontend/streamlit_app/modules/app_dataset.py`
- [ ] Criar tela de **upload CSV** para simulação e treinamento.  
- [ ] Tabelas aceitas:
  - `NFS`
  - `PRODUTO_PROCESSADO_NF`
  - `CLIENTES`
  - `AVALIACOES_BUSCA`
  - `HISTORICO_BUSCAS`
- [ ] Implementar opção “Ignorar cabeçalho” (checkbox).  
- [ ] Mostrar **exemplo de formato aceito**.  
- [ ] Realizar pré-processamento automático após upload.
- [ ] Validar se determinado campo já possui registro no banco de dados para evitar duplicatas.  
- [ ] Validar todos os campos e exibir status de aprovação/rejeição.  

---

## 🧠 **5. Extração de Entidades (NLP)**

### 🔸 Técnicas de Processamento de Linguagem Natural (PLN)
- [ ] Extrair **Marca** → comparação direta com dicionário de marcas.  
- [ ] Classificar **Categoria**/**Subcategoria** e **Características** → via palavras-chave ou modelo treinado.  
- [ ] Criar módulo `backend/processamento/nf_processor.py` com função `extract_entities_from_nf()`.  
- [ ] Armazenar resultados na tabela `PRODUTO_PROCESSADO_NF`.  

---

## 🤝 **6. Módulo de Recomendação (`backend/recomendador/`)**

### 🔹 Estrutura de Abordagens
- [ ] **Filtragem colaborativa — Usuário**  
- [ ] **Filtragem colaborativa — Item**  
- [ ] **Filtragem baseada em conteúdo**  
- [ ] **Modelo híbrido com média ponderada**  
- [ ] **Implementar paralelismo para processamento de grandes volumes**  
- [ ] **Gerar justificativas da recomendação ("motivo da sugestão")**  

### 🔹 Componentes de IA
- [ ] Implementar vetor TF-IDF para descrição de produtos.  
- [ ] Calcular similaridade de cosseno (cosine similarity).  
- [ ] Utilizar LightFM ou Scikit-Learn para comparação de acurácia.  

---

## 📊 **7. Métricas de Avaliação**
| Métrica | Descrição |
|----------|------------|
| **Precision@K** | Itens recomendados corretamente entre os K primeiros |
| **Recall@K** | Itens relevantes identificados entre os K primeiros |
| **RMSE / MAE** | Erro médio das previsões |
| **F1-Score** | Equilíbrio entre precisão e revocação |

---

## 🧪 **8. Testes e Validação**
- [ ] Testes unitários de validação e pré-processamento.  
- [ ] Testes de integridade entre tabelas (FKs e dependências).  
- [ ] Testes de desempenho do motor de recomendação.  
- [ ] Verificação da acurácia mínima esperada (≥ 80%).  

---

## ⚙️ **9. Stack Técnica**

| Categoria | Ferramentas |
|------------|-------------|
| Linguagem | Python 3.12 |
| WebApp/UI | Streamlit |
| Dados | Pandas, BigQuery, CSV |
| IA/ML | Scikit-Learn, LightFM |
| Banco | SQLite / BigQuery |
| Container | Docker |
| Lint/Teste | Ruff, Black, Pylint, Pytest |
| Versionamento | Git + GitHub/GitLab |

---

## 🚀 **10. Próximos Passos**
- [ ] Finalizar scripts de popular banco (`popular_todos.py`).  
- [ ] Integrar frontend de upload com backend de validação.  
- [ ] Conectar o módulo de recomendação com base tratada.  
- [ ] Ajustar pesos e medir métricas de desempenho.  
- [ ] Criar relatório final de acurácia e justificar recomendações.  
- [ ] Redigir documentação e preparar artigo técnico.  

---

📝 **Autor(es):**  
Juliana B. Lima · Lucas C. dos Santos · Osvaldo T. Viana Junior  
**Instituição:** Escola Superior de Tecnologia – UEA  
**Projeto:** *AmazIA — Sistema Híbrido de Recomendação Baseado em Dados Fiscais*
