import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances


class CollaborativeRecommender:
    """
    Implementa a lógica de recomendação baseada em filtragem colaborativa
    (User-Based e Item-Based) usando a Correlação de Pearson.
    """

    def __init__(self, ratings_df: pd.DataFrame, products_df: pd.DataFrame):
        """
        Inicializa o recomendador com os dataframes necessários.

        Args:
            ratings_df (pd.DataFrame): DataFrame com colunas ['CPF', 'PRODUCT_ID', 'RATING'].
            products_df (pd.DataFrame): DataFrame com detalhes dos produtos, incluindo ['PRODUCT_ID', 'DESCRICAO'].
        """
        # Garante que os IDs sejam do tipo string para evitar problemas de junção (merge)
        self.ratings_df = ratings_df.copy()
        self.products_df = products_df.copy()

        self.ratings_df['PRODUCT_ID'] = self.ratings_df['PRODUCT_ID'].astype(str)
        self.products_df['PRODUCT_ID'] = self.products_df['PRODUCT_ID'].astype(str)

        # Inicializa os dataframes como vazios. Serão preenchidos pelo método train().
        self.user_item_matrix = pd.DataFrame()
        self.user_similarity_df = pd.DataFrame()
        self.item_similarity_df = pd.DataFrame()

    def train(self):
        """
        Prepara a matriz de utilidade (usuário-item) e a matriz de similaridade entre usuários.
        Este método "treina" o modelo com os dados fornecidos no construtor.
        """
        print("Criando a matriz usuário-item...")
        # Cria a matriz de utilidade, onde linhas são usuários (CPF) e colunas são produtos (PRODUCT_ID)
        self.user_item_matrix = self.ratings_df.pivot_table(
            index='CPF',
            columns='PRODUCT_ID',
            values='RATING'
        ).fillna(0)

        print("Calculando a similaridade entre usuários (Correlação de Pearson)...")
        # Calcula a distância de correlação (1 - Pearson) e converte para similaridade
        # Usamos pairwise_distances por ser computacionalmente eficiente
        user_similarity_matrix = 1 - pairwise_distances(self.user_item_matrix.values, metric='correlation')

        # Converte a matriz de similaridade para um DataFrame para fácil consulta
        self.user_similarity_df = pd.DataFrame(
            user_similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        print("Calculando a similaridade entre itens (Similaridade de Cosseno)...")
        # Para a similaridade de itens (Item-Item), usamos a Similaridade de Cosseno.
        # Primeiro, binarizamos a matriz: 1 se o cliente comprou o produto, 0 caso contrário.
        item_user_matrix_binary = (self.user_item_matrix.T > 0).astype(bool)
        
        # A distância de Cosseno é 1 - similaridade. Então, para obter a similaridade, fazemos 1 - distância.
        item_similarity_matrix = 1 - pairwise_distances(item_user_matrix_binary.values, metric='cosine')

        self.item_similarity_df = pd.DataFrame(
            item_similarity_matrix,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns
        )

    def get_similar_users(self, user_cpf: str, n: int = 5):
        """
        Encontra os 'n' usuários mais similares a um usuário específico.

        Args:
            user_cpf (str): O CPF do usuário de referência.
            n (int): O número de usuários similares a retornar.

        Returns:
            list: Uma lista de tuplas (cpf_similar, pontuacao_similaridade).
        """
        if user_cpf not in self.user_similarity_df.index:
            return []

        # Obtém a série de similaridades para o usuário, remove o próprio usuário e ordena
        similar_users = self.user_similarity_df[user_cpf].drop(user_cpf).sort_values(ascending=False)

        return list(similar_users.head(n).items())

    def recommend_products_for_user(self, user_cpf: str, n: int = 10):
        """
        Recomenda 'n' produtos para um usuário com base nos gostos de usuários similares.

        Args:
            user_cpf (str): O CPF do usuário para quem gerar recomendações.
            n (int): O número de produtos a recomendar.

        Returns:
            pd.DataFrame: DataFrame com os produtos recomendados e seus detalhes.
        """
        if self.user_item_matrix.empty:
            raise RuntimeError("O modelo não foi treinado. Chame o método `train()` primeiro.")

        if user_cpf not in self.user_item_matrix.index:
            return pd.DataFrame(columns=['PRODUCT_ID', 'DESCRICAO', 'predicted_rating'])

        # 1. Encontra os usuários mais similares (vizinhos)
        similar_users = self.user_similarity_df[user_cpf].drop(user_cpf).sort_values(ascending=False)
        # Filtra apenas vizinhos com similaridade positiva
        similar_users = similar_users[similar_users > 0]

        if similar_users.empty:
            return pd.DataFrame(columns=['PRODUCT_ID', 'DESCRICAO', 'predicted_rating'])

        # 2. Identifica os produtos que o usuário alvo ainda não comprou
        target_user_items = self.user_item_matrix.loc[user_cpf]
        unrated_items = target_user_items[target_user_items == 0].index

        # 3. Calcula a pontuação prevista para cada produto não comprado
        # Ponderando as avaliações dos vizinhos pela similaridade
        predicted_ratings = {}
        for item in unrated_items:
            # Pega as avaliações dos vizinhos para este item
            neighbor_ratings = self.user_item_matrix.loc[similar_users.index, item]
            # Pega a similaridade desses vizinhos
            neighbor_similarities = similar_users
            
            # Numerador: soma(similaridade * rating do vizinho)
            weighted_sum = (neighbor_similarities * neighbor_ratings).sum()
            # Denominador: soma(similaridade dos vizinhos que avaliaram o item)
            similarity_sum = neighbor_similarities[neighbor_ratings > 0].sum()
            
            if similarity_sum > 0:
                predicted_ratings[item] = weighted_sum / similarity_sum

        # 4. Formata e retorna o resultado
        recommendations_df = pd.DataFrame.from_dict(predicted_ratings, orient='index', columns=['predicted_rating'])
        recommendations_df = recommendations_df.sort_values('predicted_rating', ascending=False).head(n)
        
        # Junta com os detalhes dos produtos
        recommendations_df = recommendations_df.merge(
            self.products_df,
            left_index=True,
            right_on='PRODUCT_ID'
        )

        return recommendations_df[['PRODUCT_ID', 'DESCRICAO', 'predicted_rating']]

    def recommend_similar_products(self, product_id: str, n: int = 10):
        """
        Encontra 'n' produtos mais similares a um produto específico (Item-Item).

        Args:
            product_id (int): O ID do produto de referência.
            n (int): O número de produtos similares a retornar.

        Returns:
            pd.DataFrame: DataFrame com os produtos similares e seus detalhes.
        """
        if self.item_similarity_df.empty:
            raise RuntimeError("O modelo não foi treinado. Chame o método `train()` primeiro.")

        # Garante que o ID do produto seja string para a busca
        product_id = str(product_id)

        if product_id not in self.item_similarity_df.index:
            return pd.DataFrame(columns=['PRODUCT_ID', 'DESCRICAO', 'similarity_score'])

        # Obtém a série de similaridades para o produto, remove o próprio produto e ordena
        similar_items = self.item_similarity_df[product_id].drop(product_id).sort_values(ascending=False)

        # Pega os 'n' produtos mais similares
        top_n_similar_items = similar_items.head(n)

        # Formata o resultado em um DataFrame e renomeia as colunas
        similar_products_df = pd.DataFrame(top_n_similar_items).reset_index()
        similar_products_df.columns = ['PRODUCT_ID', 'similarity_score']

        # Junta com os detalhes dos produtos para obter a descrição
        recommendations = similar_products_df.merge(self.products_df[['PRODUCT_ID', 'DESCRICAO']], on='PRODUCT_ID')

        # Filtra para remover qualquer produto que tenha a mesma descrição do produto original
        original_product_description = self.products_df.loc[self.products_df['PRODUCT_ID'] == product_id, 'DESCRICAO'].iloc[0]
        recommendations = recommendations[recommendations['DESCRICAO'] != original_product_description]

        # Garante que o resultado final ainda tenha no máximo 'n' itens após a filtragem
        recommendations = recommendations.head(n)

        return recommendations[['PRODUCT_ID', 'DESCRICAO', 'similarity_score']]