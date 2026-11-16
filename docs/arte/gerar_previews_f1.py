"""Capturas reais F.1, sem main/save manager. Execute na raiz.

--fullscreen testa uma janela real SDL SCALED|FULLSCREEN por 90 frames.
Sem argumento usa SDL dummy. Prévia restrita não deve entrar no Git.
"""
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT))
FULL='--fullscreen' in sys.argv
if not FULL:
    os.environ['SDL_VIDEODRIVER']='dummy'
else:
    os.environ.pop('SDL_VIDEODRIVER',None)
os.environ['SDL_AUDIODRIVER']='dummy'
import copy
import hashlib
import json
import random
import runpy
from collections import defaultdict
import pygame as pg
pg.init()
screen=pg.display.set_mode((1280,720),pg.SCALED|pg.FULLSCREEN if FULL else 0)
from core.game_scene import Gamescene
from entities.objetos.item import get_item
from ui.hud.status import BarrasStatus
from ui.estilo import Fonte_texto
Old=runpy.run_path(str(ROOT/'docs/arte/referencias/status_antes_f1.py'))['BarrasStatus']
OUT=ROOT/'docs/arte/previews'
font=Fonte_texto(18)
random.seed(0)
evidencias={}


def save(s,name):
    pg.image.save(s,str(OUT/f'hud_f1_{name}_restrito.png'))


def capture(scene,name):
    actual=scene.hud.desenhar
    images={}
    def hook(surface,p,b):
        before=surface.copy()
        oldhud=copy.copy(scene.hud)
        for key,val in vars(oldhud).items():
            if hasattr(val,'__dict__'):
                setattr(oldhud,key,copy.copy(val))
        oldhud.status=Old(scene.hud.fonte_pequena)
        type(oldhud).desenhar(oldhud,before,p,b)
        actual(surface,p,b)
        images['antes']=before
        images['depois']=surface.copy()
    scene.hud.desenhar=hook
    scene.desenhar()
    scene.hud.desenhar=actual
    for key,s in images.items(): save(s,f'{name}_{key}')
    a=images['antes'].copy();b=images['depois'].copy()
    # Tudo fora da região de status deve ficar idêntico.
    for s in (a,b): s.fill((0,0,0),(18,18,282,94))
    assert pg.image.tobytes(a,'RGB')==pg.image.tobytes(b,'RGB'), name
    board=pg.Surface((2560,756));board.fill((15,16,22))
    for i,key in enumerate(('antes','depois')):
        board.blit(font.render(f'{name} — {key} — 1280x720',True,(220,224,235)),(i*1280+20,8))
        board.blit(images[key],(i*1280,36))
    save(board,f'{name}_comparativo')
    p=scene.player
    evidencias[name]=dict(hp=p.hp,hp_max=p.hp_max,stamina=p.stamina,
                          stamina_max=p.stamina_max,delay=p.stamina_delay,
                          frame=p._frame_atual,buff=p.buff_stamina_duracao,
                          zoom=scene.camera.zoom,fora_status_identico=True)
    return images


scene=Gamescene(screen)
for _ in range(12): scene.atualizar([])
for _ in range(60): scene.camera.atualizar(scene.player.rect)
if FULL:
    clock=pg.time.Clock()
    for _ in range(90):
        scene.atualizar(pg.event.get());scene.desenhar();pg.display.flip();clock.tick(60)
    save(screen,'fullscreen')
    (OUT/'hud_f1_fullscreen.json').write_text(json.dumps(dict(driver=pg.display.get_driver(),
        superficie=screen.get_size(),janela=pg.display.get_window_size(),frames=90,
        flags=screen.get_flags()),indent=2),encoding='utf-8')
    pg.quit()
    sys.exit()

