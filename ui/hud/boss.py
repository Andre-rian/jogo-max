import pygame
from settings import Screen_widht, Screen_height
from ui.estilo import Roxo_espectral

# Barra de vida do boss no rodapé da tela.

class BarraBoss:

    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._boss_hp_display  = 0
        self._boss_hp_real     = 0
        self._boss_hp_anterior = 0
        self._boss_ultimo_dano = 0
        self._boss_timer_dano  = 0

    def atualizar(self):
        if self._boss_hp_display > self._boss_hp_real:
            self._boss_hp_display = max(self._boss_hp_real, self._boss_hp_display - 2)

        if self._boss_timer_dano > 0:
            self._boss_timer_dano -= 1
            if self._boss_timer_dano == 0:
                self._boss_ultimo_dano = 0

    def desenhar(self, tela, boss):
        self._boss_hp_real = boss.hp

        if self._boss_hp_display == 0:
            self._boss_hp_display = boss.hp_max
            self._boss_hp_anterior = boss.hp_max

        bar_w, bar_h = 400, 18
        bar_x = Screen_widht // 2 - bar_w // 2
        bar_y = Screen_height - 60
        fundo = pygame.Surface((bar_w + 60, 54), pygame.SRCALPHA)

        fundo.fill((0, 0, 0, 160))
        tela.blit(fundo, (bar_x - 30, bar_y - 26))

        nome = self.fonte_media.render(boss.nome, True, Roxo_espectral)
        tela.blit(nome, (Screen_widht // 2 - nome.get_width() // 2, bar_y - 22))

        ratio_display = max(0, self._boss_hp_display / boss.hp_max)
        pygame.draw.rect(tela, (45, 12, 16),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        cor_boss = (170, 40, 50)
        if ratio_display > 0:
            pygame.draw.rect(tela, cor_boss,
                             (bar_x, bar_y, int(bar_w * ratio_display), bar_h), border_radius=4)

        ratio_real = max(0, boss.hp / boss.hp_max)
        if ratio_real > 0:
            pygame.draw.rect(tela, cor_boss,
                             (bar_x, bar_y, int(bar_w * ratio_real), bar_h), border_radius=4)

        pygame.draw.rect(tela, (110, 40, 46),
                         (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        if self._boss_hp_real < self._boss_hp_anterior:
            self._boss_ultimo_dano += self._boss_hp_anterior - self._boss_hp_real
            self._boss_timer_dano = 120

        self._boss_hp_anterior = self._boss_hp_real

        if self._boss_timer_dano > 0:
            txt_dano = self.fonte_media.render(f"-{self._boss_ultimo_dano}", True, (255, 80, 80))
            tela.blit(txt_dano, (bar_x + bar_w + 8, bar_y))