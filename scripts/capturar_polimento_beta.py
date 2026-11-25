"""Capturas comparáveis de pontos locais; posicionamento de câmera, não teste de percurso."""
from pathlib import Path
import argparse
import os
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from core.game_scene import Gamescene

PONTOS = (
    ("01_celas_saida", "bloco_celas_esquecidas", 119, 24),
    ("02_arsenal_entrada", "antigo_arsenal_guardas", 5, 18),
    ("03_arsenal_galeria", "antigo_arsenal_guardas", 40, 13),
    ("04_arsenal_saida", "antigo_arsenal_guardas", 65, 18),
    ("05_corredores_galeria", "corredores_profundos", 65, 11),
    ("06_corredores_saida", "corredores_profundos", 105, 18),
    ("07_arena_entrada", "arena_chefe", 5, 18),
)


def capturar(etapa):
    os.chdir(RAIZ)
    pygame.init()
    tela = pygame.display.set_mode((1280, 720))
    destino = RAIZ / "docs/beta/polimento" / etapa
    destino.mkdir(parents=True, exist_ok=True)
    cena = Gamescene(tela)
    for nome, sala, col, linha in PONTOS:
        cena._carregar_sala(sala)
        cena.player.rect.topleft = (col * 32, linha * 32)
        cena.tutorial_contextual = None
        cena.hud.limpar_mensagem()
        for _ in range(100):
            cena.camera.atualizar(cena.player.rect)
        cena.desenhar()
        pygame.image.save(tela, str(destino / f"{nome}.png"))
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("etapa", choices=("antes", "depois"))
    capturar(parser.parse_args().etapa)
