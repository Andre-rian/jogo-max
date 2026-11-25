"""LY015 opcional: superfícies prontas em cache, sem redistribuir o sprite."""
from functools import lru_cache
from pathlib import Path
import pygame
from core.recursos import carregar_imagem

CAMINHO_TRILHO = (Path(__file__).resolve().parents[2] / 'assets/sprites/_entrada'
                  / 'itens/lygame_dark_fantasy/UI/ProgressTrack.png')
# LY015: 48x12, interior [3:45, 3:9]; pontas e bordas de 3 px.
MARGEM = 3
CONTORNO = (10, 12, 18)
BORDA = (107, 118, 137)
FUNDO = (24, 26, 34)


@lru_cache(maxsize=1)
def _origem():
    imagem = carregar_imagem(str(CAMINHO_TRILHO), converter_alfa=False)
    if imagem.get_size() != (48, 12):
        return None
    paleta = {(10, 10, 12): CONTORNO, (32, 32, 35): FUNDO,
              (129, 39, 36): BORDA}
    fria = pygame.Surface((48, 12), pygame.SRCALPHA)
    for y in range(12):
        for x in range(48):
            cor = imagem.get_at((x, y))
            fria.set_at((x, y), (*paleta.get(tuple(cor[:3]), tuple(cor[:3])), cor.a))
    return fria


@lru_cache(maxsize=8)
def obter_trilho(largura, altura_util, usar_asset=True):
    """3-slice horizontal 1x; repete interior vertical, preservando bordas.

    Superfície compartilhada: consumidores apenas fazem blit, nunca a alteram.
    O fallback é procedural e não depende de nenhum pixel do pack.
    """
    if largura < 7 or altura_util not in (6, 8, 10):
        raise ValueError('Trilho exige largura >= 7 e interior de 6, 8 ou 10 px')
    altura = altura_util + 2 * MARGEM
    destino = pygame.Surface((largura, altura), pygame.SRCALPHA)
    origem = _origem() if usar_asset else None
    if origem is None:
        destino.fill(CONTORNO)
        pygame.draw.rect(destino, BORDA, (1, 1, largura-2, altura-2), 1)
        pygame.draw.rect(destino, FUNDO, (3, 3, largura-6, altura_util))
        return destino

    horizontal = pygame.Surface((largura, 12), pygame.SRCALPHA)
    horizontal.blit(origem, (0, 0), (0, 0, MARGEM, 12))
    for x in range(MARGEM, largura-MARGEM):
        horizontal.blit(origem, (x, 0), (24, 0, 1, 12))
    horizontal.blit(origem, (largura-MARGEM, 0), (45, 0, MARGEM, 12))
    destino.blit(horizontal, (0, 0), (0, 0, largura, MARGEM))
    for y in range(MARGEM, altura-MARGEM):
        destino.blit(horizontal, (0, y), (0, 3, largura, 1))
    destino.blit(horizontal, (0, altura-MARGEM), (0, 9, largura, MARGEM))
    return destino


def limpar_cache():
    obter_trilho.cache_clear()
    _origem.cache_clear()
