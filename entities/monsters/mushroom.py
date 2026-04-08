import pygame
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite

class Mushroom(Entity):

    Patrulha = "patrulha"
    Perseguir = "perseguir"
    Atacando = "atacando"
    Morto = "morto"

    Dano = 12
    Vel_patrulha = 1.0
    Vel_perseguir = 2.0
    Alcance_detec = 180
    Alcance_ataq = 40
    Cooldown_ataq = 100

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=36, altura=60, hp_max=80)

        self.patrulha_esq = patrulha_esq
        self.patrulha_dir = patrulha_dir

        self.estado = self.Patrulha
        self.cooldown_ataq = 0
        self._frame = 0
        self.timer_knockback = 0

        self.vel.x = self.Vel_patrulha
        self.olhando_dir = True

        Mush = "assets/sprites/enemies/monsters/mushroom/"

        self.animacoes = {
            self.Patrulha:  AnimatedSprite(Mush + "Idle.png",     150, 150, velocidade=10, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Mush + "Run.png",      150, 150, velocidade=6,  escala=2, n_frames=8),
            self.Atacando:  AnimatedSprite(Mush + "Attack.png",   150, 150, velocidade=5,  escala=2, n_frames=8),
            self.Morto:     AnimatedSprite(Mush + "Death.png",    150, 150, velocidade=8,  escala=2, n_frames=4),
        }
        self.anim_hit = AnimatedSprite(Mush + "Take Hit.png", 150, 150, velocidade=4, escala=2, n_frames=4)

        self._estado_anterior = self.Patrulha
        self.anim_atual = self.animacoes[self.Patrulha]
        self._em_hit = False
        self._timer_hit = 0

    def atualizar(self, rects_solidos, player):
        if not self.vivo:
            if not hasattr(self, "_timer_morte"):
                self._timer_morte = 60
                self.estado = self.Morto
                self.anim_atual = self.animacoes[self.Morto]
                self.anim_atual.resetar()

            if not self.anim_atual.terminou:
                self.anim_atual.atualizar()

            self._timer_morte -= 1
            if self._timer_morte <= 0:
                return 0
            return -1

        self._frame += 1

        if self.timer_knockback > 0:
            self.timer_knockback -= 1
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            self.atualizar_invencibilidade()
            if self.cooldown_ataq > 0:
                self.cooldown_ataq -= 1

            if self._em_hit:
                self._timer_hit -= 1
                if self._timer_hit <= 0:
                    self._em_hit = False
                    self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Patrulha])
                    self.anim_atual.resetar()
                    self._estado_anterior = self.estado
                else:
                    self.anim_atual = self.anim_hit
                    if not self.anim_hit.terminou:
                        self.anim_atual.atualizar()
            return 0

        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq:
                self.estado = self.Atacando
                self.vel.x = 0
                self._em_hit = False
                self._tentar_atacar(player)
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

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()

        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1

        if self._em_hit:
            self._timer_hit -= 1
            if self._timer_hit <= 0:
                self._em_hit = False
                self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado
            else:
                self.anim_atual = self.anim_hit
                if not self.anim_hit.terminou:
                    self.anim_atual.atualizar()
            return 0

        else:
            if self.estado != self._estado_anterior:
                self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

        self.anim_atual.atualizar()
        return 0

    def _tentar_atacar(self, player):
        if self.cooldown_ataq > 0:
            return
        self.cooldown_ataq = self.Cooldown_ataq
        player.receber_dano(self.Dano)

    def receber_hit(self, dano, direçao_knockback):
        self.receber_dano(dano)
        self.vel.x = direçao_knockback * 3
        self.vel.y = -2
        self.timer_knockback = 20

        if not self.vivo and not hasattr(self, "_timer_morte"):
            self._timer_morte = 60
            self.estado = self.Morto
            self.anim_atual = self.animacoes[self.Morto]
            self.anim_atual.resetar()

        if self.vivo:
            self._em_hit = True
            self._timer_hit = 20
            self.anim_hit.resetar()

    def desenhar(self, tela, camera):
        if not self.vivo and (not hasattr(self, '_timer_morte') or self._timer_morte <= 0):
            return

        sr = camera.aplicar(self.rect)

        if self.vivo and self.invencivel and self._frame % 6 < 3:
            return

        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        if self.olhando_dir:
            offset_x = sr.centerx - sprite_w // 2 - 10
        else:
            offset_x = sr.centerx - sprite_w // 2 + 10
        offset_y = sr.bottom - sprite_h + 100

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

    def _desenhar_hp(self, tela, sr):
        bar_w = sr.width
        ratio = self.hp / self.hp_max
        pygame.draw.rect(tela, (60, 20, 20),
                (sr.x, sr.y - 8, bar_w, 4), border_radius=2)
        if ratio > 0:
            pygame.draw.rect(tela, (200, 40, 40),
                    (sr.x, sr.y - 8, int(bar_w * ratio), 4), border_radius=2)