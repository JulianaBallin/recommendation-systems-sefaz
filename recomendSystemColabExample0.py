import streamlit as st  # Importa a biblioteca Streamlit para criar interfaces web interativas
from math import sqrt  # Importa a função de raiz quadrada (não utilizada neste código)

# Dicionário com as avaliações dos usuários para diferentes bandas/músicas
users = {
    "Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0, "Norah Jones": 4.5, "Phoenix": 5.0, "Slightly Stoopid": 1.5, "The Strokes": 2.5, "Vampire Weekend": 2.0},
    "Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5, "Deadmau5": 4.0, "Phoenix": 2.0, "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0},
    "Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0, "Deadmau5": 1.0, "Norah Jones": 3.0, "Phoenix": 5, "Slightly Stoopid": 1.0},
    "Dan": {"Blues Traveler": 3.0, "Broken Bells": 4.0, "Deadmau5": 4.5, "Phoenix": 3.0, "Slightly Stoopid": 4.5, "The Strokes": 4.0, "Vampire Weekend": 2.0},
    "Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0, "Norah Jones": 4.0, "The Strokes": 4.0, "Vampire Weekend": 1.0},
    "Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0, "Norah Jones": 5.0, "Phoenix": 5.0, "Slightly Stoopid": 4.5, "The Strokes": 4.0, "Vampire Weekend": 4.0},
    "Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0, "Norah Jones": 3.0, "Phoenix": 5.0, "Slightly Stoopid": 4.0, "The Strokes": 5.0},
    "Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0, "Phoenix": 4.0, "Slightly Stoopid": 2.5, "The Strokes": 3.0}
}

# Função que calcula a distância de Minkowski entre dois usuários
# É uma generalização da distância de Manhattan (r=1) e Euclidiana (r=2)
def minkowski(rating1, rating2, r):
    distance = 0
    commonRatings = False
    for key in rating1:
        if key in rating2:
            distance += pow(abs(rating1[key] - rating2[key]), r)
            commonRatings = True

    if commonRatings:
        return pow(distance, 1/r)  # Retorna a raiz da soma das potências
    else:
        return 0  # Indica que não há itens em comum


# Função que encontra o vizinho mais próximo (usuário mais parecido)
def computeNearestNeighbor(username, users):
    distances = []  # Lista de tuplas (distância, nome_do_usuário)

    for user in users:
        if user != username:
            distance = minkowski(users[user], users[username], 2)  # Calcula a distância
            distances.append((distance, user))

    distances.sort()  # Ordena pela menor distância (mais semelhante primeiro)
    return distances


# Função que gera recomendações baseadas no vizinho mais próximo
def recommend(username, users):
    nearest = computeNearestNeighbor(username, users)[0][1]  # Nome do usuário mais próximo
    recommendations = []  # Lista de recomendações

    neighborRatings = users[nearest]  # Avaliações do vizinho
    userRatings = users[username]  # Avaliações do usuário

    for artist in neighborRatings:
        if artist not in userRatings:
            recommendations.append((artist, neighborRatings[artist]))  # Adiciona recomendação

    # Ordena por maior pontuação do vizinho
    return sorted(recommendations, key=lambda artistTuple: artistTuple[1], reverse=True)


# Função que monta a interface do aplicativo no Streamlit
def recommend_app():
    st.title("Sistema de Recomendação Colaborativo de Música")  # Título do app

    username = st.text_input("Digite o nome de usuário:")  # Campo de entrada para o nome

    if st.button("Recomendar Músicas"):  # Botão para gerar recomendação
        if username in users:
            recommendations = recommend(username, users)  # Gera recomendações
            st.write(f"Recomendações para {username}:")
            for recommendation in recommendations:
                st.write(f"{recommendation[0]} - Pontuação: {recommendation[1]}")  # Exibe recomendações
        else:
            st.write("Nome de usuário não encontrado. Por favor, insira um nome de usuário válido.")  # Mensagem de erro


# Função principal do programa
def main():
    recommend_app()  # Chama a interface


# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    main()