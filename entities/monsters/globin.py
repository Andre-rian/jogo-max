import pygame
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite

class Globin(InimigoBase):

    Dano_normal = 10
    Dano_dash = 15
    Dano_bomba = 20
    Vel_patrulha = 1.9
    Vel_perseguir = 3.0
    Alcance_detec = 350
    Alcance_ataq_normal = 80
    Alcance_ataq_dash = 55
    Alcance_ataq_bomba = 200
    Cooldown_ataq = 300
    Cooldown_bomba_max = 400

    Duracao_morte = 60

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=44, hp_max=40,
                          patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)

        self.vel.x = self.Vel_patrulha
        self.ecos_drop = 15

        self.cooldown_bomba = 0
        self._cooldowns_extra = ["cooldown_bomba"]  # a base decrementa isso sozinha agora

        self.bombas_spawnar = []  # recolhido no game_scene

        Gob = "assets/sprites/enemies/monsters/goblin/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Gob + "Idle.png",   150, 150, velocidade=10, escala=1, n_frames=4),
            self.Perseguir: AnimatedSprite(Gob + "Run.png",    150, 150, velocidade=6,  escala=1, n_frames=8),
            self.Atacando:  AnimatedSprite(Gob + "Attack.png", 150, 150, velocidade=5,  escala=1, n_frames=8),
            self.Morto:     AnimatedSprite(Gob + "Death.png",  150, 150, velocidade=8,  escala=1, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Gob + "Attack2.png", 150, 150, velocidade=5, escala=1, n_frames=8)
        self.anim_attack3 = AnimatedSprite(Gob + "Attack3.png", 150, 150, velocidade=5, escala=1, n_frames=12)
        self.anim_hit = AnimatedSprite(Gob + "Take Hit.png", 150, 150, velocidade=4, escala=1, n_frames=4)
        self.anim_atual = self.animaçoes[self.Patrulha]

    #  IA 

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_dash:
                self.estado = self.Atacando
                self.vel.x = 0
                if self.cooldown_ataq <= 0:
                    self._tentar_atacar(dist, player)

            elif dist < self.Alcance_ataq_normal:
                if self.cooldown_ataq <= 0:
                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)
                else:
                    self._perseguir(player)

            elif dist < self.Alcance_ataq_bomba:
                if self.cooldown_bomba <= 0:
                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)
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

        if dist < self.Alcance_ataq_dash:
            self._iniciar_ataque("dash", direçao)
        elif dist < self.Alcance_ataq_normal:
            if random.random() < 0.5:
                self._iniciar_ataque("normal")
            else:
                self._iniciar_ataque("dash", direçao)
        else:
            if self.cooldown_bomba <= 0:
                self._iniciar_ataque("bomba", direçao, player)
                self.cooldown_bomba = self.Cooldown_bomba_max
            else:
                self._perseguir(player)

    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        self._ataque_atual = tipo
        self._animando_ataque = True

        if tipo == "normal":
            direçao_atq = 1 if self.olhando_dir else -1
            self.vel.x = direçao_atq * self.Vel_perseguir
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()

        elif tipo == "dash":
            self.vel.x = -direçao * 4
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()

        elif tipo == "bomba":
            self.anim_atual = self.anim_attack3
            self.anim_atual.resetar()
            self._bombar_spawnar = {"direçao": direçao, "frame_spawn": 6, "spawnando": False}

    def _atualizar_animacao_ataque(self, player):
        self.anim_atual.atualizar()

        if self._ataque_atual == "normal":
            if self.anim_atual._frame_idx == 3 and not hasattr(self, "_dano_normal_aplicado"):
                self._dano_normal_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:
                    player.receber_dano(self.Dano_normal, frames_invenc=10)

        elif self._ataque_atual == "dash":
            if self.anim_atual._frame_idx == 6 and not hasattr(self, "_dano_dash_aplicado"):
                self._dano_dash_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:
                    player.receber_dano(self.Dano_dash)
            self.vel.x *= 0.8

        elif self._ataque_atual == "bomba":
            if not self._bombar_spawnar["spawnando"] and self.anim_atual._frame_idx >= self._bombar_spawnar["frame_spawn"]:
                self._bombar_spawnar["spawnando"] = True
                from entities.projeteis.bomba import Bomba
                bomba = Bomba(self.rect.centerx, self.rect.centery,
                               self._bombar_spawnar["direçao"], self.Dano_bomba)
                self.bombas_spawnar.append(bomba)

        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            for attr in ("_dano_normal_aplicado", "_dano_dash_aplicado"):
                if hasattr(self, attr):
                    delattr(self, attr)
            self._resetar_para_estado_atual()  # antes era repetido manualmente

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h + 72
        return offset_x, offset_y