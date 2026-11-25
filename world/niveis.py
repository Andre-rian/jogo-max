# Dados de configuração dos níveis (conexões, spawns, inimigos e drops).
# Separados de world/rooms.py, que guarda apenas as grades (grids) das salas.

SALAS_BETA = (
    "bloco_celas_esquecidas", "antigo_arsenal_guardas",
    "corredores_profundos", "arena_chefe",
)
TITULOS_BETA = dict(zip(SALAS_BETA, (
    "Bloco das Celas Esquecidas", "Antigo Arsenal dos Guardas",
    "Corredores Profundos", "Arena do Chefe",
)))

# Referência: Espada Longa inicial = 25 por golpe simples. Sem alterar a IA,
# janelas de ataque, i-frames, knockback ou guarda dos perfis existentes.
VIDA_INIMIGOS_BETA = {
    "globin": 85,          # 4 golpes simples; combos continuam recompensados
    "flying_eye": 80,      # 4 golpes simples; combos continuam recompensados
    "mushroom": 145,       # 6 golpes simples; combos continuam recompensados
    "skeleton": 150,       # 6 golpes simples; combos continuam recompensados
    "esqueleto_boss": 495,  # 20 golpes simples sem bloqueio; combos continuam recompensados
}

Conexoes = {
    **{sala: {"esquerda": SALAS_BETA[i - 1] if i else None,
              "direita": SALAS_BETA[i + 1] if i + 1 < len(SALAS_BETA) else None}
       for i, sala in enumerate(SALAS_BETA)},
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
    "antigo_arsenal_guardas": [(2, 36, 19), (4, 40, 19)],
    "corredores_profundos": [(7, 31, 19), (2, 65, 12), (8, 69, 12), (4, 100, 19), (2, 102, 19)],
    "calabouço_4": [
        (5, 5, 10.7),  # id_item=5, col=5, linha=5 — ajusta a posição depois
    ],
}

MATERIAL_PISO = {
    'calabouço_1': 'pedra',
    'calabouço_2': 'pedra',
    'calabouço_3': 'pedra',
    'calabouço_4': 'pedra',
    'calabouço_5': 'pedra',
}