capture(scene,'exploracao')
scene.player.stamina=0
scene.player.stamina_delay=30
capture(scene,'stamina_vazia')
for _ in range(45): scene.atualizar([])
assert scene.player.stamina>0
capture(scene,'regenerando')
scene.player.hp=40
scene.player.stamina=26
capture(scene,'vida_baixa')
scene.player.inventario['itens'][4]=1
get_item(4).usar(scene.player,scene.player.inventario)
capture(scene,'buff_raiz')

# Três alturas na mesma superfície de mundo, pela classe integrada real.
world=[]
original=scene.hud.desenhar
scene.hud.desenhar=lambda surface,*args: world.append(surface.copy())
scene.desenhar();scene.hud.desenhar=original
matrix=pg.Surface((960,800));matrix.fill((15,16,22))
for col,h in enumerate((6,8,10)):
    matrix.blit(font.render(f'Stamina: {h} px úteis',True,(220,224,235)),(col*320+10,8))
    for row,ratio in enumerate((1,.5,.1,0)):
        p=copy.copy(scene.player);p.hp=int(p.hp_max*ratio);p.stamina=p.stamina_max*ratio
        s=world[0].copy();BarrasStatus(scene.hud.fonte_pequena,altura_stamina=h).desenhar(s,p)
        save(s,f'altura_{h}_estado_{row}')
        matrix.blit(s,(col*320+10,row*185+40),(10,10,300,110))
        matrix.blit(font.render(f'{int(ratio*100)}% | recorte 1x',True,(220,224,235)),(col*320+10,row*185+156))
save(matrix,'alturas_6_8_10')
fallback=world[0].copy()
BarrasStatus(scene.hud.fonte_pequena,usar_asset=False).desenhar(fallback,scene.player)
save(fallback,'fallback')

scene=Gamescene(screen,modo_teste_combate=True)
scene.hud.limpar_mensagem()
scene.inimigos=[e for e in scene.inimigos if e is not scene.boss_atual];scene.boss_atual=None
for _ in range(12): scene.atualizar([])
scene.player.rect.midbottom=(scene.inimigos[0].rect.centerx-55,scene.inimigos[0].rect.bottom)
for _ in range(60): scene.camera.atualizar(scene.player.rect)
scene.player._disparar_ataque(False)
for _ in range(12): scene.atualizar([])
capture(scene,'combate')

scene=Gamescene(screen)
scene._carregar_sala('calabouço_5',posiçao_spwan=(4,8))
scene.player.equipar(get_item(1));boss=scene.boss_atual
scene.player.rect.midbottom=(boss.rect.centerx-100,boss.rect.bottom)
for _ in range(60): scene.camera.atualizar(scene.player.rect)
scene.player._disparar_ataque(False)
for _ in range(14): scene.atualizar([])
capture(scene,'chefe')

scene=Gamescene(screen)
held=defaultdict(bool);held[pg.K_d]=True
original_keys=pg.key.get_pressed
pg.key.get_pressed=lambda:held
story=pg.Surface((1280,3*390));story.fill((15,16,22))
positions=[]
try:
    for i in range(6):
        for _ in range(8): scene.atualizar([])
        positions.append(list(scene.player.rect))
        scene.desenhar()
        save(screen,f'movimento_{i}')
        x=i%2*640;y=i//2*390
        story.blit(font.render(f'Movimento D — tick {(i+1)*8}',True,(220,224,235)),(x+8,y+4))
        story.blit(pg.transform.scale(screen,(640,360)),(x,y+30))
finally:
    pg.key.get_pressed=original_keys
assert len({p[0] for p in positions})>1
save(story,'movimento_sequencia')
evidencias['movimento']=positions
(OUT/'hud_f1_evidencias.json').write_text(json.dumps(evidencias,ensure_ascii=False,indent=2),encoding='utf-8')
before=json.loads((OUT/'hud_f1_integridade_inicio.json').read_text(encoding='utf-8'))
changed=[p for p,h in before.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert changed==['ui\\hud\\status.py'],changed
print('OK: capturas reais, diferenças apenas no status; movimento; integridade:',changed)
pg.quit()
