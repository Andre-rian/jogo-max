import pygame
from settings import Screen_height
from ui.estilo import (
    Azul_espectral, Azul_claro, Cinza_texto,
    escurecer
)

# Slot de poção no canto inferior esquerdo.

class SlotPocao:

    def __init__(self, fonte_pequena):
        self.fonte_pequena = fonte_pequena
        self._flash_da_pocao = 0

    def flash(self):
        self._flash_da_pocao = 12

    def atualizar(self):
        if self._flash_da_pocao > 0:
            self._flash_da_pocao -= 1

    def desenhar(self, tela, player):
        if not hasattr(player, "pocao"):
            return

        slot_x  = 20
        slot_y  = Screen_height - 90
        slot_w  = 52
        slot_h  = 52

        #flash ao usar
        cor_borda = Azul_claro if self._flash_da_pocao > 0 else escurecer(Azul_espectral, 0.5)
        alfa_fundo = 190 if self._flash_da_pocao > 0 else 130

        #fundo do slot
        fundo = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
        fundo.fill((22, 22, 28, alfa_fundo))
        tela.blit(fundo, (slot_x, slot_y))
        pygame.draw.rect(tela, cor_borda,
                         (slot_x, slot_y, slot_w, slot_h), 2, border_radius=4)

        #icone da poçao desenhando ventorialmente enquanto nao coloco uma sprite
        cx = slot_x + slot_w // 2
        cy = slot_y + slot_h // 2

        if player.pocao.cargas > 0:
            cor_liquido = (150, 28, 40)
            cor_frasco = (190, 180, 190)
        else:
            cor_liquido = (44, 10, 14) #vazio - frasco escuro
            cor_frasco = (88, 72, 82)

        #corpo do frasco
        pygame.draw.ellipse(tela, cor_liquido,
                            (cx - 12, cy - 6, 24, 22))

        #gargalo
        pygame.draw.rect(tela, cor_frasco,
                         (cx - 5, cy - 18, 10, 14), border_radius=2)

        #tampa
        pygame.draw.rect(tela, (110, 90, 66),
                         (cx - 7, cy - 20, 14, 4), border_radius=2)

        # brilho no frasco
        pygame.draw.ellipse(tela, (205, 215, 255),
                            (cx - 7, cy - 2, 6, 8))

        #tecla f
        tecla = self.fonte_pequena.render("F", True, Cinza_texto)
        tela.blit(tecla, (slot_x + 2, slot_y + slot_h - 16))

        # cargas bolinhas abaixo do slot de poçoes
        for i in range(player.pocao.cargas_max):
            cor = (150, 28, 40) if i < player.pocao.cargas else (44, 12, 16)
            pygame.draw.circle(tela, cor,
                               (slot_x + 8 + i * 16, slot_y + slot_h + 10), 5)
            pygame.draw.circle(tela, (110, 30, 42),
                               (slot_x + 8 + i * 16, slot_y + slot_h + 10), 5, 1)