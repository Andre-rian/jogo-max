from dataclasses import dataclass, field
from enum import Enum

import pygame


class FaseAtaque(Enum):
    STARTUP = "startup"
    ACTIVE = "active"
    RECOVERY = "recovery"
    FINISHED = "finished"


class PoliticaHit(Enum):
    UMA_VEZ = "uma_vez"
    MULTI_HIT = "multi_hit"
    PIERCE = "pierce"
    PERSISTENTE = "persistente"


class ModoMovimento(Enum):
    LIVRE = "livre"
    REDUZIDO = "reduzido"
    TRAVADO = "travado"


@dataclass(frozen=True)
class KnockbackSpec:
    forca_x: float = 0.0
    forca_y: float = 0.0
    frames: int = 0


@dataclass(frozen=True)
class DanoSpec:
    dano_base: int = 0
    multiplicador: float = 1.0
    knockback: KnockbackSpec = field(default_factory=KnockbackSpec)
    hitstop: int = 0
    stagger: bool = True
    duracao_hit: int | None = None
    frames_invenc: int | None = None

    def calcular(self):
        return max(0, int(round(self.dano_base * self.multiplicador)))


@dataclass(frozen=True)
class HitboxSpec:
    usar_mascara_animacao: bool = True
    largura: int = 0
    altura: int = 0
    offset_x: int = 0
    offset_y: int = 0
    inflar_rect: tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class JanelaGolpe:
    nome: str
    frame_inicio: int
    frame_fim: int
    hitbox: HitboxSpec = field(default_factory=HitboxSpec)
    politica: PoliticaHit = PoliticaHit.UMA_VEZ
    canal: str = "principal"
    intervalo: int = 0
    bloqueia_por_parede: bool = True

    def ativa_no_frame(self, frame):
        return self.frame_inicio <= frame <= self.frame_fim


@dataclass(frozen=True)
class DefinicaoAtaque:
    nome: str
    animacao: object
    janelas: tuple[JanelaGolpe, ...]
    movimento: ModoMovimento = ModoMovimento.REDUZIDO
    lunge: float = 0.0
    custo_stamina: float = 0.0
    dano: DanoSpec = field(default_factory=DanoSpec)
    prioridade: int = 0
    cancelavel_apos_frame: int | None = None

    @property
    def total_frames(self):
        return len(self.animacao.frames)

    @property
    def velocidade(self):
        return self.animacao.velocidade

    @property
    def duracao_ticks(self):
        return self.total_frames * self.velocidade

    @property
    def primeiro_frame_ativo(self):
        if not self.janelas:
            return 0
        return min(j.frame_inicio for j in self.janelas)

    @property
    def ultimo_frame_ativo(self):
        if not self.janelas:
            return 0
        return max(j.frame_fim for j in self.janelas)

    def fase_em(self, frame):
        if not self.janelas:
            return FaseAtaque.STARTUP
        if frame < self.primeiro_frame_ativo:
            return FaseAtaque.STARTUP
        if frame > self.ultimo_frame_ativo:
            return FaseAtaque.RECOVERY
        if any(j.ativa_no_frame(frame) for j in self.janelas):
            return FaseAtaque.ACTIVE
        return FaseAtaque.RECOVERY

    def janelas_no_frame(self, frame):
        return tuple(j for j in self.janelas if j.ativa_no_frame(frame))


def rect_do_golpe_retangular(dono, especificacao, direcao):
    if especificacao.inflar_rect != (0, 0):
        return dono.rect.inflate(*especificacao.inflar_rect)

    if especificacao.largura <= 0 or especificacao.altura <= 0:
        return dono.rect.copy()

    largura = especificacao.largura
    altura = especificacao.altura
    if direcao >= 0:
        x = dono.rect.right + especificacao.offset_x
    else:
        x = dono.rect.left - especificacao.offset_x - largura
    y = dono.rect.centery + especificacao.offset_y - altura // 2
    return pygame.Rect(x, y, largura, altura)
