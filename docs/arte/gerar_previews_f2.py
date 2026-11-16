"""Capturas F.2 reproduzíveis: SDL dummy, sem main, logs ou gerenciador de saves.

Execute na raiz: python docs/arte/gerar_previews_f2.py
PNG *_local.png: capturas completas, não versionar. Comparativo compacto:
somente os dois componentes, originais/CC0, sobre fundos sintéticos.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import runpy
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame as pg

from core.game_scene import Gamescene
from entities.objetos.item import get_item
from entities.objetos.pocao import Pocao
from ui.estilo import Fonte_texto, Fonte_titulo
from ui.hud.ecos import IndicadorEcos
from ui.hud.pocao import SlotPocao
from ui.hud.status import BarrasStatus

OUT = ROOT / 'docs/arte/previews'
OldPotion = runpy.run_path(str(ROOT / 'docs/arte/referencias/pocao_antes_f2.py'))['SlotPocao']
OldEcos = runpy.run_path(str(ROOT / 'docs/arte/referencias/ecos_antes_f2.py'))['IndicadorEcos']


def estado(player):
    campos = ('hp', 'hp_max', 'stamina', 'stamina_max', 'stamina_delay',
              '_frame_atual', 'buff_stamina_duracao', 'ecos', 'inventario')
    return copy.deepcopy({**{k: getattr(player, k) for k in campos}, 'pocao': vars(player.pocao)})


def integridade():
    return {nome: hashlib.sha256((ROOT / nome).read_bytes()).hexdigest()
            for nome in ('saves.db', 'jogo.log') if (ROOT / nome).exists()}


def capturar(cena, nome):
    original = cena.hud.desenhar
    imagens = {}
    antes = estado(cena.player)
    boss_hp = cena.boss_atual.hp if cena.boss_atual else None

    def hook(tela, player, boss):
        antiga = copy.copy(cena.hud)
        for chave, valor in vars(antiga).items():
            if hasattr(valor, '__dict__'):
                setattr(antiga, chave, copy.copy(valor))
        antiga.pocao_slot = OldPotion(cena.hud.fonte_pequena)
        antiga.pocao_slot._flash_da_pocao = cena.hud.pocao_slot._flash_da_pocao
        antiga.ecos = OldEcos(cena.hud.fonte_media)
        antiga.ecos._frame_hud = cena.hud.ecos._frame_hud
        anterior = tela.copy()
        type(antiga).desenhar(antiga, anterior, player, boss)
        original(tela, player, boss)
        imagens.update(antes=anterior, depois=tela.copy())

    cena.hud.desenhar = hook
    try:
        cena.desenhar()
    finally:
        cena.hud.desenhar = original
    assert estado(cena.player) == antes
    assert boss_hp == (cena.boss_atual.hp if cena.boss_atual else None)
    mascaradas = []
    for chave, imagem in imagens.items():
        pg.image.save(imagem, OUT / f'hud_f2_{nome}_{chave}_local.png')
        mascara = imagem.copy()
        for rect in ((16, 626, 156, 78), (896, 610, 384, 110)):
            mascara.fill((0, 0, 0), rect)
        mascaradas.append(pg.image.tobytes(mascara, 'RGB'))
    assert mascaradas[0] == mascaradas[1], nome
    return dict(hp=cena.player.hp, stamina=cena.player.stamina,
                cargas=cena.player.pocao.cargas, cooldown=cena.player.pocao._colldown,
                flash=cena.hud.pocao_slot._flash_da_pocao, ecos=cena.player.ecos,
                boss_hp=boss_hp, zoom=cena.camera.zoom,
                fora_componentes_identico=True, dados_preservados=True)


def comparativo():
    fonte = Fonte_texto(14)
    media = Fonte_titulo(18, negrito=True)
    # Todos os recortes são 1x: a prancha não redimensiona sprites nem textos.
    prancha = pg.Surface((1136, 832))
    prancha.fill((13, 13, 18))
    for i, label in enumerate(('ANTES F.2', 'DEPOIS F.2')):
        prancha.blit(media.render(label, True, (220, 224, 235)), (i * 568 + 16, 10))
    casos = [(3, 0, False), (1, 137, False), (0, 1234567890123456789, False),
             (2, 137, True), (3, 10**59 + 123, False)]
    for linha, (cargas, ecos, flash) in enumerate(casos):
        y = 42 + linha * 158
        cor = (210, 214, 222) if linha % 2 else (18, 20, 28)
        p = SimpleNamespace(pocao=Pocao(), ecos=ecos)
        p.pocao.cargas = cargas
        label = f'Cargas {cargas}/3 | ' + ('flash de uso' if flash else f'Ecos {ecos}')
        prancha.blit(fonte.render(label, True, (220, 224, 235)), (12, y))
        for coluna, (PocaoHUD, EcoHUD) in enumerate(((OldPotion, OldEcos), (SlotPocao, IndicadorEcos))):
            tela = pg.Surface((1280, 720))
            tela.fill(cor)
            slot, contador = PocaoHUD(fonte), EcoHUD(media)
            if flash:
                slot.flash()
            slot.desenhar(tela, p)
            contador.desenhar(tela, p)
            x = coluna * 568
            prancha.blit(tela, (x + 8, y + 26), (16, 626, 156, 78))
            # Área do contador recortada separadamente, sem escala.
            prancha.blit(tela, (x + 172, y + 26), (896, 594, 384, 110))
    pg.image.save(prancha, OUT / 'hud_f2_comparativo.png')


def main():
    arquivos_antes = integridade()
    pg.init()
    random.seed(0)
    tela = pg.display.set_mode((1280, 720))
    evidencias = {}
    try:
        cena = Gamescene(tela)
        # Todas as capturas desta fase usam o status público, sem LY015.
        cena.hud.status = BarrasStatus(cena.hud.fonte_pequena, usar_asset=False)
        for _ in range(12):
            cena.atualizar([])
        for _ in range(60):
            cena.camera.atualizar(cena.player.rect)
        evidencias['exploracao'] = capturar(cena, 'exploracao')
        cena.player.hp, cena.player.stamina = 40, 0
        cena.player.stamina_delay = 30
        cena.player.pocao.cargas = 1
        cena.player.ecos = 137
        evidencias['vida_baixa_stamina_vazia'] = capturar(cena, 'vida_baixa_stamina_vazia')
        assert cena.player.pocao.usar(cena.player)
        # Apenas o slot observa o uso para parear o mesmo flash nas duas versões.
        cena.hud.pocao_slot.desenhar(pg.Surface((1280, 720)), cena.player)
        evidencias['uso_pocao'] = capturar(cena, 'uso_pocao')
        for _ in range(12):
            cena.hud.atualizar()
        cena.player.ecos = 1234567890123456789
        evidencias['sem_cargas_ecos_grandes'] = capturar(cena, 'sem_cargas_ecos_grandes')

        cena = Gamescene(tela)
        cena.hud.status = BarrasStatus(cena.hud.fonte_pequena, usar_asset=False)
        cena._carregar_sala('calabouço_5', posiçao_spwan=(4, 8))
        cena.player.equipar(get_item(1))
        boss = cena.boss_atual
        cena.player.rect.midbottom = (boss.rect.centerx - 100, boss.rect.bottom)
        for _ in range(60):
            cena.camera.atualizar(cena.player.rect)
        cena.player._disparar_ataque(False)
        for _ in range(14):
            cena.atualizar([])
        assert boss.hp < boss.hp_max
        cena.player.ecos = 1234567890123456789
        evidencias['chefe'] = capturar(cena, 'chefe')
        comparativo()
        assert integridade() == arquivos_antes
        evidencias['arquivos_pessoais_inalterados'] = arquivos_antes
        (OUT / 'hud_f2_evidencias.json').write_text(
            json.dumps(evidencias, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('OK: cinco cenários, comparativo 1x, dados e arquivos pessoais preservados.')
    finally:
        pg.quit()


if __name__ == '__main__':
    main()
