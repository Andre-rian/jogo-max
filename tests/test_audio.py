import logging

import pygame
import pytest

from core.audio import (
    ESPECIFICACOES,
    RAIZ_PROJETO,
    AudioManager,
)


@pytest.fixture(autouse=True)
def limpar_mixer():
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()
        pygame.mixer.set_num_channels(24)
        pygame.mixer.set_reserved(2)
    yield
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()


def criar_manager(agora_ms=None, raiz=None):
    manager = AudioManager(raiz=raiz, agora_ms=agora_ms)
    assert manager.inicializar()
    return manager


def test_todos_os_sons_registrados_existem():
    for spec in ESPECIFICACOES.values():
        caminho = RAIZ_PROJETO / "assets" / "sons" / spec.arquivo
        assert caminho.is_file(), caminho


def test_audio_desabilitado_por_ambiente(monkeypatch):
    monkeypatch.setenv("PROFANE_AUDIO", "0")
    manager = AudioManager()
    assert manager.inicializar() is False
    assert manager.play_sfx("ui_confirm") is False


def test_evento_desconhecido_nao_falha(caplog):
    manager = criar_manager()
    with caplog.at_level(logging.WARNING):
        assert manager.play_sfx("evento_inexistente") is False
    assert "evento desconhecido" in caplog.text


def test_arquivos_ausentes_nao_derrubam_o_jogo(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        manager = AudioManager(raiz=tmp_path)
        assert manager.inicializar()
        assert manager.play_sfx("ui_confirm") is False
    assert "não foi possível carregar" in caplog.text


def test_volumes_sao_limitados():
    manager = criar_manager()
    manager.set_master_volume(2.0)
    assert manager.master_volume == 1.0
    manager.set_sfx_volume(-1.0)
    assert manager.sfx_volume == 0.0
    manager.set_categoria_volume("combat", 4.0)
    assert manager.volumes_categoria["combat"] == 1.0


def test_volumes_afetam_sons_em_reproducao():
    manager = criar_manager()
    assert manager.play_sfx("ui_confirm")
    assert manager.play_sfx("player_hurt")

    canal_ui = pygame.mixer.Channel(0)
    canal_jogador = pygame.mixer.Channel(1)
    volume_ui_antes = canal_ui.get_volume()
    volume_jogador_antes = canal_jogador.get_volume()

    manager.set_master_volume(0.4)

    assert canal_ui.get_volume() < volume_ui_antes
    assert canal_jogador.get_volume() < volume_jogador_antes
    assert canal_ui.get_volume() == pytest.approx(0.4 * 1.0 * 0.7, abs=0.02)
    assert canal_jogador.get_volume() == pytest.approx(0.4 * 1.0 * 0.9, abs=0.02)


def test_efeitos_criticos_tocam_simultaneamente():
    manager = criar_manager()
    assert manager.play_sfx("player_hurt")
    assert manager.play_sfx("ui_confirm")
    assert pygame.mixer.Channel(0).get_busy()
    assert pygame.mixer.Channel(1).get_busy()


def test_morte_interrompe_dano_no_canal_critico():
    manager = criar_manager()
    assert manager.play_sfx("player_hurt")
    assert manager.play_sfx("player_death")
    assert manager._ativos[-1].chave == "player_death"


def test_cooldown_por_grupo():
    agora = [0]
    manager = criar_manager(agora_ms=lambda: agora[0])
    assert manager.play_sfx("hit")
    assert manager.play_sfx("hit") is False
    agora[0] = 60
    assert manager.play_sfx("hit")


def test_variacoes_de_passo_alternam():
    agora = [0]
    manager = criar_manager(agora_ms=lambda: agora[0])
    chaves = []
    for _ in range(3):
        assert manager.play_sfx("player_step")
        chaves.append(manager._ativos[-1].chave)
        pygame.mixer.stop()
        manager._ativos.clear()
        agora[0] += 100
    assert chaves == ["player_step_1", "player_step_2", "player_step_3"]


def test_troca_de_ataque_nao_toca_os_dois():
    manager = criar_manager()
    assert manager.ataque_player == "slash"
    assert manager.play_sfx("player_attack")
    assert manager._ativos[-1].chave == "player_attack_slash"

    assert manager.alternar_ataque_player() == "ataque"
    manager._ultimos.clear()
    pygame.mixer.stop()
    assert manager.play_sfx("player_attack")
    assert manager._ativos[-1].chave == "player_attack_ataque"


def test_stop_all_sfx():
    manager = criar_manager()
    assert manager.play_sfx("ui_confirm")
    manager.stop_all_sfx()
    assert not pygame.mixer.Channel(0).get_busy()
