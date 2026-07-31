import pygame
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from entities.projeteis.projetil_boss import ProjetilBoss


class EsqueletoBoss(InimigoBase):

    ESTADO_PADRAO = "Perseguir"   
    Duracao_morte = 120

    Dano_normal           = 25
    Dano_varrido          = 30
    Dano_projetil         = 20


    # NOVO — boss é pesado: quase nao é empurrado, flinch curto,
    # e depois fica ~0.67s imune a novo stagger (mas continua tomando dano normal)
    KB_FORCA_X = 1
    KB_FORCA_Y = -1
    KB_FRAMES = 6
    HITSTUN_FRAMES = 10
    IMUNIDADE_STAGGER_FRAMES = 40

    Vel_perseguir         = 1.8

    Alcance_detec         = 400
    Alcance_ataq_normal   = 90
    Alcance_ataq_varrido  = 120
    Alcance_ataq_projetil = 160
    Alcance_escudo        = 150

    Cooldown_ataq         = 150
    Cooldown_projetil_max = 280
    Cooldown_escudo_max   = 350
    Duracao_escudo_max    = 90

    def __init__(self, x, y, callback_morte=None):
        super().__init__(x, y, largura=50, altura=90, hp_max=300,
                          callback_morte=callback_morte)

        self.cooldown_projetil = random.randint(0, self.Cooldown_projetil_max)
        self.cooldown_escudo   = random.randint(0, self.Cooldown_escudo_max)
        self._cooldowns_extra  = ["cooldown_projetil", "cooldown_escudo"]

        self._duracao_escudo = 0
        self._escudo_ativo   = False

        self.projeteis_spawnar = []

        Boss_skeleton = "assets/sprites/enemies/monsters/esqueletos/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Boss_skeleton + "Idle.png",   150, 150, velocidade=8, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Boss_skeleton + "Walk.png",   150, 150, velocidade=8, escala=2, n_frames=4),
            self.Atacando:  AnimatedSprite(Boss_skeleton + "Attack.png", 150, 150, velocidade=6, escala=2, n_frames=8),
            self.Morto:     AnimatedSprite(Boss_skeleton + "Death.png",  150, 150, velocidade=8, escala=2, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Boss_skeleton + "Attack2.png", 150, 150, velocidade=6, escala=2, n_frames=8)
        self.anim_attack3 = AnimatedSprite(Boss_skeleton + "Attack3.png", 150, 150, velocidade=6, escala=2, n_frames=6)
        self.anim_shield  = AnimatedSprite(Boss_skeleton + "Shield.png",  150, 150, velocidade=8, escala=2, n_frames=4)
        self.anim_hit     = AnimatedSprite(Boss_skeleton + "Take Hit.png", 150, 150, velocidade=10, escala=2, n_frames=4)
        self.anim_atual   = self.animaçoes[self.Perseguir]

        self.ecos_drop = 150

    @property
    def nome(self):
        return "Carrasco Esquelético"

    #escudo

    def _estado_especial(self, rects_solidos, player):
        if not self._escudo_ativo:
            return None

        self._duracao_escudo -= 1
        self.anim_atual = self.anim_shield
        self.anim_shield.atualizar()

        if self.cooldown_escudo > 0:
            self.cooldown_escudo -= 1

        if self._duracao_escudo <= 0:
            self._escudo_ativo = False
            self.estado = self.Perseguir
            self._resetar_para_estado_atual()

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_mask()
        
        return 0

    # IA 

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_normal:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)

            elif dist < self.Alcance_ataq_varrido:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)

            elif dist < self.Alcance_ataq_projetil and self.cooldown_projetil <= 0:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)

            elif self.cooldown_escudo <= 0 and dist < self.Alcance_escudo:
                self._escudo_ativo = True
                self._duracao_escudo = self.Duracao_escudo_max
                self.cooldown_escudo = self.Cooldown_escudo_max
                self.vel.x = 0

            else:
                self.estado = self.Perseguir
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0
        else:
            self.estado = self.Patrulha
            self.vel.x = 0

        return 0

    def _tentar_atacar(self, dist, player):
        if self.cooldown_ataq > 0:
            return

        self.cooldown_ataq = self.Cooldown_ataq
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.olhando_dir = direçao > 0

        if dist < self.Alcance_ataq_normal:
            self._iniciar_ataque("normal")
        elif dist < self.Alcance_ataq_varrido:
            self._iniciar_ataque("varrido")
        else:
            if self.cooldown_projetil <= 0:
                self._iniciar_ataque("projetil", direçao, player)
                self.cooldown_projetil = self.Cooldown_projetil_max
            else:
                self.estado = self.Perseguir
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0

    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        self._ataque_atual = tipo
        self._animando_ataque = True

        if tipo == "normal":
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()
        elif tipo == "varrido":
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()
        elif tipo == "projetil":
            self._projetil_info = {"direçao": direçao, "frame_spawn": 3, "spawnando": False}
            self.anim_atual = self.anim_attack3
            self.anim_atual.resetar()

    def _atualizar_animacao_ataque(self, player):
        self.anim_atual.atualizar()

        if self._ataque_atual == "normal":
            if self.anim_atual._frame_idx == 4 and not hasattr(self, "_dano_normal_aplicado"):
                self._dano_normal_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:
                    direçao_kb = 1 if player.rect.centerx > self.rect.centerx else -1
                    player.receber_dano(self.Dano_normal, frames_invenc=20)

                    player.vel.x = direçao_kb * 5
                    player.vel.y = -4

        elif self._ataque_atual == "varrido":
            if self.anim_atual._frame_idx == 4 and not hasattr(self, "_dano_varrido_aplicado"):
                self._dano_varrido_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_varrido:
                    direçao_kb = 1 if player.rect.centerx > self.rect.centerx else -1
                    player.receber_dano(self.Dano_varrido, frames_invenc=30)
                    player.vel.x = direçao_kb * 8
                    player.vel.y = -4

        elif self._ataque_atual == "projetil":
            if not self._projetil_info["spawnando"] and self.anim_atual._frame_idx >= self._projetil_info["frame_spawn"]:
                self._projetil_info["spawnando"] = True
                p = ProjetilBoss(
                    self.rect.centerx, self.rect.centery - 35,
                    self._projetil_info["direçao"], self.Dano_projetil
                )
                self.projeteis_spawnar.append(p)

        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            for attr in ("_dano_normal_aplicado", "_dano_varrido_aplicado"):
                if hasattr(self, attr):
                    delattr(self, attr)
            self._resetar_para_estado_atual()



    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        return sr.centerx - sprite_w // 2, sr.centery - sprite_h + 143

    def _desenhar_extra(self, tela, sr):
        if self._escudo_ativo:
            pygame.draw.rect(tela, (0, 150, 255), sr, 3)