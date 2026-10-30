from core.combat import CombatSystem
from entities.player import Player
from entities.projeteis.bomba import Bomba
from entities.projeteis.esporo_mushroom import EsporoMushroom
from entities.projeteis.projetil_boss import ProjetilBoss
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye


def _player_em(x=200, y=300):
    player = Player(x, y)
    player.rect.midbottom = (x, y)
    player.atualizar_mask()
    return player


def _resolver_uma_vez(player, projetil):
    sistema = CombatSystem()
    return sistema.resolver(player, [], [projetil], [])


def test_projetil_flying_eye_acerta_e_desativa():
    player = _player_em()
    projetil = ProjetilFlyingEye(player.rect.centerx, player.rect.centery, 0, 0, 15)

    eventos = _resolver_uma_vez(player, projetil)

    assert len(eventos) == 1
    assert eventos[0].aplicado
    assert player.hp == player.hp_max - 15
    assert not projetil.ativo


def test_projetil_boss_acerta_e_desativa():
    player = _player_em()
    projetil = ProjetilBoss(player.rect.centerx, player.rect.centery, 1, 20)

    eventos = _resolver_uma_vez(player, projetil)

    assert len(eventos) == 1
    assert eventos[0].aplicado
    assert player.hp == player.hp_max - 20
    assert not projetil.ativo


def test_esporo_acerta_e_desativa():
    player = _player_em()
    esporo = EsporoMushroom(player.rect.centerx, player.rect.centery, 0, 0, 8)
    esporo._timer_delay = 0

    eventos = _resolver_uma_vez(player, esporo)

    assert len(eventos) == 1
    assert eventos[0].aplicado
    assert player.hp == player.hp_max - 8
    assert not esporo.ativo


def test_bomba_explode_e_acerta_apenas_uma_vez():
    player = _player_em()
    bomba = Bomba(player.rect.centerx + 20, player.rect.centery - 40, 1, 20)
    bomba.explodindo = True
    sistema = CombatSystem()

    eventos = []
    for _ in range(10):
        player.atualizar_mask()
        eventos.extend(sistema.resolver(player, [], [bomba], []))

    acertos = [e for e in eventos if e.aplicado]
    assert len(acertos) == 1
    assert acertos[0].dano == 20
    assert player.hp == player.hp_max - 20
    assert bomba.ativo


def test_player_usa_iframes_contra_segundo_projetil_no_mesmo_frame():
    player = _player_em()
    primeiro = ProjetilFlyingEye(player.rect.centerx, player.rect.centery, 0, 0, 15)
    segundo = ProjetilFlyingEye(player.rect.centerx, player.rect.centery, 0, 0, 15)
    sistema = CombatSystem()

    eventos = sistema.resolver(player, [], [primeiro, segundo], [])

    assert len(eventos) == 2
    assert eventos[0].aplicado
    assert not eventos[1].aplicado
    assert player.hp == player.hp_max - 15
    assert not primeiro.ativo
    assert segundo.ativo


def test_projetil_bloqueado_por_iframes_pode_acertar_depois():
    player = _player_em()
    primeiro = ProjetilFlyingEye(player.rect.centerx, player.rect.centery, 0, 0, 15)
    segundo = ProjetilFlyingEye(player.rect.centerx, player.rect.centery, 0, 0, 15)
    sistema = CombatSystem()

    sistema.resolver(player, [], [primeiro, segundo], [])
    assert player.hp == player.hp_max - 15
    assert segundo.ativo

    for _ in range(25):
        player.atualizar_invencibilidade()
        sistema.resolver(player, [], [segundo], [])

    assert player.hp == player.hp_max - 30
    assert not segundo.ativo
