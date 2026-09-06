# Dados de configuração dos níveis (conexões, spawns, inimigos e drops).
# Separados de world/rooms.py, que guarda apenas as grades (grids) das salas.

Conexoes = {
    'calabouço_1': {"direita": "calabouço_2", "esquerda": None        },
    'calabouço_2': {"direita": "calabouço_3", "esquerda": "calabouço_1"},
    'calabouço_3': {"direita": "calabouço_4", "esquerda": "calabouço_2"},
    'calabouço_4': {"direita": "calabouço_5", "esquerda": "calabouço_3"},
    'calabouço_5': {"direita": None,          "esquerda": "calabouço_4"},
}

spwans = {
    'calabouço_1': (10, 15),
    'calabouço_2': (1, 10),
    'calabouço_3': (2, 10),
    'calabouço_4': (2, 10),
    'calabouço_5': (2, 10),
}

Inimigos_por_sala = {
    'calabouço_1': [],
    'calabouço_2': [
        ("flying_eye", 12, 5, 200, 500),
    ],
    'calabouço_3': [
        ("skeleton", 10, 10, 100, 500),
        ("globin",   5,  10, 100, 300),
        ("mushroom", 12, 10, 350, 550),
    ],
    'calabouço_4': [],   # só fogueira, sem inimigos
    'calabouço_5': [
        ("esqueleto_boss", 14, 9),
    ],
}

Drops_inimigos = {
    "globin"    : [(1.0, 4)],   # 100% por enquanto, id_item 4 = Raiz Amarga
    "skeleton"  : [],
    "mushroom"  : [],
    "flying_eye": [],
}

Drops_fixos = {
    "calabouço_4": [
        (5, 5, 10.7),  # id_item=5, col=5, linha=5 — ajusta a posição depois
    ],
}