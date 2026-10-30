import pygame
import random
import math
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, KnockbackSpec, ModoMovimento

class Mushroom(InimigoBase):

    USAR_MOVIMENTO_SUBPIXEL = True

    Dano_normal = 12
    Dano_forte = 20
    Dano_esporo = 8

    #knockback curto: 2 px por tick durante 4 ticks = 8 px no total
    KB_FORCA_X = 2
    KB_FORCA_Y = -1
    KB_FRAMES = 4
    RECUPERACAO_HIT_FRAMES = 0
    RETOMADA_FRAMES = 8  # ~133 ms em velocidade de patrulha antes da perseguição plena


    Vel_patrulha = 0.8
    Vel_perseguir = 1.5

    Alcance_detec = 250
    Alcance_ataq_perto = 50
    Alcance_ataq_esporo = 180

    #alcance real do golpe por distância de borda (gap)
    Alcance_conectar = 25
    Alcance_conectar_forte = 30

    Cooldown_ataq = 120
    Cooldown_forte_max = 200
    Cooldown_esporo_max = 400

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=36, altura=60, hp_max=80,
                          patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)

        self.vel.x = self.Vel_patrulha
        self.ecos_drop = 25
        self._timer_retomada = 0

        self.cooldown_forte = 0
        self.cooldown_esporo = 0
        self._cooldowns_extra = ["cooldown_forte", "cooldown_esporo"]

        self.esporos_spawnar = []

        Mush = "assets/sprites/enemies/monsters/mushroom/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Mush + "Idle.png",   150, 150, velocidade=10, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Mush + "Run.png",    150, 150, velocidade=6,  escala=2, n_frames=8),
            self.Atacando:  AnimatedSprite(Mush + "Attack.png", 150, 150, velocidade=5,  escala=2, n_frames=8, loop=False),
            self.Morto:     AnimatedSprite(Mush + "Death.png",  150, 150, velocidade=8,  escala=2, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Mush + "Attack2.png", 150, 150, velocidade=5, escala=2, n_frames=8, loop=False)
        self.anim_attack3 = AnimatedSprite(Mush + "Attack3.png", 150, 150, velocidade=5, escala=2, n_frames=11, loop=False)
        self.anim_hit = AnimatedSprite(Mush + "Take Hit.png", 150, 150, velocidade=5, escala=2, n_frames=4, loop=False)
        self.anim_patrulha = AnimatedSprite(Mush + "Run.png", 150, 150, velocidade=11, escala=2, n_frames=8)
        self.anim_atual = self.animaçoes[self.Patrulha]

        self._configurar_ataques()

    def _configurar_ataques(self):
        dano_normal = DanoSpec(
            dano_base=self.Dano_normal,
            knockback=KnockbackSpec(forca_x=3, forca_y=-1, frames=10),
            duracao_hit=14,
            frames_invenc=15,
        )
        dano_forte = DanoSpec(
            dano_base=self.Dano_forte,
            knockback=KnockbackSpec(forca_x=5, forca_y=-1, frames=12),
            duracao_hit=16,
            frames_invenc=20,
        )
        self._registrar_ataque(
            "normal",
            self.animaçoes[self.Atacando],
            [self._criar_janela("golpe", 6, 7)],
            dano_normal,
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )
        self._registrar_ataque(
            "forte",
            self.anim_attack2,
            [self._criar_janela("golpe_forte", 6, 7)],
            dano_forte,
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )
        self._registrar_ataque(
            "esporo",
            self.anim_attack3,
            [],
            DanoSpec(),
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )

    def _resetar_flags_ataque(self):
        self._esporo_spawnado = False
        self._esporo_direçao = 1
        self._esporo_player = None

    #IA

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_perto:
                self.vel.x = 0
                if self.cooldown_ataq <= 0:
                    self._tentar_atacar(dist, player)
                else:
                    #em cooldown fica em idle, sem pose de ataque sem golpe ativo
                    self.estado = self.Patrulha

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
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.olhando_dir = direçao > 0
        if self._timer_retomada > 0:
            #retomada em dois estágios: patrulha -> perseguição plena
            self.estado = self.Patrulha
            self.vel.x = self.Vel_patrulha * direçao
            self._timer_retomada -= 1
        else:
            self.estado = self.Perseguir
            self.vel.x = self.Vel_perseguir * direçao

    def _patrulhar(self):
        self.estado = self.Patrulha
        self._timer_retomada = 0
        if self.rect.left <= self.patrulha_esq:
            self.olhando_dir = True
        elif self.rect.right >= self.patrulha_dir:
            self.olhando_dir = False

        direcao = 1 if self.olhando_dir else -1
        self.vel.x = self.Vel_patrulha * direcao

    def _animacao_extra_hook(self):
        if self.estado != self.Patrulha:
            return

        if self.vel.x != 0:
            if self.anim_atual is not self.anim_patrulha:
                self.anim_patrulha.resetar()
            self.anim_atual = self.anim_patrulha
        else:
            anim_idle = self.animaçoes[self.Patrulha]
            if self.anim_atual is not anim_idle:
                anim_idle.resetar()
            self.anim_atual = anim_idle

    def _ao_terminar_hit(self):
        self._timer_retomada = self.RETOMADA_FRAMES

    def _ao_terminar_recuperacao(self):
        self._timer_retomada = self.RETOMADA_FRAMES

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
        if not self.iniciar_ataque(tipo, player):
            return
        self.vel.x = 0
        self._timer_retomada = 0
        self._esporo_direçao = direçao
        self._esporo_player = player

    def _ao_tick_ataque(self, player, frame):
        if self._ataque_atual == "esporo" and frame >= 6 and not self._esporo_spawnado:
            self._esporo_spawnado = True
            self._spawnar_esporos(player)

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