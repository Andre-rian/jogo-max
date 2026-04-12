import pygame
import math
from entities.projeteis.projetil import Projetil
from core.animated_sprite import AnimatedSprite

class ProjetilFlyingEye(Projetil):

    def __init__(self, x, y, vel_x, vel_y, dano=15):
        super().__init__(x, y, vel_x=vel_x, vel_y=vel_y, dano=dano, tem_gravidade=False)
        self.rect = pygame.Rect(x, y, 16, 16)
        self._timer_vida = 300  # 5 segundos

        Eye = "assets/sprites/enemies/monsters/flying_eye/"
        self.anim = AnimatedSprite(
            Eye + "projectile_sprite.png",
            frame_width=48, frame_height=48,
            velocidade=4, escala=1,
            n_frames=8
        )

    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return

        self._timer_vida -= 1
        if self._timer_vida <= 0:
            self.ativo = False
            return

        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self.ativo = False
                return

        if player.vivo and self.rect.colliderect(player.rect):
            player.receber_dano(self.dano, frames_invenc=20)
            self.ativo = False

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