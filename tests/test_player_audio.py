import pytest

from entities import player as player_module
from entities.player import Player


class AudioFalso:
    def __init__(self):
        self.chamadas = []

    def play_sfx(self, chave, ajuste=1.0):
        self.chamadas.append(chave)
        return True


@pytest.fixture
def audio_falso(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(player_module, "audio", falso)
    return falso


@pytest.fixture
def jogador():
    return Player(100, 300)


def test_dash_toca_som_somente_com_stamina(audio_falso, jogador):
    jogador._iniciar_dash(1)
    assert audio_falso.chamadas == ["player_dash"]

    jogador.em_dahs = False
    jogador.stamina = 0
    audio_falso.chamadas.clear()
    jogador._iniciar_dash(1)
    assert audio_falso.chamadas == []


def test_ataque_toca_um_som_por_golpe(audio_falso, jogador):
    jogador._disparar_ataque(combo=False)
    assert audio_falso.chamadas == ["player_attack"]


def test_pocao_abre_e_bebe(audio_falso, jogador):
    jogador._iniciar_bebida()
    assert audio_falso.chamadas == ["potion_open"]

    jogador.timer_bebida = 1
    jogador._atualizar_times()
    assert audio_falso.chamadas == ["potion_open", "potion_drink"]


def test_passos_por_distancia_no_chao(audio_falso, jogador):
    jogador.no_chao = True
    jogador.rect.x += jogador.Distancia_passo
    jogador._atualizar_audio_movimento(True, 1, jogador.rect.x - jogador.Distancia_passo)
    assert audio_falso.chamadas == ["player_step"]


def test_passos_somam_distancia_entre_frames(audio_falso, jogador):
    jogador.no_chao = True
    metade = jogador.Distancia_passo // 2
    x_inicial = jogador.rect.x

    for _ in range(2):
        jogador.rect.x += metade
        jogador._atualizar_audio_movimento(True, 1, jogador.rect.x - metade)

    assert audio_falso.chamadas == ["player_step"]


def test_passos_resetam_ao_parar(audio_falso, jogador):
    jogador.no_chao = True
    metade = jogador.Distancia_passo // 2
    jogador.rect.x += metade
    jogador._atualizar_audio_movimento(True, 1, jogador.rect.x - metade)

    x_parado = jogador.rect.x
    jogador._atualizar_audio_movimento(True, 1, x_parado)
    jogador.rect.x += jogador.Distancia_passo
    jogador._atualizar_audio_movimento(True, 1, jogador.rect.x - jogador.Distancia_passo)

    assert audio_falso.chamadas == ["player_step"]


@pytest.mark.parametrize(
    "estado",
    ["em_dahs", "atacando", "_em_hit", "_pegando", "_bebendo", "_escalando"],
)
def test_passos_suprimidos_em_estados_incompativeis(audio_falso, jogador, estado):
    jogador.no_chao = True
    setattr(jogador, estado, True)
    jogador.rect.x += jogador.Distancia_passo
    jogador._atualizar_audio_movimento(True, 1, jogador.rect.x - jogador.Distancia_passo)
    assert audio_falso.chamadas == []


def test_sem_passo_no_ar(audio_falso, jogador):
    jogador.no_chao = False
    jogador.rect.x += jogador.Distancia_passo
    jogador._atualizar_audio_movimento(False, 6, jogador.rect.x - jogador.Distancia_passo)
    assert audio_falso.chamadas == []


def test_pouso_toca_na_transicao_para_o_chao(audio_falso, jogador):
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 6, jogador.rect.x)
    assert audio_falso.chamadas == ["player_land"]


def test_pouso_ignora_queda_pequena(audio_falso, jogador):
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 2, jogador.rect.x)
    assert audio_falso.chamadas == []


def test_pouso_suprimido_durante_drop(audio_falso, jogador):
    jogador.no_chao = True
    jogador._timer_atravessar = 8
    jogador._atualizar_audio_movimento(False, 6, jogador.rect.x)
    assert audio_falso.chamadas == []


def test_pouso_suprimido_apos_respawn(audio_falso, jogador):
    jogador.respawnar()
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 6, jogador.rect.x)
    assert audio_falso.chamadas == []
    assert jogador._audio_suprimir_pouso is False
