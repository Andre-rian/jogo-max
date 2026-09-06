import pygame
import math
import random

from settings import Screen_widht, Screen_height

Preto_absoluto      = (13, 13, 15)
Cinza_carvao        = (24, 24, 28)
Cinza_azulado       = (37, 41, 54)
Azul_espectral      = (82, 104, 168)
Azul_claro          = (120, 141, 204)
Roxo_profundo       = (67, 36, 95)
Roxo_espectral      = (112, 64, 160)
Branco_texto        = (214, 211, 216)
Cinza_texto         = (152, 148, 160)
Cinza_texto_escuro  = (98, 95, 108)
Vermelho_ritual     = (168, 42, 54)
Verde_cura          = (92, 168, 118)

_FONTES_TITULO  = ("palatinolinotype", "georgia", "cambria", "constantia", "timesnewroman", "sylfaen")
_FONTES_TEXTO   = ("georgia", "constantia", "palatinolinotype", "cambria", "sylfaen")

_fontes_ok = None
_fonte_cache = {}

_cache = {}
_particulas = None


def _fontes_disponiveis():
    global _fontes_ok
    if _fontes_ok is None:
        _fontes_ok = set(pygame.font.get_fonts())
    return _fontes_ok


def _primeira_fonte(candidatos):
    disp = _fontes_disponiveis()
    for c in candidatos:
        if c in disp:
            return c
    return None


def fonte(candidatos, tamanho, negrito=False):
    chave = (tuple(candidatos), tamanho, negrito)
    if chave not in _fonte_cache:
        nome = _primeira_fonte(candidatos)
        _fonte_cache[chave] = pygame.font.SysFont(nome, tamanho, bold=negrito)
    return _fonte_cache[chave]


def Fonte_titulo(tamanho, negrito=False):
    return fonte(_FONTES_TITULO, tamanho, negrito)


def Fonte_texto(tamanho):
    return fonte(_FONTES_TEXTO, tamanho)


def clarear(cor, fator):
    return tuple(min(255, int(c + (255 - c) * fator)) for c in cor)


def escurecer(cor, fator):
    return tuple(int(c * (1 - fator)) for c in cor)


def misturar(cor1, cor2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(cor1, cor2))


def desenhar_titulo(tela, texto, fonte_tit, cor, centro_x, y, espacamento=4):
    total = 0
    for c in texto:
        total += fonte_tit.size(c)[0]
    total += espacamento * max(0, len(texto) - 1)
    x = int(centro_x - total / 2)
    for c in texto:
        surf = fonte_tit.render(c, True, cor)
        tela.blit(surf, (x, y))
        x += surf.get_width() + espacamento


def desenhar_linha_ornamental(tela, centro_x, y, meia_largura, cor):
    pygame.draw.line(tela, escurecer(cor, 0.55),
                     (centro_x - meia_largura, y), (centro_x - 14, y), 1)
    pygame.draw.line(tela, escurecer(cor, 0.55),
                     (centro_x + 14, y), (centro_x + meia_largura, y), 1)
    l = 5
    pontos = [(centro_x, y - l), (centro_x + l, y), (centro_x, y + l), (centro_x - l, y)]
    pygame.draw.lines(tela, cor, True, pontos, 1)


def _brilho_radial(raio, cor):
    chave = ("brilho", raio, cor)
    if chave not in _cache:
        surf = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for r in range(raio, 0, -1):
            t = (raio - r) / raio
            alpha = int(255 * (t ** 1.5))
            pygame.draw.circle(surf, (*cor, alpha), (raio, raio), r)
        _cache[chave] = surf
    return _cache[chave]


def adicionar_brilho(tela, cx, cy, raio, cor, frame, intensidade=0.35):
    pulso = 0.6 + 0.4 * math.sin(frame * 0.05)
    alfa = int(255 * intensidade * pulso)
    surf = _brilho_radial(int(raio), cor)
    surf.set_alpha(alfa)
    tela.blit(surf, (int(cx - raio), int(cy - raio)), special_flags=pygame.BLEND_ADD)


