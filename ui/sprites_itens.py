# Sprites finais dos itens do inventário, mapeados pelo ID real do item.
# Cache preguiçoso: cada PNG é carregado e escalado uma única vez por sessão.

import logging
import os

import pygame

from core.recursos import carregar_imagem

logger = logging.getLogger(__name__)

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PASTA_ITENS = os.path.join(_RAIZ_PROJETO, "assets", "sprites", "itens")

TAMANHO_NATIVO = 24
ESCALA = 2
TAMANHO_ICONE = TAMANHO_NATIVO * ESCALA

_MAPA_SPRITES = {
    1: os.path.join(_PASTA_ITENS, "equipamentos", "espada_longa.png"),
    2: os.path.join(_PASTA_ITENS, "consumiveis", "pocao_vida.png"),
    3: os.path.join(_PASTA_ITENS, "equipamentos", "machado_guerra.png"),
    4: os.path.join(_PASTA_ITENS, "consumiveis", "raiz_amarga.png"),
    5: os.path.join(_PASTA_ITENS, "materiais", "umbrita.png"),
}

_CAMINHO_FALLBACK = os.path.join(
    _PASTA_ITENS, "_default", "item_desconhecido.png"
)

_cache = {}
_falhas = set()
_fallback = None
_fallback_carregado = False


def _carregar(caminho):
    if not caminho or not os.path.isfile(caminho):
        return None
    surface = carregar_imagem(caminho)
    if surface.get_size() == (1, 1):
        return None
    if surface.get_size() != (TAMANHO_ICONE, TAMANHO_ICONE):
        surface = pygame.transform.scale(
            surface, (TAMANHO_ICONE, TAMANHO_ICONE)
        )
    return surface


def obter_sprite_item(item_id):
    if item_id in _cache:
        return _cache[item_id]
    if item_id in _falhas:
        return None

    caminho = _MAPA_SPRITES.get(item_id)
    try:
        surface = _carregar(caminho)
    except pygame.error as e:
        logger.warning(f"[SPRITES] falha ao carregar item {item_id}: {e}")
        surface = None

    if surface is None:
        _falhas.add(item_id)
        return None

    _cache[item_id] = surface
    return surface


def obter_sprite_de_item(item):
    item_id = getattr(item, "id", None)
    if item_id is None and getattr(item, "icone", None) == "pocao":
        item_id = 2
    return obter_sprite_item(item_id)


def obter_fallback():
    global _fallback, _fallback_carregado
    if not _fallback_carregado:
        try:
            _fallback = _carregar(_CAMINHO_FALLBACK)
        except pygame.error as e:
            logger.warning(f"[SPRITES] falha ao carregar fallback: {e}")
            _fallback = None
        _fallback_carregado = True
    return _fallback


def precarregar():
    for item_id in _MAPA_SPRITES:
        obter_sprite_item(item_id)
    obter_fallback()


def limpar_cache():
    global _fallback, _fallback_carregado
    _cache.clear()
    _falhas.clear()
    _fallback = None
    _fallback_carregado = False
