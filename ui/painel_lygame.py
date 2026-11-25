import logging
import os

import pygame

from core.recursos import carregar_imagem

logger = logging.getLogger(__name__)

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CAMINHO_PAINEL = os.path.join(
    _RAIZ_PROJETO, "assets", "sprites", "_entrada", "itens",
    "lygame_dark_fantasy", "UI", "Panel1.png",
)

MARGEM = 12
GRAFITE = (30, 31, 37)

_MAPA_CORES = {
    (10, 10, 12): (21, 23, 30),
    (32, 32, 35): (50, 54, 66),
    (65, 65, 65): (94, 101, 118),
    (200, 187, 162): (196, 199, 210),
}

_cache = {"painel": None, "carregada": False}


def _obter_painel():
    if not _cache["carregada"]:
        painel = carregar_imagem(_CAMINHO_PAINEL)
        if painel.get_size() == (1, 1):
            logger.warning("[PAINEL LYGAME] Panel1.png indisponível; usando moldura anterior")
            painel = None
        else:
            painel = _ajustar_cores(painel)
        _cache["painel"] = painel
        _cache["carregada"] = True
    return _cache["painel"]


def disponivel():
    return _obter_painel() is not None


def _ajustar_cores(origem):
    destino = pygame.Surface(origem.get_size(), pygame.SRCALPHA)
    for y in range(origem.get_height()):
        for x in range(origem.get_width()):
            cor = origem.get_at((x, y))
            r, g, b = _MAPA_CORES.get(
                (cor.r, cor.g, cor.b), (cor.r, cor.g, cor.b)
            )
            destino.set_at((x, y), (r, g, b, cor.a))
    return destino


def _tile_horizontal(destino, origem, area, destino_rect):
    x = destino_rect.x
    while x < destino_rect.right:
        largura = min(area.width, destino_rect.right - x)
        destino.blit(origem, (x, destino_rect.y),
                     (area.x, area.y, largura, area.height))
        x += area.width


def _tile_vertical(destino, origem, area, destino_rect):
    y = destino_rect.y
    while y < destino_rect.bottom:
        altura = min(area.height, destino_rect.bottom - y)
        destino.blit(origem, (destino_rect.x, y),
                     (area.x, area.y, area.width, altura))
        y += area.height


def desenhar_painel_lygame(tela, rect):
    origem = _obter_painel()
    if origem is None:
        return False

    x, y, w, h = rect
    if w <= MARGEM * 2 or h <= MARGEM * 2:
        return False

    sw, sh = origem.get_size()

    pygame.draw.rect(tela, GRAFITE,
                     (x + MARGEM, y + MARGEM,
                      w - MARGEM * 2, h - MARGEM * 2))

    tela.blit(origem, (x, y), (0, 0, MARGEM, MARGEM))
    tela.blit(origem, (x + w - MARGEM, y), (sw - MARGEM, 0, MARGEM, MARGEM))
    tela.blit(origem, (x, y + h - MARGEM), (0, sh - MARGEM, MARGEM, MARGEM))
    tela.blit(origem, (x + w - MARGEM, y + h - MARGEM),
              (sw - MARGEM, sh - MARGEM, MARGEM, MARGEM))

    topo = pygame.Rect(MARGEM, 0, sw - MARGEM * 2, MARGEM)
    base = pygame.Rect(MARGEM, sh - MARGEM, sw - MARGEM * 2, MARGEM)
    esquerda = pygame.Rect(0, MARGEM, MARGEM, sh - MARGEM * 2)
    direita = pygame.Rect(sw - MARGEM, MARGEM, MARGEM, sh - MARGEM * 2)

    _tile_horizontal(tela, origem, topo,
                     pygame.Rect(x + MARGEM, y, w - MARGEM * 2, MARGEM))
    _tile_horizontal(tela, origem, base,
                     pygame.Rect(x + MARGEM, y + h - MARGEM,
                                 w - MARGEM * 2, MARGEM))
    _tile_vertical(tela, origem, esquerda,
                   pygame.Rect(x, y + MARGEM, MARGEM, h - MARGEM * 2))
    _tile_vertical(tela, origem, direita,
                   pygame.Rect(x + w - MARGEM, y + MARGEM,
                               MARGEM, h - MARGEM * 2))
    return True
