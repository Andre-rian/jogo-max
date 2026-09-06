import pygame
from settings import Screen_height
from ui.estilo import (
    Azul_espectral, Azul_claro, Cinza_azulado,
    escurecer
)

# Barras de vida e stamina + ícone de status do player.

class BarrasStatus:

    def __init__(self, fonte_pequena):
        self.fonte_pequena = fonte_pequena

    def desenhar(self, tela, player):
        margin_x  = 20
        margin_y  = 20
        bar_w     = 200
        hp_h      = 16
        st_h      = 10
        gap       = 6        # espaço entre as barras
        icone_r   = 22       # raio do ícone circular

        #posiçao dos icones
        icone_cx = margin_x + icone_r
        icone_cy = margin_y + icone_r

        #posiçao das barras(começando a direita do icone)
        bar_x = icone_cx + icone_r + 8
        hp_y = margin_y + 4
        st_y = hp_y + hp_h + gap

        #fundo semitransparente
        fundo_w = icone_r * 2 + 8 + bar_w + 4
        fundo_h = icone_r * 2
        fundo = pygame.Surface((fundo_w, fundo_h), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 100))
        tela.blit(fundo, (margin_x, margin_y))

        #icone cicula
        pygame.draw.circle(tela, Cinza_azulado, (icone_cx, icone_cy), icone_r)
        pygame.draw.circle(tela, escurecer(Azul_espectral, 0.5), (icone_cx, icone_cy), icone_r, 2)
        # símbolo de cruz no ícone

        pygame.draw.line(tela, Azul_claro,
                         (icone_cx, icone_cy - 12), (icone_cx, icone_cy + 12), 2)
        pygame.draw.line(tela, Azul_claro,
                         (icone_cx - 8, icone_cy - 4), (icone_cx + 8, icone_cy - 4), 2)

        #barra de hp

        #fundo
        pygame.draw.rect(tela, (28, 10, 12),
                         (bar_x, hp_y, bar_w, hp_h), border_radius=2)

        #preenchimento
        ratio_hp = max(0, player.hp / player.hp_max)
        if ratio_hp > 0.6:
            cor_hp = (150, 34, 44)
        elif ratio_hp > 0.3:
            cor_hp = (168, 66, 30)
        else:
            cor_hp = (200, 30, 40)
        if ratio_hp > 0:
            pygame.draw.rect(tela, cor_hp,
                             (bar_x, hp_y, int(bar_w * ratio_hp), hp_h),
                             border_radius=2)

        #borda
        pygame.draw.rect(tela, (96, 32, 40),
                         (bar_x, hp_y, bar_w, hp_h), 1, border_radius=2)

        #texto hp
        txt = self.fonte_pequena.render(f"{player.hp} /  {player.hp_max}", True, (205, 180, 184))
        tela.blit(txt, (bar_x + bar_w - txt.get_width() - 2, hp_y + 1))

        #barra stamina
        pygame.draw.rect(tela, (10, 26, 22),
                         (bar_x, st_y, bar_w, st_h), border_radius=2)
        ratio_st = max(0, player.stamina / player.stamina_max)
        cor_st = (58, 132, 110) if ratio_st > 0.3 else (36, 88, 72)
        if ratio_st > 0:
            pygame.draw.rect(tela, cor_st,
                             (bar_x, st_y, int(bar_w * ratio_st), st_h),
                             border_radius=2)
            pygame.draw.rect(tela, (42, 92, 76),
                             (bar_x, st_y, bar_w, st_h), 1, border_radius=2)

        #psicar esperando recarregar
        if player.stamina_delay > 0 and player.stamina < player.stamina_max:
            if player._frame_atual % 20 < 10:
                aviso = self.fonte_pequena.render("...", True, (80, 160, 80))
                tela.blit(aviso, (bar_x + 2, st_y - 14))

        # simbolo de buff de stamina
        if player.buff_stamina_duracao > 0:
            bx = bar_x
            by = st_y + st_h + 4
            pygame.draw.circle(tela, (22, 46, 38), (bx + 8, by + 8), 8)
            pygame.draw.circle(tela, (60, 170, 110), (bx + 8, by + 8), 8, 2)

            pygame.draw.line(tela, (70, 190, 120),
                             (bx + 10, by + 2), (bx + 6, by + 8), 2)
            pygame.draw.line(tela, (70, 190, 120),
                             (bx + 6, by + 8), (bx + 10, by + 14), 2)