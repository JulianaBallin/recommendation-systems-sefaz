# Relatório

## Objetivo do Sistema

O projeto consiste no desenvolvimento de um sistema de recomendação para um cenário de varejo local, utilizando como base dados de notas fiscais de compras. O objetivo é aplicar técnicas de **Filtragem Colaborativa** para gerar dois tipos principais de recomendações:

1.  **Recomendação por Similaridade de Produto (Item-Item)**: Sugerir produtos com base na premissa de que "clientes que compraram este item também compraram estes outros".
2.  **Recomendação por Similaridade de Cliente (User-User)**: Sugerir produtos para um cliente com base nas compras de outros clientes com gostos e históricos de compra parecidos.

O sistema é composto por um backend em FastAPI, que serve a lógica de recomendação, e um frontend em Streamlit, que fornece uma interface interativa para visualizar os dados e as recomendações geradas.

## Como executar o frontend e backend

Siga os passos abaixo para configurar e executar o projeto localmente.

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

### 2. Instalação

Clone o repositório e instale as dependências:
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/recommendation-systems-sefaz.git
cd recommendation-systems-sefaz

# Instale as dependências
pip install -r requirements.txt
```

### 3. Preparação dos Dados

Antes de iniciar a aplicação, é necessário executar a sequência de scripts que geram os datasets de treino:
```bash
# 1. Cria uma lista de produtos únicos para a interface
python backend/dataset/product_deduplicator.py

# 2. Simula o histórico de compras (ratings.csv) com base em perfis de consumo
python backend/dataset/simulator.py
```

### 4. Execução

Abra dois terminais na pasta raiz do projeto.

**Terminal 1 - Backend (API):**
```bash
uvicorn backend.main:app --reload
```
Aguarde a mensagem `Recursos carregados com sucesso!`.

**Terminal 2 - Frontend (Streamlit):**
```bash
streamlit run frontend/streamlit_app/00_🏠Home.py
```
Acesse a URL fornecida pelo Streamlit (geralmente `http://localhost:8501`) no seu navegador.

## Explicação da lógica de recomendação
1. Similaridade de Clientes (User-User Collaborative Filtering)
Esta é a funcionalidade da página "Recomendações por Cliente". O processo é o seguinte:

**Criação da Matriz de Utilidade**: O sistema primeiro cria uma grande tabela (matriz) onde as linhas são os clientes (CPF) e as colunas são os produtos. O valor em cada célula é a "nota" (rating) que o cliente deu ao produto. Se um cliente não comprou um produto, a nota é 0.

**Cálculo da Similaridade entre Clientes**: Usando a **Correlação de Pearson**, o sistema compara o vetor de notas de cada cliente com todos os outros. O resultado é uma pontuação de similaridade entre -1 (gostos opostos) e 1 (gostos idênticos). Clientes com pontuações altas são considerados "vizinhos" ou "almas gêmeas de compras".

**Geração de Recomendações**:
> O sistema pega os produtos que os "vizinhos" compraram e que você ainda não comprou.
> Ele calcula uma "nota prevista" para cada um desses produtos, dando mais peso às notas dos vizinhos mais parecidos com você.
> Os produtos com as maiores notas previstas são recomendados.

Em resumo: "Clientes que são como você também compraram estes produtos, que talvez você goste."


2. Similaridade de Produtos (Item-Item Collaborative Filtering)
Esta é a funcionalidade da página "Recomendações por Produto". A lógica é um pouco diferente:

**Criação da Matriz (Transposta)**: A mesma matriz do método anterior é usada, mas de forma "invertida" (transposta). Agora, as linhas são os produtos e as colunas são os clientes.

**Cálculo da Similaridade entre Produtos**: Usando a **Similaridade de Cosseno**, o sistema compara o vetor de clientes de cada produto com todos os outros. O resultado é uma pontuação que indica quais produtos são comprados por padrões de clientes semelhantes.

**Geração de Recomendações**:
> Quando você seleciona um produto (ex: "Biscoito Recheado"), o sistema busca na matriz de similaridade quais outros produtos têm a maior pontuação em relação a ele.
> Os produtos mais similares são então recomendados.

Em resumo: "Clientes que compraram este produto também costumam comprar estes outros."


## Justificativa da métrica de similaridade usada
Foram escolhidas métricas diferentes e adequadas para cada tipo de recomendação:

#### 1. Similaridade de Clientes (User-User): **Correlação de Pearson**
A Correlação de Pearson foi usada para comparar clientes porque ela é excelente em encontrar "gostos" similares, independentemente do volume de compras.
*   **Corrige o Viés do Comprador**: A métrica neutraliza as diferenças entre clientes que compram muito e os que compram pouco. Ela foca no padrão de preferência de cada um.
*   **Identifica Interesses Reais**: Ao ajustar pela média de cada cliente, a Correlação de Pearson dá mais peso a compras de produtos específicos que fogem do comum, revelando gostos genuínos.

#### 2. Similaridade de Produtos (Item-Item): **Similaridade de Cosseno**
A Similaridade de Cosseno foi usada para comparar produtos porque ela é ideal para medir a coocorrência de itens nos carrinhos de compra.
*   **Foco na Coocorrência**: A métrica mede o "ângulo" entre os vetores de compra de dois produtos. Se os mesmos clientes compram os produtos A e B, seus vetores apontam na mesma direção, resultando em alta similaridade.
*   **Padrão da Indústria**: É a métrica mais comum e bem-sucedida para sistemas de recomendação Item-Item baseados em dados implícitos (comprou/não comprou).


## Cálculo e análise da acurácia
A acurácia do sistema de recomendação Item-Item foi medida para validar sua eficácia. O processo, implementado no script `backend/recommender/evaluate_accuracy.py`, segue os seguintes passos:

1.  **Divisão dos Dados (Train/Test Split)**:
    *   Para um usuário aleatório, seu histórico de compras é dividido em duas partes: 50% para **treino** e 50% para **teste** (que funciona como "gabarito").
    *   O conjunto de treino do usuário é combinado com os dados de todos os outros clientes para formar o dataset de treinamento.

2.  **Geração de Recomendações**:
    *   O modelo de recomendação Item-Item é treinado **apenas com o conjunto de treino**.
    *   O produto mais comprado pelo usuário no seu conjunto de treino é usado como referência para gerar **5 novas recomendações**.

3.  **Cálculo da Acurácia**:
    *   As 5 recomendações geradas são comparadas com a lista de produtos que o usuário realmente comprou no conjunto de teste (o "gabarito").
    *   A acurácia é calculada pela fórmula: `Acurácia = (Número de Acertos) / (Número de Itens Recomendados)`

### Resultado da Avaliação
Ao executar o script de avaliação (`backend/recommender/evaluate_accuracy.py`) ou através da página "Avaliação e Análise" no frontend, é possível obter o relatório da acurácia para um usuário aleatório.
