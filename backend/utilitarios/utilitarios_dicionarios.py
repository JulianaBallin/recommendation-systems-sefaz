# backend/utilitarios/utilitarios_dicionarios.py

DICIONARIO_MARCAS = {
    # Higiene / cuidados pessoais
    "dove": ["dove", "dov", "dovv"],
    "colgate": ["colgate", "colg", "colgte"],
    "neve": ["neve", "nev"],
    "nivea": ["nivea", "niv", "nivva"],
    "palmolive": ["palmolive", "palmol", "palmoliv", "palm"],
    "flor de lotus": ["flor de lotus", "flor", "flor de lotus", "flor lotus"],
    
    
    # Alimentos
    "perdigao": ["perdigao", "perdi", "perd", "perdg"],
    "sadia": ["sadia", "sad", "sdia"],
    "pilao": ["pilao", "pil", "pila", "pilão"],
    "nescau": ["nescau", "nesc", "nscau"],
    "nestle": ["nestle", "nestl", "nstl", "nest"],
    "tio joão": ["tio", "tio joao", "tjoao", "t joao", "tjoa", "t.joao"],
    "soya": ["soya", "soia", "soi"],
    "renata": ["renata", "renat", "rnt"],
    "união": ["uniao", "unia", "uni"],
    "aviacao": ["aviacao", "aviao", "aviac"],
    "concord": ["concord", "conc"],
    "dubom": ["dubom", "dub"],
    "scrush": ["scrush", "scr"],
    "mococa": ["mococa", "moc"],
    "trigolino": ["trigolino", "trig"],
    "seara": ["seara", "sea"],
    "rap10": ["rap10", "rap"],
    "galo": ["galo", "gal"],
    "campi": ["campi", "camp"],
    "nissin": ["nissin", "niss"],
    "freegells": ["freegells", "freeg", "freege", "freegels"],
    "toya": ["toya", "toy"],
    "jo": ["jo alimentos", "joalimentos", "jo alim"],
    "big bom": ["big bom", "bigbom", "big b"],
    "tirol": ["tirol", "tiro", "tir"],


    # Iogurtes
    "itambe": ["itambe", "itamb"],
    "batavo": ["batavo", "bat"],
    "parmalat": ["parmalat", "parma", "prmlt"],


    # Bebidas
    "coca cola": ["coca cola", "cocacola", "coca", "cola"],
    "guarana antartica": ["guarana", "antartica", "guara", "guaraná"],
    "laranjinha": ["laranjinha"],
    "kapo": ["kapo", "kap"],
    "dafruta": ["dafruta", "daf"],
    "grapette": ["grapette", "grap"],
    "bare": ["bare", "bar"],
    

    # Genérico
    "generico": ["generico", "sem marca"]
}


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
