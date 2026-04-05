import pygame
from entities.entity import Entity
from settings import Gravidade, Max_Fall_Speed

class Enemy(Entity):

    #estados do inimigo

    Patrulha = "patrulha"
    Perseguir = "perseguir"
    Atacando = "atacando"
    Morto = "morto"


    #atributos da ia/inimigo
    Dano = 15
    Vel_patrulha = 1.5
    Vel_perseguir = 3.0
    Alcance_detec = 250
    Alcance_ataq = 48
    Cooldown_ataq = 90

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=48, hp_max=60)

        #limites da patrulha em pixels
        self.patrulha_esq = patrulha_esq
        self.patrulha_dir = patrulha_dir

        self.estado = self.Patrulha
        self.cooldown_ataq = 0
        self._frame = 0

        #começa a patrulha pela a direita
        self.vel.x = self.Vel_patrulha
        self.olhando_dir = True

        #update/ atualizar do inimigo

    def atualizar(self, rects_solidos, player):
        #retorna o dano causado ao player no frame, 0 se nao causou

        if not self.vivo:
            return 0
            
        self._frame += 1
        dano_causado = 0

        #distancia horizontal/x ate o player
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            #player está no alcance 
            if dist < self.Alcance_ataq:
                #perto o suficante para a ia enteder que pode atacar
                self.estado = self.Atacando
                self.vel.x = 0
                dano_causado = self._tentar_atacar(player)
            else:
                #persegue o player
                self.estado = self.Perseguir
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1 
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0
        else:
            #se o player nao esta no seu campo de visao, inimigo continua patrulhando
            self.estado = self.Patrulha
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = self.Vel_patrulha
                self.olhando_dir = True

            elif self.rect.right <= self.patrulha_dir:
                self.vel.x = -self.Vel_patrulha
                self.olhando_dir = False

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()

        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1
        return dano_causado
        
    #ATAQUEE
    def _tentar_atacar(self, player):
        #causa dano se o cooldown zerou
        if self.cooldown_ataq > 0:
            return 0
        self.cooldown_ataq = self.Cooldown_ataq
        player.receber_dano(self.Dano)
        return self.Dano
        
    def receber_hit(self, dano, direçao_knockback):
        #a funçao é chamada quando o player acerta o inimigo

        self.receber_dano(dano)
        # knoback o inimigo sofre a repulsao quando atacado
        self.vel.x = direçao_knockback * 7
        self.vel.y = -4 #o saltinho pra cima de lei

    #DESENHO
    def desenhar(self, tela, camera):
        if not self.vivo:
            return
            
        sr = camera.aplicar(self.rect)

        #piscar durante invecibilidade
        if self.invencivel and self._frame % 6 < 3:
            return
            
        #corpo vermelho escuro (provisorio enquanto nao tem sprites)
        cor = (120, 35, 35)
        pygame.draw.rect(tela, cor, sr, border_radius=4)

        #capaceta
        pygame.draw.rect(tela, (80, 25, 25),
                        (sr.x + 2, sr.y, sr.width - 4, 18), border_radius=5)
            
        #olho - branco se esta em patrulha - vermelho se estiver atacando
        cor_olho = (220, 60, 60) if self.estado in (
            self.Perseguir, self.Atacando) else (220, 220, 220)
        olho_x = sr.centerx + (5 if self.olhando_dir else -5)
        pygame.draw.circle(tela, cor_olho, (olho_x, sr.y +10), 4)

        def _desenhar_hp(self, tela, sr):
            bar_w = sr.width
            ratio = self.hp / self.hp_max

            #fundo
            pygame.draw.rect(tela, (60, 20, 20),
                        (sr.x, sr.y - 8, bar_w, 4), border_radius=2)
                
            #preenchimento
            if ratio > 0:
                pygame.draw.rect(tela, (200, 40, 40),
                            (sr.x, sr.y - 8, int(bar_w * ratio), 4),
                                border_radius=2)