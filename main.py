import pygame
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("jogo.log", mode="w", encoding="utf-8"),

    ],
    force=True
)

log = logging.getLogger("main")
log.debug("Loggin inicializado")    #sanity check
print("Handlers no root:", logging.getLogger().handlers)    #sanity check-extra


from settings import *
from core.menu import MenuInicial
from core.game_scene import Gamescene
from save_manager import Savemaneger



class Jogo:
    def __init__(self):
        pygame.init()
        self.Criar_janela()
        self.clock = pygame.time.Clock()
        self.save_manager = Savemaneger()
        self.estado = "menu" #menu do jogo
        self.slot_atual = None
        self.scene = None

        self.menu = MenuInicial(self.tela, self.save_manager)
        self.menu.callback_iniciar = self._iniciar_jogo
        

    def _atualizar_visibilidade_mouse(self):
        if self.estado == "menu":
            pygame.mouse.set_visible(True)
            return

        if self.estado == "jogo" and self.scene:
            menu_aberto = (
                self.scene.pausado or self.scene.inventario.aberto or self.scene.menu_fogueira.aberto
            )
            pygame.mouse.set_visible(menu_aberto)
        else:
            pygame.mouse.set_visible(True)

    def _iniciar_jogo(self, slot, dados_save):
        self.slot_atual = slot
        self.scene = Gamescene(self.tela)
        self.scene._menu_callback = self._voltar_menu

        def _fazer_save():
            if self.scene:
                self.scene.salvar(self.save_manager, self.slot_atual)
        self.scene._save_callback = _fazer_save


        if dados_save is not None:
            #carrega o save no gameScene
            self.scene.carregar_save(dados_save)

        self.estado = "jogo"


    def _voltar_menu(self):
        
        self.estado = "menu"
        self.scene = None
        self.slot_atual = None
        self.menu.slot_selecionado = 1



    def Criar_janela(self):
        flags = pygame.SCALED
        if Telacheia_normal:
            flags |= pygame.FULLSCREEN
        self.tela = pygame.display.set_mode(
            (Screen_widht, Screen_height), flags
        )
        pygame.display.set_caption(Titulo)

    def _Mudar_telacheia(self):
        pygame.display.toggle_fullscreen()

    def rodar(self):
        while True:
            eventos = pygame.event.get()
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_F11:
                        self._Mudar_telacheia()
                    if evento.key == pygame.K_ESCAPE and self.estado == "jogo" and self.scene:
                        if not (self.scene.inventario.aberto or self.scene.menu_fogueira.aberto):
                            self.scene.alternar_pausa()

            self._atualizar_visibilidade_mouse()


            self.tela.fill(Preto)

            if self.estado == "menu":
                self.menu.atualizar(eventos)
                self.menu.desenhar()

            elif self.estado == "jogo" and self.scene:
                
                self.scene.atualizar(eventos)
                if self.scene:
                    self.scene.desenhar()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Jogo().rodar()