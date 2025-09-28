import sys
import os
from backend.dataset.simulator import RatingSimulator

def main():
    """
    Ponto de entrada para executar o simulador de avaliações.
    Uso: python run_simulator.py [numero_de_avaliacoes]
    """
    # Define um número padrão de avaliações a serem geradas
    num_ratings_to_generate = 350

    if len(sys.argv) > 1:
        try:
            num_ratings_to_generate = int(sys.argv[1])
        except ValueError:
            print("Argumento inválido. Por favor, forneça um número inteiro.")
            return

    simulator = RatingSimulator()
    added_count = simulator.generate_new_ratings(num_ratings_to_generate)

    # Se novos dados foram gerados, remove o arquivo de parâmetros para forçar a re-otimização
    if added_count > 0:
        params_file = 'data/models/best_svd_params.json'
        if os.path.exists(params_file):
            os.remove(params_file)
            print(f"\nArquivo de parâmetros '{params_file}' removido para forçar a re-otimização do modelo.")

    if added_count < num_ratings_to_generate:
        print("\n⚠️  Aviso: O número de avaliações geradas foi menor que o solicitado.")
        print("Isso pode indicar que o dataset está próximo da saturação (poucas combinações de cliente-produto restantes).")

if __name__ == "__main__":
    main()
