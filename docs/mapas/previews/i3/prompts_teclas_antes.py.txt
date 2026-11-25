# Sprites e prompts de teclas (HUD e mundo).
# Baseado no spritesheet gdb-keyboard-2.png (greatdocbrown, CC0).
# Recortes validados por uso: E normal/pressionado conforme G.1.

import logging
import math
import os

import pygame

from core.recursos import carregar_imagem
from ui.estilo import Azul_espectral, Branco_texto, Cinza_carvao, Fonte_texto, registrar_observador_escala

logger = logging.getLogger(__name__)

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CAMINHO_TECLAS = os.path.join(
    _RAIZ_PROJETO, "assets", "sprites", "_entrada", "prompts",
    "greatdocbrown_gamepad_ui", "gdb-keyboard-2.png",
)

# Recortes HUD existentes (nao alterar sem validar).
_RECORTES = {
    "esc": (32, 16, 16, 16),
    "tab": (36, 48, 24, 16),
    "enter": (244, 64, 24, 16),
    "seta_cima": (320, 80, 16, 16),
    "seta_esquerda": (304, 96, 16, 16),
    "seta_baixo": (320, 96, 16, 16),
    "seta_direita": (336, 96, 16, 16),
    "delete": (80, 16, 16, 16),
}

# Teclas para prompts no mundo (G.1). E conforme especificacao.
_RECORTES_MUNDO = {
    "e": {"normal": (96, 48, 16, 16), "pressionado": (96, 64, 16, 16)},
    # Candidatos best-effort no mesmo layout; fallback textual se invalidos.
    "a": {"normal": (32, 48, 16, 16), "pressionado": (32, 64, 16, 16)},
    "d": {"normal": (48, 48, 16, 16), "pressionado": (48, 64, 16, 16)},
    "k": {"normal": (160, 48, 16, 16), "pressionado": (160, 64, 16, 16)},
    "espaco": {"normal": (496, 112, 64, 16), "pressionado": (496, 112, 64, 16)},
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
    "e": "E",
    "a": "A",
    "d": "D",
    "k": "K",
    "espaco": "SPACE",
}

_cache = {}
_cache_escalas = {}
_cache_mundo = {}
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


def _criar_fallback(nome, tamanho=None):
    rotulo = _ROTULOS_FALLBACK.get(nome, str(nome).upper()[:5] or "?")
    fonte = Fonte_texto(12)
    texto = fonte.render(rotulo, True, Branco_texto)
    if tamanho is not None:
        largura, altura = tamanho
        largura = max(largura, texto.get_width() + 8)
        altura = max(altura, 16)
    else:
        largura = max(16, texto.get_width() + 8)
        altura = 16
    surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(surface, Cinza_carvao, (0, 0, largura, altura), border_radius=3)
    pygame.draw.rect(surface, Azul_espectral, (0, 0, largura, altura), 1, border_radius=3)
    surface.blit(texto, ((largura - texto.get_width()) // 2,
                         (altura - texto.get_height()) // 2))
    return surface


def _extrair_recorte(rect, nome, fallback_tamanho=None):
    folha = _obter_folha()
    if folha is None or rect is None:
        return _criar_fallback(nome, fallback_tamanho)
    try:
        area = pygame.Rect(*rect)
        if area.width <= 0 or area.height <= 0:
            raise ValueError("rect vazio")
        folha_rect = folha.get_rect()
        if not folha_rect.contains(area):
            raise ValueError("rect fora da folha")
        surface = folha.subsurface(area).copy()
        if pygame.mask.from_surface(surface).count() == 0:
            raise ValueError("recorte vazio")
        return surface
    except ValueError as e:
        logger.warning(f"[TECLAS] recorte invalido para '{nome}': {e}")
        return _criar_fallback(nome, fallback_tamanho or (rect[2], rect[3]) if rect else None)


def _tecla_base(nome):
    if nome in _cache:
        return _cache[nome]
    # delete usa fallback textual para manter legibilidade consistente
    if nome == "delete":
        surface = _criar_fallback(nome)
        _cache[nome] = surface
        return surface
    recorte = _RECORTES.get(nome)
    surface = _extrair_recorte(recorte, nome)
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
        _cache_escalas[chave] = pygame.transform.scale(base, (largura, altura))
    return _cache_escalas[chave]


def obter_tecla_mundo(nome, estado="normal", escala=1.0):
    nome = str(nome).lower()
    chave = (nome, estado, escala)
    if chave in _cache_mundo:
        return _cache_mundo[chave]
    spec = _RECORTES_MUNDO.get(nome)
    if spec is None:
        base = _criar_fallback(nome)
    else:
        rect = spec.get(estado) or spec.get("normal")
        tamanho = None
        if rect is not None:
            tamanho = (rect[2], rect[3])
        base = _extrair_recorte(rect, f"{nome}:{estado}", tamanho)
    if escala != 1.0:
        base = pygame.transform.scale(
            base, (max(1, round(base.get_width() * escala)),
                   max(1, round(base.get_height() * escala)))
        )
    _cache_mundo[chave] = base
    return base


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


class PromptTeclaMundo:
    """Sprite de tecla flutuando no mundo (desenhado na surface 'vista')."""

    def __init__(self, tecla="e", escala=1.0):
        self.tecla = str(tecla).lower()
        self.escala = escala
        self._timer = 0
        self._press_timer = 0
        self._press_interval = 150
        self._press_duracao = 8
        self._offset_flutuar = 2
        self._offset_press = 1

    def atualizar(self, pressionada=False):
        self._timer += 1
        if pressionada:
            self._press_timer = self._press_duracao
        else:
            if self._press_timer > 0:
                self._press_timer -= 1
            # pulso discreto periodico enquanto disponivel
            if self._timer % self._press_interval == 0:
                self._press_timer = max(self._press_timer, self._press_duracao)

    @property
    def estado(self):
        return "pressionado" if self._press_timer > 0 else "normal"

    def desenhar(self, tela_vista, camera, centro_mundo_x, topo_mundo_y, visivel=True):
        if not visivel:
            return False
        sprite = obter_tecla_mundo(self.tecla, self.estado, self.escala)
        # flutuacao discreta
        fase = (self._timer // 18) % 4
        flutuar = (0, -1, -self._offset_flutuar, -1)[fase]
        desloc_y = flutuar + (self._offset_press if self.estado == "pressionado" else 0)
        x = int(centro_mundo_x - sprite.get_width() // 2 - camera.offset.x)
        y = int(topo_mundo_y - sprite.get_height() + desloc_y - camera.offset.y)
        rect = sprite.get_rect(topleft=(x, y))
        tela_rect = tela_vista.get_rect()
        if not rect.colliderect(tela_rect):
            return False
        tela_vista.blit(sprite, rect.topleft)
        return True


def limpar_cache():
    global _folha, _folha_carregada
    _cache.clear()
    _cache_escalas.clear()
    _cache_mundo.clear()
    _folha = None
    _folha_carregada = False


def _ao_mudar_escala_texto(_escala):
    limpar_cache()


registrar_observador_escala(_ao_mudar_escala_texto)
