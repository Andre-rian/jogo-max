import pygame
import math
import random
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye



class FlyingEye(Entity):
    
    Voando = "voando"
    Atacando = "atacando"
    Morto = "morto"

    Dano_mordida = 15
    Dano_dash = 12
    Dano_projetil = 15
    Vel_voo = 2.5                   #velocidade de voo normal
    Vel_ataque = 6                  #velocidade do dash de ataque
    Altura_voo = 40                 #altura que o olho voa em relação ao player
    Alcance_detec = 350             #distancia maxima para detectar o player
    Alcence_perto = 60              #distancia para considerar o player "perto" e usar o ataque de mordida
    Alcance_medio = 200             #distancia para usar o ataque de dash, entre perto e medio usa o dash, depois do medio usa o projétil
    Cooldown_ataque = 150           #cooldown entre ataques em frames
    Cooldown_projetil_max = 350     #cooldown entre ataques de projétil em frames


    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=30, hp_max=60)

        self.patrulha_esq = patrulha_esq
        self.patrulha_dir = patrulha_dir

        self.estado = self.Voando
        self.cooldown_ataq = 0
        self.cooldown_projetil = random.randint(0, self.Cooldown_projetil_max) #delay aleatorio para o primeiro ataque de projétil, para evitar que todos os olhos ataquem juntos
        self._frame = 0
        self.timer_knockback = 0

        self._ataque_atual = None                       #guarda o tipo do ataque atual para a animação
        self._animando_ataque = False                   #indica se está no meio de uma animação de ataque, para travar o movimento durante a animação
        self._fase_ataque = False                       #usado para controlar as fases do ataque, ex: dash tem fase de aproximação e fase de recuo
        self._vel_ataque = pygame.Vector2(0, 0)         #guarda a velocidade do ataque atual, para aplicar o movimento durante a animação
        self.projeteis_spawnar = []                      #lista de projeteis que o olho deve spawnar, para evitar spawnar direto na função de ataque e causar bugs de colisao

        self.olhando_dir = True

        Eye = "assets/sprites/enemies/monsters/flying_eye/"

        self.animaçoes = {
            self.Voando: AnimatedSprite(Eye + "Flight.png", 150, 150, velocidade=6, escala=2, n_frames=8),
            self.Atacando: AnimatedSprite(Eye + "Attack.png", 150, 150, velocidade=5, escala=2, n_frames=8),
            self.Morto: AnimatedSprite(Eye + "Death.png", 150, 150, velocidade=6, escala=2, n_frames=4)}
        
        self.anim_attack2 = AnimatedSprite(Eye + "Attack2.png", 150, 150, velocidade=4, escala=2, n_frames=8)
        self.anim_attac3 = AnimatedSprite(Eye + "Attack3.png", 150, 150, velocidade=4, escala=2, n_frames=6)
        self.anim_hit = AnimatedSprite(Eye + "Take Hit.png", 150, 150, velocidade=6, escala=2, n_frames=4)   

        self._estado_anterior = self.Voando
        self.anim_atual = self.animaçoes[self.Voando]
        self._em_hit = False
        self._timer_hit = 0


    def atualizar(self, rects_solidos, player):
        if not self.vivo:
            if not hasattr(self, "_timer_morte"):
                self._timer_morte = 60
                self.estado = self.Morto
                self.anim_atual = self.animaçoes[self.Morto]
                self.anim_atual.resetar()

            if not self.anim_atual.terminou:
                self.anim_atual.atualizar()

            self._timer_morte -= 1
            if self._timer_morte <= 0:
                return 0
            return -1
        
        
        self._frame += 1

        #knockback
        if self.timer_knockback > 0:
            self.timer_knockback -= 1
            #o eye nao possui gravidade
            self.rect.x += int(self.vel.x)
            self.rect.y += int(self.vel.y)
            self.vel.x *= 0.85
            self.vel.y *= 0.85
            self.atualizar_invencibilidade()
            if self.cooldown_ataq > 0: self.cooldown_ataq -= 1
            if self.cooldown_projetil > 0: self.cooldown_projetil -= 1

            if self._em_hit:
                self._timer_hit -= 1
                if self._timer_hit <= 0:
                    self._em_hit = False
                    self.anim_atual = self.animaçoes[self.Voando]
                    self.anim_atual.resetar()
                    self._estado_anterior = self.Voando
                else:
                    self.anim_atual = self.anim_hit
                    if not self.anim_atual.terminou:
                        self.anim_atual.atualizar()
            return 0
        
        #animando ataque
        if self._animando_ataque:
            self._atualizar_animacao_ataque(player, rects_solidos)
            if self.cooldown_ataq > 0: self.cooldown_ataq -= 1
            if self.cooldown_projetil > 0: self.cooldown_projetil -= 1
            return 0
        
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            #voa em direção ao player, mantendo a altura fixa
            self._voar_para(player, rects_solidos)

            if dist < self.Alcence_perto and self.cooldown_ataq <= 0:
                #perto - mordida ou dash
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                if random.random() < 0.6:
                    self._iniciar_ataque("mordida", player)
                else:
                    self._iniciar_ataque("dash", player)

            elif dist < self.Alcance_medio and self.cooldown_ataq <= 0:
                #medio - dash
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("dash", player)

            elif dist < self.Alcance_detec and self.cooldown_projetil <= 0 and self.cooldown_ataq <= 0:
                #longe - projétil
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("projétil", player)

        else:
            #patrulha voando
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = 1.5
                self.olhando_dir = True

            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -1.5
                self.olhando_dir = False
            self.rect.x += int(self.vel.x)


        self.atualizar_invencibilidade()
        if self.cooldown_ataq > 0: self.cooldown_ataq -= 1
        if self.cooldown_projetil > 0: self.cooldown_projetil -= 1


        if self._em_hit:
            self._timer_hit -= 1
            if self._timer_hit <= 0:
                self._em_hit = False
                self.anim_atual = self.animaçoes[self.Voando]
                self.anim_atual.resetar()
                self._estado_anterior = self.Voando
            else:
                self.anim_atual = self.anim_hit
                if not self.anim_atual.terminou:
                    self.anim_atual.atualizar()
            return 0
        
        else:
            if self.estado != self._estado_anterior:
                self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Voando])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

        self.anim_atual.atualizar()
        return 0
    
    def _voar_para(self, player, rects_solidos):
        #voa em direção ao player, mantendo a altura fixa
        alvo_x = player.rect.centerx
        alvo_y = player.rect.centery - self.Altura_voo

        dx = alvo_x - self.rect.centerx
        dy = alvo_y - self.rect.centery

        #move suavamente em direção ao alvo
        if abs(dx) > 4:
            self.vel.x = math.copysign(self.Vel_voo, dx)
        else:
            self.vel.x = 0
        
        if abs(dy) > 4:
            self.vel.y = math.copysign(self.Vel_voo * 0.7, dy)
        else:
            self.vel.y = 0
        

        self.estado = self.Voando

        self.rect.x += int(self.vel.x)
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.x > 0:
                    self.rect.right = tile.left
                elif self.vel.x < 0:
                    self.rect.left = tile.right
                self.vel.x = 0

        self.rect.y += int(self.vel.y)
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.y < 0:
                    self.rect.top = tile.bottom
                    self.vel.y = 0
                



    def _iniciar_ataque(self, tipo, player):
        self._ataque_atual = tipo
        self._animando_ataque = True
        self._dano_aplicado = False

        direçao = 1 if player.rect.centerx > self.rect.centerx else -1

        if tipo == "mordida":
            self.cooldown_ataq = self.Cooldown_ataque
            #velocidade de descida em direção ao player
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                self._vel_ataque = pygame.Vector2(
                    (dx / dist) * self._vel_ataque,
                    (dy / dist) * self._vel_ataque
                )
            
            self._fase_ataque = "descendo"
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()

        elif tipo == "dash":
            self.cooldown_ataq = self.Cooldown_ataque
            self._vel_ataque = pygame.Vector2(direçao * self.Vel_ataque * 1.5, 0)
            self._fase_ataque = "dashando"
            self._dash_timer = 20
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()
        
        elif tipo == "projetil":
            self.cooldown_ataq = self.Cooldown_ataque
            self.cooldown_projetil = self.Cooldown_projetil_max
            self._fase_ataque = "atirando"
            self._projetil_player = player
            self._projetil_spwanado = False
            self.anim_atual = self.anim_attac3
            self.anim_atual.resetar()


    def _atualizar_animacao_ataque(self, player, rects_solidos):
        self.anim_atual.atualizar()


        if self._ataque_atual == "mordida":
            if self._fase_ataque == "descendo":
                #move se em direçao ao player
                self.rect.x += int(self._vel_ataque.x)
                self.rect.y += int(self._vel_ataque.y)

                #verificar o dano
                if not self._dano_aplicado and self.rect.colliderect(player.rect):
                    self._dano_aplicado = True
                    player.receber_dano(self.Dano_mordida, frames_invenc=25)

                #sobe de voltar apos o ataque
                if self.anim_atual._frame_idx >= 7 or self._dano_aplicado:
                    self._fase_ataque = "subindo"
                    self._vel_ataque = pygame.Vector2(0, -self.Vel_ataque)

            elif self._fase_ataque == "subindo":
                self.rect.y += int(self._vel_ataque.y)
                self._vel_ataque *= 0.9 #vai desacerelando ao subir
        
        
        elif  self._ataque_atual == "dash":
            if self._fase_ataque == "dashando":
                self.rect.x += int(self._vel_ataque.x)
                self._vel_ataque.x *= 0.92 #desacerela o dash
                if not self._dano_aplicado and self.rect.colliderect(player.rect):
                    self._dano_aplicado = True
                    player.receber_dano(self.Dano_dash, frames_invenc=20)
                
                
                
                self._dash_timer -= 1
                if self._dash_timer <= 0:
                    self._vel_ataque.x = 0


        elif self._ataque_atual == "projetil":


            #spwana o projetil no 3 frame
            if self.anim_atual._frame_idx >= 3 and not self._projetil_spwanado:
                self._projetil_spwanado = True
                self._spawnar_projetil(self._projetil_player)


        #terminou a animação
        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            self._fase_ataque = None
            self.estado = self.Voando
            self.anim_atual = self.animaçoes[self.Voando]
            self.anim_atual.resetar()
            self._estado_anterior = self.Voando
    
    def _spawnar_projetil(self, player):

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > 0:
            vel_x = (dx / dist) * 7
            vel_y = (dy / dist) * 7
        
        else:
            vel_x = (1 if self.olhando_dir else -1)
            vel_y = 0

        proj = ProjetilFlyingEye(
            self.rect.centerx,
            self.rect.centery,
            vel_x, vel_y,
            self.Dano_projetil
        )
        self.projeteis_spawnar.append(proj)


    def receber_hit(self, dano, direçao_knockback):
        self.receber_dano(dano)
        self.vel.x = direçao_knockback * 5
        self.vel.y = -3
        self.timer_knockback = 15
        self._animando_ataque = False
        self._ataque_atual = None
        self._fase_ataque = None


        if not self.vivo and not hasattr(self, "_timer_morte"):
            self._timer_morte = 60
            self.estado = self.Morto
            self.anim_atual = self.animaçoes[self.Morto]
            self.anim_atual.resetar()

        
        if self.vivo:
            self._em_hit = True
            self._timer_hit = 15
            self.anim_hit.resetar()


    def aplicar_gravidade(self):
        pass

    def mover_com_colisão(self, rects_solidos):
        pass


    def desenhar(self, tela, camera):
        if not self.vivo and (not hasattr(self, "_timer_morte") or self._timer_morte <= 0):
            return
        
        sr = camera.aplicar(self.rect)
        
        if self.vivo and self.invencivel and self._frame % 6 < 3:
            return
        
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h // 2

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

    def _desenhar_hp(self, tela, sr):
        bar_w = sr.width
        ratio = self.hp / self.hp_max
        pygame.draw.rect(tela, (60, 20, 20),
                         (sr.x, sr.y - 8, bar_w, 4), border_radius=2)
        if ratio > 0:
            pygame.draw.rect(tela, (200, 40, 40),
                             (sr.x, sr.y - 8, int(bar_w * ratio), 4), border_radius=2)        