# 📌 Roadmap – O que Falta Implementar

## 1. Backend ✅

- ✅ Ajustar validações dos uploads: validar colunas obrigatórias (ex.: "descricao", "cpf").
- ✅ Criar rota:
  - POST /recomendar → retornar recomendações reais.
- ✅ Melhorar respostas das rotas com informações mais completas (tempo, quantidades, etc.).

  - O que foi feito:
    - Validações: Implementadas verificações de colunas obrigatórias nos uploads de CSV.
    - Rotas: Criada a rota `/recomendacao/recomendar` que integra os modelos de recomendação.
    - Respostas: Padronização das respostas da API com metadados de tempo de execução e status.

---

## 2. Pipeline (NFS → Produtos Finalizados) ✅

- ✅ Ajustar lógica TF-IDF + Fuzzy para reduzir duplicações.
- ✅ Garantir que produtos iguais fiquem sempre no mesmo cluster em `produtos_base/`.
- ✅ Tornar a pipeline **incremental** (processar só novas linhas).
- ✅ Garantir IDs determinísticos ou mapeamento consistente ao reprocessar.

  - O que foi feito:
    - Pipeline Incremental: O sistema agora verifica quais linhas são novas antes de processar.
    - IDs Determinísticos: Implementada lógica para garantir que o mesmo produto gere sempre o mesmo ID.
    - Deduplicação: Melhoria na lógica de agrupamento (clustering) usando TF-IDF e Fuzzy Matching.

---

## 3. Dataset (CSV) ✅

- ✅ Padronizar o campo `product_id` em `avaliacoes.csv`.
- ✅ Atualizar avaliações automaticamente quando IDs forem regenerados.

  - O que foi feito:
    - Padronização do product_id: Os scripts de geração (gerar_avaliacoes.py) e adição (adicionar_avaliacoes.py) já incluem o campo product_id no arquivo avaliacoes.csv. O loader.py e o engine.py também já utilizam esse campo.
    - Atualização automática: O script reprocessar_tudo.py possui a função atualizar_avaliacoes, que mapeia os IDs antigos para os novos quando o pipeline é reexecutado, garantindo a integridade dos dados.

---

## 4. Recomendador

- ✅ Implementar filtragem colaborativa (usuário e item).
- ✅ Implementar recomendação por conteúdo (TF-IDF).
- Implementar recomendador híbrido.
- Criar função explicando o motivo da recomendação.

  - Sobre o Item 4 (Recomendador), o que falta implementar é:
    - Recomendador Híbrido: Combinar as pontuações do modelo colaborativo e do modelo baseado em conteúdo para gerar uma recomendação mais robusta.
    - Explicação da Recomendação: Criar uma função que justifique ao usuário o motivo da sugestão (ex: "Recomendado porque você comprou X" ou "Similar a produtos que você avaliou bem").

---

## 5. Frontend (Streamlit) ✅

- ✅ Ajustar página de avaliação de produtos e marcas.
- ✅ Criar página de recomendações:
  - ✅ Seleciona usuário
  - ✅ Seleciona tipo de filtragem
  - ✅ Seleciona quantidade de recomendações
  - ✅ Executa cálculo
- ✅ Melhorar cores padrão na barra lateral e botões.

---

## 6. Scripts ✅

- ✅ Finalizar `reprocessar_tudo.py`:

  - ✅ Regenerar IDs sem quebrar ratings.
  - ✅ Lidar com produtos “NOT_FOUND”.
  - ✅ Fazer backup antes de sobrescrever.

- O que foi feito:
  - Fazer backup antes de sobrescrever: O script agora cria uma cópia dataset/standardized/produtos_padronizados.csv.bak antes de iniciar a limpeza e reprocessamento.

---

## 7. Diagnóstico ✅

- ✅ Verificação de clusters inconsistentes:

  - ✅ produtos duplicados dentro de um mesmo cluster.
  - ✅ produtos espalhados entre clusters diferentes.

  - O que foi feito:
    - Verificação de clusters inconsistentes: Criação do script backend/scripts/diagnostico_clusters.py.
      - Ele percorre todos os arquivos de cluster e verifica:
        - Duplicatas internas: Se o mesmo produto aparece duas vezes no mesmo arquivo.
        - Inconsistência entre clusters: Se o mesmo produto aparece em arquivos diferentes.

---

## 8. Métricas & Feedback ✅

- ✅ Implementar feedback binário (“gostou / não gostou”) nas recomendações.
- ✅ Calcular **Precision, Recall e F1-score** com base nos feedbacks dos usuários.
- ✅ Integrar feedback para ajustar automaticamente o modelo colaborativo e de conteúdo.
- ✅ Criar relatório de desempenho das recomendações (por usuário e geral).

  - O que foi feito:
    - Criação do script `gerar_relatorio_performance.py` em `backend/scripts/`.
      - Ele avalia todos os usuários com histórico suficiente.
      - Calcula métricas para os modelos (Conteúdo e Colaborativo).
      - Gera um CSV detalhado (dataset/reports/performance_report.csv) e um resumo no console.
        Para executar o script, digite no terminal: `python -m backend.scripts.gerar_relatorio_performance`

---
