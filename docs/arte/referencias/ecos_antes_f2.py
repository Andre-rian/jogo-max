import pygame
from settings import Screen_widht, Screen_height
from ui.estilo import Branco_texto, desenhar_eco_profano

# Contador de ecos no canto inferior direito.

class IndicadorEcos:

    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._frame_hud = 0

    def desenhar(self, tela, player):
        self._frame_hud += 1

        #posiçao no canto inferior direito
        x = Screen_widht - 220
        y = Screen_height - 60

        #simbolo do eco
        cx = x + 22
        cy = y + 18

        desenhar_eco_profano(tela, cx, cy, 15, self._frame_hud)

        #numero dos ecos
        txt = self.fonte_media.render(str(player.ecos), True, Branco_texto)
        tela.blit(txt, (cx + 24, cy - txt.get_height() // 2))