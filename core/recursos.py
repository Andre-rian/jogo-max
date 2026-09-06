# Carregamento centralizado de recursos (imagens) com fallback seguro.
# Um asset faltando não deve derrubar o jogo: registra um warning e devolve
# uma surface placeholder em vez de lançar exceção.

import logging
import pygame

logger = logging.getLogger(__name__)

COR_PLACEHOLDER = (255, 0, 255)


def carregar_imagem(caminho, converter_alfa=True):
    """Carrega uma imagem com pygame.image.load.

    Retorna a Surface carregada (convertível para alpha) ou, em caso de erro,
    uma Surface placeholder magenta de 1x1 (nunca None). Falhas são logadas.
    """
    try:
        surface = pygame.image.load(caminho)
    except (pygame.error, FileNotFoundError, OSError) as e:
        logger.warning(f"[RECURSOS] não foi possível carregar imagem '{caminho}': {e}")
        return _placeholder()
    if not converter_alfa:
        return surface
    try:
        return surface.convert_alpha()
    except pygame.error as e:
        logger.warning(f"[RECURSOS] falha ao converter '{caminho}' (tela não inicializada?): {e}")
        return surface


def _placeholder(tamanho=(1, 1)):
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    surf.fill(COR_PLACEHOLDER + (255,))
    return surf


def criar_placeholder(tamanho):
    """Surface placeholder pronta para ser usada como frame/folha ausente."""
    return pygame.transform.scale(_placeholder((1, 1)), tamanho)