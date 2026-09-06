import pygame
import sys
import atexit
import logging

from logging_config import configurar_logging

configurar_logging()

log = logging.getLogger("main")
log.debug("Logging inicializado")


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
        atexit.register(self.save_manager.fechar)
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

    def _salvar_emergencia(self):
        #tenta preservar o progresso antes de fechar por causa de erro
        if self.scene and self.slot_atual is not None:
            try:
                self.scene.salvar(self.save_manager, self.slot_atual)
                log.info("Save de emergência gravado antes do término anormal")
            except Exception as e:
                log.warning(f"Não foi possível salvar antes do término (slot {self.slot_atual}): {e}")

    def _sair(self):
        self.save_manager.fechar()
        pygame.quit()
        sys.exit()

    def rodar(self):
        while True:
            try:
                eventos = pygame.event.get()
            except Exception:
                log.exception("Falha ao ler eventos do pygame")
                self._sair()

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self._sair()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_F11:
                        self._Mudar_telacheia()
                    if evento.key == pygame.K_ESCAPE and self.estado == "jogo" and self.scene:
                        if not (self.scene.inventario.aberto or self.scene.menu_fogueira.aberto):
                            self.scene.alternar_pausa()

            try:
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

            except Exception:
                log.exception("Exceção não tratada no loop principal")
                self._salvar_emergencia()
                self._sair()


if __name__ == "__main__":
    Jogo().rodar()