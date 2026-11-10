from types import SimpleNamespace

import pytest

from core.game_scene import Gamescene
from entities import inimigo_base as inimigo_base_module
from entities.monsters.skeleton import Skeleton
from entities.player import Player
from entities.projeteis import bomba as bomba_module
from entities.projeteis.bomba import Bomba


class AudioFalso:
    def __init__(self):
        self.chamadas = []

    def play_sfx(self, chave, ajuste=1.0):
        self.chamadas.append(chave)
        return True


@pytest.fixture
def audio_falso(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr("core.game_scene.audio", falso)
    return falso


def evento(atacante, alvo, aplicado=True):
    return SimpleNamespace(atacante=atacante, alvo=alvo, aplicado=aplicado)


def processar(audio_falso, player, eventos):
    cena = SimpleNamespace(player=player)
    Gamescene._processar_audio_combate(cena, eventos)
    return audio_falso.chamadas


def test_dano_no_jogador_toca_uma_vez(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(audio_falso, player, [evento(inimigo, player)])

    assert chamadas == ["player_hurt"]


def test_dano_nao_aplicado_no_jogador_nao_toca(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(audio_falso, player, [evento(inimigo, player, aplicado=False)])

    assert chamadas == []


def test_morte_do_jogador_nao_toca_dano(audio_falso):
    player = SimpleNamespace(vivo=False)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(audio_falso, player, [evento(inimigo, player)])

    assert chamadas == []


def test_acerto_em_inimigo_toca_hit(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(audio_falso, player, [evento(player, inimigo)])

    assert chamadas == ["hit"]


def test_acerto_nao_aplicado_em_inimigo_nao_toca_hit(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(
        audio_falso, player, [evento(player, inimigo, aplicado=False)]
    )

    assert chamadas == []


def test_morte_de_inimigo_toca_som_de_morte(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=False)

    chamadas = processar(audio_falso, player, [evento(player, inimigo)])

    assert chamadas == ["enemy_death"]


def test_bloqueio_no_escudo_toca_block(audio_falso):
    player = SimpleNamespace(vivo=True)
    boss = SimpleNamespace(vivo=True, _escudo_ativo=True)

    chamadas = processar(
        audio_falso, player, [evento(player, boss, aplicado=False)]
    )

    assert chamadas == ["block"]


def test_ataque_de_inimigo_nao_e_audio_de_impacto(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigo = SimpleNamespace(vivo=True)

    chamadas = processar(audio_falso, player, [evento(inimigo, SimpleNamespace(vivo=True))])

    assert chamadas == []


def test_varios_acertos_na_mesma_janela_tocam_um_por_evento(audio_falso):
    player = SimpleNamespace(vivo=True)
    inimigos = [SimpleNamespace(vivo=True) for _ in range(3)]
    eventos = [evento(player, inimigo) for inimigo in inimigos]

    chamadas = processar(audio_falso, player, eventos)

    assert chamadas == ["hit", "hit", "hit"]


def test_inimigo_toca_ataque_ao_iniciar(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(inimigo_base_module, "audio", falso)
    player = Player(200, 300)
    inimigo = Skeleton(160, 300, 0, 500)

    assert inimigo.iniciar_ataque("normal", player)
    assert falso.chamadas == ["enemy_attack"]


def test_ataque_invalido_de_inimigo_nao_toca(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(inimigo_base_module, "audio", falso)
    player = Player(200, 300)
    inimigo = Skeleton(160, 300, 0, 500)

    assert inimigo.iniciar_ataque("inexistente", player) is False
    assert falso.chamadas == []


def test_bomba_toca_explosao_uma_vez(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(bomba_module, "audio", falso)
    bomba = Bomba(0, 0, 1)

    bomba._iniciar_explosao()
    bomba._iniciar_explosao()

    assert falso.chamadas == ["bomb_explosion"]
