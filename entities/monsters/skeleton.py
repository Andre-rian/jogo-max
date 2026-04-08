import pygame
from entities.entity import Entity
from settings import Gravidade, Max_Fall_Speed
from core.animated_sprite import AnimatedSprite

class Skeleton(Entity):

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
        self.timer_knockback = 0

        #começa a patrulha pela a direita
        self.vel.x = self.Vel_patrulha
        self.olhando_dir = True


        #sprites
        Skel = "assets/sprites/enemies/monsters/skeleton/"

        self.animacoes = {
                self.Patrulha:  AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=8, escala=3, n_frames=11),
                self.Perseguir: AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=5, escala=3, n_frames=11),
                self.Atacando:  AnimatedSprite(Skel + "Skeleton Attack.png", 43, 37, velocidade=4, escala=3, n_frames=18),
                self.Morto:     AnimatedSprite(Skel + "Skeleton Dead.png",   33, 32, velocidade=6, escala=3, n_frames=15),
        }
        self.anim_hit = AnimatedSprite(Skel + "Skeleton Hit.png", 30, 32, velocidade=6, escala=3, n_frames=8)
        self.anim_idle = AnimatedSprite(Skel + "Skeleton Idle.png", 24, 32, velocidade=8, escala=3, n_frames=11)
        self._estado_anterior = self.Patrulha
        self.anim_atual = self.animacoes[self.Patrulha]
        self._em_hit = False #flag para animação de hit
        self._timer_hit = 0
        
        
        #update/ atualizar do inimigo

    def atualizar(self, rects_solidos, player):
        #retorna o dano causado ao player no frame, 0 se nao causou


        if not self.vivo:
            # inicializa só uma vez
            if not hasattr(self, "_timer_morte"):
                self._timer_morte = 90
                self.estado = self.Morto
                self.anim_atual = self.animacoes[self.Morto]
                self.anim_atual.resetar()
    

            # só avança a animação se não terminou
            if not self.anim_atual.terminou:
                self.anim_atual.atualizar()
    
            self._timer_morte -= 1
            if self._timer_morte <= 0:
                return 0
            return -1
            
        self._frame += 1
        dano_causado = 0

        #parte do knockback
        if self.timer_knockback > 0:
            self.timer_knockback -= 1
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            self.atualizar_invencibilidade()
            if self.cooldown_ataq > 0:
                self.cooldown_ataq -= 1
            
            #atualiza a animação de hit durante o knockback
            if self._em_hit:
                self._timer_hit -= 1
                if self._timer_hit <= 0:
                    self._em_hit = False
                    #reseta a animação ao sair do hit
                    self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Patrulha])
                    self.anim_atual.atualizar()
                else:
                    self.anim_atual = self.anim_hit
                    #so avança a animação se nao terminou
                    if not self.anim_hit.terminou:
                        self.anim_atual.atualizar()
            
            return 0 #nao rodar a ia do inimigo


        #distancia horizontal/x ate o player
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            #player está no alcance 
            if dist < self.Alcance_ataq:
                #perto o suficante para a ia enteder que pode atacar
                self.estado = self.Atacando
                self.vel.x = 0
                #cancela a animação de hit ao atacar
                self._em_hit = False
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

            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -self.Vel_patrulha
                self.olhando_dir = False

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()

        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1

        if self._em_hit:
            self._timer_hit -= 1
            if self._timer_hit <= 0:
                self._em_hit = False
                self.anim_atual = self.animacoes.get(self.animacoes, self.animacoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

            else:
                self.anim_atual = self.anim_hit
                if not self.anim_hit.terminou:
                    self.anim_atual.atualizar()
                return dano_causado
            
        else:
            
            if self.estado != self._estado_anterior:
                self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

        if self.estado == self.Patrulha and self.vel.x == 0:
            self.anim_atual = self.anim_idle

        self.anim_atual.atualizar()

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

        self.vel.x = direçao_knockback * 4
    
        self.vel.y = -2 #o saltinho pra cima de lei
        self.timer_knockback = 20 #knockback nao estava sendo aplicado 

        # se morreu nesse hit, criar um time para ser removido da lista
        if not self.vivo and not hasattr(self, "_timer_morto"):
            self._timer_morte = 90
            self.estado = self.Morto
            self.anim_atual = self.animacoes[self.Morto]
            self.anim_atual.resetar()


        #ativa a animaçao de hit, só se tiver vivo
        if self.vivo:
            self._em_hit = True
            self._timer_hit = 20 
            self.anim_hit.resetar()
        
        
    #DESENHO
    def desenhar(self, tela, camera):
    # só esconde depois que o timer zerou
        if not self.vivo and (not hasattr(self, '_timer_morte') or self._timer_morte <= 0):
            return
        
        sr = camera.aplicar(self.rect)

        if  self.vivo  and self.invencivel and self._frame % 6 < 3:
            return
        
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        if self.olhando_dir:
            offset_x = sr.centerx - sprite_w // 2 - 10
        
        else:
            offset_x = sr.centerx - sprite_w // 2 + 10
            
        
        offset_y = sr.bottom - sprite_h

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

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