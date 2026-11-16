"""Capturas reais F.3, sem main/gerenciador de saves ou logging em arquivo.

Executar na raiz: python docs/arte/gerar_previews_f3.py
Antes obtido do commit F.2 (histórico Git necessário). Quadros completos locais;
comparativo versionável usa somente UI própria e poção CC0, sem LY015.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame as pg
from core.game_scene import Gamescene
from entities.objetos.item import get_item
from ui.hud import trilho_status

BASE = 'c5f67921094b5ef9d28069469626e28b97d3afcc'
OUT = ROOT / 'docs/arte/previews'


def classe_anterior(arquivo, nome):
    origem = subprocess.check_output(['git', 'show', f'{BASE}:{arquivo}'], text=True)
    namespace = {}
    exec(compile(origem, f'{BASE}:{arquivo}', 'exec'), namespace)
    return namespace[nome]


OldBoss = classe_anterior('ui/hud/boss.py', 'BarraBoss')
OldNotif = classe_anterior('ui/hud/notificacao.py', 'NotificacaoItem')
OldMsg = classe_anterior('ui/hud/mensagens.py', 'Mensagens')


def integridade():
    return {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
            for n in ('saves.db', 'jogo.log') if (ROOT / n).exists()}


def estado(cena):
    p = cena.player
    campos = ('hp', 'hp_max', 'stamina', 'stamina_max', 'stamina_delay',
              '_frame_atual', 'buff_stamina_duracao', 'ecos', 'inventario')
    return copy.deepcopy({**{k: getattr(p, k) for k in campos},
                          'pocao': vars(p.pocao),
                          'boss_hp': cena.boss_atual.hp if cena.boss_atual else None})


def antiga(hud):
    anterior = copy.copy(hud)
    for chave, valor in vars(hud).items():
        if hasattr(valor, '__dict__'):
            setattr(anterior, chave, copy.copy(valor))
    for atributo, classe, args, campos in (
        ('boss_bar', OldBoss, (hud.fonte_media,),
         ('_boss_hp_display', '_boss_hp_real', '_boss_hp_anterior', '_boss_ultimo_dano', '_boss_timer_dano')),
        ('notificacao_item', OldNotif, (hud.fonte_media,),
         ('_notif_item', '_notif_quantidade', '_notif_timer', '_notif_duracao')),
        ('mensagens', OldMsg, (hud.fonte_mensagem, hud.fonte_media),
         ('_mensagem', '_timer_mensagem', '_prompt')),
    ):
        objeto = classe(*args)
        for campo in campos:
            setattr(objeto, campo, getattr(getattr(hud, atributo), campo))
        setattr(anterior, atributo, objeto)
    return anterior


def desenhar_antiga(hud, tela, player, boss):
    hud.status.desenhar(tela, player)
    hud.pocao_slot.desenhar(tela, player)
    hud.mensagens.desenhar(tela)
    hud.notificacao_item.desenhar(tela)
    hud.ecos.desenhar(tela, player)
    if boss is not None:
        hud.boss_bar.desenhar(tela, boss)


def capturar(cena, nome):
    original = cena.hud.desenhar
    imagens = {}
    dados = estado(cena)

    def hook(tela, player, boss):
        antes = tela.copy()
        desenhar_antiga(antiga(cena.hud), antes, player, boss)
        original(tela, player, boss)
        imagens.update(antes=antes, depois=tela.copy())

    cena.hud.desenhar = hook
    try:
        cena.desenhar()
    finally:
        cena.hud.desenhar = original
    assert estado(cena) == dados
    mascaradas = []
    for chave, imagem in imagens.items():
        pg.image.save(imagem, OUT / f'hud_f3_{nome}_{chave}_local.png')
        mascara = imagem.copy()
        # Região documentada que contém as três apresentações antigas e novas.
        mascara.fill((0, 0, 0), (300, 240, 680, 460))
        mascaradas.append(pg.image.tobytes(mascara, 'RGB'))
    assert mascaradas[0] == mascaradas[1], nome
    prancha = pg.Surface((2560, 752))
    prancha.fill((13, 13, 18))
    for i, chave in enumerate(('antes', 'depois')):
        prancha.blit(cena.hud.fonte_media.render(f'{chave.upper()} F.3 | {nome}', True, (220, 224, 235)), (i * 1280 + 20, 8))
        prancha.blit(imagens[chave], (i * 1280, 32))
    pg.image.save(prancha, OUT / f'hud_f3_{nome}_comparativo_local.png')
    return dict(hp=dados['hp'], stamina=dados['stamina'], boss_hp=dados['boss_hp'],
                sala=cena.sala_atual, zoom=cena.camera.zoom,
                boss=list(cena.hud.boss_bar.rect), notificacao=list(cena.hud.notificacao_item.rect),
                prompt=list(cena.hud.mensagens.rect_prompt), mensagem=list(cena.hud.mensagens.rect_mensagem),
                fora_area_comparada_identico=True, dados_funcionais_preservados=True)


def comparativo_compacto(cena):
    # Só HUD em fundo sintético: permite publicar a direção visual sem cenas/assets de mundo.
    hud, player, boss = cena.hud, cena.player, cena.boss_atual
    hud.mostrar_item_coletado(get_item(2), 3)
    hud.mostrar_prompt('[E] Abrir porta')
    hud.mostra_mensagem('Você recuperou seus Ecos Profanos')
    prancha = pg.Surface((1280, 500))
    prancha.fill((13, 13, 18))
    for i, label in enumerate(('ANTES F.3', 'DEPOIS F.3')):
        s = pg.Surface((1280, 720))
        s.fill((210, 214, 222))
        if i == 0:
            antigo = antiga(hud)
            antigo.mensagens.desenhar(s)
            antigo.notificacao_item.desenhar(s)
            antigo.boss_bar.desenhar(s, boss)
        else:
            hud.mensagens.desenhar(s)
            hud.notificacao_item.desenhar(s)
            hud.boss_bar.desenhar(s, boss)
        prancha.blit(s, (i * 640, 32), (320, 240, 640, 460))
        prancha.blit(hud.fonte_media.render(label, True, (220, 224, 235)), (i * 640 + 16, 8))
    pg.image.save(prancha, OUT / 'hud_f3_comparativo.png')


def main():
    arquivos = integridade()
    pg.init()
    random.seed(0)
    tela = pg.display.set_mode((1280, 720))
    # Fallback público garantido mesmo em máquinas com LY015 instalado.
    trilho_status.CAMINHO_TRILHO = ROOT / 'docs/arte/previews/ly015_inexistente_f3.png'
    trilho_status.limpar_cache()
    resultado = dict(base=BASE, resolucao=[1280, 720], driver=pg.display.get_driver(), cenarios={})
    try:
        cena = Gamescene(tela)
        for _ in range(12):
            cena.atualizar([])
        for _ in range(60):
            cena.camera.atualizar(cena.player.rect)
        cena.hud.mostrar_item_coletado(get_item(3), 1)
        resultado['cenarios']['exploracao_item'] = capturar(cena, 'exploracao_item')
        cena.hud.mostrar_prompt('[E] Abrir baú')
        resultado['cenarios']['prompt_item'] = capturar(cena, 'prompt_item')
        cena.hud.mostra_mensagem('Você recuperou seus Ecos Profanos')
        resultado['cenarios']['mensagem_item'] = capturar(cena, 'mensagem_item')

        cena = Gamescene(tela)
        # Parâmetro existente contorna o spawn preexistente; nenhuma correção de mundo.
        cena._carregar_sala('calabouço_5', posiçao_spwan=(4, 8))
        cena.player.equipar(get_item(1))
        boss = cena.boss_atual
        cena.player.rect.midbottom = (boss.rect.centerx - 100, boss.rect.bottom)
        for _ in range(60):
            cena.camera.atualizar(cena.player.rect)
        resultado['cenarios']['chefe_cheio'] = capturar(cena, 'chefe_cheio')
        cena.player._disparar_ataque(False)
        for _ in range(14):
            cena.atualizar([])
        assert boss.hp < boss.hp_max
        resultado['cenarios']['combate_real'] = capturar(cena, 'combate_real')
        boss.hp = boss.hp_max // 2
        resultado['cenarios']['chefe_dano'] = capturar(cena, 'chefe_dano')
        for _ in range(120):
            cena.hud.atualizar()
        resultado['cenarios']['chefe_meio'] = capturar(cena, 'chefe_meio')
        boss.hp = boss.hp_max // 10
        cena.hud.boss_bar.desenhar(pg.Surface((1280, 720)), boss)
        for _ in range(120):
            cena.hud.atualizar()
        resultado['cenarios']['chefe_baixo'] = capturar(cena, 'chefe_baixo')
        cena.hud.mostrar_item_coletado(get_item(2), 3)
        resultado['cenarios']['chefe_item'] = capturar(cena, 'chefe_item')
        cena.hud.mostrar_prompt('[E] Abrir porta')
        cena.hud.mostra_mensagem('Você recuperou seus Ecos Profanos')
        cena.player.hp, cena.player.stamina = 40, 26
        cena.player.buff_stamina_duracao = 180
        cena.player.ecos = 1234567890123456789
        resultado['cenarios']['combate_completo'] = capturar(cena, 'combate_completo')
        comparativo_compacto(cena)
        boss.hp = 0
        cena.hud.boss_bar.desenhar(pg.Surface((1280, 720)), boss)
        for _ in range(120):
            cena.hud.atualizar()
        resultado['cenarios']['chefe_zero'] = capturar(cena, 'chefe_zero')
        # Medição isolada da HUD após aquecimento; não é benchmark do jogo completo.
        inicio = time.perf_counter()
        for _ in range(600):
            cena.hud.desenhar(tela, cena.player, boss)
            cena.hud.atualizar()
        resultado['hud_ms_por_frame_600_desenhos'] = round((time.perf_counter() - inicio) * 1000 / 600, 3)
        assert integridade() == arquivos
        resultado['arquivos_pessoais_inalterados'] = arquivos
        resultado['fullscreen'] = 'Não validado: sem display ou ferramentas de desktop nesta sessão.'
        (OUT / 'hud_f3_evidencias.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('OK: 11 cenários reais pareados, dados/log intactos e comparativo 1x.')
    finally:
        pg.quit()


if __name__ == '__main__':
    main()
