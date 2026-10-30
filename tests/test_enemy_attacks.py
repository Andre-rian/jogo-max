from core.combat import CombatSystem
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.skeleton import Skeleton
from entities.monsters.skeleton_boss import EsqueletoBoss
from entities.player import Player


def _posicionar_alvo(player, inimigo):
    inimigo.rect.midbottom = (player.rect.centerx - 40, player.rect.bottom)
    inimigo.olhando_dir = True
    player.olhando_dir = False


def _rodar(sistema, player, inimigo, frames):
    eventos = []
    for _ in range(frames):
        player.atualizar_mask()
        inimigo.atualizar_mask()
        eventos.extend(sistema.resolver(player, [inimigo], [], []))
    return eventos


def _novo_player():
    return Player(200, 300)


def test_skeleton_acerta_e_aplica_hitstun_uma_vez():
    player = _novo_player()
    inimigo = Skeleton(160, 300, 0, 500)
    _posicionar_alvo(player, inimigo)
    inimigo.iniciar_ataque("normal", player)
    sistema = CombatSystem()

    eventos = _rodar(sistema, player, inimigo, frames=80)

    acertos = [e for e in eventos if e.aplicado]
    assert len(acertos) == 1
    assert player.hp == player.hp_max - acertos[0].dano
    assert player._em_hit


def test_todos_os_inimigos_registram_ataques():
    eye = FlyingEye(0, 0, -50, 50)
    boss = EsqueletoBoss(0, 0)
    globin = Globin(0, 0, 0, 100)
    mushroom = Mushroom(0, 0, 0, 100)

    assert set(eye.definicoes_ataque) == {"mordida", "dash", "projetil"}
    assert set(boss.definicoes_ataque) == {"normal", "varrido", "projetil"}
    assert set(globin.definicoes_ataque) == {"normal", "dash", "bomba"}
    assert set(mushroom.definicoes_ataque) == {"normal", "forte", "esporo"}


def test_flying_eye_spawna_projetil_pelo_hook():
    player = _novo_player()
    eye = FlyingEye(300, 300, 0, 600)
    eye.rect.center = (300, 300)
    eye._iniciar_ataque("projetil", player)
    sistema = CombatSystem()

    for _ in range(50):
        player.atualizar_mask()
        eye.atualizar_mask()
        sistema.resolver(player, [eye], eye.projeteis_spawnar, [])
        if eye.projeteis_spawnar:
            break

    assert len(eye.projeteis_spawnar) == 1


def test_globin_spawna_bomba_pelo_hook():
    player = _novo_player()
    globin = Globin(160, 300, 0, 500)
    globin._iniciar_ataque("bomba", -1, player)
    sistema = CombatSystem()

    for _ in range(50):
        player.atualizar_mask()
        globin.atualizar_mask()
        sistema.resolver(player, [globin], globin.bombas_spawnar, [])
        if globin.bombas_spawnar:
            break

    assert len(globin.bombas_spawnar) == 1


def test_mushroom_spawna_esporos_pelo_hook():
    player = _novo_player()
    mushroom = Mushroom(160, 300, 0, 500)
    mushroom._iniciar_ataque("esporo", -1, player)
    sistema = CombatSystem()

    for _ in range(50):
        player.atualizar_mask()
        mushroom.atualizar_mask()
        sistema.resolver(player, [mushroom], mushroom.esporos_spawnar, [])
        if mushroom.esporos_spawnar:
            break

    assert len(mushroom.esporos_spawnar) == 3


def test_boss_spawna_projetil_pelo_hook():
    player = _novo_player()
    boss = EsqueletoBoss(160, 300)
    boss._iniciar_ataque("projetil", -1, player)
    sistema = CombatSystem()

    for _ in range(50):
        player.atualizar_mask()
        boss.atualizar_mask()
        sistema.resolver(player, [boss], boss.projeteis_spawnar, [])
        if boss.projeteis_spawnar:
            break

    assert len(boss.projeteis_spawnar) == 1


def test_inimigos_comuns_nao_ganham_iframes_entre_golpes_do_player():
    player = _novo_player()
    primeiro = Skeleton(160, 300, 0, 500)
    segundo = Skeleton(200, 300, 0, 500)
    for inimigo in (primeiro, segundo):
        inimigo.rect.midbottom = (player.rect.centerx + 50, player.rect.bottom)
    player._disparar_ataque(combo=False)

    sistema = CombatSystem()
    eventos = []
    for _ in range(60):
        player.atualizar_mask()
        for inimigo in (primeiro, segundo):
            inimigo.atualizar_mask()
        eventos.extend(sistema.resolver(player, [primeiro, segundo], [], []))

    acertos = [e for e in eventos if e.aplicado]
    assert len(acertos) >= 2
    assert primeiro.hp < primeiro.hp_max
    assert segundo.hp < segundo.hp_max
