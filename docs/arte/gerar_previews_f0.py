"""Estudo offline F.0. Execute na raiz: python docs/arte/gerar_previews_f0.py.
Não importa main/save_manager; não escreve assets nem código do jogo.
Todos os PNGs novos são conservadoramente locais (*restrito*).
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
import json
import random
import hashlib
import pygame as pg
pg.init()
screen = pg.display.set_mode((1280, 720))
from core.game_scene import Gamescene
from entities.objetos.item import get_item
from ui.estilo import Fonte_texto, Fonte_titulo

OUT = Path('docs/arte/previews')
AB = Path('assets/sprites/_entrada/ui/abyssowl_gothic_pixel_ui/split_assets/frames and bars')
LY = Path('assets/sprites/_entrada/itens/lygame_dark_fantasy/UI')
KB = Path('assets/sprites/_entrada/ui/kibyra_medieval_fantasy_ui/UI Icons')
font = Fonte_texto(16)
small = Fonte_texto(14)
title = Fonte_titulo(22, True)

def load(path):
    return pg.image.load(str(path)).convert_alpha()

def save(surf, name):
    pg.image.save(surf, str(OUT / f'hud_f0_{name}_restrito.png'))

def text(surf, value, x, y, f=font, color=(220, 224, 235)):
    surf.blit(f.render(str(value), True, color), (x, y))

def panel(surf, rect, ornate=False):
    pg.draw.rect(surf, (24, 26, 34), rect)
    pg.draw.rect(surf, (81, 94, 120), rect, 1)
    if ornate:
        r = pg.Rect(rect)
        for x, y in [r.topleft, r.topright, r.bottomleft, r.bottomright]:
            pg.draw.polygon(surf, (143, 146, 163), [(x,y-3),(x+3,y),(x,y+3),(x-3,y)])

def cool(src):
    dst = src.copy()
    for y in range(src.get_height()):
        for x in range(src.get_width()):
            r,g,b,a = src.get_at((x,y))
            v = int((r+g+b)/3)
            dst.set_at((x,y), (int(v*.80), int(v*.88), min(255,int(v*1.08)), a))
    return dst

def stretch3(src, width, cap):
    """Preserva pontas; repete uma coluna central sem interpolação."""
    w,h = src.get_size()
    dst = pg.Surface((width,h), pg.SRCALPHA)
    dst.blit(src, (0,0), (0,0,cap,h))
    for x in range(cap,width-cap):
        dst.blit(src, (x,0), (w//2,0,1,h))
    dst.blit(src,(width-cap,0),(w-cap,0,cap,h))
    return dst

ab = cool(load(AB/'54x20px_bar_02.png'))
ly = cool(load(LY/'ProgressTrack.png'))
potion = load('assets/sprites/itens/consumiveis/pocao_vida.png')
eco = load('docs/arte/propostas_recursos/eco_profano_d1.png')

def bar(s, kind, x,y,w,ratio,color):
    ratio = max(0,min(1,ratio))
    if kind == 'A':
        pg.draw.rect(s,(10,12,18),(x,y,w,12))
        pg.draw.rect(s,color,(x+2,y+2,int((w-4)*ratio),8))
        pg.draw.rect(s,(107,118,137),(x,y,w,12),1)
    else:
        src,cap,scale = (ab,12,2) if kind == 'B' else (ly,5,1)
        frame = stretch3(src,w//scale,cap)
        frame = pg.transform.scale_by(frame,scale)
        h=frame.get_height()
        inset = 12 if kind=='B' else 3
        pg.draw.rect(s,(10,12,18),(x+inset,y+h//2-3*scale,w-2*inset,6*scale))
        pg.draw.rect(s,color,(x+inset,y+h//2-3*scale,int((w-2*inset)*ratio),6*scale))
        s.blit(frame,(x,y))
        if kind == 'C':
            # LY015 é opaco: interior vem depois do trilho.
            pg.draw.rect(s,color,(x+3,y+3,int((w-6)*ratio),6))

def mock(world, state, kind):
    s=world.copy()
    widths={'A':252,'B':308,'C':276}
    w=widths[kind]
    h=116 if kind=='B' else 88
    panel(s,(20,20,w,h),kind!='A')
    if kind == 'C':
        pg.draw.rect(s,(112,64,160),(20,20,3,h))
    text(s,'VIDA',32,26,small)
    text(s,f"{state['hp']} / {state['hp_max']}",w-75,26,small)
    bar(s,kind,32,47,w-24,state['hp']/state['hp_max'],(184,51,65))
    sy=89 if kind=='B' else 73
    bar(s,kind,32,sy,w-24,state['stamina']/state['stamina_max'],(68,153,125))
    if state['buff']:
        pg.draw.lines(s,(118,215,155),False,[(w+34,sy),(w+28,sy+7),(w+34,sy+14)],2)
    if state['delay'] and state['stamina'] < state['stamina_max']:
        text(s,'...',w+28,47)
    panel(s,(20,626,118,74),kind!='A')
    s.blit(potion,(32,638))
    text(s,'F',68,636)
    text(s,f"{state['cargas']} / {state['cargas_max']}",68,661)
    panel(s,(1070,650,190,46),kind!='A')
    s.blit(eco,(1080,661))
    text(s,state['ecos'],1116,661)
    if state['boss']:
        panel(s,(408,621,464,79),kind!='A')
        text(s,state['boss']['nome'],438,627)
        bar(s,kind,420,653,440,state['boss']['hp']/state['boss']['max'],(184,51,65))
        if state['boss']['dano']:
            text(s,f"-{state['boss']['dano']}",880,657,color=(255,100,110))
    if state['item']:
        panel(s,(470,528,340,64),kind!='A')
        icon=load('assets/sprites/itens/equipamentos/machado_guerra.png')
        s.blit(pg.transform.scale_by(icon,2),(482,536))
        text(s,state['item'],542,549)
    return s

def capture(scene,name):
    world=[]
    original=scene.hud.desenhar
    def hook(surface,*args):
        world.append(surface.copy())
        original(surface,*args)
    scene.hud.desenhar=hook
    scene.desenhar()
    scene.hud.desenhar=original
    save(screen,'captura_'+name)
    p=scene.player
    state=dict(hp=p.hp,hp_max=p.hp_max,stamina=p.stamina,stamina_max=p.stamina_max,
               cargas=p.pocao.cargas,cargas_max=p.pocao.cargas_max,ecos=p.ecos,
               buff=p.buff_stamina_duracao,delay=p.stamina_delay,arma=p.arma_id,
               item=scene.hud.notificacao_item._notif_item.nome if scene.hud.notificacao_item._notif_timer>0 else None,
               boss=dict(nome=scene.boss_atual.nome,hp=scene.boss_atual.hp,max=scene.boss_atual.hp_max,dano=scene.hud.boss_bar._boss_ultimo_dano) if scene.boss_atual else None,
               sala=scene.sala_atual,zoom=scene.camera.zoom,player_rect=list(p.rect))
    states[name]=state
    worlds[name]=world[0]
    for kind in 'ABC':
        img=mock(world[0],state,kind)
        proposals[kind,name]=img
        save(img,f'proposta_{kind.lower()}_{name}')

states,worlds,proposals={},{},{}
random.seed(0)
scene=Gamescene(screen)
for _ in range(12): scene.atualizar([])
for _ in range(60): scene.camera.atualizar(scene.player.rect)
capture(scene,'exploracao')
scene=Gamescene(screen,modo_teste_combate=True)
scene.hud.limpar_mensagem()
boss=scene.boss_atual
scene.inimigos=[e for e in scene.inimigos if e is not boss]
scene.boss_atual=None
for _ in range(12): scene.atualizar([])
for _ in range(60): scene.camera.atualizar(scene.player.rect)
scene.player.rect.midbottom=(scene.inimigos[0].rect.centerx-55,scene.inimigos[0].rect.bottom)
for _ in range(60): scene.camera.atualizar(scene.player.rect)
scene.player._disparar_ataque(False)
for _ in range(12): scene.atualizar([])
capture(scene,'combate')
scene.player.hp=40
scene.player.stamina=26
scene.player.pocao.cargas=1
scene.player.ecos=137
capture(scene,'vida_baixa')
scene.player.equipar(get_item(3))
scene.player.inventario['itens'][4]=1
get_item(4).usar(scene.player,scene.player.inventario)
scene.hud.mostrar_item_coletado(get_item(3))
capture(scene,'machado_raiz')
scene=Gamescene(screen)
scene._carregar_sala('calabouço_5', posiçao_spwan=(4, 8))
boss=scene.boss_atual
scene.player.equipar(get_item(1))
scene.player.rect.midbottom=(boss.rect.centerx-100,boss.rect.bottom)
for _ in range(60): scene.camera.atualizar(scene.player.rect)
scene.player._disparar_ataque(False)
for _ in range(14): scene.atualizar([])
capture(scene,'boss')
story=pg.Surface((1280,3*390))
story.fill((15,16,22))
for i in range(6):
    for _ in range(8): scene.atualizar([])
    scene.desenhar()
    x=(i%2)*640;y=(i//2)*390
    text(story,f'Quadro {i+1} | intervalo 8 ticks | renderer real',x+10,y+4)
    story.blit(pg.transform.scale(screen,(640,360)),(x,y+30))
save(story,'movimento_atual')

board=pg.Surface((1280*3,780*2))
board.fill((15,16,22))
for col,kind in enumerate('ABC'):
    for row,name in enumerate(['exploracao','boss']):
        x=col*1280;y=row*780
        text(board,{'A':'A — Minimalista','B':'B — Medieval sombria','C':'C — Híbrida'}[kind],x+20,y+8,title)
        text(board,f'{name} | 1280 × 720 | composição offline',x+20,y+35)
        board.blit(proposals[kind,name],(x,y+60))
save(board,'comparativo_abc')

# Estados controlados; fundos sintéticos explicitamente separados das capturas.
matrix=pg.Surface((1200,1160)); matrix.fill((15,16,22))
for col,kind in enumerate('ABC'):
    text(matrix,f'{kind} | cheio / meio / baixo / vazio',col*400+10,8)
    for row,ratio in enumerate([1,.5,.1,0]):
        for light in [False,True]:
            y=44+row*276+int(light)*134
            bg=pg.Surface((1280,720));bg.fill((188,191,198) if light else (9,10,17))
            st=dict(states['vida_baixa']);st.update(hp=int(ratio*st['hp_max']),stamina=ratio*st['stamina_max'])
            tile=mock(bg,st,kind)
            matrix.blit(tile,(col*400,y),(12,16,380,128))
save(matrix,'legibilidade_estados')

# Catálogo medido, originais sem remapeamento + amostra ampliada nearest.
assets=[(f'AB{26+i:03}',AB/n) for i,n in enumerate(['54x16px_bar_01.png','54x20px_bar_02.png','56x16px_bar_02.png','60x24px_bar_01.png','bar_fill_01.png','bar_fill_02.png','bar_fill_03.png'])]
assets += [('LY014',LY/'ProgressBar.png'),('LY015',LY/'ProgressTrack.png')]
assets += [('M095',Path('assets/sprites/itens/consumiveis/pocao_vida.png')),('M067',Path('assets/sprites/itens/consumiveis/raiz_amarga.png')),('A017',Path('assets/sprites/itens/equipamentos/espada_longa.png')),('A045',Path('assets/sprites/itens/equipamentos/machado_guerra.png')),('Eco D1',Path('docs/arte/propostas_recursos/eco_profano_d1.png'))]
assets += [(f'KB{i:03}',KB/f'icon{i}.png') for i in [9,17,20,23]]
sheet=pg.Surface((1100,len(assets)*90));sheet.fill((24,26,34)); metrics=[]
for i,(id,path) in enumerate(assets):
    src=load(path); w,h=src.get_size(); alpha=[src.get_at((x,y)).a for y in range(h) for x in range(w)]
    metrics.append(dict(id=id,path=path.as_posix(),size=[w,h],transparent=alpha.count(0),partial=sum(0<a<255 for a in alpha),opaque=alpha.count(255)))
    text(sheet,f'{id}  {path.name}  {w}×{h}',12,i*90+6)
    sheet.blit(src,(480,i*90+12));sheet.blit(pg.transform.scale_by(src,2),(610,i*90+12))
save(sheet,'curadoria_sprites')
kb=pg.Surface((1024,640));kb.fill((24,26,34))
for i in range(64):
    icon=load(KB/f'icon{i+1}.png');x=(i%8)*128;y=(i//8)*80
    text(kb,f'KB{i+1:03}',x+8,y+3,small);kb.blit(icon,(x+20,y+28))
save(kb,'kibyra_triagem')
(OUT/'hud_f0_evidencias.json').write_text(json.dumps(dict(states=states,assets=metrics),ensure_ascii=False,indent=2),encoding='utf-8')
before=json.loads((OUT/'hud_f0_integridade_inicio.json').read_text(encoding='utf-8'))
changed=[p for p,h in before.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changed, changed
print('OK: capturas, 15 mockups, comparativo, estados, sequência e curadoria; integridade:',len(before),'arquivos intactos')
pg.quit()
