import os, sys, pygame
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.makedirs("docs/arte/previews", exist_ok=True)
pygame.init(); tela = pygame.display.set_mode((1280,720))
from core.preferencias import escala_texto, ESCALAS_TEXTO, normalizar
from ui.estilo import definir_escala_texto
from core.menu import MenuInicial
from core.inventario import Inventario
from core.menu_fogueira import MenuFogueira
from save_manager import Savemaneger
from entities.player import Player
from ui.hud.hud import Hud
from entities.objetos.item import get_item
import core.menu as cm, core.inventario as ci, core.menu_fogueira as cf
class AudioNoop:
    def play_sfx(self,*a,**k): return True
    def play_music(self,*a,**k): return True
    def stop_music(self,*a,**k): return True
    def aplicar_preferencias_audio(self,*a,**k): return None
    def stop_world_sfx(self,*a,**k): return None
noop=AudioNoop(); cm.audio=noop; ci.audio=noop; cf.audio=noop
for nome, escala in ESCALAS_TEXTO.items():
    definir_escala_texto(escala)
    save=Savemaneger(); menu=MenuInicial(tela, save); menu.estado="menu_principal"; menu.opcao_selecionada=0
    tela.fill((0,0,0)); menu.desenhar(); pygame.image.save(tela, f"docs/arte/previews/fase_h_menu_{nome}_local.png")
    menu.estado="opcoes_acessibilidade"; menu.opcao_selecionada=0
    tela.fill((0,0,0)); menu.desenhar(); pygame.image.save(tela, f"docs/arte/previews/fase_h_acessibilidade_{nome}_local.png")
    player=Player(100,300)
    try:
        player.inventario["equipamentos"].append(1); player.inventario["itens"][2]=3
    except Exception: pass
    inv=Inventario(tela); inv.aberto=True; inv.slot_selecionado=0
    tela.fill((20,20,24)); inv.desenhar(player); pygame.image.save(tela, f"docs/arte/previews/fase_h_inventario_{nome}_local.png")
    fog=MenuFogueira(tela, player, lambda: None, lambda: None); fog.abrir(); fog.estado=MenuFogueira.MENU_PRINCIPAL
    tela.fill((20,20,24)); fog.desenhar(); pygame.image.save(tela, f"docs/arte/previews/fase_h_ecofoco_{nome}_local.png")
    fog.estado=MenuFogueira.LEVEL_UP; tela.fill((20,20,24)); fog.desenhar(); pygame.image.save(tela, f"docs/arte/previews/fase_h_ecofoco_levelup_{nome}_local.png")
    hud=Hud(); player.hp=35; player.hp_max=100; player.stamina=20; player.stamina_max=100; player.ecos=12345678901234567890
    try: player.pocao.cargas=2; player.pocao.cargas_max=3
    except Exception: pass
    tela.fill((30,30,30)); hud.desenhar(tela, player, boss_atual=None)
    boss=type("B",(),{"nome":"Carrasco Esqueletico","hp":150,"hp_max":300})()
    hud.boss_bar.desenhar(tela,boss)
    hud.mensagens.mostrar("Mensagem de teste longa para verificar quebra e escala sem cortes")
    hud.notificacao_item.mostrar(get_item(2), 1)
    hud.mensagens.desenhar(tela); hud.notificacao_item.desenhar(tela)
    pygame.image.save(tela, f"docs/arte/previews/fase_h_hud_{nome}_local.png")
pygame.quit(); print("captures ok")
