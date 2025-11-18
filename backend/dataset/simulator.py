import pandas as pd
import numpy as np
import random
from backend.dataset import loader

class RatingSimulator:
    """
    Simula a geração de avaliações de produtos por clientes para enriquecer o dataset.
    """

    def __init__(self):
        print("Iniciando o simulador...")
        self.clients = loader.load_raw_clients()
        self.products = loader.load_derived_products()
        self.ratings = loader.load_ratings()

        if self.clients.empty or self.products.empty:
            raise ValueError("Clientes e produtos precisam ser carregados para a simulação.")

        # Garante que todos os CPFs tenham 11 dígitos, adicionando zeros à esquerda se necessário.
        # Esta é uma camada de segurança para corrigir CPFs que perderam o zero inicial.
        self.clients['CPF'] = self.clients['CPF'].astype(str).str.zfill(11)

        self.client_personas = self._create_client_personas()
        print(f"Simulador pronto. {len(self.clients)} clientes e {len(self.products)} produtos carregados.")

    def _create_client_personas(self):
        """
        Cria 'personas' para cada cliente, atribuindo preferências aleatórias
        por categorias e marcas para gerar avaliações mais coerentes.
        """
        print("Criando personas de clientes baseadas em perfis...")
        personas = {}
        available_categories = self.products['CATEGORIA'].dropna().unique().tolist()
        available_brands = self.products['MARCA'].dropna().unique().tolist()

        # Perfis de consumidor predefinidos
        PERSONA_TEMPLATES = {
            'familia': {'fav_cats': ['PADARIA', 'LATICINIOS', 'LIMPEZA'], 'dislike_cats': ['BEBIDAS ALCOOLICAS']},
            'saudavel': {'fav_cats': ['HORTIFRUTI', 'CARNES'], 'dislike_cats': ['ALIMENTO INDUSTRIALIZADO']},
            'jovem_pratico': {'fav_cats': ['ALIMENTO INDUSTRIALIZADO', 'BEBIDAS NAO ALCOOLICAS'], 'dislike_cats': ['HORTIFRUTI']},
            'churrasqueiro': {'fav_cats': ['CARNES', 'BEBIDAS ALCOOLICAS'], 'dislike_cats': ['PADARIA']}
        }
        template_keys = list(PERSONA_TEMPLATES.keys())

        for cpf in self.clients['CPF']:
            # Atribui um perfil base para o cliente
            template_key = random.choice(template_keys)
            template = PERSONA_TEMPLATES[template_key]
            
            persona = {'categories': {}, 'brands': {}}

            # Define afinidades com base no template
            for cat in template['fav_cats']:
                if cat in available_categories:
                    persona['categories'][cat] = random.uniform(0.8, 1.5) # Gosta muito
            for cat in template['dislike_cats']:
                if cat in available_categories:
                    persona['categories'][cat] = random.uniform(-1.5, -0.8) # Não gosta

            # Adiciona uma preferência de marca aleatória para individualizar
            if available_brands:
                fav_brand = random.choice(available_brands)
                persona['brands'][fav_brand] = random.uniform(0.5, 1.0)

            personas[cpf] = persona
        return personas

    def _generate_single_rating(self, client_cpf, product_id):
        """
        Gera uma única avaliação com base na persona do cliente e no produto.
        """
        persona = self.client_personas.get(client_cpf)
        product = self.products[self.products['ID'] == product_id].iloc[0]

        base_rating = 3 # Ponto de partida neutro

        # Ajusta a nota com base nas afinidades da persona
        if persona:
            base_rating += persona['categories'].get(product['CATEGORIA'], 0) * 1.5 # Aumenta o impacto da categoria
            base_rating += persona['brands'].get(product['MARCA'], 0) * 1.2   # Aumenta o impacto da marca
        
        # Adiciona um pouco de ruído para não ser determinístico
        # O ruído agora é menos frequente, para fortalecer o sinal da persona.
        noise = random.choice([-1, 0, 0, 0, 1])
        final_rating = round(base_rating) + noise

        # Garante que a nota final esteja entre 1 e 5
        return int(max(1, min(5, final_rating)))

    def generate_new_ratings(self, num_ratings: int):
        """
        Gera um lote de novas avaliações e as salva no arquivo.
        """
        print(f"Gerando {num_ratings} novas avaliações...")
        new_ratings = []
        
        # Cria um set de (cpf, produto_id) para checagem rápida de duplicatas
        existing_pairs = set(
            tuple(row) for row in self.ratings[['CPF_CLIENTE', 'ID_PRODUTO']].itertuples(index=False)
        )

        attempts = 0
        while len(new_ratings) < num_ratings and attempts < num_ratings * 5:
            attempts += 1
            
            client_cpf = random.choice(self.clients['CPF'].tolist())
            product_id = random.choice(self.products['ID'].tolist())

            # Evita gerar uma avaliação que já existe
            if (client_cpf, str(product_id)) in existing_pairs:
                continue

            rating_value = self._generate_single_rating(client_cpf, product_id)

            new_entry = {
                "CPF_CLIENTE": client_cpf,
                "ID_PRODUTO": product_id,
                "RATING_DESCRICAO": rating_value,
                "RATING_CATEGORIA": None, # Simulador foca na avaliação principal
                "RATING_MARCA": None,
            }
            new_ratings.append(new_entry)
            existing_pairs.add((client_cpf, str(product_id)))

        if not new_ratings:
            print("Nenhuma nova avaliação foi gerada. O dataset pode estar saturado.")
            return 0

        # Concatena as novas avaliações com as existentes e salva
        new_ratings_df = pd.DataFrame(new_ratings)
        updated_ratings = pd.concat([self.ratings, new_ratings_df], ignore_index=True)
        
        # Usa a função do loader para garantir a consistência e salvar
        loader.save_ratings(updated_ratings)

        added_count = len(new_ratings)
        print("-" * 30)
        print(f"✅ Simulação concluída!")
        print(f"Adicionadas {added_count} novas avaliações.")
        print(f"Total de avaliações agora: {len(updated_ratings)}")
        print("-" * 30)
        return added_count
