"""
test_validacao_dados.py
Verifica o funcionamento das funções de validação do módulo
backend/utilitarios/validacao_dados.py, garantindo a integridade dos dados
antes da inserção no banco AmazIA.
"""

import sys
import os
import pytest

# Garante que o backend seja importável
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.utilitarios.validacao_dados import (
    validar_cpf,
    validar_nome,
    validar_data_nascimento,
    validar_genero,
    validar_cep_manaus,
    validar_cnpj,
    validar_descricao,
    validar_texto_simples,
    validar_preco,
    validar_timestamp,
    validar_nota_avaliacao,
)

# ============================================================
# CPF
# ============================================================

def test_validar_cpf_valido():
    """Deve retornar True para CPF válido."""
    assert validar_cpf("529.982.247-25") is True

def test_validar_cpf_invalido():
    """Deve retornar False para CPF inválido."""
    assert validar_cpf("123.456.789-00") is False

def test_validar_cpf_vazio():
    """Deve retornar False para campo vazio."""
    assert validar_cpf("") is False

# ============================================================
# Nome
# ============================================================

def test_validar_nome_valido():
    """Deve aceitar nome apenas com letras e espaços."""
    assert validar_nome("Juliana Lima") is True

def test_validar_nome_invalido():
    """Deve recusar nome com números."""
    assert validar_nome("Juliana123") is False

# ============================================================
# Data de nascimento
# ============================================================

def test_validar_data_nascimento_formatos_validos():
    """Deve aceitar datas nos formatos DD/MM/AAAA e AAAA-MM-DD."""
    assert validar_data_nascimento("05/04/1998") is True
    assert validar_data_nascimento("1998-04-05") is True

def test_validar_data_nascimento_invalida():
    """Deve retornar False para data inexistente."""
    assert validar_data_nascimento("31/02/2020") is False

# ============================================================
# Gênero
# ============================================================

@pytest.mark.parametrize("valor", ["F", "M", "O", "f", "m", "o"])
def test_validar_genero_valido(valor):
    """Deve aceitar apenas F, M ou O (maiúsculos ou minúsculos)."""
    assert validar_genero(valor) is True

@pytest.mark.parametrize("valor", ["X", "", None])
def test_validar_genero_invalido(valor):
    """Deve recusar valores fora do padrão."""
    assert validar_genero(valor) is False

# ============================================================
# CEP (Manaus-AM)
# ============================================================

def test_validar_cep_manaus_valido():
    """Deve aceitar CEPs dentro da faixa de Manaus (69000-000 a 69099-999)."""
    assert validar_cep_manaus("69077-200") is True

def test_validar_cep_manaus_invalido():
    """Deve recusar CEPs fora da faixa."""
    assert validar_cep_manaus("68900-000") is False

# ============================================================
# CNPJ
# ============================================================

def test_validar_cnpj_valido():
    """Deve aceitar CNPJ com 14 dígitos."""
    assert validar_cnpj("12.345.678/0001-95") is True

def test_validar_cnpj_invalido():
    """Deve recusar CNPJ com menos de 14 dígitos."""
    assert validar_cnpj("12345678") is False

# ============================================================
# Descrição, marca e categoria
# ============================================================

def test_validar_descricao_valida():
    """Deve aceitar descrição textual até 150 caracteres."""
    assert validar_descricao("Sabão em pó Omo Lavagem Perfeita 800g") is True

def test_validar_descricao_vazia():
    """Deve recusar campo vazio."""
    assert validar_descricao("") is False

def test_validar_texto_simples_valido():
    """Deve aceitar texto apenas com letras."""
    assert validar_texto_simples("Limpeza") is True

def test_validar_texto_simples_invalido():
    """Deve recusar texto com números."""
    assert validar_texto_simples("Categoria1") is False

# ============================================================
# Preço e Timestamp
# ============================================================

def test_validar_preco_valido():
    """Deve aceitar preço real positivo."""
    assert validar_preco(12.50) is True
    assert validar_preco("8.99") is True

def test_validar_preco_invalido():
    """Deve recusar preços negativos ou não numéricos."""
    assert validar_preco(-1) is False
    assert validar_preco("abc") is False

def test_validar_timestamp_valido():
    """Deve aceitar timestamps válidos."""
    assert validar_timestamp("2025-10-07 13:45:00") is True

def test_validar_timestamp_invalido():
    """Deve recusar formatos inválidos."""
    assert validar_timestamp("07/10/2025 13:45") is False

# ============================================================
# Notas de Avaliação
# ============================================================

@pytest.mark.parametrize("nota", [0, 3, 5, None])
def test_validar_nota_avaliacao_valida(nota):
    """Deve aceitar notas entre 0 e 5, ou None."""
    assert validar_nota_avaliacao(nota) is True

@pytest.mark.parametrize("nota", [-1, 6, "abc"])
def test_validar_nota_avaliacao_invalida(nota):
    """Deve recusar notas fora do intervalo ou não numéricas."""
    assert validar_nota_avaliacao(nota) is False
