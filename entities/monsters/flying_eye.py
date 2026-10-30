import pygame
import math
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, FaseAtaque, HitboxSpec, KnockbackSpec
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
    Alcance_medio = 120

    #knockback
    KB_FORCA_X = 6
    KB_FORCA_Y = -3
    KB_FRAMES = 14
    HITSTUN_FRAMES = 12  # 4 frames de hit a 3 ticks = ~200 ms (reação completa)
    
    Cooldown_ataque = 150
    Cooldown_projetil_max = 350

    #hitbox de contato (infla o rect lógico 30x30 pro corpo-no-ar); antes usava a
    #máscara do sprite 300x300, que fazia a mordida/dash acertar de muito longe
    Folga_contato_x = 20
    Folga_contato_y = 10

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=30, hp_max=60,
                          patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)

        self.cooldown_projetil = random.randint(0, self.Cooldown_projetil_max)
        self._cooldowns_extra = ["cooldown_projetil"]

        self._fase_ataque = False
        self._vel_ataque = pygame.Vector2(0, 0)
        self._lunge_restante = 0.0
        self.projeteis_spawnar = []

        Eye = "assets/sprites/enemies/monsters/flying_eye/"
        self.animaçoes = {
            self.Voando:    AnimatedSprite(Eye + "Flight.png", 150, 150, velocidade=6, escala=2, n_frames=8),
            self.Atacando:  AnimatedSprite(Eye + "Attack.png", 150, 150, velocidade=5, escala=2, n_frames=8, loop=False),
            self.Morto:     AnimatedSprite(Eye + "Death.png",  150, 150, velocidade=6, escala=2, n_frames=4, loop=False),
        }
        self.anim_attack2 = AnimatedSprite(Eye + "Attack2.png", 150, 150, velocidade=4, escala=2, n_frames=8, loop=False)
        self.anim_attac3 = AnimatedSprite(Eye + "Attack3.png", 150, 150, velocidade=4, escala=2, n_frames=6, loop=False)
        self.anim_hit = AnimatedSprite(Eye + "Take Hit.png", 150, 150, velocidade=3, escala=2, n_frames=4, loop=False)
        self.anim_atual = self.animaçoes[self.Voando]

        self.ecos_drop = 15

        self._configurar_ataques()

    def _configurar_ataques(self):
        contato = HitboxSpec(
            usar_mascara_animacao=False,
            inflar_rect=(self.Folga_contato_x, self.Folga_contato_y),
        )
        dano_mordida = DanoSpec(
            dano_base=self.Dano_mordida,
            knockback=KnockbackSpec(forca_x=4, forca_y=-2, frames=12),
            duracao_hit=12,
            frames_invenc=25,
        )
        dano_dash = DanoSpec(
            dano_base=self.Dano_dash,
            knockback=KnockbackSpec(forca_x=5, forca_y=-1, frames=10),
            duracao_hit=10,
            frames_invenc=20,
        )
        self._registrar_ataque(
            "mordida",
            self.animaçoes[self.Atacando],
            [self._criar_janela("mordida", 3, 7, hitbox=contato)],
            dano_mordida,
            recuperacao_ticks=8,
        )
        self._registrar_ataque(
            "dash",
            self.anim_attack2,
            [self._criar_janela("investida", 6, 7, hitbox=contato)],
            dano_dash,
            recuperacao_ticks=8,
        )
        self._registrar_ataque(
            "projetil",
            self.anim_attac3,
            [],
            DanoSpec(),
            recuperacao_ticks=8,
        )

    def _resetar_flags_ataque(self):
        self._fase_ataque = None
        self._lunge_restante = 0.0
        self._projetil_spawnado = False

    #IA

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            self._voar_para(player, rects_solidos)

            if dist < self.Alcence_perto and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("mordida", player)

            elif dist < self.Alcance_medio and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("dash", player)

            elif dist < self.Alcance_detec and self.cooldown_projetil <= 0 and self.cooldown_ataq <= 0:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.olhando_dir = direçao > 0
                self._iniciar_ataque("projetil", player)
        else:
            self.vel.y = 0
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = 1.5
                self.olhando_dir = True
            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -1.5
                self.olhando_dir = False
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
        #o deslocamento real acontece no mover_com_colisão() do InimigoBase

    #Ataques 

    def _iniciar_ataque(self, tipo, player):
        if not self.iniciar_ataque(tipo, player):
            return

        direçao = 1 if player.rect.centerx > self.rect.centerx else -1

        if tipo == "mordida":
            self.cooldown_ataq = self.Cooldown_ataque
            self._lunge_restante = 30.0
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                self._vel_ataque = pygame.Vector2(
                    (dx / dist) * (self.Vel_ataque * 0.5),
                    (dy / dist) * (self.Vel_ataque * 0.5)
                )
            else:
                self._vel_ataque = pygame.Vector2(0, self.Vel_ataque * 0.5)
            self._fase_ataque = "descendo"

        elif tipo == "dash":
            self.cooldown_ataq = self.Cooldown_ataque
            self._vel_ataque = pygame.Vector2(direçao * self.Vel_ataque * 1.5, 0)
            self._fase_ataque = "dashando"
            self._dash_timer = 20

        elif tipo == "projetil":
            self.cooldown_ataq = self.Cooldown_ataque
            self.cooldown_projetil = self.Cooldown_projetil_max
            self._fase_ataque = "atirando"
            self._projetil_player = player

    def _atualizar_ataque_em_curso(self, rects_solidos, player):
        frame = self.ataque_ativo.frame if self.ataque_ativo is not None else 0

        if self.ataque_ativo is not None and self.ataque_ativo.fase == FaseAtaque.RECOVERY:
            self.vel.x = 0
            self.vel.y = 0
            self._vel_ataque = pygame.Vector2(0, 0)
            self._decrementar_cooldowns()
            return 0

        if self._ataque_atual == "mordida":
            if self._fase_ataque == "descendo":
                self._mover_ataque(rects_solidos, limitar=True)
                if frame >= 7:
                    self._fase_ataque = "subindo"
                    self._vel_ataque = pygame.Vector2(0, -self.Vel_ataque)
            elif self._fase_ataque == "subindo":
                self._mover_ataque(rects_solidos)
                self._vel_ataque *= 0.9

        elif self._ataque_atual == "dash":
            if self._fase_ataque == "dashando":
                self._mover_ataque(rects_solidos)
                self._vel_ataque.x *= 0.92
                self._dash_timer -= 1
                if self._dash_timer <= 0:
                    self._vel_ataque.x = 0

        self._decrementar_cooldowns()
        return 0

    def _mover_ataque(self, rects_solidos, limitar=False):
        #usa a colisão da Entity para o ataque não atravessar paredes
        vel = self._vel_ataque.copy()

        if limitar:
            if self._lunge_restante <= 0:
                return
            dist = vel.length()
            if dist <= 0:
                return
            consumido = min(dist, self._lunge_restante)
            if consumido < dist:
                vel = vel.normalize() * consumido
            self._lunge_restante -= consumido

        self.vel.x, self.vel.y = vel.x, vel.y
        self.mover_com_colisão(rects_solidos)
        self._vel_ataque.x, self._vel_ataque.y = self.vel.x, self.vel.y

    def _ao_tick_ataque(self, player, frame):
        if self._ataque_atual == "projetil":
            if frame >= 3 and not self._projetil_spawnado:
                self._projetil_spawnado = True
                self._spawnar_projetil(player)

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

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        return sr.centerx - sprite_w // 2, sr.centery - sprite_h // 2