import pygame

from core.combat.colisao import construir_hitboxes


def _pontos_mask(mask, pos, camera):
    if mask is None:
        return []
    ox = pos[0] - camera.offset.x
    oy = pos[1] - camera.offset.y
    return [(x + ox, y + oy) for x, y in mask.outline(every=2)]


def desenhar_hurtbox(vista, camera, entidade, cor=(0, 255, 255)):
    mask = getattr(entidade, "mask", None)
    if mask is None:
        return
    pos = getattr(entidade, "_mask_pos", entidade.rect.topleft)
    pontos = _pontos_mask(mask, pos, camera)
    if len(pontos) >= 3:
        pygame.draw.lines(vista, cor, True, pontos, 1)


def desenhar_hitboxes_ativas(vista, camera, entidade, cor=(255, 0, 255)):
    ataque = getattr(entidade, "ataque_ativo", None)
    if ataque is None:
        return
    for hitbox in construir_hitboxes(ataque):
        pygame.draw.rect(vista, cor, camera.aplicar(hitbox.rect), 1)
        pontos = _pontos_mask(hitbox.mask, hitbox.pos, camera)
        if len(pontos) >= 3:
            pygame.draw.lines(vista, cor, True, pontos, 1)
