import pygame
import math
from settings import Screen_height, Screen_widht, Dourado, Branco

class Hud:

    def __init__(self):
        pygame.font.init()
        self.fonte_pequena  = pygame.font.SysFont("Georgia", 13)
        self.fonte_media    = pygame.font.SysFont("Georgia", 18, bold=True)
        self.fonte_mensagem = pygame.font.SysFont("Georgia", 28, bold=True)
        self.fonte_cargas   = pygame.font.SysFont("Georgia", 16, bold=True)

        self._mensagem = ""
        self._timer_mensagem = 0

        #boss
        self._boss_hp_display  = 0
        self._boss_hp_real     = 0
        self._boss_hp_anterior = 0
        self._boss_ultimo_dano = 0
        self._boss_timer_dano  = 0

        #poçao - um flashzinho ao usae
        self._flash_da_pocao = 0

    #publica
    def mostra_mensagem(self, texto, duracao=180):
        self._mensagem = texto
        self._timer_mensagem = duracao

    def flash_pocao(self):
        self._flash_da_pocao = 12

    def atualizar(self):
        if self._timer_mensagem > 0:
            self._timer_mensagem -= 1
        
        if self._flash_da_pocao > 0:
            self._flash_da_pocao -= 1

        
        if self._boss_hp_display > self._boss_hp_real:
            self._boss_hp_display = max(self._boss_hp_real, self._boss_hp_display - 2)

        if self._boss_timer_dano > 0:
            self._boss_timer_dano -= 1
            if self._boss_timer_dano == 0:
                self._boss_ultimo_dano = 0

    #draw principal
    def desenhar(self, tela, player, boss_atual=None):
        self._desenhar_status(tela, player)
        self._desenhar_slot_pocao(tela, player)
        self._desenhar_mensagem(tela)
        self._desenhar_debug(tela, player)
        if boss_atual:
            self._desenhar_barra_boss(tela, boss_atual)


    #status
    def _desenhar_status(self, tela, player):
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
        pygame.draw.circle(tela, (40, 35, 30), (icone_cx, icone_cy), icone_r)
        pygame.draw.circle(tela, (100, 80, 60), (icone_cx, icone_cy), icone_r, 2)
        # símbolo de cruz no ícone

        pygame.draw.line(tela, (180, 140, 100),
                         (icone_cx, icone_cy - 12), (icone_cx, icone_cy + 12), 2)
        pygame.draw.line(tela, (180, 140, 100),
                         (icone_cx - 8, icone_cy - 4), (icone_cx + 8, icone_cy - 4), 2)      

        #barra de hp
        
        #fundo
        pygame.draw.rect(tela, (30, 10, 10),
                         (bar_x, hp_y, bar_w, hp_h), border_radius=2)
        
        #preenchimento
        ratio_hp = max(0, player.hp / player.hp_max)
        if ratio_hp > 0.6:
            cor_hp = (180, 30, 30)
        elif ratio_hp > 0.3:
            cor_hp = (180, 80, 20)
        else:
            cor_hp = (200, 20, 20)
        if ratio_hp > 0:
            pygame.draw.rect(tela, cor_hp,
                             (bar_x, hp_y, int(bar_w * ratio_hp), hp_h),
                             border_radius=2)
            

        #borda
        pygame.draw.rect(tela, (80, 40, 40),
                         (bar_x, hp_y, bar_w, hp_h), 1, border_radius=2)
        
        #texto hp
        txt = self.fonte_pequena.render(f"{player.hp} /  {player.hp_max}", True, (200, 180, 180))
        tela.blit(txt, (bar_x + bar_w - txt.get_width() - 2, hp_y + 1))

        #barra stamina
        pygame.draw.rect(tela, (10, 25, 15),
                         (bar_x, st_y, bar_w, st_h), border_radius=2)
        ratio_st = max(0, player.stamina / player.stamina_max)
        cor_st = (50, 140, 60) if ratio_st > 0.3 else (30, 80, 40)
        if ratio_st > 0:
            pygame.draw.rect(tela, cor_st,
                             (bar_x, st_y, int(bar_w *  ratio_st), st_h),
                             border_radius=2)
            pygame.draw.rect(tela, (40, 80, 50),
                             (bar_x, st_y, bar_w, st_h), 1, border_radius=2)
            
        #psicar esperando recarregar
        if player.stamina_delay > 0 and player.stamina < player.stamina_max:
            if player._frame_atual % 20 < 10:
                aviso = self.fonte_pequena.render("...", True, (80, 160, 80))
                tela.blit(aviso, (bar_x + 2, st_y - 14))

        # simbolo de buff de stamina
        if player.buff_stamina_duracao > 0:
            # fundo do icone
            bx = bar_x
            by = st_y + st_h + 4
            pygame.draw.circle(tela, (20, 50, 30), (bx + 8, by + 8), 8)
            pygame.draw.circle(tela, (50, 180, 80), (bx + 8, by + 8), 8, 2)
            
            # simbolo de raio dentro do circulo
            pygame.draw.line(tela, (50, 200, 80),
                             (bx + 10, by + 2), (bx + 6, by + 8), 2)
            pygame.draw.line(tela, (50, 200, 80),
                             (bx + 6, by + 8), (bx + 10, by + 14), 2)
        

    def _desenhar_slot_pocao(self, tela, player):
        if not hasattr(player, "pocao"):
            return
        
        slot_x  = 20
        slot_y  = Screen_height - 90
        slot_w  = 52
        slot_h  = 52


        #flash ao usar
        cor_borda = (255, 220, 80) if self._flash_da_pocao > 0 else (100, 80, 50)
        alfa_fundo = 180 if self._flash_da_pocao > 0 else 120

        #fundo do slot
        fundo = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
        fundo.fill((20, 15, 10, alfa_fundo))
        tela.blit(fundo, (slot_x, slot_y))
        pygame.draw.rect(tela, cor_borda,
                         (slot_x, slot_y, slot_w, slot_h), 2, border_radius=4)
        
        #icone da poçao desenhando ventorialmente enquanto nao coloco uma sprite
        cx = slot_x + slot_w // 2
        cy = slot_y + slot_h // 2

        if player.pocao.cargas > 0:
            cor_liquido = (220, 160, 30)
            cor_frasco = (180, 140, 60)

        else:
            cor_liquido = (60, 50, 30) #vazio - frasco escuro
            cor_frasco = (80, 70, 50)


        #corpo do frasco
        pygame.draw.ellipse(tela, cor_liquido,
                            (cx - 12, cy - 6, 24, 22))
        
        #gargalo
        pygame.draw.rect(tela, cor_frasco,
                         (cx - 5, cy - 18, 10, 14), border_radius=2)
        
        #tampa
        pygame.draw.rect(tela, (120, 100, 60),
                         (cx - 7, cy - 20, 14, 4), border_radius=2)
        
        # brilho no frasco
        pygame.draw.ellipse(tela, (255, 230, 120),
                            (cx - 7, cy - 2, 6, 8))
        
        #tecla f
        tecla = self.fonte_pequena.render("F", True, (150, 130, 80))
        tela.blit(tecla, (slot_x + 2, slot_y + slot_h - 16))


        #cargas bolinhas abaixo do slot de poçoes

        for i in range(player.pocao.cargas_max):
            cor = (220, 180, 60) if i < player.pocao.cargas else (50, 40, 25)
            pygame.draw.circle(tela, cor,
                               (slot_x + 8 + i * 16, slot_y + slot_h + 10), 5)
            pygame.draw.circle(tela, (100, 80, 40),
                               (slot_x + 8 + i * 16, slot_y + slot_h + 10), 5, 1)


    #mensagem central
    def _desenhar_mensagem(self, tela):
        if self._timer_mensagem <= 0:
            return
        alpha = min(255, self._timer_mensagem * 5)
        msg = self.fonte_mensagem.render(self._mensagem, True, Dourado)
        msg.set_alpha(alpha)
        x = Screen_widht // 2 - msg.get_width() // 2
        y = Screen_height // 2 - 100
        tela.blit(msg, (x, y))


    #barra de hp do boss
    def _desenhar_barra_boss(self, tela, boss):
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
        
        
        
        nome = self.fonte_media.render(boss.nome, True, Dourado)
        tela.blit(nome, (Screen_widht // 2 - nome.get_width() // 2, bar_y - 22))
        ratio_display = max(0, self._boss_hp_display / boss.hp_max)
        pygame.draw.rect(tela, (60, 15, 15),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        
        if ratio_display > 0:
            pygame.draw.rect(tela, (200, 40, 40),
                             (bar_x, bar_y, int(bar_w * ratio_display), bar_h), border_radius=4)
            

        ratio_real = max(0, boss.hp / boss.hp_max)
        if ratio_real > 0:
            pygame.draw.rect(tela, (200, 40, 40),
                             (bar_x, bar_y, int(bar_w * ratio_real), bar_h), border_radius=4)
        pygame.draw.rect(tela, (120, 60, 60),
                         (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        
        
        if self._boss_hp_real < self._boss_hp_anterior:
            self._boss_ultimo_dano += self._boss_hp_anterior - self._boss_hp_real
            self._boss_timer_dano = 120
        
        
        self._boss_hp_anterior = self._boss_hp_real
        
        if self._boss_timer_dano > 0:
            txt_dano = self.fonte_media.render(f"-{self._boss_ultimo_dano}", True, (255, 80, 80))
            tela.blit(txt_dano, (bar_x + bar_w + 8, bar_y))
    
    #debug para ajuda na criaçao do jogo
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
        