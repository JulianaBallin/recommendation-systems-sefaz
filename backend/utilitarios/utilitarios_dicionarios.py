# backend/utilitarios/utilitarios_dicionarios.py

DICIONARIO_MARCAS = {
    # Higiene / cuidados pessoais
    "dove": ["dove", "dov", "dovv"],
    "colgate": ["colgate", "colg", "colgte"],
    "neve": ["neve", "nev"],
    "nivea": ["nivea", "niv", "nivva"],

    # Alimentos
    "perdigao": ["perdigao", "perdi", "perd", "perdg"],
    "sadia": ["sadia", "sad", "sdia"],
    "pilao": ["pilao", "pil", "pila"],
    "nescau": ["nescau", "nesc", "nscau"],
    "nestle": ["nestle", "nestl", "nstl", "nest"],
    "tio joao": ["tio joao", "tjoao", "t joao", "tjoa", "t.joao"],
    "soya": ["soya", "soia", "soi"],
    "renata": ["renata", "renat", "rnt"],
    "união": ["uniao", "unia", "uni"],
    "aviacao": ["aviacao", "aviao", "aviac"],

    # Iogurtes
    "itambe": ["itambe", "itamb"],
    "batavo": ["batavo", "bat"],
    "parmalat": ["parmalat", "parma", "prmlt"],

    # Bebidas
    "coca cola": ["coca cola", "cocacola", "coca", "cola"],
    "guarana antartica": ["guarana", "antartica", "guara", "guaraná"],

    # Genérico
    "generico": ["generico", "sem marca"]
}


# backend/utilitarios/utilitarios_dicionarios.py

def detectar_marca(descricao_limpa: str) -> str:
    """
    Detecta marca com base no DICIONARIO_MARCAS.
    Se nenhuma marca for identificada, retorna 'generico'.
    """

    if not isinstance(descricao_limpa, str) or not descricao_limpa.strip():
        return "generico"

    palavras = descricao_limpa.split()

    for marca_oficial, variacoes in DICIONARIO_MARCAS.items():
        for var in variacoes:
            if var in palavras:
                return marca_oficial

    return "generico"
