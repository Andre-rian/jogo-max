import pygame

from core.combat import CombatSystem, JanelaGolpe, KnockbackSpec
from core.combat.dano import DamageEvent
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.skeleton import Skeleton
from entities.monsters.skeleton_boss import EsqueletoBoss
from entities.player import Player


def _evento(alvo, duracao_hit=12):
    return DamageEvent(
        atacante=None,
        alvo=alvo,
        fonte=None,
        janela=JanelaGolpe("teste", 0, 1),
        dano=1,
        direcao=1,
        knockback=KnockbackSpec(forca_x=0, forca_y=0, frames=1),
        duracao_hit=duracao_hit,
        stagger=True,
    )


def test_hitstun_nao_encurta_a_reacao_de_globin_e_mushroom():
    for classe in (Globin, Mushroom):
        inimigo = classe(100, 100, 0, 500)

        inimigo.receber_evento(_evento(inimigo, duracao_hit=12))

        assert inimigo._em_hit
        assert inimigo._timer_hit == max(inimigo.HITSTUN_FRAMES, 12)


def test_flying_eye_knockback_nao_atravessa_parede():
    eye = FlyingEye(100, 100, 0, 500)
    parede = pygame.Rect(160, 0, 32, 400)

    eye.receber_hit(1, 1, forca_x=20, forca_y=0, frames_kb=10, duracao_hit=1)
    for _ in range(10):
        eye._atualizar_knockback([parede])

    assert eye.rect.right <= parede.left


def test_flying_eye_ataque_nao_atravessa_parede():
    eye = FlyingEye(100, 100, 0, 500)
    player = Player(300, 100)
    parede = pygame.Rect(160, 0, 32, 400)

    eye._iniciar_ataque("dash", player)
    for _ in range(20):
        eye._atualizar_ataque_em_curso([parede], player)

    assert eye.rect.right <= parede.left


def test_animacao_de_hit_completa_antes_de_voltar_ao_estado():
    player = Player(5000, 300)
    alvos = [
        (Globin, (100, 300, 0, 500)),
        (Mushroom, (100, 300, 0, 500)),
        (Skeleton, (100, 300, 0, 500)),
        (FlyingEye, (100, 300, 0, 500)),
        (EsqueletoBoss, (100, 300)),
    ]

    for classe, args in alvos:
        inimigo = classe(*args)
        inimigo.receber_evento(_evento(inimigo))

        vistos = set()
        for _ in range(inimigo.HITSTUN_FRAMES + 2):
            inimigo.atualizar([], player)
            if inimigo.anim_atual is inimigo.anim_hit:
                vistos.add(inimigo.anim_atual.frame_index)

        assert max(vistos) == len(inimigo.anim_hit.frames) - 1
        assert inimigo.anim_atual is not inimigo.animaçoes[inimigo.Atacando]


def test_hit_durante_ataque_nao_deixa_pose_de_ataque():
    player = Player(120, 300)
    alvos = [
        (Globin, (100, 300, 0, 500)),
        (Mushroom, (100, 300, 0, 500)),
        (Skeleton, (100, 300, 0, 500)),
    ]

    for classe, args in alvos:
        inimigo = classe(*args)
        inimigo.iniciar_ataque("normal", player)
        inimigo.cooldown_ataq = 120

        inimigo.receber_evento(_evento(inimigo))
        for _ in range(inimigo.HITSTUN_FRAMES + 4):
            inimigo.atualizar([], player)

        assert inimigo.estado != inimigo.Atacando
        assert inimigo.anim_atual is not inimigo.animaçoes[inimigo.Atacando]


def test_mesmo_golpe_so_aplica_uma_vez_com_hitbox_em_contato():
    player = Player(200, 300)
    inimigo = Skeleton(240, 300, 0, 500)
    inimigo.rect.midbottom = (player.rect.centerx + 40, player.rect.bottom)
    player.olhando_dir = True
    player._disparar_ataque(combo=False)

    sistema = CombatSystem()
    acertos = 0
    for _ in range(60):
        player.atualizar_mask()
        inimigo.atualizar_mask()
        for evento in sistema.resolver(player, [inimigo], [], []):
            if evento.aplicado:
                acertos += 1

    assert acertos == 1


def test_inimigo_morto_nao_se_move_nem_ataca():
    player = Player(120, 300)
    inimigo = Globin(100, 300, 0, 500)
    inimigo.hp = 1

    inimigo.receber_evento(_evento(inimigo))
    assert not inimigo.vivo

    posicao = inimigo.rect.topleft
    for _ in range(10):
        inimigo.atualizar([], player)

    assert inimigo.rect.topleft == posicao
    assert inimigo.ataque_ativo is None
    assert not inimigo._animando_ataque


def test_recuperacao_pos_hit_mantem_inimigo_parado_antes_de_voltar_a_ia():
    player = Player(480, 300)

    for classe in (Globin, Mushroom):
        inimigo = classe(300, 300, 0, 500)
        inimigo.cooldown_ataq = 999
        for atributo in ("cooldown_bomba", "cooldown_esporo"):
            if hasattr(inimigo, atributo):
                setattr(inimigo, atributo, 999)

        inimigo.receber_evento(_evento(inimigo))
        for _ in range(200):
            if inimigo._em_recuperacao:
                break
            inimigo.atualizar([], player)

        assert inimigo._em_recuperacao
        assert inimigo.estado == getattr(inimigo, inimigo.ESTADO_PADRAO)

        x = inimigo.rect.x
        for _ in range(inimigo.RECUPERACAO_HIT_FRAMES - 1):
            inimigo.atualizar([], player)
            assert inimigo.rect.x == x
            assert not inimigo._animando_ataque

        assert inimigo._em_recuperacao
        x = inimigo.rect.x
        inimigo.atualizar([], player)
        assert not inimigo._em_recuperacao
        assert inimigo.rect.x == x
