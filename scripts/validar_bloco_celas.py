"""Percurso com entradas de teclado e física real, sem teletransportar o jogador.

python scripts/validar_bloco_celas.py --capturas
Usa SDL dummy; não abre janela nem lê/grava saves.
"""
from pathlib import Path
import argparse
from collections import defaultdict
import json
import os
import sys
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from core.game_scene import Gamescene
from settings import Screen_widht, Screen_height

SAIDA = RAIZ / "docs/mapas/previews/i2"


class Percurso:
    def __init__(self, scene, capturas=False):
        self.scene = scene
        self.capturas = capturas
        self.frames = 0
        self.saltos = 0
        self.marcos = []

    def passo(self, *keys):
        teclas = defaultdict(bool, {key: True for key in keys})
        with patch("pygame.key.get_pressed", return_value=teclas):
            self.scene.atualizar([])
        self.frames += 1
        p, m, c = self.scene.player, self.scene.mapa, self.scene.camera
        assert p.vivo and p.hp == p.hp_max
        assert not p.em_dahs, "O percurso deve funcionar sem dash"
        assert p.rect.collidelist(m.rects_solidos) == -1, (self.frames, p.rect)
        assert 0 <= p.rect.left < p.rect.right <= self.scene.largura_mapa
        assert 0 <= p.rect.top < p.rect.bottom <= self.scene.altura_mapa
        assert 0 <= c.offset.x <= self.scene.largura_mapa - Screen_widht / c.zoom + 1
        assert 0 <= c.offset.y <= self.scene.altura_mapa - Screen_height / c.zoom + 1
        if pygame.K_SPACE in keys:
            self.saltos += 1

    def andar(self, x):
        for _ in range(1400):
            p = self.scene.player
            delta = x - p.rect.centerx
            if abs(delta) <= 3:
                return
            direita = delta > 0
            keys = [pygame.K_d if direita else pygame.K_a]
            # Um pulo comum ao chegar perto de um degrau/obstáculo sólido.
            probe = pygame.Rect(p.rect.right if direita else p.rect.left - 28,
                                p.rect.bottom - 24, 28, 23)
            if p.no_chao and probe.collidelist(self.scene.mapa.rects_solidos) != -1:
                keys.append(pygame.K_SPACE)
            self.passo(*keys)
        raise AssertionError(f"Caminho bloqueado: alvo x={x}, jogador={p.rect}")

    def escalar(self, topo):
        for _ in range(260):
            p = self.scene.player
            if abs(p.rect.top - topo) <= 3:
                return
            self.passo(pygame.K_w if p.rect.top > topo else pygame.K_s)
        raise AssertionError(f"Escada bloqueada: alvo y={topo}, jogador={p.rect}")

    def repousar(self, frames=55):
        for _ in range(frames):
            self.passo()

    def marco(self, nome):
        self.repousar()
        self.marcos.append({"nome": nome, "frame": self.frames,
                            "posicao": list(self.scene.player.rect.topleft)})
        if self.capturas:
            self.scene.desenhar()
            pygame.image.save(self.scene.tela, str(SAIDA / (nome + ".png")))

    def executar(self):
        self.marco("01_spawn")
        self.andar(21 * 32 + 16)
        self.escalar(24 * 32)
        self.andar(25 * 32)
        self.marco("02_corredor")
        self.andar(54 * 32 + 16)
        self.escalar(9 * 32)
        self.andar(63 * 32)
        self.marco("03_cela_destruida")
        self.andar(80 * 32)
        self.marco("04_passagem_profana")
        self.andar(54 * 32 + 16)
        self.escalar(24 * 32)
        self.andar(67 * 32 + 16)
        self.escalar(18 * 32)
        self.andar(70 * 32)
        self.marco("05_plataforma")
        assert self.scene.player._sobre_plataforma
        self.passo(pygame.K_s, pygame.K_SPACE)
        self.repousar()
        assert self.scene.player.rect.bottom == 26 * 32
        self.andar(80 * 32 + 16)
        self.escalar(16 * 32)
        self.andar(83 * 32)
        self.marco("06_galeria")
        assert self.scene.player._sobre_plataforma
        self.passo(pygame.K_s, pygame.K_SPACE)
        self.repousar()
        self.andar(122 * 32 + 16)
        self.marco("07_saida")
        assert self.scene.sala_atual == "bloco_celas_esquecidas"
        # Retorno integral pelo mesmo corredor e escada inicial.
        self.andar(21 * 32 + 16)
        self.escalar(9 * 32)
        self.andar(11 * 32 + 19)
        self.marco("08_retorno")
        assert self.scene.player.rect.bottom == 12 * 32
        return {"frames": self.frames, "saltos_e_drops": self.saltos, "marcos": self.marcos}


def capturar_mapa(scene):
    offset = scene.camera.offset.copy()
    scene.camera.offset.xy = (0, 0)
    full = pygame.Surface((scene.largura_mapa, scene.altura_mapa))
    scene.mapa.desenhar(full, scene.camera)
    for tocha in scene.tochas:
        tocha.desenhar(full, scene.camera)
    scene.player.desenhar(full, scene.camera)
    pygame.image.save(full, str(SAIDA / "bloco_completo.png"))
    pygame.image.save(pygame.transform.scale(full, (2048, 512)), str(SAIDA / "bloco_visao_geral.png"))
    pygame.image.save(full.subsurface((0, 32, 2752, 416)), str(SAIDA / "celas_detalhe.png"))
    for rect in scene.mapa.rects_solidos:
        pygame.draw.rect(full, (60, 160, 240), rect, 1)
    for rect in scene.mapa.rects_plataforma:
        pygame.draw.rect(full, (50, 255, 80), rect, 2)
    for rect in scene.mapa.rects_escada:
        pygame.draw.rect(full, (255, 220, 40), rect, 2)
    pygame.image.save(full, str(SAIDA / "colisoes.png"))
    scene.camera.offset = offset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capturas", action="store_true")
    args = parser.parse_args()
    os.chdir(RAIZ)
    pygame.init()
    tela = pygame.display.set_mode((Screen_widht, Screen_height))
    scene = Gamescene(tela, sala_teste="bloco_celas_esquecidas")
    SAIDA.mkdir(parents=True, exist_ok=True)
    if args.capturas:
        capturar_mapa(scene)
    resultado = Percurso(scene, args.capturas).executar()
    (SAIDA / "percurso.json").write_text(json.dumps(resultado, indent=2), encoding="utf-8")
    print(json.dumps(resultado, indent=2))
    pygame.quit()


if __name__ == "__main__":
    main()
