# 📌 Roadmap – O que Falta Implementar

## 1. Backend
- Ajustar validações dos uploads: validar colunas obrigatórias (ex.: "descricao", "cpf").
- Criar rota:
  - GET /recomendar/{cpf}  → retornar recomendações reais.
- Melhorar respostas das rotas com informações mais completas (tempo, quantidades, etc.).

---

## 2. Pipeline (NFS → Produtos Finalizados)
- Ajustar lógica TF-IDF + Fuzzy para reduzir duplicações.
- Garantir que produtos iguais fiquem sempre no mesmo cluster em `produtos_base/`.
- Tornar a pipeline **incremental** (processar só novas linhas).
- Garantir IDs determinísticos ou mapeamento consistente ao reprocessar.

---

## 3. Dataset (CSV)
- Padronizar o campo `product_id` em `avaliacoes.csv`.
- Atualizar avaliações automaticamente quando IDs forem regenerados.

---

## 4. Recomendador
- Implementar filtragem colaborativa (usuário e item).
- Implementar recomendação por conteúdo (TF-IDF).
- Implementar recomendador híbrido.
- Criar função explicando o motivo da recomendação.

---

## 5. Frontend (Streamlit)
- Ajustar página de avaliação de produtos e marcas.
- Criar página de recomendações:
  - Seleciona usuário
  - Seleciona tipo de filtragem
  - Seleciona quantidade de recomendações
  - Executa cálculo
- Melhorar cores padrão na barra lateral e botões.

---

## 6. Scripts
- Finalizar `reprocessar_tudo.py`:
  - Regenerar IDs sem quebrar ratings.
  - Lidar com produtos “NOT_FOUND”.
  - Fazer backup antes de sobrescrever.

---

## 7. Diagnóstico
- Verificação de clusters inconsistentes:
  - produtos duplicados dentro de um mesmo cluster.
  - produtos espalhados entre clusters diferentes.

---

## 8. Métricas & Feedback
- Implementar feedback binário (“gostou / não gostou”) nas recomendações.
- Calcular **Precision, Recall e F1-score** com base nos feedbacks dos usuários.
- Integrar feedback para ajustar automaticamente o modelo colaborativo e de conteúdo.
- Criar relatório de desempenho das recomendações (por usuário e geral).

---
