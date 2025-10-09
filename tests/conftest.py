"""
conftest.py
Configura o ambiente de testes do sistema AmazIA, garantindo que os módulos
sejam corretamente importados durante a execução do pytest.
"""

import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
