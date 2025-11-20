import pandas as pd
import random
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Gerar dataset simulado de avaliações.")
    parser.add_argument("--qtd", type=int, default=200, help="Quantidade de avaliações a gerar (padrão: 20)")
    args = parser.parse_args()
    
    qtd = args.qtd
    
    # Caminhos dos arquivos
    usuarios_path = "dataset/raw/usuarios_simulados.csv"
    produtos_path = "dataset/standardized/produtos_padronizados.csv"
    output_path = "dataset/raw/avaliacoes.csv"
    
    # Verificar existência dos arquivos base
    if not os.path.exists(usuarios_path):
        print(f"❌ Erro: Arquivo de usuários não encontrado: {usuarios_path}")
        return
        
    if not os.path.exists(produtos_path):
        print(f"❌ Erro: Arquivo de produtos não encontrado: {produtos_path}")
        return
        
    print("Carregando dados...")
    df_usuarios = pd.read_csv(usuarios_path)
    df_produtos = pd.read_csv(produtos_path)
    
    if df_usuarios.empty:
        print("❌ Erro: Arquivo de usuários está vazio.")
        return
        
    if df_produtos.empty:
        print("❌ Erro: Arquivo de produtos está vazio.")
        return
        
    print(f"Gerando {qtd} avaliações simuladas...")
    
    avaliacoes = []
    
    for _ in range(qtd):
        # Escolher usuário aleatório
        usuario = df_usuarios.sample(1).iloc[0]
        
        # Escolher produto aleatório
        produto = df_produtos.sample(1).iloc[0]
        
        # Gerar avaliações aleatórias (1 a 5)
        # Peso maior para notas altas para simular dados mais realistas (opcional, mas bom)
        notas = [1, 2, 3, 4, 5]
        pesos = [0.1, 0.1, 0.2, 0.3, 0.3] # Tendência a gostar
        
        avaliacao_desc = random.choices(notas, weights=pesos, k=1)[0]
        avaliacao_marca = random.choices(notas, weights=pesos, k=1)[0]
        
        avaliacoes.append({
            "nome_usuario": usuario["nome"],
            "cpf": usuario["cpf"],
            "descricao_produto": produto["descricao"],
            "avaliacao_descricao": avaliacao_desc,
            "marca_produto": produto["marca"],
            "avaliacao_marca": avaliacao_marca
        })
        
    df_avaliacoes = pd.DataFrame(avaliacoes)
    
    # Salvar arquivo
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_avaliacoes.to_csv(output_path, index=False)
    
    print(f"✅ Arquivo gerado com sucesso: {output_path}")
    print(df_avaliacoes.head())

if __name__ == "__main__":
    main()
