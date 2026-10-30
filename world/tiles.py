# Definição dos tiles do mundo (classes de desenho e registro global de ids).
# Separados de settings.py para manter a configuração do jogo apenas com constantes.

import logging
import pygame
from settings import Tile_size, Stone_gray, stone_light, Torch_Orange
from core.recursos import carregar_imagem, criar_placeholder

logger = logging.getLogger(__name__)

# gids globais (TMX) de tiles de plataforma one-way estilo Terraria:
# anda/salta por baixo, desce com S+Espaço, segura apenas caindo de cima
PLATAFORMA_GIDS = frozenset({2594, 2595, 2596, 2609, 2610, 2611})


class Tile:

    def __init__(self, tile_id, solid, color, damage=0, lethal=False, folhas_variantes=None):
        self.title_id = tile_id

        self.solid = solid

        self.color = color

        self.damage = damage

        self.lethal = lethal

        self.folhas_variantes_path = folhas_variantes

        self._variantes = None  # lista de surface, cortadas sobre demanda

    def on_enter(self, player):

        if self.damage > 0:
            player.take_damage(self.damage)

    def _carregar_variantes(self):
        folha = carregar_imagem(self.folhas_variantes_path)
        cols = folha.get_width() // Tile_size
        rows = folha.get_height() // Tile_size
        if cols < 1 or rows < 1:
            logger.warning(
                f"[TILES] variantes de '{self.folhas_variantes_path}' muito pequenas "
                f"({folha.get_width()}x{folha.get_height()}) — usando placeholder magenta"
            )
            return [criar_placeholder((Tile_size, Tile_size))]
        variantes = []
        for r in range(rows):
            for c in range(cols):
                pedaco = folha.subsurface((c * Tile_size, r * Tile_size, Tile_size, Tile_size))
                variantes.append(pedaco)
        return variantes

    def draw(self, tela, rect, col=0, linha=0):
        if self.folhas_variantes_path:
            if self._variantes is None:
                self._variantes = self._carregar_variantes()
            indice = (col * 7 + linha * 13) % len(self._variantes)  # escolha determinística
            tela.blit(self._variantes[indice], rect)
        else:
            pygame.draw.rect(tela, self.color, rect)


# tiles especiais, herdam as características do tile original
class Espinho(Tile):

    def __init__(self):
        super().__init__(
            tile_id=4,
            solid=False,
            color=(120, 20, 20),
            damage=20
        )

    def draw(self, tela, rect, col=0, linha=0):
        pts = [
            (rect.centerx, rect.top + 4),
            (rect.right - 4, rect.bottom - 4),
            (rect.left + 4, rect.bottom - 4)]

        pygame.draw.polygon(tela, self.color, pts)


class Torcha(Tile):

    def __init__(self):

        super().__init__(
            tile_id=7,
            solid=False,
            color=Torch_Orange
        )

    def draw(self, tela, rect, col=0, linha=0):

        # cabo da torcha
        pygame.draw.rect(tela, (100, 70, 30),
                         (rect.centerx - 3, rect.centery, 6, 16))

        # fogo da tocha
        pygame.draw.ellipse(tela, Torch_Orange, (rect.centerx - 7, rect.top + 8, 14, 18))

        pygame.draw.ellipse(tela, (255, 220, 80), (rect.centerx - 4, rect.top + 11, 8, 11))


# Registro = dicionário de todos os ids/tile

# chave id = bau()
Registro_ID = {
    0: None,  # nao desenhar nada
    1: Tile(tile_id=1, solid=True, color=Stone_gray, folhas_variantes="assets/tileset/calabouco/parede_variantes.png"),
    2: Tile(tile_id=2, solid=True, color=(60, 60, 68), folhas_variantes="assets/tileset/calabouco/chao_variantes.png"),
    3: Tile(tile_id=3, solid=False, color=(80, 60, 30)),  # escada
    4: Espinho(),
    5: Tile(tile_id=5, solid=True, color=(90, 55, 20)),  # porta
    6: None,  # bau
    7: Torcha(),
    9: None,  # fogueira
}


# ids em ordem numérica para não esquecer
Tile_vazio = 0
Tile_parede = 1
Tile_chão = 2
Tile_escada = 3
Tile_espinho = 4
Tile_porta = 5
Tile_bau = 6
Tile_torcha = 7
Tile_fogueira = 9