import pygame
import sys
from settings import Screen_widht, Screen_height, FPS, Titulo, Telacheia_normal


class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(Titulo)

        self.tela_cheia = Telacheia_normal
        self.screen = self.Criar_janela()
        self.clock = pygame.time.Clock()
    
    def Criar_janela(self):

        if self.tela_cheia:
            info = pygame.display.Info()
            largura = info.current_w
            altura = info.current_h
            return pygame.display.set_mode(
                (largura, altura),
                pygame.NOFRAME | pygame.SCALED
            )

        else:
            return pygame.display.set_mode(
                (Screen_widht, Screen_height), pygame.SCALED)
        

    def _Mudar_telacheia(self):

        self.tela_cheia = not self.tela_cheia
        self.screen = self.Criar_janela()

    def rodar(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit
                    sys.exit()
                    

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._Mudar_telacheia() 
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            #sem update por agora

            #desenhar
            self.screen.fill((22, 20, 28))
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Jogo().rodar()