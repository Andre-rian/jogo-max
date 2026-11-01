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


def _preparar_corrida(jogador):
    jogador.no_chao = True
    jogador.estado = Player.Correndo
    jogador.anim_atual = jogador.animacoes[Player.Correndo]
    jogador.anim_atual.resetar()


def test_passo_toca_ao_entrar_no_frame_de_contato(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=0, deslocamento=4)

    assert audio_falso.chamadas == ["player_step"]


def test_passo_nao_repete_enquanto_fica_no_frame_de_contato(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=1, deslocamento=4)

    assert audio_falso.chamadas == []


def test_passo_nao_toca_fora_dos_frames_de_contato(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.anim_atual.definir_frame(2)

    jogador._atualizar_audio_passos(frame_antes=1, deslocamento=4)

    assert audio_falso.chamadas == []


def test_passo_nao_toca_sem_deslocamento(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=0, deslocamento=0)

    assert audio_falso.chamadas == []


def test_passo_nao_toca_fora_do_estado_correndo(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.estado = Player.Parado
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=0, deslocamento=4)

    assert audio_falso.chamadas == []


def test_passo_nao_toca_no_ar(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador.no_chao = False
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=0, deslocamento=4)

    assert audio_falso.chamadas == []


def test_passo_suprimido_apos_respawn(audio_falso, jogador):
    _preparar_corrida(jogador)
    jogador._audio_suprimir_pouso = True
    jogador.anim_atual.definir_frame(1)

    jogador._atualizar_audio_passos(frame_antes=0, deslocamento=4)

    assert audio_falso.chamadas == []


def test_animacao_de_corrida_toca_dois_passos_por_ciclo(audio_falso, jogador):
    _preparar_corrida(jogador)

    for _ in range(60):
        frame_antes = jogador.anim_atual.frame_index
        jogador.anim_atual.atualizar()
        jogador._atualizar_audio_passos(frame_antes, deslocamento=4)

    assert audio_falso.chamadas == ["player_step", "player_step"]


def test_pouso_toca_na_transicao_para_o_chao(audio_falso, jogador):
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 6)
    assert audio_falso.chamadas == ["player_land"]


def test_pouso_ignora_queda_pequena(audio_falso, jogador):
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 2)
    assert audio_falso.chamadas == []


def test_pouso_suprimido_durante_drop(audio_falso, jogador):
    jogador.no_chao = True
    jogador._timer_atravessar = 8
    jogador._atualizar_audio_movimento(False, 6)
    assert audio_falso.chamadas == []


def test_pouso_suprimido_apos_respawn(audio_falso, jogador):
    jogador.respawnar()
    jogador.no_chao = True
    jogador._atualizar_audio_movimento(False, 6)
    assert audio_falso.chamadas == []
    assert jogador._audio_suprimir_pouso is False
