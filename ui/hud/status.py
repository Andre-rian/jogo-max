"""Painel híbrido experimental F.1; somente apresentação de dados do Player."""
import pygame
from ui.hud.trilho_status import obter_trilho

ALTURA_STAMINA = 8


class BarrasStatus:
    def __init__(self, fonte_pequena, *, altura_stamina=ALTURA_STAMINA, usar_asset=True):
        self.fonte_pequena = fonte_pequena
        self._painel = pygame.Surface((276, 88))
        self._painel.fill((24, 26, 34))
        pygame.draw.rect(self._painel, (81, 94, 120), (0, 0, 276, 88), 1)
        pygame.draw.rect(self._painel, (112, 64, 160), (0, 0, 3, 88))
        for x, y in ((272, 3), (272, 84)):
            pygame.draw.polygon(self._painel, (143, 146, 163),
                                [(x, y-3), (x+3, y), (x, y+3), (x-3, y)])
        self._painel.blit(fonte_pequena.render('VIDA', True, (220, 224, 235)), (12, 6))
        self._hp_trilho = obter_trilho(252, 6, usar_asset)
        self._st_trilho = obter_trilho(252, altura_stamina, usar_asset)
        self._hp_interior = pygame.Rect(35, 50, 246, 6)
        self._st_interior = pygame.Rect(35, 76, 246, altura_stamina)
        self._aviso = fonte_pequena.render('...', True, (80, 160, 80))
        self._valores_hp = None
        self._texto_hp = None

    @staticmethod
    def _proporcao(valor, maximo):
        # Proteção exclusivamente visual; nunca corrige atributos do jogador.
        return max(0, min(1, valor / maximo)) if maximo > 0 else 0

    def desenhar(self, tela, player):
        tela.blit(self._painel, (20, 20))
        tela.blit(self._hp_trilho, (32, 47))
        tela.blit(self._st_trilho, (32, 73))
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
        tela.set_clip(clip.clip(pygame.Rect(90, 24, 194, 22)))
        tela.blit(self._texto_hp, (284-self._texto_hp.get_width(), 26))
        tela.set_clip(clip)

        # Mesmas condições e fase de piscar; nenhum timer avança aqui.
        if player.stamina_delay > 0 and player.stamina < player.stamina_max:
            if player._frame_atual % 20 < 10:
                tela.blit(self._aviso, (262, 89))

        if player.buff_stamina_duracao > 0:
            bx, by = 32, 88
            pygame.draw.circle(tela, (22, 46, 38), (bx+8, by+8), 8)
            pygame.draw.circle(tela, (60, 170, 110), (bx+8, by+8), 8, 2)
            pygame.draw.line(tela, (70, 190, 120), (bx+10, by+2), (bx+6, by+8), 2)
            pygame.draw.line(tela, (70, 190, 120), (bx+6, by+8), (bx+10, by+14), 2)
