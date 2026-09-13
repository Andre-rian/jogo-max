import logging
import pygame
from settings import Tile_size
from core.recursos import carregar_imagem, criar_placeholder

logger = logging.getLogger(__name__)

#folha da tocha: 128x128 com 2 tochas empilhadas, cada uma 32x64:
#  linhas 0 e 1  -> tocha fraca (fogo leve)      -> 4 frames de animação (colunas)
#  linhas 2 e 3  -> tocha forte (fogo forte)     -> 4 frames de animação (colunas)
CAMINHO_TOCHA = "assets/tileset/calabouco/Torch Sprite Sheet 32x64.png"
NOME_TILESET_TOCHA = "Torch Sprite Sheet 32x64"
LANCADA = 32
ALTURA = 64
COLUNAS = 4
#linhas da folha que são o FOGO (teto da tocha); a haste fica na linha seguinte
FLAME_ROWS = (0, 2)

_CACHE_FRAMES = {}


def carregar_frames_tocha(variante="forte"):
    #fatia 4 frames de 32x64 de UMA única tocha (linha da folha)
    linha_folha = 0 if variante == "fraca" else 2
    if linha_folha not in _CACHE_FRAMES:
        sheet = carregar_imagem(CAMINHO_TOCHA)
        if sheet.get_width() < LANCADA * COLUNAS or sheet.get_height() < ALTURA:
            logger.warning(
                f"[TOCHA] spritesheet '{CAMINHO_TOCHA}' menor que 128x128 - usando placeholder"
            )
            sheet = criar_placeholder((LANCADA * COLUNAS, ALTURA))

        frames = []
        for c in range(COLUNAS):
            frames.append(sheet.subsurface(pygame.Rect(c * LANCADA, linha_folha * (ALTURA // 2),
                                                       LANCADA, ALTURA)))
        _CACHE_FRAMES[linha_folha] = frames
    return _CACHE_FRAMES[linha_folha]


class Tocha:
    #tocha decorativa animada: uma sprite 32x64 (fogo + haste), 4 frames de tremulação

    def __init__(self, x, y, col, linha, variante="forte", velocidade=6):
        self.col = col
        self.linha = linha
        self.variante = variante
        self.rect = pygame.Rect(x, y, LANCADA, ALTURA)
        self.velocidade = velocidade
        self.frames = carregar_frames_tocha(variante)
        self._contador = 0
        self._frame_idx = 0

    def atualizar(self):
        self._contador += 1
        if self._contador >= self.velocidade:
            self._contador = 0
            self._frame_idx = (self._frame_idx + 1) % len(self.frames)

    def desenhar(self, tela, camera):
        sr = camera.aplicar(self.rect)
        frame = self.frames[self._frame_idx]
        if frame.get_width() != sr.width or frame.get_height() != sr.height:
            frame = pygame.transform.scale(frame, (sr.width, sr.height))
        tela.blit(frame, sr)