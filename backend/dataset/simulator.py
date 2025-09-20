# Generate/simulate client-product ratings
import pandas as pd
import numpy as np
import os
import random

def create_purchase_simulator():
    """
    Gera um dataset de ratings (compras) simulando perfis de consumidores
    para criar correlações lógicas entre produtos.
    """
    print("Iniciando a simulação de perfis de compra...")

    # --- 1. Definir caminhos ---
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed")

    # --- 2. Carregar os datasets ---
    try:
        clients_path = os.path.join(RAW_DATA_PATH, 'clients.csv')
        products_path = os.path.join(PROCESSED_DATA_PATH, 'products_unique.csv') # Usar a lista de produtos únicos
        clients_df = pd.read_csv(clients_path)
        products_df = pd.read_csv(products_path)
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivo: {e}. Verifique os caminhos e se os arquivos existem.")
        return

    # O products_unique.csv já é limpo e único, mas garantimos que não há descrições nulas.
    products_df.dropna(subset=['PRODUCT_ID', 'DESCRICAO'], inplace=True)

    # --- 3. Definir Perfis de Consumo (cestas de produtos) ---
    # Mapeia palavras-chave na descrição dos produtos para um perfil
    print("Definindo perfis de consumo...")
    profiles = {
        "churrasco": ["CARNE", "CERVEJA", "CARVAO", "LINGUICA", "FAROFA", "FRANGO", "REFRIGERANTE"],
        "cafe_da_manha": ["CAFE", "PÃO", "LEITE", "MANTEIGA", "QUEIJO", "BISCOITO", "PRESUNTO", "IOGURTE"],
        "limpeza": ["SABAO", "DETERGENTE", "AMACIANTE", "AGUA SANITARIA", "PAPEL HIGIENICO"],
        "basicos": ["AGUA", "ARROZ", "FEIJAO", "ACUCAR", "SAL", "OLEO", "MACARRAO"],
        "massa_molho": ["MACARRAO", "MOLHO DE TOMATE", "QUEIJO RALADO"],
        "higiene": ["SHAMPOO", "SABONETE", "CREME DENTAL", "ESCOVA DENTAL"],
    }

    product_to_profile = {}
    for product_id, desc in zip(products_df['PRODUCT_ID'], products_df['DESCRICAO']):
        for profile, keywords in profiles.items():
            if any(keyword in desc.upper() for keyword in keywords):
                if profile not in product_to_profile:
                    product_to_profile[profile] = []
                product_to_profile[profile].append(product_id)
                break # Atribui ao primeiro perfil que encontrar

    # --- 4. Atribuir Perfis aos Clientes ---
    print("Atribuindo perfis de preferência aos clientes...")
    client_cpfs = clients_df['CPF'].unique()
    client_profiles = {}
    available_profiles = [p for p in product_to_profile if product_to_profile[p]] # Apenas perfis que encontraram produtos

    if not available_profiles:
        print("ERRO: Nenhum perfil de consumo encontrou produtos correspondentes. Verifique as palavras-chave e as descrições dos produtos.")
        return

    np.random.seed(25)
    for cpf in client_cpfs:
        # Cada cliente terá de 1 a 3 perfis de preferência
        num_profiles = np.random.randint(1, 4)
        client_profiles[cpf] = np.random.choice(available_profiles, size=num_profiles, replace=False).tolist()

    # --- 5. Gerar as Compras (Ratings) ---
    print("Gerando transações de compra com base nos perfis...")
    all_ratings = []
    num_transactions_per_client = 30 # Aumentando para gerar mais dados para o teste de acurácia

    for cpf, preferred_profiles in client_profiles.items():
        for _ in range(num_transactions_per_client):
            # Escolhe um dos perfis preferidos para esta "ida ao mercado"
            current_profile = np.random.choice(preferred_profiles)
            
            # Pega os produtos daquele perfil
            products_in_profile = product_to_profile.get(current_profile, [])
            if not products_in_profile:
                continue

            # Cliente compra entre 2 e 5 itens do perfil escolhido
            num_items_to_buy = np.random.randint(2, min(7, len(products_in_profile) + 1))
            products_bought_ids = np.random.choice(products_in_profile, size=num_items_to_buy, replace=False)

            # Adiciona um "ruído": 20% de chance de comprar um item aleatório fora do perfil
            if random.random() < 0.2:
                all_product_ids = products_df['PRODUCT_ID'].tolist()
                random_product = random.choice(all_product_ids)
                products_bought_ids = np.append(products_bought_ids, random_product)

            for product_id in products_bought_ids:
                # A quantidade (rating) será entre 1 e 5
                quantity = np.random.randint(1, 6)
                all_ratings.append({
                    "CPF": cpf,
                    "PRODUCT_ID": product_id,
                    "RATING": quantity
                })

    if not all_ratings:
        print("Nenhum rating foi gerado. Verifique os perfis e descrições dos produtos.")
        return

    # --- 6. Agregar e Salvar ---
    print("Agregando e salvando o dataset de ratings...")
    ratings_df = pd.DataFrame(all_ratings)

    # Agrupa para somar as quantidades, simulando múltiplas compras do mesmo item
    final_ratings_df = ratings_df.groupby(['CPF', 'PRODUCT_ID'])['RATING'].sum().reset_index()

    # Salva o dataframe final
    output_file = os.path.join(OUTPUT_PATH, 'ratings.csv')
    final_ratings_df.to_csv(output_file, index=False)

    print("\n" + "="*80)
    print(f"Arquivo 'ratings.csv' gerado com sucesso em '{OUTPUT_PATH}'!")
    print(f"Total de ratings (interações cliente-produto) criados: {len(final_ratings_df)}")
    print("\nAmostra do novo dataset de ratings:")
    print(final_ratings_df.head())
    print("="*80 + "\n")

if __name__ == "__main__":
    # Para executar este script, use o comando:
    # python backend/dataset/purchase_simulator.py
    create_purchase_simulator()