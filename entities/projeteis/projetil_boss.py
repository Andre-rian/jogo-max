import pygame
from entities.projeteis.projetil import Projetil
from core.animated_sprite import AnimatedSprite

class ProjetilBoss(Projetil):

    Vel_projetil = 6
    Timer_vida   = 300   # some depois de 5 segundos se nao acertar nada

    def __init__(self, x, y, direcao, dano=20):
        super().__init__(x, y,
                         vel_x=direcao * self.Vel_projetil,
                         vel_y=0,
                         dano=dano,
                         tem_gravidade=True,
                         gravidade=0.05)

        self.rect     = pygame.Rect(x, y, 60, 40)
        self.direcao  = direcao
        self._timer_vida = self.Timer_vida
        self._dano_aplicado = False

        Boss = "assets/sprites/enemies/monsters/esqueletos/"
        self.anim = AnimatedSprite(Boss + "Sword_sprite.png",
                                   92, 102,
                                   velocidade=6, escala=2, n_frames=8)

    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return

        # fisica
        self.vel.y = min(self.vel.y + self.gravidade, 15)
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        # timer de vida
        self._timer_vida -= 1
        if self._timer_vida <= 0:
            self.ativo = False
            return

        # colisao com o chao
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self.ativo = False
                return

        # colisao com o player
        if player.vivo and not self._dano_aplicado and self.rect.colliderect(player.rect):
            self._dano_aplicado = True
            player.receber_dano(self.dano)
            self.ativo = False

        self.anim.atualizar()

    def desenhar(self, tela, camera):
        if not self.ativo:
            return

        sr = camera.aplicar(self.rect)

        # espelha conforme a direção
        espelhado = self.direcao < 0
        sprite_w  = self.anim.largura
        sprite_h  = self.anim.altura
        offset_x  = sr.centerx - sprite_w // 2
        offset_y  = sr.centery - sprite_h // 2

        self.anim.desenhar(tela, offset_x, offset_y, espelhado)

        # debug
        pygame.draw.rect(tela, (255, 200, 0), sr, 2)