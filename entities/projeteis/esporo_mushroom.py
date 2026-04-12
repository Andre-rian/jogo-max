import pygame
import math
from entities.projeteis.projetil import Projetil
from core.animated_sprite import AnimatedSprite

class EsporoMushroom(Projetil):

    Velocida = 4 #velocidade do esporo
    Raio_curva = 0.08  #quanto ele corrige a direção por frame — baixo = menos preciso
    Timer_vida = 180 #tempo de vida do esporo em frames

    def __init__(self, x, y, vel_x, vel_y, dano=8):
        super().__init__(x, y, vel_x, vel_y, dano=dano, tem_gravidade=False)
        self.rect = pygame.Rect(x, y, 12, 12)  #tamanho do hitbox do esporo
        self.timer_vida = self.Timer_vida
        self._timer_delay = 15 #delay antes de começar a perseguir o alvo


        Mush = "assets/sprites/enemies/monsters/mushroom/"
        self.anim = AnimatedSprite(
            Mush + "Projectile_sprite.png",
              frame_width=50,
              frame_height=50,
              velocidade=4,
              escala=1,
                n_frames=8)
        
    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return

        self.timer_vida -= 1
        if self.timer_vida <= 0:
            self.ativo = False
            return
            
        #delay antes de começar a perseguir o alvo, voa reto por um tempo
        if self._timer_delay > 0:
            self._timer_delay -= 1
        else:
            #ajusta a direção do esporo em direção ao player
            if player.vivo:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    #direçao desejada
                    alvo_x = (dx / dist) * self.Velocida
                    alvo_y = (dy / dist) * self.Velocida
                    # interpolação para suavizar a mudança de direção, fazendo o raio ser mais rapido, porem menos preciso
                    self.vel.x += (alvo_x - self.vel.x) * self.Raio_curva
                    self.vel.y += (alvo_y - self.vel.y) * self.Raio_curva

        #move o esporo
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        #colisao com as paredes
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self.ativo = False
                return
                
        #colisao com o player
        if player.vivo and self.rect.colliderect(player.rect):
            player.receber_dano(self.dano, frames_invenc=15)
            self.ativo = False
            return
        self.anim.atualizar()

    def desenhar(self, tela, camera):
        if not self.ativo:
            return

        sr = camera.aplicar(self.rect)
        sprite_w = self.anim.largura
        sprite_h = self.anim.altura
        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h // 2
        self.anim.desenhar(tela, offset_x, offset_y)    
        
