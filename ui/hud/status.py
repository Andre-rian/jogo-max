"""Painel híbrido experimental F.1; somente apresentação de dados do Player."""
import pygame
from ui.hud.trilho_status import obter_trilho

ALTURA_STAMINA = 8


class BarrasStatus:
    def __init__(self, fonte_pequena, *, altura_stamina=ALTURA_STAMINA, usar_asset=True):
        self.fonte_pequena = fonte_pequena
        self.altura_stamina = altura_stamina
        self.usar_asset = usar_asset
        self._construir()
        self._valores_hp = None
        self._texto_hp = None

    def _construir(self):
        fh = self.fonte_pequena.get_height()
        self._w = max(276, 220 + fh * 4)
        self._h = max(88, fh * 4 + 24)
        self._painel = pygame.Surface((self._w, self._h))
        self._painel.fill((24, 26, 34))
        pygame.draw.rect(self._painel, (81, 94, 120), (0, 0, self._w, self._h), 1)
        pygame.draw.rect(self._painel, (112, 64, 160), (0, 0, 3, self._h))
        for x, y in ((self._w - 4, 3), (self._w - 4, self._h - 4)):
            pygame.draw.polygon(self._painel, (143, 146, 163),
                                [(x, y-3), (x+3, y), (x, y+3), (x-3, y)])
        self._painel.blit(self.fonte_pequena.render('VIDA', True, (220, 224, 235)), (12, 6))
        tw = self._w - 24
        self._hp_trilho = obter_trilho(tw, 6, self.usar_asset)
        self._st_trilho = obter_trilho(tw, self.altura_stamina, self.usar_asset)
        # coordenadas absolutas na tela (painel em 20,20)
        self._hp_y = 20 + 6 + fh + 8
        self._st_y = self._hp_y + 6 + max(10, fh)
        self._hp_interior = pygame.Rect(35, self._hp_y + 3, tw - 6, 6)
        self._st_interior = pygame.Rect(35, self._st_y + 3, tw - 6, self.altura_stamina)
        self._aviso = self.fonte_pequena.render('...', True, (80, 160, 80))

    @staticmethod
    def _proporcao(valor, maximo):
        # Proteção exclusivamente visual; nunca corrige atributos do jogador.
        return max(0, min(1, valor / maximo)) if maximo > 0 else 0

    def desenhar(self, tela, player):
        tela.blit(self._painel, (20, 20))
        tela.blit(self._hp_trilho, (32, self._hp_y))
        tela.blit(self._st_trilho, (32, self._st_y))
        hp = self._proporcao(player.hp, player.hp_max)
        stamina = self._proporcao(player.stamina, player.stamina_max)
        cor_hp = (184, 51, 65) if hp > .3 else (200, 30, 40)
        for interior, proporcao, cor in (
            (self._hp_interior, hp, cor_hp),
            (self._st_interior, stamina, (68, 153, 125)),
        ):
            largura = int(interior.width * proporcao)
            if largura:
                pygame.draw.rect(tela, cor, (interior.x, interior.y, largura, interior.height))

        valores = (player.hp, player.hp_max)
        if valores != self._valores_hp:
            self._valores_hp = valores
            self._texto_hp = self.fonte_pequena.render(
                f'{player.hp} / {player.hp_max}', True, (220, 224, 235))
        clip = tela.get_clip()
        area_txt = pygame.Rect(90, 24, self._w - 82, self.fonte_pequena.get_height() + 4)
        tela.set_clip(clip.clip(area_txt))
        tela.blit(self._texto_hp, (20 + self._w - 12 - self._texto_hp.get_width(), 26))
        tela.set_clip(clip)

        if player.stamina_delay > 0 and player.stamina < player.stamina_max:
            if player._frame_atual % 20 < 10:
                tela.blit(self._aviso, (20 + self._w - 34, self._st_y + self.altura_stamina + 8))

        if player.buff_stamina_duracao > 0:
            bx, by = 32, self._st_y + self.altura_stamina + 8
            pygame.draw.circle(tela, (22, 46, 38), (bx+8, by+8), 8)
            pygame.draw.circle(tela, (60, 170, 110), (bx+8, by+8), 8, 2)
            pygame.draw.line(tela, (70, 190, 120), (bx+10, by+2), (bx+6, by+8), 2)
            pygame.draw.line(tela, (70, 190, 120), (bx+6, by+8), (bx+10, by+14), 2)
