import pygame

from core.audio import audio
from core.combat import (
    DanoSpec,
    Hitbox,
    HitboxSpec,
    JanelaGolpe,
    KnockbackSpec,
    PoliticaHit,
)


class Projetil:
    #classe base para todos os projeteis do jogo

    NOME_JANELA = "projetil"
    SOM_PROJETIL = None

    def __init__(self, x, y, vel_x, vel_y, dano, tem_gravidade=False, gravidade=0.4, frames_invenc=None):
        self.rect = pygame.Rect(x, y, 20, 20)  # Tamanho base, cada inimigo pode ter um tamanho diferente
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.dano = dano
        self.tem_gravidade = tem_gravidade
        self.ativo = True  # Para controlar se o projétil ainda está ativo ou deve ser removido
        self.gravidade = gravidade
        self.frames_invenc = frames_invenc
        self._som_voo_tocado = False
        self._timer_som_voo = 0
        self._tocar_som_projetil("disparo")

        self._janela = JanelaGolpe(
            nome=self.NOME_JANELA,
            frame_inicio=0,
            frame_fim=10_000,
            hitbox=HitboxSpec(usar_mascara_animacao=False),
            politica=PoliticaHit.UMA_VEZ,
            canal=self.NOME_JANELA,
            bloqueia_por_parede=False,
        )

    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return

        if self.tem_gravidade:
            self.vel.y = min(self.vel.y + self.gravidade, 15)  # Limite de velocidade de queda

        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        #colisao com as paredes
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self._ao_colidir_mundo(tile)
                return

    def _tocar_som_projetil(self, fase):
        if self.SOM_PROJETIL:
            audio.play_projectile(self.SOM_PROJETIL, fase)

    def _atualizar_som_voo(self):
        if not self.SOM_PROJETIL or self._som_voo_tocado:
            return
        self._timer_som_voo += 1
        if self._timer_som_voo >= 6:
            self._som_voo_tocado = True
            self._tocar_som_projetil("voo")

    def _ao_colidir_mundo(self, tile):
        #conportamento padrao, se colidir = desetivar
        self._tocar_som_projetil("impacto")
        self.ativo = False

    def dano_spec(self):
        return DanoSpec(
            dano_base=self.dano,
            knockback=KnockbackSpec(forca_x=4, forca_y=-2, frames=10),
            stagger=True,
            duracao_hit=12,
            frames_invenc=self.frames_invenc,
        )

    def hitboxes_ativas(self):
        if not self.ativo:
            return ()
        direcao = 1 if self.vel.x >= 0 else -1
        return [Hitbox.de_rect(self.rect, self.dano_spec(), self._janela, self, direcao)]

    def ao_acertar(self, player, evento):
        #comportamento padrao: some ao acertar
        self._tocar_som_projetil("impacto")
        self.ativo = False

    def desenhar(self, tela, camera):
        if not self.ativo:
            return

        sr = camera.aplicar(self.rect)

        #placerholder, cada filho implementar a sua sprite
        pygame.draw.circle(tela, (255, 0, 0), sr.center, 6)
