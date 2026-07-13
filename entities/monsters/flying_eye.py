import pygame
import math
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye


class FlyingEye(InimigoBase):

    Voando = "voando"          
    ESTADO_PADRAO = "Voando"
    TEM_GRAVIDADE = False

    Dano_mordida = 15
    Dano_dash = 12
    Dano_projetil = 15
    Vel_voo = 2.5
    Vel_ataque = 6
    Altura_voo = 40
    Alcance_detec = 350
    Alcence_perto = 60
    Alcance_medio = 200
    Cooldown_ataque = 150
    Cooldown_projetil_max = 350

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=30, hp_max=60,
                          patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)

        self.cooldown_projetil = random.randint(0, self.Cooldown_projetil_max)
        self._cooldowns_extra = ["cooldown_projetil"]

        self._fase_ataque = False
        self._vel_ataque = pygame.Vector2(0, 0)
        self.projeteis_spawnar = []

        Eye = "assets/sprites/enemies/monsters/flying_eye/"
        self.animaçoes = {
            self.Voando:    AnimatedSprite(Eye + "Flight.png", 150, 150, velocidade=6, escala=2, n_frames=8),
            self.Atacando:  AnimatedSprite(Eye + "Attack.png", 150, 150, velocidade=5, escala=2, n_frames=8),
            self.Morto:     AnimatedSprite(Eye + "Death.png",  150, 150, velocidade=6, escala=2, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Eye + "Attack2.png", 150, 150, velocidade=4, escala=2, n_frames=8)
        self.anim_attac3 = AnimatedSprite(Eye + "Attack3.png", 150, 150, velocidade=4, escala=2, n_frames=6)
        self.anim_hit = AnimatedSprite(Eye + "Take Hit.png", 150, 150, velocidade=6, escala=2, n_frames=4)
        self.anim_atual = self.animaçoes[self.Voando]

        self.ecos_drop = 15

   
    def mover_com_colisão(self, rects_solidos):
        pass

    #IA

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            self._voar_para(player, rects_solidos)

            if dist < self.Alcence_perto and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("mordida" if random.random() < 0.6 else "dash", player)

            elif dist < self.Alcance_medio and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("dash", player)

            elif dist < self.Alcance_detec and self.cooldown_projetil <= 0 and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("projetil", player)
        else:
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = 1.5
                self.olhando_dir = True
            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -1.5
                self.olhando_dir = False
            self.rect.x += int(self.vel.x)
            self.estado = self.Voando

        return 0

    def _voar_para(self, player, rects_solidos):
        alvo_x = player.rect.centerx
        alvo_y = player.rect.centery - self.Altura_voo

        dx = alvo_x - self.rect.centerx
        dy = alvo_y - self.rect.centery

        self.vel.x = math.copysign(self.Vel_voo, dx) if abs(dx) > 4 else 0
        self.vel.y = math.copysign(self.Vel_voo * 0.7, dy) if abs(dy) > 4 else 0

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

    #Ataques 

    def _iniciar_ataque(self, tipo, player):
        self._ataque_atual = tipo
        self._animando_ataque = True
        self._dano_aplicado = False

        direçao = 1 if player.rect.centerx > self.rect.centerx else -1

        if tipo == "mordida":
            self.cooldown_ataq = self.Cooldown_ataque
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                # FIX: era self._vel_ataque (sempre 0,0) — agora usa a constante Vel_ataque
                self._vel_ataque = pygame.Vector2(
                    (dx / dist) * self.Vel_ataque,
                    (dy / dist) * self.Vel_ataque
                )
            else:
                self._vel_ataque = pygame.Vector2(0, self.Vel_ataque)

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

    def _atualizar_animacao_ataque(self, player):
        self.anim_atual.atualizar()

        if self._ataque_atual == "mordida":
            if self._fase_ataque == "descendo":
                self.rect.x += int(self._vel_ataque.x)
                self.rect.y += int(self._vel_ataque.y)

                if not self._dano_aplicado and self.colide_mask_com_mask(player):
                    self._dano_aplicado = True
                    player.receber_dano(self.Dano_mordida, frames_invenc=25)

                if self.anim_atual._frame_idx >= 7 or self._dano_aplicado:
                    self._fase_ataque = "subindo"
                    self._vel_ataque = pygame.Vector2(0, -self.Vel_ataque)

            elif self._fase_ataque == "subindo":
                self.rect.y += int(self._vel_ataque.y)
                self._vel_ataque *= 0.9

        elif self._ataque_atual == "dash":
            if self._fase_ataque == "dashando":
                self.rect.x += int(self._vel_ataque.x)
                self._vel_ataque.x *= 0.92
                if not self._dano_aplicado and self.colide_mask_com_mask(player):
                    self._dano_aplicado = True
                    player.receber_dano(self.Dano_dash, frames_invenc=20)

                self._dash_timer -= 1
                if self._dash_timer <= 0:
                    self._vel_ataque.x = 0

        elif self._ataque_atual == "projetil":
            if self.anim_atual._frame_idx >= 3 and not self._projetil_spwanado:
                self._projetil_spwanado = True
                self._spawnar_projetil(self._projetil_player)

        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            self._fase_ataque = None
            self.estado = self.Voando
            self._resetar_para_estado_atual()

    def _spawnar_projetil(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > 0:
            vel_x = (dx / dist) * 7
            vel_y = (dy / dist) * 7
        else:
            vel_x = 1 if self.olhando_dir else -1
            vel_y = 0

        proj = ProjetilFlyingEye(self.rect.centerx, self.rect.centery, vel_x, vel_y, self.Dano_projetil)
        self.projeteis_spawnar.append(proj)

    def receber_hit(self, dano, direçao_knockback):
        super().receber_hit(dano, direçao_knockback, forca_x=5, forca_y=-3, frames_kb=15)
        self._fase_ataque = None

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        return sr.centerx - sprite_w // 2, sr.centery - sprite_h // 2