def _construir_fundo():
    w, h = Screen_widht, Screen_height
    base = pygame.Surface((w, h))
    base.fill(Preto_absoluto)

    for y in range(h):
        t = y / h
        cor = misturar(Cinza_carvao, Preto_absoluto, t)
        pygame.draw.line(base, cor, (0, y), (w, y))

    glow = _brilho_radial(260, Azul_espectral)
    base.blit(glow, (w // 2 - 260, h // 2 - 130))

    rnd = random.Random(7)
    for _ in range(520):
        x = rnd.randint(0, w - 1)
        y = rnd.randint(0, h - 1)
        escolha = rnd.random()
        if escolha < 0.5:
            cor = Cinza_azulado
        elif escolha < 0.85:
            cor = (30, 32, 40)
        else:
            cor = (52, 58, 80)
        fator = rnd.uniform(0.1, 0.5)
        pygame.draw.circle(base, escurecer(cor, 1 - fator), (x, y), rnd.randint(1, 2))

    base.blit(_vignete(w, h, 130))
    return base


def _vignete(w, h, forca=120):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    faixa = int(h * 0.30)
    for i in range(faixa):
        t = (faixa - i) / faixa
        a = int(forca * t)
        cor = (6, 6, 9, a)
        pygame.draw.line(s, cor, (0, i), (w, i))
        pygame.draw.line(s, cor, (0, h - 1 - i), (w, h - 1 - i))
    faixa = int(w * 0.30)
    for i in range(faixa):
        t = (faixa - i) / faixa
        a = int(forca * t)
        cor = (6, 6, 9, a)
        pygame.draw.line(s, cor, (i, 0), (i, h))
        pygame.draw.line(s, cor, (w - 1 - i, 0), (w - 1 - i, h))
    return s


def _construir_particulas():
    rnd = random.Random(11)
    cores = [Azul_espectral, Azul_claro, Roxo_espectral, Roxo_profundo]
    lista = []
    for _ in range(42):
        lista.append({
            "x": rnd.uniform(0, 1) * Screen_widht,
            "y": rnd.uniform(0, 1) * Screen_height,
            "vel": rnd.uniform(0.08, 0.35),
            "raio": rnd.randint(1, 2),
            "fase": rnd.uniform(0, math.tau),
            "vel_fase": rnd.uniform(0.008, 0.03),
            "cor": rnd.choice(cores),
        })
    return lista


def _desenhar_particulas(tela, frame):
    global _particulas
    if _particulas is None:
        _particulas = _construir_particulas()
    for p in _particulas:
        y = (p["y"] - frame * p["vel"]) % Screen_height
        x = p["x"] + math.sin(frame * 0.004 + p["fase"]) * 6
        brilho = 0.35 + 0.3 * (0.5 + 0.5 * math.sin(frame * p["vel_fase"] + p["fase"]))
        cor = escurecer(p["cor"], 1 - brilho)
        pygame.draw.circle(tela, cor, (int(x), int(y)), p["raio"])


def desenhar_fundo(tela, frame):
    if "fundo" not in _cache:
        _cache["fundo"] = _construir_fundo()
    tela.blit(_cache["fundo"], (0, 0))

    pulso = 0.5 + 0.5 * math.sin(frame * 0.02)
    glow = _brilho_radial(230, Roxo_profundo)
    glow.set_alpha(int(20 + 16 * pulso))
    tela.blit(glow, (Screen_widht // 2 - 230, Screen_height // 2 - 120),
              special_flags=pygame.BLEND_ADD)

    _desenhar_particulas(tela, frame)


def desenhar_overlay(tela, alpha=165):
    if "overlay" not in _cache:
        _cache["overlay"] = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
        _cache["overlay_vinheta"] = _vignete(Screen_widht, Screen_height, 170)
    ov = _cache["overlay"]
    ov.fill((9, 9, 11, alpha))
    ov.blit(_cache["overlay_vinheta"])
    tela.blit(ov, (0, 0))


def _desenhar_cantos(tela, rect, cor, tamanho=6):
    x, y, w, h = rect
    pygame.draw.line(tela, cor, (x, y + tamanho), (x, y), 1)
    pygame.draw.line(tela, cor, (x, y), (x + tamanho, y), 1)
    pygame.draw.line(tela, cor, (x + w - 1, y), (x + w - 1, y + tamanho), 1)
    pygame.draw.line(tela, cor, (x + w - 1, y), (x + w - 1 - tamanho, y), 1)
    pygame.draw.line(tela, cor, (x, y + h - 1), (x + tamanho, y + h - 1), 1)
    pygame.draw.line(tela, cor, (x, y + h - 1), (x, y + h - 1 - tamanho), 1)
    pygame.draw.line(tela, cor, (x + w - 1, y + h - 1), (x + w - 1, y + h - 1 - tamanho), 1)
    pygame.draw.line(tela, cor, (x + w - 1, y + h - 1), (x + w - 1 - tamanho, y + h - 1), 1)


def desenhar_painel(tela, rect, frame, cor_borda=None, titulo=None, titulo_fonte=None):
    x, y, w, h = rect
    if cor_borda is None:
        cor_borda = Azul_espectral
    pulso = 0.5 + 0.5 * math.sin(frame * 0.03)

    pygame.draw.rect(tela, Cinza_carvao, rect, border_radius=4)

    pygame.draw.rect(tela, clarear(Cinza_carvao, 0.12),
                     (x + 3, y + 3, w - 6, 2), border_radius=1)
    pygame.draw.line(tela, escurecer(Cinza_carvao, 0.5),
                     (x + 3, y + h - 3), (x + w - 3, y + h - 3), 1)

    pygame.draw.rect(tela, escurecer(cor_borda, 0.55), rect, 2, border_radius=4)
    cor_interna = misturar(cor_borda, Azul_claro, 0.30 + 0.25 * pulso)
    pygame.draw.rect(tela, cor_interna, rect.inflate(-6, -6), 1, border_radius=3)

    _desenhar_cantos(tela, rect, misturar(cor_borda, Azul_claro, 0.5))

    if titulo:
        if titulo_fonte is None:
            titulo_fonte = Fonte_titulo(22, negrito=True)
        surf = titulo_fonte.render(titulo, True, misturar(Roxo_espectral, Azul_claro, 0.35))
        tela.blit(surf, (x + 16, y + 14))
        desenhar_linha_ornamental(tela, x + 16 + surf.get_width() // 2,
                                  y + 14 + surf.get_height() + 6,
                                  min(90, w // 3), Roxo_espectral)


def desenhar_botao(tela, rect, texto, selecionado, frame,
                   fonte_btn=None, cor_texto=None, marcador=True):
    x, y, w, h = rect
    cx, cy = rect.centerx, rect.centery
    if fonte_btn is None:
        fonte_btn = Fonte_texto(22)

    if selecionado:
        adicionar_brilho(tela, cx, cy, w // 2 + 14, Roxo_profundo, frame, intensidade=0.30)
        pygame.draw.rect(tela, Cinza_azulado, rect, border_radius=4)
        cor_borda = misturar(Azul_claro, Roxo_espectral, 0.25 + 0.2 * (0.5 + 0.5 * math.sin(frame * 0.06)))
    else:
        pygame.draw.rect(tela, escurecer(Cinza_carvao, 0.18), rect, border_radius=4)
        cor_borda = escurecer(Azul_espectral, 0.55)

    pygame.draw.rect(tela, escurecer(cor_borda, 0.55), rect, 2, border_radius=4)
    pygame.draw.rect(tela, cor_borda, rect.inflate(-6, -6), 1, border_radius=3)

    cor_txt = cor_borda if selecionado else (cor_texto or Cinza_texto)
    surf = fonte_btn.render(texto, True, cor_txt)
    if selecionado and marcador:
        lado = 5
        pontos = [(x + 12, cy), (x + 12 + lado, cy - lado), (x + 12 + lado * 2, cy),
                  (x + 12 + lado, cy + lado)]
        pygame.draw.polygon(tela, cor_txt, pontos)
    tela.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))


def _fragmento(tela, x, y, cor, tamanho):
    pontos = [(x, y - tamanho), (x + tamanho, y), (x, y + tamanho), (x - tamanho, y)]
    pygame.draw.polygon(tela, cor, pontos)


def desenhar_eco_profano(tela, cx, cy, raio, frame):
    pulso = 0.5 + 0.5 * math.sin(frame * 0.035)
    rn = int(raio * (0.5 + 0.08 * pulso))

    adicionar_brilho(tela, cx, cy, int(raio * 2.0), Roxo_profundo, frame, intensidade=0.22)

    pygame.draw.circle(tela, (7, 5, 11), (cx, cy), rn)
    pygame.draw.circle(tela, Roxo_espectral, (cx, cy), rn, 1)
    pygame.draw.circle(tela, Azul_espectral, (cx, cy), max(1, int(rn * 0.6)), 1)

    fragmentos = [
        (0.020, raio + 3, Azul_claro, 3),
        (0.031, raio + 6, Roxo_espectral, 2),
        (0.024, raio + 8, Azul_espectral, 2),
    ]
    for i, (vel, dist, cor, tam) in enumerate(fragmentos):
        ang = frame * vel + i * 2.1
        fx = int(cx + math.cos(ang) * dist)
        fy = int(cy + math.sin(ang) * dist)
        _fragmento(tela, fx, fy, cor, tam)