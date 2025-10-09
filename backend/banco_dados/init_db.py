"""
init_db.py
Cria todas as tabelas do banco de dados SQLite do sistema AmazIA.

Execução:
    python backend/banco_dados/init_db.py
"""

from sqlalchemy import text

from backend.banco_dados.conexao import obter_engine

def criar_tabelas():
    """
    Cria as tabelas principais do banco, caso ainda não existam.
    """
    engine = obter_engine()
    with engine.connect() as conexao:
        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS CATEGORIA (
            Id_Categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            Descricao_Categoria TEXT NOT NULL
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS MARCA (
            Id_Marca INTEGER PRIMARY KEY AUTOINCREMENT,
            Descricao_Marca TEXT NOT NULL
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS PRODUTOS (
            Id_Produto INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_Categoria INTEGER NOT NULL,
            Id_Marca INTEGER NOT NULL,
            Descricao_Produto TEXT NOT NULL,
            FOREIGN KEY (Id_Categoria) REFERENCES CATEGORIA(Id_Categoria),
            FOREIGN KEY (Id_Marca) REFERENCES MARCA(Id_Marca)
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS CLIENTES (
            Cpf TEXT PRIMARY KEY,
            Nome TEXT NOT NULL,
            DataNasc TEXT,
            Genero TEXT,
            Cep TEXT
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS SUPERMERCADOS (
            Id_Supermercado TEXT PRIMARY KEY,
            Cnpj TEXT NOT NULL,
            Nome TEXT NOT NULL,
            Cep TEXT NOT NULL,
            Bairro TEXT,
            Rua TEXT,
            Num TEXT
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS NFS (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_Supermercado TEXT NOT NULL,
            Id_Produto INTEGER NOT NULL,
            Preco REAL NOT NULL,
            TimeStamp_Registro TEXT NOT NULL,
            FOREIGN KEY (Id_Supermercado) REFERENCES SUPERMERCADOS(Id_Supermercado),
            FOREIGN KEY (Id_Produto) REFERENCES PRODUTOS(Id_Produto)
        );
        """))

        conexao.execute(text("""
        CREATE TABLE IF NOT EXISTS AVALIACOES_BUSCA (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Cpf_Cliente TEXT NOT NULL,
            Id_Categoria INTEGER,
            Avaliacao_Categoria INTEGER,
            Qtd_Busca_Categoria INTEGER,
            Id_Marca INTEGER,
            Avaliacao_Marca INTEGER,
            Qtd_Busca_Marca INTEGER,
            Id_Produto INTEGER,
            Avaliacao_Produto INTEGER,
            Qtd_Busca_Produto INTEGER,
            Cnpj_Supermercado TEXT,
            Avaliacao_Supermercado INTEGER,
            Qtd_Busca_Supermercado INTEGER,
            FOREIGN KEY (Cpf_Cliente) REFERENCES CLIENTES(Cpf),
            FOREIGN KEY (Id_Categoria) REFERENCES CATEGORIA(Id_Categoria),
            FOREIGN KEY (Id_Marca) REFERENCES MARCA(Id_Marca),
            FOREIGN KEY (Id_Produto) REFERENCES PRODUTOS(Id_Produto)
        );
        """))

    print("✅ Banco AmazIA criado e pronto para uso.")

if __name__ == "__main__":
    criar_tabelas()
