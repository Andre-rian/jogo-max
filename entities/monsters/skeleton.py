import pygame
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, KnockbackSpec

class Skeleton(InimigoBase):

    Dano = 15
    Vel_patrulha = 1.5
    Vel_perseguir = 3.0
    Alcance_detec = 250
    Alcance_ataq = 48
    Cooldown_ataq = 90

    #alcance real do golpe por distância de borda (gap) — o exoesqueleto só conecta
    #de perto, no frame de conexão da animação de ataque (não mais instantâneo)
    Alcance_conectar = 20

    Duracao_morte = 90
    HITSTUN_FRAMES = 16  # 8 frames de hit a 2 ticks = ~267 ms (reação completa)

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=48, hp_max=60, patrulha_esq=patrulha_esq, patrulha_dir=patrulha_dir)


        self.vel.x = self.Vel_patrulha
        self.escos_drop = 20

        Skel = "assets/sprites/enemies/monsters/skeleton/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=8, escala=3, n_frames=11),
            self.Perseguir: AnimatedSprite(Skel + "Skeleton Walk.png",   22, 33, velocidade=5, escala=3, n_frames=11),
            self.Atacando:  AnimatedSprite(Skel + "Skeleton Attack.png", 43, 37, velocidade=4, escala=3, n_frames=18, loop=False),
            self.Morto:     AnimatedSprite(Skel + "Skeleton Dead.png",   33, 32, velocidade=6, escala=3, n_frames=15),
        }
        self.anim_hit = AnimatedSprite(Skel + "Skeleton Hit.png", 30, 32, velocidade=2, escala=3, n_frames=8)
        self.anim_idle = AnimatedSprite(Skel + "Skeleton Idle.png", 24, 32, velocidade=8, escala=3, n_frames=11)
        self.anim_atual = self.animaçoes[self.Patrulha]

        self._configurar_ataques()

    def _configurar_ataques(self):
        dano = DanoSpec(
            dano_base=self.Dano,
            knockback=KnockbackSpec(forca_x=3, forca_y=-1, frames=10),
            duracao_hit=12,
            frames_invenc=15,
        )
        janela = self._criar_janela("corte", 6, 8)
        self._registrar_ataque(
            "normal",
            self.animaçoes[self.Atacando],
            [janela],
            dano,
        )

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq:
                self.vel.x = 0
                if self.cooldown_ataq <= 0:
                    return self._tentar_atacar(player)
                #em cooldown fica em idle; não entra na pose de ataque sem golpe ativo
                self.estado = self.Patrulha
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
        self.iniciar_ataque("normal", player)
        return 0

    def _animacao_extra_hook(self):
        if self.estado == self.Patrulha and self.vel.x == 0:
            self.anim_atual = self.anim_idle

    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        offset_x = sr.centerx - sprite_w // 2 + (-10 if self.olhando_dir else 10)
        offset_y = sr.bottom - sprite_h
        return offset_x, offset_y