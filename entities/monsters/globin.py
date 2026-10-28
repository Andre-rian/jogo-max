import pygame
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, KnockbackSpec

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

    #alcance REAL do golpe, medido por distância de borda (gap) — o Alcance_ataq_* acima
    #só decide qual golpe a IA usa; o dano só conecta se as hitboxes estiverem perto
    Alcance_conectar = 35
    Alcance_conectar_dash = 15
    Cooldown_ataq = 300
    Cooldown_bomba_max = 400

    Duracao_morte = 60
    HITSTUN_FRAMES = 16  # 4 frames de hit a 4 ticks = ~267 ms (reação completa)
    RECUPERACAO_HIT_FRAMES = 8  # ~133 ms parado antes de voltar a perseguir

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
            self.Atacando:  AnimatedSprite(Gob + "Attack.png", 150, 150, velocidade=5,  escala=1, n_frames=8, loop=False),
            self.Morto:     AnimatedSprite(Gob + "Death.png",  150, 150, velocidade=8,  escala=1, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Gob + "Attack2.png", 150, 150, velocidade=5, escala=1, n_frames=8, loop=False)
        self.anim_attack3 = AnimatedSprite(Gob + "Attack3.png", 150, 150, velocidade=5, escala=1, n_frames=12, loop=False)
        self.anim_hit = AnimatedSprite(Gob + "Take Hit.png", 150, 150, velocidade=4, escala=1, n_frames=4)
        self.anim_atual = self.animaçoes[self.Patrulha]

        self._configurar_ataques()

    def _configurar_ataques(self):
        dano_normal = DanoSpec(
            dano_base=self.Dano_normal,
            knockback=KnockbackSpec(forca_x=3, forca_y=-1, frames=10),
            duracao_hit=12,
            frames_invenc=10,
        )
        dano_dash = DanoSpec(
            dano_base=self.Dano_dash,
            knockback=KnockbackSpec(forca_x=5, forca_y=-1, frames=12),
            duracao_hit=14,
            frames_invenc=15,
        )
        self._registrar_ataque(
            "normal",
            self.animaçoes[self.Atacando],
            [self._criar_janela("corte", 6, 7)],
            dano_normal,
        )
        self._registrar_ataque(
            "dash",
            self.anim_attack2,
            [self._criar_janela("investida", 6, 7)],
            dano_dash,
        )
        self._registrar_ataque("bomba", self.anim_attack3, [], DanoSpec())

    def _resetar_flags_ataque(self):
        self._bomba_spawnada = False
        self._bomba_direcao = 1

    #  IA 

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_dash:
                self.vel.x = 0
                if self.cooldown_ataq <= 0:
                    self._tentar_atacar(dist, player)
                else:
                    #em cooldown fica em idle, sem pose de ataque sem golpe ativo
                    self.estado = self.Patrulha

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
        if not self.iniciar_ataque(tipo, player):
            return

        self._bomba_direcao = direçao
        if tipo == "normal":
            self.vel.x = (1 if self.olhando_dir else -1) * self.Vel_perseguir
        elif tipo == "dash":
            self.vel.x = direçao * 4
        elif tipo == "bomba":
            self.vel.x = 0

    def _ao_tick_ataque(self, player, frame):
        if self._ataque_atual == "dash":
            self.vel.x *= 0.8
        elif self._ataque_atual == "bomba":
            if frame >= 6 and not self._bomba_spawnada:
                self._bomba_spawnada = True
                from entities.projeteis.bomba import Bomba
                bomba = Bomba(
                    self.rect.centerx,
                    self.rect.centery,
                    self._bomba_direcao,
                    self.Dano_bomba,
                )
                self.bombas_spawnar.append(bomba)

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h + 72
        return offset_x, offset_y