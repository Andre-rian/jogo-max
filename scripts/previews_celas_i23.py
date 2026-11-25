"""Captura o mapa real sem iniciar main, saves ou configuração de log.

python scripts/previews_celas_i23.py --estado antes|depois
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
from scripts.auditar_celas_i22 import REGIOES

SAIDA = RAIZ / "docs/mapas/previews/i23"


def capturar(estado):
    if estado == "antes" and (SAIDA / "antes_completo.png").exists():
        raise SystemExit("Captura anterior já existe; preservada para comparação.")
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
    fonte = pygame.font.SysFont("consolas", 20)
    for nome, rect in REGIOES.items():
        atual = full.subsurface(rect)
        pygame.image.save(atual, str(SAIDA / f"{estado}_{nome}.png"))
        anterior = SAIDA / f"antes_{nome}.png"
        if estado == "depois" and anterior.exists():
            tamanho = (min(rect[2], 960), round(rect[3] * min(1, 960 / rect[2])))
            par = pygame.Surface((tamanho[0] * 2, tamanho[1] + 40))
            par.fill((15, 18, 25))
            par.blit(fonte.render("ANTES | I.2.2", True, (230, 215, 200)), (12, 9))
            par.blit(fonte.render("DEPOIS | I.2.3", True, (200, 225, 210)), (tamanho[0] + 12, 9))
            par.blit(pygame.transform.scale(pygame.image.load(str(anterior)), tamanho), (0, 40))
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
