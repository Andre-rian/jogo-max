
import pygame
import sys
from settings import *
from core.game_scene import Gamescene


class Jogo:
    def __init__(self):
        pygame.init()
        self.Criar_janela()
        self.clock = pygame.time.Clock()

        
        self.scene = Gamescene(self.tela)

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
                    if evento.key == pygame.K_ESCAPE:
                        self.scene.alternar_pausa()
                    if evento.key == pygame.K_F11:
                        self._Mudar_telacheia()

            self.tela.fill(Preto)

            self.scene.atualizar(eventos)
            self.scene.desenhar()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Jogo().rodar()