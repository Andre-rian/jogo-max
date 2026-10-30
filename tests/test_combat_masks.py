import pygame

from entities.player import Player


def test_mascara_frame_tem_cache_por_frame_e_espelhamento():
    player = Player(100, 300)
    anim = player.animacoes[player.Parado]

    normal = anim.mascara_frame(0, False)
    normal_de_novo = anim.mascara_frame(0, False)
    espelhada = anim.mascara_frame(0, True)

    assert normal is normal_de_novo
    assert espelhada is not normal
    assert (0, False) in anim._mascaras
    assert (0, True) in anim._mascaras


def test_player_hurtbox_usa_animacao_idle_mesmo_durante_ataque():
    player = Player(100, 300)
    player.anim_atual = player.animacoes_ataque["espada"]["normal"]["parado"]

    player.atualizar_mask()

    assert player.anim_hurtbox is player.animacoes[player.Parado]
    assert player.mask is not None
    assert player._mask_pos == player._offset_para_anim(player.animacoes[player.Parado])


def test_hitbox_de_mascara_colide_com_hurtbox():
    from core.combat import Hitbox, HitboxSpec, JanelaGolpe, PoliticaHit

    player = Player(100, 300)
    player.atualizar_mask()

    mask = player.anim_hurtbox.mascara_frame(0, False)
    janela = JanelaGolpe("teste", 0, 1, hitbox=HitboxSpec(usar_mascara_animacao=True), politica=PoliticaHit.UMA_VEZ)
    hitbox = Hitbox(
        mask=mask,
        rect=pygame.Rect(player._mask_pos[0], player._mask_pos[1], player.anim_hurtbox.largura, player.anim_hurtbox.altura),
        pos=player._mask_pos,
        dano=None,
        janela=janela,
        dono=player,
    )

    assert hitbox.colide_com(player)


def test_hitbox_de_mascara_nao_cai_para_rect_quando_pixels_nao_se_tocam():
    from core.combat import Hitbox, HitboxSpec, JanelaGolpe, PoliticaHit

    class Alvo:
        pass

    alvo = Alvo()
    alvo.rect = pygame.Rect(0, 0, 20, 20)
    alvo._mask_pos = (0, 0)
    alvo.mask = pygame.Mask((20, 20))
    alvo.mask.set_at((19, 19), 1)

    mask_hitbox = pygame.Mask((20, 20))
    mask_hitbox.set_at((0, 0), 1)

    janela = JanelaGolpe("teste", 0, 1, hitbox=HitboxSpec(usar_mascara_animacao=True), politica=PoliticaHit.UMA_VEZ)
    hitbox = Hitbox(
        mask=mask_hitbox,
        rect=alvo.rect.copy(),
        pos=(0, 0),
        dano=None,
        janela=janela,
        dono=None,
    )

    assert hitbox.rect.colliderect(alvo.rect)
    assert not hitbox.colide_com(alvo)
