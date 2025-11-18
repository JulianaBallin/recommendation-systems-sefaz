# =========================================
# 🛠️ Makefile - AmazIA
# =========================================

# Nome do ambiente virtual
VENV = .venv

# Caminho do Python dentro do ambiente
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Diretórios a serem ignorados na listagem
IGNORE_DIRS = __pycache__|.venv|venv|seg|.mypy_cache|.pytest_cache|.git|.idea|__pypackages__

# -------------------------
# 📦 Setup inicial do projeto
# -------------------------
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Ambiente virtual criado e dependências instaladas!"

# -------------------------
# ▶️ Executar servidor
# -------------------------
run:
	$(PYTHON) -m uvicorn backend.main:app --reload

# -------------------------
# 🔥 Limpar arquivos temporários
# -------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
	@echo "🧹 Arquivos temporários removidos."

# -------------------------
# 📦 Atualizar dependências
# -------------------------
update:
	$(PIP) install --upgrade -r requirements.txt
	@echo "📦 Dependências atualizadas!"

# -------------------------
# 🗄️ Iniciar Banco de Dados
# -------------------------
db-init:
	cd backend/banco_dados && python init_db.py

# -------------------------
# 🌳 Exibir estrutura do projeto (sem caches/venv)
# -------------------------
tree:
	@echo "📁 Estrutura limpa do projeto:"
	@tree -I "$(IGNORE_DIRS)"

# -------------------------
# 🌳 Salvar estrutura do projeto em arquivo
# -------------------------
tree-save:
	@echo "📄 Salvando estrutura limpa em estrutura.txt..."
	@tree -I "$(IGNORE_DIRS)" > estrutura.txt
	@echo "✅ Arquivo 'estrutura.txt' gerado com sucesso!"

# -------------------------
# 🧰 Ajuda
# -------------------------
help:
	@echo "Comandos disponíveis:"
	@echo "  make setup       → cria venv e instala dependências"
	@echo "  make run         → executa o servidor FastAPI"
	@echo "  make clean       → remove caches e temporários"
	@echo "  make update      → atualiza dependências"
	@echo "  make db-init     → inicializa o banco de dados local"
	@echo "  make tree        → mostra estrutura do projeto"
	@echo "  make tree-save   → salva estrutura limpa em estrutura.txt"