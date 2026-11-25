"""Capturas de curadoria; lê o TMX, nunca gera ou modifica o mapa.

python scripts/auditar_celas_i22.py --estado antes|depois
"""
from pathlib import Path
import argparse
import json
import os
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from core.game_scene import Gamescene

SAIDA = RAIZ / "docs/mapas/previews/i22"
REGIOES = {
    "cela_spawn": (0, 32, 832, 416),
    "cela_fechada": (800, 32, 800, 416),
    "cela_destruida": (1536, 32, 832, 416),
    "passagem": (2176, 192, 576, 256),
    "corredor_oeste": (0, 384, 1536, 480),
    "galeria": (2048, 384, 768, 480),
    "corredor_leste": (2784, 384, 1312, 480),
    "saida": (3584, 576, 512, 288),
}


def capturar(estado):
    pygame.init()
    pygame.display.set_mode((1280, 720))
    cena = Gamescene(pygame.display.get_surface(), sala_teste="bloco_celas_esquecidas")
    cena.camera.offset.xy = (0, 0)
    full = pygame.Surface((cena.largura_mapa, cena.altura_mapa))
    cena.mapa.desenhar(full, cena.camera)
    for tocha in cena.tochas:
        tocha.desenhar(full, cena.camera)
    cena.player.desenhar(full, cena.camera)
    SAIDA.mkdir(parents=True, exist_ok=True)
    pygame.image.save(full, str(SAIDA / f"{estado}_completo.png"))
    pygame.image.save(pygame.transform.scale(full, (2048, 512)), str(SAIDA / f"{estado}_visao_geral.png"))
    font = pygame.font.SysFont("consolas", 20)
    for nome, rect in REGIOES.items():
        atual = full.subsurface(rect)
        pygame.image.save(atual, str(SAIDA / f"{estado}_{nome}.png"))
        antes = SAIDA / f"antes_{nome}.png"
        if estado == "depois" and antes.exists():
            anterior = pygame.image.load(str(antes))
            w, h = atual.get_size()
            escala = min(1, 960 / w)
            tamanho = (int(w * escala), int(h * escala))
            par = pygame.Surface((tamanho[0] * 2, tamanho[1] + 40))
            par.fill((15, 18, 25))
            par.blit(font.render("ANTES | I.2.1", True, (230, 215, 200)), (12, 9))
            par.blit(font.render("DEPOIS | I.2.2", True, (200, 225, 210)), (tamanho[0] + 12, 9))
            par.blit(pygame.transform.scale(anterior, tamanho), (0, 40))
            par.blit(pygame.transform.scale(atual, tamanho), (tamanho[0], 40))
            pygame.image.save(par, str(SAIDA / f"comparativo_{nome}.png"))
    (SAIDA / "regioes.json").write_text(json.dumps(REGIOES, indent=2), encoding="utf-8")
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estado", choices=("antes", "depois"), required=True)
    args = parser.parse_args()
    os.chdir(RAIZ)
    capturar(args.estado)
