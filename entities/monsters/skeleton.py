import pygame
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite

class Skeleton(InimigoBase):

    Dano = 15
    Vel_patrulha = 1.5
    Vel_perseguir = 3.0
    Alcance_detec = 250
    Alcance_ataq = 48
    Cooldown_ataq = 90

    Duracao_morte = 90

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=48, hp_max=60, patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)


        self.vel.x = self.Vel_patrulha
        self.escos_drop = 20

        Skel = "assets/sprites/enemies/monsters/skeleton/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=8, escala=3, n_frames=11),
            self.Perseguir: AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=5, escala=3, n_frames=11),
            self.Atacando:  AnimatedSprite(Skel + "Skeleton Attack.png", 43, 37, velocidade=4, escala=3, n_frames=18),
            self.Morto:     AnimatedSprite(Skel + "Skeleton Dead.png",   33, 32, velocidade=6, escala=3, n_frames=15),
        }
        self.anim_hit = AnimatedSprite(Skel + "Skeleton Hit.png", 30, 32, velocidade=6, escala=3, n_frames=8)
        self.anim_idle = AnimatedSprite(Skel + "Skeleton Idle.png", 24, 32, velocidade=8, escala=3, n_frames=11)
        self.anim_atual = self.animaçoes[self.Patrulha]

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq:
                self.estado = self.Atacando
                self.vel.x = 0
                self._em_hit = False
                return self._tentar_atacar(player)
            else:
                self.estado = self.Perseguir
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0

        else:

            self.estado = self.Patrulha
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = self.Vel_patrulha
                self.olhando_dir = True
            
            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -self.Vel_patrulha
                self.olhando_dir = False

        return 0
    
    def _tentar_atacar(self, player):
        if self.cooldown_ataq > 0:
            return 0
        self.cooldown_ataq = self.Cooldown_ataq
        player.receber_dano(self.Dano)
        return self.Dano
    
    def _animacao_extra_hook(self):
        if self.estado == self.Patrulha and self.vel.x == 0:
            self.anim_atual = self.anim_idle

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2 + (-10 if self.olhando_dir else 10)
        offset_y = sr.bottom - sprite_h
        return offset_x, offset_y