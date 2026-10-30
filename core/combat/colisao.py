from dataclasses import dataclass, replace

import pygame

from core.combat.tipos import JanelaGolpe, rect_do_golpe_retangular


@dataclass
class Hitbox:
    mask: pygame.Mask | None
    rect: pygame.Rect
    pos: tuple[int, int]
    dano: object
    janela: JanelaGolpe
    dono: object
    direcao: int = 1
    frames_invenc: int | None = None

    def colide_com(self, alvo):
        mask_alvo = getattr(alvo, "mask", None)
        if self.mask is not None and mask_alvo is not None:
            ax, ay = getattr(alvo, "_mask_pos", alvo.rect.topleft)
            offset = (int(ax - self.pos[0]), int(ay - self.pos[1]))
            return self.mask.overlap(mask_alvo, offset) is not None

        return self.rect.colliderect(alvo.rect)

    @classmethod
    def de_rect(cls, rect, dano, janela, dono, direcao=1):
        return cls(
            mask=None,
            rect=rect.copy(),
            pos=rect.topleft,
            dano=dano,
            janela=janela,
            dono=dono,
            direcao=direcao,
            frames_invenc=dano.frames_invenc,
        )


def _rect_da_mask(mask, pos, animacao):
    partes = mask.get_bounding_rects()
    if not partes:
        return pygame.Rect(pos[0], pos[1], animacao.largura, animacao.altura)
    esquerda = min(r.left for r in partes)
    topo = min(r.top for r in partes)
    direita = max(r.right for r in partes)
    baixo = max(r.bottom for r in partes)
    return pygame.Rect(
        pos[0] + esquerda,
        pos[1] + topo,
        direita - esquerda,
        baixo - topo,
    )


def construir_hitbox(dono, janela, dano, direcao):
    if janela.hitbox.usar_mascara_animacao:
        animacao = getattr(dono, "anim_atual", None)
        if animacao is not None:
            mask = animacao.mascara_frame(
                animacao.frame_index,
                espelhado=not dono.olhando_dir,
            )
            pos = dono._offset_mask()
            return Hitbox(
                mask=mask,
                rect=_rect_da_mask(mask, pos, animacao),
                pos=pos,
                dano=dano,
                janela=janela,
                dono=dono,
                direcao=direcao,
                frames_invenc=dano.frames_invenc,
            )

    rect = rect_do_golpe_retangular(dono, janela.hitbox, direcao)
    return Hitbox.de_rect(rect, dano, janela, dono, direcao)


def construir_hitboxes(instancia):
    dono = instancia.atacante
    direcao = 1 if getattr(dono, "olhando_dir", True) else -1
    dano = replace(instancia.definicao.dano, dano_base=instancia.dano_base)
    return [
        construir_hitbox(dono, janela, dano, direcao)
        for janela in instancia.janelas_ativas()
    ]
