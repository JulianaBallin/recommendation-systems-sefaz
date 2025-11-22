import random
import pandas as pd
import argparse
import os

def gerar_cpf():
    """Gera um CPF válido."""
    cpf = [random.randint(0, 9) for _ in range(9)]

    # Primeiro dígito verificador
    soma = sum(val * (10 - idx) for idx, val in enumerate(cpf))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    cpf.append(d1)

    # Segundo dígito verificador
    soma = sum(val * (11 - idx) for idx, val in enumerate(cpf))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    cpf.append(d2)

    return "".join(map(str, cpf))

def gerar_nome():
    """Gera um nome aleatório."""
    nomes = [
        "Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Julia",
        "Lucas", "Mariana", "Nicolas", "Olivia", "Pedro", "Rafaela", "Samuel", "Tatiana", "Vinicius", "Yasmin",
        "Andre", "Beatriz", "Caio", "Diana", "Felipe", "Gabriela", "Henrique", "Isabela", "Joao", "Larissa",
        "Matheus", "Natalia", "Otavio", "Patricia", "Renato", "Sofia", "Thiago", "Vitoria", "William", "Zoe"
    ]
    sobrenomes = [
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
        "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
        "Rocha", "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado", "Mendes", "Freitas",
        "Cardoso", "Ramos", "Goncalves", "Santana", "Teixeira"
    ]
    
    nome = random.choice(nomes)
    sobrenome1 = random.choice(sobrenomes)
    sobrenome2 = random.choice(sobrenomes)
    
    # Evitar sobrenomes repetidos (ex: Silva Silva)
    while sobrenome2 == sobrenome1:
        sobrenome2 = random.choice(sobrenomes)
        
    return f"{nome} {sobrenome1} {sobrenome2}"

def main():
    parser = argparse.ArgumentParser(description="Gerar dados simulados de clientes.")
    parser.add_argument("--qtd", type=int, default=20, help="Quantidade de clientes a gerar (padrão: 20)")
    args = parser.parse_args()
    
    qtd = args.qtd
    print(f"Gerando {qtd} clientes simulados...")
    
    dados = []
    cpfs_gerados = set()
    
    while len(dados) < qtd:
        cpf = gerar_cpf()
        
        # Garantir unicidade do CPF no lote gerado
        if cpf in cpfs_gerados:
            continue
            
        cpfs_gerados.add(cpf)
        
        dados.append({
            "cpf": cpf,
            "nome": gerar_nome()
        })
    
    df = pd.DataFrame(dados)
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset/processado"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "usuarios.csv")
    
    df.to_csv(output_path, index=False)
    print(f"✅ Arquivo gerado com sucesso: {output_path}")
    print(df.head())

if __name__ == "__main__":
    main()
