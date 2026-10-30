import random

from core.combat import CombatSystem
from entities.monsters.skeleton import Skeleton
from entities.objetos.item import get_item
from entities.player import Player


def _duelo(arma=None):
    random.seed(0)
    player = Player(100, 300)
    if arma is not None:
        player.equipar(arma)
    inimigo = Skeleton(160, 300, 0, 500)
    inimigo.rect.midbottom = (player.rect.centerx + 35, player.rect.bottom)
    player.olhando_dir = True
    inimigo.olhando_dir = False
    return player, inimigo


def _rodar_combate(sistema, player, inimigos, projeteis=(), frames=80):
    eventos = []
    for _ in range(frames):
        player.atualizar_mask()
        for inimigo in inimigos:
            inimigo.atualizar_mask()
        eventos.extend(sistema.resolver(player, list(inimigos), list(projeteis), []))
    return eventos


def test_soco_acerta_o_inimigo_uma_unica_vez():
    player, inimigo = _duelo()
    player._disparar_ataque(combo=False)
    sistema = CombatSystem()

    eventos = _rodar_combate(sistema, player, [inimigo], frames=60)

    acertos = [e for e in eventos if e.tipo == "melee" and e.aplicado]
    assert len(acertos) == 1
    assert acertos[0].dano == 5
    assert inimigo.hp == inimigo.hp_max - 5


def test_espada_tem_janelas_de_combo_distintas():
    player, _ = _duelo(get_item(1))
    definicao = player.definicoes_ataque["espada"]["combo"]["parado"]

    assert len(definicao.janelas) == 2
    assert definicao.janelas[0].nome != definicao.janelas[1].nome
    assert player.calcular_dano("combo") > player.calcular_dano("normal")


def test_ataque_com_arma_aplica_dano_da_arma():
    player, inimigo = _duelo(get_item(1))
    player._tier_ataque = "normal"
    dano_esperado = player.calcular_dano("normal")
    player._disparar_ataque(combo=False)
    sistema = CombatSystem()

    eventos = _rodar_combate(sistema, player, [inimigo], frames=60)

    acertos = [e for e in eventos if e.aplicado]
    assert len(acertos) == 1
    assert acertos[0].dano == dano_esperado


def test_player_nao_ataca_durante_hitstun():
    player, inimigo = _duelo()
    player._em_hit = True
    player.timer_hit = 5

    player._atacar([False] * 512)

    assert player.ataque_ativo is None
    assert not player.atacando
