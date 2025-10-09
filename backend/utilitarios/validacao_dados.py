"""
validacao_dados.py
Valida os dados dos arquivos CSV antes da inserção no banco de dados AmazIA.

Cada função retorna True/False ou o dado corrigido, dependendo do contexto.
Mensagens de sucesso/erro podem ser exibidas no Streamlit via mensagens_ui.
"""

import re
from datetime import datetime

# =============================
# 🔹 CLIENTES
# =============================

def validar_cpf(cpf: str) -> bool:
    """Verifica se o CPF possui formato válido e apenas dígitos numéricos."""
    cpf = re.sub(r'\D', '', str(cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digito(cpf, peso):
        soma = sum(int(d) * p for d, p in zip(cpf[:peso - 1], range(peso, 1, -1)))
        dig = (soma * 10) % 11
        return '0' if dig == 10 else str(dig)

    return cpf[-2:] == calc_digito(cpf, 10) + calc_digito(cpf, 11)


def validar_nome(nome: str) -> bool:
    """Verifica se o nome contém apenas letras e espaços."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", str(nome)))


def validar_data_nascimento(data: str) -> bool:
    """Verifica se a data está em formato válido (DD/MM/AAAA ou AAAA-MM-DD)."""
    try:
        if "/" in data:
            datetime.strptime(data, "%d/%m/%Y")
        else:
            datetime.strptime(data, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validar_genero(valor: str) -> bool:
    """Verifica se o gênero é válido (F, M ou O)."""
    return str(valor).upper() in ["F", "M", "O"]


def validar_cep_manaus(cep: str) -> bool:
    """
    Verifica se o CEP pertence ao intervalo de Manaus-AM.
    Faixa principal: 69000-000 a 69099-999.
    """
    cep = re.sub(r'\D', '', str(cep))
    return cep.isdigit() and 69000000 <= int(cep) <= 69099999


# =============================
# 🔹 SUPERMERCADOS
# =============================

def validar_cnpj(cnpj: str) -> bool:
    """Valida formato de CNPJ (apenas checagem estrutural simples)."""
    cnpj = re.sub(r'\D', '', str(cnpj))
    return len(cnpj) == 14


# =============================
# 🔹 PRODUTOS, CATEGORIAS E MARCAS
# =============================

def validar_descricao(texto: str, max_len: int = 150) -> bool:
    """Verifica se o texto de descrição é válido e dentro do limite."""
    if not isinstance(texto, str) or len(texto.strip()) == 0:
        return False
    return len(texto.strip()) <= max_len


def validar_texto_simples(texto: str) -> bool:
    """Verifica se contém apenas letras (para marca/categoria)."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", str(texto)))


# =============================
# 🔹 NFS / AVALIAÇÕES
# =============================

def validar_preco(preco) -> bool:
    """Verifica se o preço é um número real positivo."""
    try:
        return float(preco) > 0
    except Exception:
        return False


def validar_timestamp(valor: str) -> bool:
    """Verifica se o timestamp segue formato reconhecido (AAAA-MM-DD HH:MM:SS)."""
    try:
        datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
        return True
    except Exception:
        return False


def validar_nota_avaliacao(nota) -> bool:
    """Verifica se a nota é None ou um valor inteiro entre 0 e 5."""
    if nota is None:
        return True
    try:
        valor = int(nota)
        return 0 <= valor <= 5
    except Exception:
        return False
