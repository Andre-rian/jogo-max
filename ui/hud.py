# ui/hud.py
import pygame
from settings import Screen_widht, Screen_height, Dourado, Branco
from settings import Stamina_recarga, Stamina_delay as Stamina_delay_max

class Hud:

    def __init__(self):
        pygame.font.init()
        self.fonte_pequena  = pygame.font.SysFont("Arial", 14)
        self.fonte_media    = pygame.font.SysFont("Arial", 18, bold=True)
        self.fonte_mensagem = pygame.font.SysFont("Arial", 26, bold=True)

        self._mensagem       = ""
        self._timer_mensagem = 0

    def mostra_mensagem(self, texto, duracao=180):
        self._mensagem       = texto
        self._timer_mensagem = duracao

    def atualizar(self):
        if self._timer_mensagem > 0:
            self._timer_mensagem -= 1

    # ── draw principal — chama todos os métodos 
    def desenhar(self, tela, player):
        self._desenhar_barra_hp(tela, player)
        self._desenhar_barra_stamina(tela, player)
        self._desenhar_inventario(tela, player)
        self._desenhar_mensagem(tela)
        self._desenhar_debug(tela, player)

    # ── barra de HP 
    def _desenhar_barra_hp(self, tela, player):
        fundo = pygame.Surface((230, 44), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 140))
        tela.blit(fundo, (12, 12))

        label = self.fonte_pequena.render("HP", True, (200, 80, 80))
        tela.blit(label, (18, 20))

        bar_x, bar_y = 44, 22
        bar_w, bar_h = 180, 14

        pygame.draw.rect(tela, (50, 15, 15),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=3)

        ratio  = max(0, player.hp / player.hp_max)
        fill_w = int(bar_w * ratio)

        if ratio > 0.6:
            cor_hp = (60, 180, 60)
        elif ratio > 0.3:
            cor_hp = (200, 180, 30)
        else:
            cor_hp = (200, 40, 40)

        if fill_w > 0:
            pygame.draw.rect(tela, cor_hp,
                             (bar_x, bar_y, fill_w, bar_h),
                             border_radius=3)

        # borda das barras
        pygame.draw.rect(tela, (120, 80, 80),
                         (bar_x, bar_y, bar_w, bar_h),
                         1, border_radius=3)

        texto_hp = self.fonte_pequena.render(
            f"{player.hp} / {player.hp_max}", True, Branco)
        tela.blit(texto_hp, (bar_x + bar_w + 8, bar_y))

    # ── barra de stamina 
    def _desenhar_barra_stamina(self, tela, player):
        fundo = pygame.Surface((230, 34), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 140))
        tela.blit(fundo, (12, 54))

        label = self.fonte_pequena.render("ST", True, (80, 160, 200))
        tela.blit(label, (18, 62))

        bar_x, bar_y = 44, 62
        bar_w, bar_h = 180, 10

        pygame.draw.rect(tela, (15, 30, 50),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=3)

        ratio  = max(0, player.stamina / player.stamina_max)
        fill_w = int(bar_w * ratio)

        cor_st = (60, 160, 220) if ratio > 0.3 else (40, 80, 160)

        if fill_w > 0:
            pygame.draw.rect(tela, cor_st,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        pygame.draw.rect(tela, (40, 100, 140),
                         (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        texto_st = self.fonte_pequena.render(
            f"{int(player.stamina)} / {player.stamina_max}", True, Branco)
        tela.blit(texto_st, (bar_x + bar_w + 8, bar_y))

        # pisca "..." quando está esperando recarregar
        if player.stamina_delay > 0 and player.stamina < player.stamina_max:
            if player._frame_atual % 20 < 10:
                aviso = self.fonte_pequena.render("...", True, (100, 140, 180))
                tela.blit(aviso, (bar_x, bar_y - 14))

    # ── inventário (provisorio)
    def _desenhar_inventario(self, tela, player):
        x, y = 18, 96

        cor = Dourado if player.tem_espada else (60, 60, 60)

        pygame.draw.line(tela, cor, (x + 10, y + 2),  (x + 10, y + 22), 2)
        pygame.draw.line(tela, cor, (x + 5,  y + 14), (x + 15, y + 14), 2)
        pygame.draw.circle(tela, cor, (x + 10, y + 24), 3)   

        if player.tem_espada:
            txt = self.fonte_pequena.render("Espada", True, Dourado)
            tela.blit(txt, (x + 20, y + 10))

    # ── mensagem central 
    def _desenhar_mensagem(self, tela):
        if self._timer_mensagem <= 0:
            return

        alpha = min(255, self._timer_mensagem * 5)
        msg   = self.fonte_mensagem.render(self._mensagem, True, Dourado)
        msg.set_alpha(alpha)

        x = Screen_widht  // 2 - msg.get_width()  // 2
        y = Screen_height // 2 - 100
        tela.blit(msg, (x, y))

    # ── debug so pra me ajudar durante a criaçao do jogo
    def _desenhar_debug(self, tela, player):
        linhas = [
            f'Estado : {player.estado}',
            f'Pos    : ({player.rect.x}, {player.rect.y})',
            f'Vel    : ({player.vel.x:.1f}, {player.vel.y:.1f})',
            f'Dash CD: {player.cooldown_dash}',
            f'No chao: {player.no_chao}',
            f'Stamina: {int(player.stamina)}',
        ]
        for i, linha in enumerate(linhas):
            txt = self.fonte_pequena.render(linha, True, (140, 140, 140))
            tela.blit(txt, (Screen_widht - 240,
                            Screen_height - 128 + i * 18))