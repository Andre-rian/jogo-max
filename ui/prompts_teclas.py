# Prompts de teclado do inventário e do menu.
# Extrai as teclas de gdb-keyboard-2.png (greatdocbrown, CC0) e mantém um
# fallback desenhado caso o spritesheet não esteja disponível.

import logging
import os

import pygame

from core.recursos import carregar_imagem
from ui.estilo import (
    Azul_espectral, Branco_texto, Cinza_carvao, Fonte_texto
)

logger = logging.getLogger(__name__)

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CAMINHO_TECLAS = os.path.join(
    _RAIZ_PROJETO, "assets", "sprites", "_entrada", "prompts",
    "greatdocbrown_gamepad_ui", "gdb-keyboard-2.png",
)

_RECORTES = {
    "esc": (32, 16, 16, 16),
    "tab": (36, 48, 24, 16),
    "enter": (244, 64, 24, 16),
    "seta_cima": (320, 80, 16, 16),
    "seta_esquerda": (304, 96, 16, 16),
    "seta_baixo": (320, 96, 16, 16),
    "seta_direita": (336, 96, 16, 16),
}

_ROTULOS_FALLBACK = {
    "esc": "ESC",
    "tab": "TAB",
    "enter": "ENTER",
    "delete": "DEL",
    "seta_cima": "^",
    "seta_esquerda": "<",
    "seta_baixo": "v",
    "seta_direita": ">",
}

_cache = {}
_cache_escalas = {}
_folha = None
_folha_carregada = False


def _obter_folha():
    global _folha, _folha_carregada
    if not _folha_carregada:
        try:
            _folha = carregar_imagem(_CAMINHO_TECLAS)
            if _folha.get_size() == (1, 1):
                _folha = None
        except pygame.error as e:
            logger.warning(f"[TECLAS] falha ao carregar spritesheet: {e}")
            _folha = None
        _folha_carregada = True
    return _folha


def _criar_fallback(nome):
    rotulo = _ROTULOS_FALLBACK.get(nome, "?")
    fonte = Fonte_texto(12)
    texto = fonte.render(rotulo, True, Branco_texto)
    largura = max(16, texto.get_width() + 8)
    altura = 16
    surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(surface, Cinza_carvao, (0, 0, largura, altura),
                     border_radius=3)
    pygame.draw.rect(surface, Azul_espectral, (0, 0, largura, altura), 1,
                     border_radius=3)
    surface.blit(texto, ((largura - texto.get_width()) // 2,
                         (altura - texto.get_height()) // 2))
    return surface


def _tecla_base(nome):
    if nome in _cache:
        return _cache[nome]

    recorte = _RECORTES.get(nome)
    folha = _obter_folha()
    surface = None
    if folha is not None and recorte is not None:
        try:
            surface = folha.subsurface(pygame.Rect(*recorte)).copy()
        except ValueError as e:
            logger.warning(f"[TECLAS] recorte inválido para '{nome}': {e}")

    if surface is None:
        surface = _criar_fallback(nome)

    _cache[nome] = surface
    return surface


def obter_tecla(nome, escala=1.0):
    base = _tecla_base(nome)
    if escala == 1.0:
        return base

    chave = (nome, escala)
    if chave not in _cache_escalas:
        largura = max(1, round(base.get_width() * escala))
        altura = max(1, round(base.get_height() * escala))
        _cache_escalas[chave] = pygame.transform.scale(
            base, (largura, altura)
        )
    return _cache_escalas[chave]


def _normalizar_padding(padding):
    if isinstance(padding, (tuple, list)):
        pad_x = padding[0] if len(padding) > 0 else 0
        pad_y = padding[1] if len(padding) > 1 else pad_x
        return max(0, int(pad_x)), max(0, int(pad_y))
    valor = max(0, int(padding))
    return valor, valor


def criar_prompt(teclas, texto, fonte, cor_texto, espaco_teclas=2,
                 espaco_texto=6, escala=1.0, padding=0, cor_fundo=None,
                 raio_fundo=4):
    surfaces = [obter_tecla(nome, escala) for nome in teclas]
    rotulo = fonte.render(texto, True, cor_texto)

    pad_x, pad_y = _normalizar_padding(padding)
    largura_conteudo = sum(s.get_width() + espaco_teclas for s in surfaces)
    largura_conteudo += espaco_texto + rotulo.get_width()
    altura_conteudo = max(
        [s.get_height() for s in surfaces] + [rotulo.get_height(), 16]
    )
    largura = largura_conteudo + pad_x * 2
    altura = altura_conteudo + pad_y * 2

    surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
    if cor_fundo is not None:
        pygame.draw.rect(
            surface, cor_fundo, surface.get_rect(), border_radius=raio_fundo
        )

    x = pad_x
    for tecla in surfaces:
        y = pad_y + (altura_conteudo - tecla.get_height()) // 2
        surface.blit(tecla, (x, y))
        x += tecla.get_width() + espaco_teclas
    surface.blit(
        rotulo,
        (x + espaco_texto,
         pad_y + (altura_conteudo - rotulo.get_height()) // 2)
    )
    return surface


def desenhar_prompts(tela, prompts, centro_x, y, fonte, cor_texto,
                     espaco=24, escala=1.0, padding=0, cor_fundo=None,
                     espaco_teclas=2, espaco_texto=6, raio_fundo=4):
    surfaces = [
        criar_prompt(
            teclas, texto, fonte, cor_texto,
            espaco_teclas=espaco_teclas,
            espaco_texto=espaco_texto,
            escala=escala,
            padding=padding,
            cor_fundo=cor_fundo,
            raio_fundo=raio_fundo,
        )
        for teclas, texto in prompts
    ]
    largura = sum(s.get_width() for s in surfaces)
    largura += espaco * max(0, len(surfaces) - 1)

    x = centro_x - largura // 2
    for surface in surfaces:
        tela.blit(surface, (x, y))
        x += surface.get_width() + espaco


def limpar_cache():
    global _folha, _folha_carregada
    _cache.clear()
    _cache_escalas.clear()
    _folha = None
    _folha_carregada = False
