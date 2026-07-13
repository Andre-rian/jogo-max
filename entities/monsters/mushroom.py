import pygame
import random
import math
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite

class Mushroom(InimigoBase):

    Dano_normal = 12
    Dano_forte = 20
    Dano_esporo = 8
    Vel_patrulha = 1.0
    Vel_perseguir = 2.0
    Alcance_detec = 250
    Alcance_ataq_perto = 50
    Alcance_ataq_esporo = 180
    Cooldown_ataq = 120
    Cooldown_forte_max = 200
    Cooldown_esporo_max = 400

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=36, altura=60, hp_max=80,
                          patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)

        self.vel.x = self.Vel_patrulha
        self.ecos_drop = 25

        self.cooldown_forte = 0
        self.cooldown_esporo = 0
        self._cooldowns_extra = ["cooldown_forte", "cooldown_esporo"]

        self.esporos_spawnar = []

        Mush = "assets/sprites/enemies/monsters/mushroom/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Mush + "Idle.png",   150, 150, velocidade=10, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Mush + "Run.png",    150, 150, velocidade=6,  escala=2, n_frames=8),
            self.Atacando:  AnimatedSprite(Mush + "Attack.png", 150, 150, velocidade=5,  escala=2, n_frames=8),
            self.Morto:     AnimatedSprite(Mush + "Death.png",  150, 150, velocidade=8,  escala=2, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Mush + "Attack2.png", 150, 150, velocidade=5, escala=2, n_frames=8)
        self.anim_attack3 = AnimatedSprite(Mush + "Attack3.png", 150, 150, velocidade=5, escala=2, n_frames=11)
        self.anim_hit = AnimatedSprite(Mush + "Take Hit.png", 150, 150, velocidade=4, escala=2, n_frames=4)
        self.anim_atual = self.animaçoes[self.Patrulha]

    #knockback

    def receber_hit(self, dano, direçao_knockback):
        super().receber_hit(dano, direçao_knockback, forca_x=3, forca_y=-2, frames_kb=20)

    #IA

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_perto:
                self.estado = self.Atacando
                self.vel.x = 0
                if self.cooldown_ataq <= 0:
                    self._tentar_atacar(dist, player)
                # se o cooldown ainda não zerou, só fica parado "encarando"

            elif dist < self.Alcance_ataq_esporo:
                if self.cooldown_esporo <= 0 and self.cooldown_ataq <= 0:
                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)
                else:
                    self._perseguir(player)
            else:
                self._perseguir(player)
        else:
            self._patrulhar()
        return 0

    def _perseguir(self, player):
        self.estado = self.Perseguir
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.vel.x = self.Vel_perseguir * direçao
        self.olhando_dir = direçao > 0

    def _patrulhar(self):
        self.estado = self.Patrulha
        if self.rect.left <= self.patrulha_esq:
            self.vel.x = self.Vel_patrulha
            self.olhando_dir = True
        elif self.rect.right >= self.patrulha_dir:
            self.vel.x = -self.Vel_patrulha
            self.olhando_dir = False

    #Ataques

    def _tentar_atacar(self, dist, player):
        if self.cooldown_ataq > 0:
            return

        self.cooldown_ataq = self.Cooldown_ataq
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.olhando_dir = direçao > 0

        if dist < self.Alcance_ataq_perto:
            if self.cooldown_forte <= 0 and random.random() < 0.4:
                self._iniciar_ataque("forte")
                self.cooldown_forte = self.Cooldown_forte_max
            else:
                self._iniciar_ataque("normal")
        else:
            if self.cooldown_esporo <= 0:
                self._iniciar_ataque("esporo", direçao, player)
                self.cooldown_esporo = self.Cooldown_esporo_max

    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        self._ataque_atual = tipo
        self._animando_ataque = True
        self._esporo_spawnado = False

        if tipo == "normal":
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()
        elif tipo == "forte":
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()
        elif tipo == "esporo":
            self.anim_atual = self.anim_attack3
            self.anim_atual.resetar()
            self._esporo_direçao = direçao
            self._esporo_player = player

    def _atualizar_animacao_ataque(self, player):
        self.anim_atual.atualizar()

        if self._ataque_atual == "normal":
            if self.anim_atual._frame_idx == 5 and not hasattr(self, "_dano_normal_ap"):
                self._dano_normal_ap = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_perto + 10:
                    player.receber_dano(self.Dano_normal, frames_invenc=15)

        elif self._ataque_atual == "forte":
            if self.anim_atual._frame_idx == 6 and not hasattr(self, "_dano_forte_ap"):
                self._dano_forte_ap = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_perto + 15:
                    player.receber_dano(self.Dano_forte, frames_invenc=20)

        elif self._ataque_atual == "esporo":
            if self.anim_atual._frame_idx >= 6 and not self._esporo_spawnado:
                self._esporo_spawnado = True
                self._spawnar_esporos(player)

        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            for attr in ("_dano_normal_ap", "_dano_forte_ap"):
                if hasattr(self, attr):
                    delattr(self, attr)
            self._resetar_para_estado_atual()

    def _spawnar_esporos(self, player):
        from entities.projeteis.esporo_mushroom import EsporoMushroom

        angulos = [-30, 0, 30]
        direçao = self._esporo_direçao

        for angulo in angulos:
            rad = math.radians(angulo)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                vel_x = (dx / dist) * 4
                vel_y = (dy / dist) * 4
            else:
                vel_x = direçao * 4
                vel_y = -2

            vel_x_rot = vel_x * math.cos(rad) - vel_y * math.sin(rad)
            vel_y_rot = vel_x * math.sin(rad) + vel_y * math.cos(rad)

            esporo = EsporoMushroom(
                self.rect.centerx, self.rect.centery,
                vel_x_rot, vel_y_rot, self.Dano_esporo
            )
            self.esporos_spawnar.append(esporo)

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2 + (-10 if self.olhando_dir else 10)
        offset_y = sr.bottom - sprite_h + 100
        return offset_x, offset_y