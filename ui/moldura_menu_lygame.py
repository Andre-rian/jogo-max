import logging
import os

import pygame

from core.recursos import carregar_imagem

logger = logging.getLogger(__name__)

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DIR_UI = os.path.join(
    _RAIZ_PROJETO, "assets", "sprites", "_entrada", "itens",
    "lygame_dark_fantasy", "UI",
)

MARGEM = 5

_PALETAS = {
    "vazio": {
        (10, 10, 12): (14, 16, 22),
        (32, 32, 35): (27, 28, 34),
        (65, 65, 65): (68, 74, 90),
        (200, 187, 162): (134, 142, 164),
    },
    "ocupado": {
        (10, 10, 12): (16, 18, 24),
        (32, 32, 35): (33, 35, 44),
        (65, 65, 65): (78, 85, 102),
        (200, 187, 162): (150, 158, 180),
    },
    "selecionado": {
        (10, 10, 12): (12, 14, 20),
        (32, 32, 35): (38, 42, 54),
        (65, 65, 65): (92, 112, 152),
        (200, 187, 162): (160, 184, 218),
    },
}

_ESTADOS = {
    "vazio": ("Frame1Empty.png", "vazio", (27, 28, 34)),
    "ocupado": ("Frame1Empty.png", "ocupado", (33, 35, 44)),
    "selecionado_vazio": ("Frame1Empty.png", "selecionado", (36, 40, 52)),
    "selecionado_ocupado": ("Frame1.png", "selecionado", None),
}

_cache = {}


def _ajustar_cores(origem, paleta):
    destino = pygame.Surface(origem.get_size(), pygame.SRCALPHA)
    for y in range(origem.get_height()):
        for x in range(origem.get_width()):
            cor = origem.get_at((x, y))
            r, g, b = paleta.get(
                (cor.r, cor.g, cor.b), (cor.r, cor.g, cor.b)
            )
            destino.set_at((x, y), (r, g, b, cor.a))
    return destino


def _obter_estado(estado):
    if estado in _cache:
        return _cache[estado]

    arquivo, paleta, _ = _ESTADOS[estado]
    caminho = os.path.join(_DIR_UI, arquivo)
    origem = carregar_imagem(caminho)
    if origem.get_size() == (1, 1):
        logger.warning(
            "[MOLDURA MENU LYGAME] %s indisponível; usando moldura anterior",
            arquivo,
        )
        surface = None
    else:
        surface = _ajustar_cores(origem, _PALETAS[paleta])

    _cache[estado] = surface
    return surface


def disponivel():
    return (
        _obter_estado("vazio") is not None
        and _obter_estado("selecionado_ocupado") is not None
    )


def _tile_area(destino, origem, area, destino_rect):
    if area.width <= 0 or area.height <= 0:
        return
    for y in range(destino_rect.top, destino_rect.bottom, area.height):
        altura = min(area.height, destino_rect.bottom - y)
        for x in range(destino_rect.left, destino_rect.right, area.width):
            largura = min(area.width, destino_rect.right - x)
            destino.blit(
                origem, (x, y),
                (area.x, area.y, largura, altura),
            )


def _desenhar_9slice(tela, origem, rect):
    x, y, w, h = rect
    m = MARGEM
    sw, sh = origem.get_size()

    _tile_area(
        tela, origem,
        pygame.Rect(m, m, sw - m * 2, sh - m * 2),
        pygame.Rect(x + m, y + m, w - m * 2, h - m * 2),
    )
    _tile_area(
        tela, origem,
        pygame.Rect(m, 0, sw - m * 2, m),
        pygame.Rect(x + m, y, w - m * 2, m),
    )
    _tile_area(
        tela, origem,
        pygame.Rect(m, sh - m, sw - m * 2, m),
        pygame.Rect(x + m, y + h - m, w - m * 2, m),
    )
    _tile_area(
        tela, origem,
        pygame.Rect(0, m, m, sh - m * 2),
        pygame.Rect(x, y + m, m, h - m * 2),
    )
    _tile_area(
        tela, origem,
        pygame.Rect(sw - m, m, m, sh - m * 2),
        pygame.Rect(x + w - m, y + m, m, h - m * 2),
    )

    tela.blit(origem, (x, y), (0, 0, m, m))
    tela.blit(origem, (x + w - m, y), (sw - m, 0, m, m))
    tela.blit(origem, (x, y + h - m), (0, sh - m, m, m))
    tela.blit(
        origem, (x + w - m, y + h - m),
        (sw - m, sh - m, m, m),
    )


def desenhar_moldura_slot(tela, rect, selecionado=False, ocupado=False):
    if selecionado:
        estado = "selecionado_ocupado" if ocupado else "selecionado_vazio"
    else:
        estado = "ocupado" if ocupado else "vazio"

    origem = _obter_estado(estado)
    if origem is None:
        return False

    x, y, w, h = rect
    m = MARGEM
    if w <= m * 2 or h <= m * 2:
        return False

    preenchimento = _ESTADOS[estado][2]
    if preenchimento is not None:
        pygame.draw.rect(
            tela, preenchimento,
            (x + m, y + m, w - m * 2, h - m * 2),
        )

    _desenhar_9slice(tela, origem, rect)
    return True


def limpar_cache():
    _cache.clear()
