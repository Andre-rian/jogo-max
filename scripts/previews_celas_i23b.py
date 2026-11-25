"""Revisao artistica: enquadramentos no renderer e zoom reais, sem main/saves."""
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
from settings import Screen_widht, Screen_height, ZOOM_PADRAO
from scripts.validar_bloco_celas import Percurso

SAIDA = RAIZ / "docs/mapas/previews/i23b"
ENQUADRAMENTOS = {"cela_1_confinamento": (0, 0), "cela_2_prisioneiro": (760, 0),
                  "cela_3_eco": (1536, 0), "saida": (3148, 490)}


def capturar(estado):
    destino = SAIDA / estado
    if estado == "antes" and (SAIDA / "depois").exists():
        raise SystemExit("Evidencias anteriores preservadas.")
    destino.mkdir(parents=True, exist_ok=True)
    pygame.init()
    tela = pygame.display.set_mode((Screen_widht, Screen_height))
    cena = Gamescene(tela, sala_teste="bloco_celas_esquecidas")
    percurso = Percurso(cena)
    percurso.repousar()
    meta = {"zoom": ZOOM_PADRAO, "resolucao": [Screen_widht, Screen_height],
            "enquadramentos_editoriais": {}, "capturas_jogaveis": {}}
    # Mesma escala e renderer; apenas a camera e enquadrada para inspecionar cada cela.
    # Nao move o jogador para dentro da cela fechada, nem modifica o mapa.
    for nome, offset in ENQUADRAMENTOS.items():
        cena.camera.offset.xy = offset
        cena.desenhar()
        pygame.image.save(tela, str(destino / f"{nome}.png"))
        meta["enquadramentos_editoriais"][nome] = list(offset)
    cena.camera.offset.xy = (0, 0)
    def registrar(nome):
        percurso.repousar()
        cena.desenhar()
        pygame.image.save(tela, str(destino / f"{nome}.png"))
        meta["capturas_jogaveis"][nome] = {"player": list(cena.player.rect.topleft),
                                         "camera": list(cena.camera.offset), "zoom": cena.camera.zoom}
    registrar("jogo_01_spawn")
    percurso.andar(18 * 32 + 16)
    registrar("jogo_02_vista_cela_fechada")
    percurso.andar(21 * 32 + 16)
    percurso.escalar(24 * 32)
    percurso.andar(54 * 32 + 16)
    percurso.escalar(9 * 32)
    percurso.andar(63 * 32)
    registrar("jogo_03_eco")
    percurso.andar(71 * 32)
    registrar("jogo_04_fissura")
    percurso.andar(54 * 32 + 16)
    percurso.escalar(24 * 32)
    percurso.andar(122 * 32 + 16)
    registrar("jogo_05_saida")
    (destino / "capturas.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    if estado == "depois":
        for nome in ENQUADRAMENTOS:
            # Comparacao sem reduzir as capturas de 1280x720: antes sobre depois.
            par = pygame.Surface((1280, 1480))
            par.fill((16, 20, 30))
            fonte = pygame.font.SysFont("consolas", 16)
            for y, rotulo in ((0, "ANTES"), (740, "DEPOIS")):
                par.blit(fonte.render(rotulo + " | zoom 1.35 | 1280x720", True, (215, 220, 230)), (10, y))
                par.blit(pygame.image.load(str(SAIDA / rotulo.lower() / f"{nome}.png")), (0, y + 20))
            pygame.image.save(par, str(SAIDA / f"comparativo_{nome}.png"))
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estado", choices=("antes", "depois"), required=True)
    os.chdir(RAIZ)
    capturar(parser.parse_args().estado)
