"""Medições isoladas e capturas comparáveis, sem importar main ou acessar saves pessoais."""
from collections import defaultdict
from pathlib import Path
from statistics import median
from time import perf_counter
from unittest.mock import patch
import argparse
import json
import os
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from core.combat import CombatSystem
from core.game_scene import Gamescene
from world.niveis import SALAS_BETA

SAIDA = RAIZ / "docs/beta/dano_ecofoco"


def jogador(tela):
    cena = Gamescene(tela)
    cena._carregar_sala(SALAS_BETA[1])
    next(b for b in cena.baus if b.id_item == 1)._dar_item(cena.player, cena.hud)
    cena.player.nivel = 10  # fixture solicitada; não muda o nível inicial da campanha
    return cena


def medir_impacto(cena, inimigo, combo=False):
    """Máscaras e DamageEvents reais; atores posicionados para isolar um ataque."""
    p = cena.player
    p.rect.topleft = (100, 576)
    p.vel.xy = (0, 0)
    p.olhando_dir = True
    inimigo.rect.midbottom = (p.rect.centerx + 35, p.rect.bottom)
    inimigo.olhando_dir = False
    p.encerrar_ataque()
    p._disparar_ataque(combo)
    sistema = CombatSystem()
    eventos = []
    for _ in range(90):
        p.atualizar_mask()
        inimigo.atualizar_mask()
        eventos.extend(e for e in sistema.resolver(p, [inimigo], [], []) if e.aplicado)
    return [e.dano for e in eventos]


def medir_danos(tela):
    cena = jogador(tela)
    resultados = {}
    for indice in (1, 2, 3):
        cena._carregar_sala(SALAS_BETA[indice])
        for inimigo in list(cena.inimigos):
            impactos = medir_impacto(cena, inimigo)
            assert len(impactos) == 1, (inimigo.SOM_ID, impactos)
            resultados[inimigo.SOM_ID] = {"hp": inimigo.hp_max, "normal": impactos[0]}
    cena._carregar_sala(SALAS_BETA[3])
    resultados["combo_chefe"] = medir_impacto(cena, cena.boss_atual, combo=True)
    p = cena.player
    progressao = []
    for forca, destreza in ((10, 10), (15, 10), (10, 15), (15, 15), (20, 20)):
        p.forca, p.destreza = forca, destreza
        progressao.append({"forca": forca, "destreza": destreza,
                          "normal": p.calcular_dano("normal"), "combo": p.calcular_dano("combo")})
    return {"alvos": resultados, "progressao": progressao, "hp_max_jogador": p.hp_max}


def capturar_e_medir(tela, pasta):
    cena = Gamescene(tela)
    cena._carregar_sala(SALAS_BETA[2])
    cena.inimigos.clear()  # enquadramento/benchmark isolados; percurso completo é outro teste
    foco = cena.fogueiras[0]
    cena.player.rect.midbottom = (foco.rect.centerx - 70, foco.rect.bottom)
    cena.tutorial_contextual = None
    cena.hud.limpar_mensagem()
    for _ in range(100):
        cena.camera.atualizar(cena.player.rect)
    desempenho = {}
    for estado in ("inativo", "ativo", "menu"):
        foco.ativa = estado != "inativo"
        foco._frame = 120
        if estado == "menu":
            cena.menu_fogueira.abrir()
        cena.desenhar()
        pygame.image.save(tela, str(pasta / f"ecofoco_{estado}.png"))
        tempos = []
        with patch("pygame.key.get_pressed", return_value=defaultdict(bool)):
            for i in range(270):
                inicio = perf_counter()
                cena.atualizar([])
                cena.desenhar()
                if i >= 30:
                    tempos.append((perf_counter() - inicio) * 1000)
        desempenho[estado] = {"mediana_ms": round(median(tempos), 3),
                             "p95_ms": round(sorted(tempos)[int(len(tempos)*.95)], 3),
                             "amostras": len(tempos)}
    return desempenho


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("etapa", choices=("antes", "depois"))
    args = parser.parse_args()
    pasta = SAIDA / args.etapa
    if args.etapa == "antes" and pasta.exists():
        raise SystemExit("Capturas anteriores já existem; preservar a evidência histórica.")
    pasta.mkdir(parents=True, exist_ok=True)
    os.chdir(RAIZ)
    pygame.init()
    tela = pygame.display.set_mode((1280, 720))
    resultado = {"dano": medir_danos(tela), "render": capturar_e_medir(tela, pasta),
                 "metodo": "Fixtures isoladas; DamageEvents/máscaras reais; SDL dummy 1280x720; update+draw sem limitador de FPS."}
    (pasta / "medicoes.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    pygame.quit()


if __name__ == "__main__":
    main()
