"""Slot F da HUD: apresentação das cargas, independente do estoque do ID 2."""
import pygame

from ui.estilo import Azul_claro, Branco_texto, desenhar_painel
from ui.sprites_itens import obter_sprite_item


class SlotPocao:
    def __init__(self, fonte_pequena):
        self.fonte_pequena = fonte_pequena
        self._flash_da_pocao = 0
        self._valores = None
        self._pocao_anterior = None
        self._texto = None
        self._paineis = []
        for flash in (False, True):
            painel = pygame.Surface((148, 64), pygame.SRCALPHA)
            desenhar_painel(painel, painel.get_rect(), 0,
                            cor_borda=Azul_claro if flash else (107, 118, 137))
            painel.blit(fonte_pequena.render('POÇÃO', True, Branco_texto), (66, 8))
            pygame.draw.rect(painel, (107, 118, 137), (118, 36, 20, 20), 1)
            tecla = fonte_pequena.render('F', True, Branco_texto)
            painel.blit(tecla, tecla.get_rect(center=(128, 46)))
            self._paineis.append(painel)

        # ID 2 resolve apenas a arte M095; nenhum dado do inventário é lido.
        self._icone = obter_sprite_item(2)
        if self._icone is None:
            self._icone = self._frasco_procedural()
        self._icone_vazio = self._icone.copy()
        self._icone_vazio.fill((90, 90, 105, 255), special_flags=pygame.BLEND_RGBA_MULT)

    @staticmethod
    def _frasco_procedural():
        icone = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(icone, (150, 28, 40), (12, 18, 24, 22))
        pygame.draw.rect(icone, (190, 180, 190), (19, 6, 10, 14), border_radius=2)
        pygame.draw.rect(icone, (110, 90, 66), (17, 4, 14, 4), border_radius=2)
        pygame.draw.ellipse(icone, (205, 215, 255), (17, 22, 6, 8))
        return icone

    def flash(self):
        self._flash_da_pocao = 12

    def atualizar(self):
        if self._flash_da_pocao > 0:
            self._flash_da_pocao -= 1

    def desenhar(self, tela, player):
        if not hasattr(player, 'pocao'):
            return
        valores = (player.pocao.cargas, player.pocao.cargas_max)
        # A entrada F usa Pocao.usar diretamente. Observa o uso bem-sucedido
        # sem consumir cargas, reduzir cooldown ou mudar o estado do Player.
        if (player.pocao is self._pocao_anterior
                and valores[0] < self._valores[0]
                and player.pocao._colldown > 0):
            self.flash()
        self._pocao_anterior = player.pocao
        x, y = 20, tela.get_height() - 84
        tela.blit(self._paineis[self._flash_da_pocao > 0], (x, y))
        icone = self._icone if player.pocao.cargas > 0 else self._icone_vazio
        tela.blit(icone, (x + 8, y + 8))
        if valores != self._valores:
            self._valores = valores
            self._texto = self.fonte_pequena.render(
                f'{valores[0]} / {valores[1]}', True, Branco_texto)
        tela.blit(self._texto, (x + 66, y + 35))
