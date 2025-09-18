# backend/utils/dictionaries.py

# Categorias
CATEGORY_MAP = {
    # Grãos e massas
    "ARROZ": "Grãos",
    "FEIJAO": "Grãos",
    "LENTILHA": "Grãos",
    "ERVILHA": "Grãos",
    "GRÃO DE BICO": "Grãos",
    "MACARRAO": "Massas",
    "MASSA": "Massas",
    "MIOJO": "Massas Instantâneas",

    # Laticínios
    "LEITE": "Laticínios",
    "QUEIJO": "Laticínios",
    "IOGURTE": "Laticínios",
    "MANTEIGA": "Laticínios",
    "REQUEIJAO": "Laticínios",
    "CREME DE LEITE": "Laticínios",
    "ZERO LAC": "Zero Lactose",
    "0 LAC": "Zero Lactose",

    # Snacks / industrializados
    "BISCOITO": "Alimento Industrializado",
    "BOLACHA": "Alimento Industrializado",
    "SALGADINHO": "Alimento Industrializado",
    "CHOCOLATE": "Doces",
    "BALA": "Doces",
    "PIRULITO": "Doces",
    "MAIONESE": "Condimentos",
    "KETCHUP": "Condimentos",
    "MOSTARDA": "Condimentos",

    # Bebidas
    "REFRIGERANTE": "Bebidas",
    "SUCOS": "Bebidas",
    "AGUA": "Bebidas",
    "ENERGETICO": "Bebidas",
    "CERVEJA": "Bebidas",
    "VINHO": "Bebidas",

    # Óleos e gorduras
    "OLEO": "Óleos e Gorduras",
    "AZEITE": "Óleos e Gorduras",
    "MARGARINA": "Óleos e Gorduras",

    # Higiene e limpeza
    "AMACIANTE": "Limpeza",
    "SABAO": "Limpeza",
    "DETERGENTE": "Limpeza",
    "ALCOOL": "Limpeza",
    "DESINFETANTE": "Limpeza",
    "SHAMPOO": "Higiene",
    "SABONETE": "Higiene",
    "CREME DENTAL": "Higiene",
    "PAPEL HIGIENICO": "Higiene",

    # Proteínas
    "FRANGO": "Proteínas",
    "CARNE": "Proteínas",
    "PEIXE": "Proteínas",
    "PORCO": "Proteínas",
    "LINGUICA": "Proteínas",
    "OVO": "Proteínas",

    # Fitness / saudáveis
    "WHEY": "Fitness",
    "PROTEINA": "Fitness",
    "BARRA CEREAL": "Fitness",
    "INTEGRAL": "Fitness",
    "LIGHT": "Fitness",
    "DIET": "Fitness",

    # Default
    "INDEFINIDO": "Indefinido"
}


# Marcas
BRAND_MAP = [
    # Bebidas
    "COCA-COLA", "PEPSI", "FANTA", "GUARANA ANTARCTICA", "SCHWEPPES",
    "SKOL", "BRAHMA", "ANTARCTICA", "BOHEMIA", "HEINEKEN", "AMSTEL",
    "RED BULL", "MONSTER",

    # Carnes / proteínas
    "SADIA", "PERDIGAO", "SEARA", "FRIBOI", "MARFRIG", "MINERVA",

    # Grãos e massas
    "TIO JOAO", "CAMIL", "URBANO", "PILAR", "RENATA", "ADRIELLE",

    # Laticínios
    "NESTLE", "ITALAC", "PIRACANJUBA", "BETANIA", "NINHO",
    "VERDE CAMPO", "ITAMBÉ",

    # Doces e snacks
    "LACTA", "GAROTO", "HERSHEYS", "FERRERO", "MARS", "ARCOR",
    "TRAKINAS", "CLUB SOCIAL", "BIS", "KITKAT",

    # Limpeza
    "OMO", "YPE", "BRILUX", "MINUANO", "LIMPOL",

    # Higiene
    "COLGATE", "ORAL-B", "DOVE", "PALMOLIVE", "NIVEA", "LUX"
]


# Bairros e zonas
BAIRRO_ZONA_MAP = {
    "FLORES": "Centro-Sul",
    "PARQUE 10 DE NOVEMBRO": "Centro-Sul",
    "ADRIANÓPOLIS": "Centro-Sul",
    "ALEIXO": "Centro-Sul",
    "NOSSA SENHORA DAS GRAÇAS": "Centro-Sul",
    "CENTRO": "Sul",
    "APARECIDA": "Sul",
    "MORRO DA LIBERDADE": "Sul",
    "PRAÇA 14 DE JANEIRO": "Sul",
    "EDUARDO GOMES": "Oeste",
    "ALVORADA": "Oeste",
    "SÃO JORGE": "Oeste",
    "PLANALTO": "Oeste",
    "CIDADE NOVA": "Norte",
    "COLÔNIA SANTO ANTÔNIO": "Norte",
    "COLÔNIA TERRA NOVA": "Norte",
    "MONTE DAS OLIVEIRAS": "Norte",
    "NOVA CIDADE": "Norte",
    "REDENÇÃO": "Norte",
    "JORGE TEIXEIRA": "Leste",
    "TANCREDO NEVES": "Leste",
    "ZUMBI DOS PALMARES": "Leste",
    "SÃO JOSÉ OPERÁRIO": "Leste"
}

if __name__ == "__main__":
    print("CATEGORY_MAP:", len(CATEGORY_MAP), "categorias")
    print("BRAND_MAP:", len(BRAND_MAP), "marcas")
    print("BAIRRO_ZONA_MAP:", len(BAIRRO_ZONA_MAP), "bairros")
