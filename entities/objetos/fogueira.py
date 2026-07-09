import pygame
from settings import Tile_size

class Fogueira:

    def __init__(self, x, y, col, linha, callback_descanso=None):

        self.col = col
        self.linha = linha 

        self.rect = pygame.Rect(x, y, Tile_size, Tile_size)
        

        self._callback_descanso = callback_descanso

        self._callback_abrir_menu = None


        self.ativa = False
        self._frame = 0  #contador geral para a animação


        self._timer_descanso = 0


    def atualizar(self, player, teclas, hud, sala_atual, fogueiras_ativas):

        self._frame += 1

        if self._timer_descanso > 0:
            self._timer_descanso -= 1
            hud.mostra_mensagem("Descansando...")
            return
        


        dist = abs(player.rect.centerx - self.rect.centerx)

        if dist < 80:
            if not self.ativa:
                hud.mostra_mensagem("pressione E para descansar")


                if teclas[pygame.K_e] and player.cooldown_interaçao <= 0:
                    print(f"E pressionado na fogueira id={id(self)}, callback={self._callback_abrir_menu}")
                    self.ativa = True
                    fogueiras_ativas.add((self.col, self.linha)) #registra a fogueira como ativa
                    player.defenir_checkpoint(sala_atual, x=self.rect.centerx, y=self.rect.centery)
                    player.cooldown_interaçao = 60
                    self._timer_descanso = 120
                    if self._callback_abrir_menu:
                        self._callback_abrir_menu()

            else:
                #fogueira ja ativida, pode descansar se sair da sala\
                
                if teclas[pygame.K_e] and player.cooldown_interaçao <= 0:
                    print(f"E pressionado na fogueira id={id(self)}, callback={self._callback_abrir_menu}")
                    player.cooldown_interaçao = 60
                    if self._callback_abrir_menu:
                        self._callback_abrir_menu()

    def _ativar(self, player, hud):
        self.ativa = True

        #passa a posição da fogueira para o player, para que ele respwane na fogueira

        player.defenir_checkpoint(
            player.checkpoint_sala,
            x=self.rect.x,
            y=self.rect.y
        )
        hud.mostra_mensagem("Ponto de descanso ativo")


    def desenhar(self, tela, camera):
        sr = camera.aplicar(self.rect)


        # base — pedras
        pygame.draw.rect(tela, (80, 80, 80),
                         (sr.x + 4, sr.bottom - 10, sr.width - 8, 8), border_radius=2)

        if not self.ativa:
            # apagada — só brasa
            pygame.draw.ellipse(tela, (80, 30, 10),
                                (sr.centerx - 6, sr.bottom - 16, 12, 8))
        else:
            # pulso — chama oscila usando seno
            import math
            pulso = int(math.sin(self._frame * 0.15) * 3)

            # chama externa
            pygame.draw.polygon(tela, (200, 80, 10), [
                (sr.centerx,          sr.top + 6 + pulso),
                (sr.centerx - 8,      sr.bottom - 12),
                (sr.centerx + 8,      sr.bottom - 12),
            ])
            # chama interna
            pygame.draw.polygon(tela, (240, 160, 20), [
                (sr.centerx,          sr.top + 12 + pulso),
                (sr.centerx - 5,      sr.bottom - 12),
                (sr.centerx + 5,      sr.bottom - 12),
            ])
            # brilho central
            pygame.draw.ellipse(tela, (255, 220, 80),
                                (sr.centerx - 3, sr.centery + pulso, 6, 6))

        # debug
        pygame.draw.rect(tela, (200, 100, 30), sr, 1)









