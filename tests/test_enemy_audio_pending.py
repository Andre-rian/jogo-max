from types import SimpleNamespace

import pygame

from core.audio import AudioManager
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.skeleton_boss import EsqueletoBoss
from entities.player import Player


def test_rugido_toca_so_ao_primeiro_encontro(monkeypatch):
    chamadas = []
    monkeypatch.setattr("entities.monsters.skeleton_boss.audio.play_enemy_rugido", chamadas.append)
    boss = EsqueletoBoss(100, 100)
    player = Player(2000, 100)
    boss._ia([], player)
    assert chamadas == []
    player.rect.x = 250
    for _ in range(10):
        boss._ia([], player)
    assert chamadas == ["boss_carrasco"]
    player.rect.x = 2000
    boss._ia([], player)
    player.rect.x = 250
    boss._ia([], player)
    assert chamadas == ["boss_carrasco"]


def test_asas_respeitam_intervalo_distancia_e_morte(monkeypatch):
    chamadas = []
    monkeypatch.setattr("entities.monsters.flying_eye.audio.play_enemy_asas", chamadas.append)
    eye = FlyingEye(100, 100, 0, 500)
    player = SimpleNamespace(rect=pygame.Rect(150, 100, 30, 30), vivo=True)
    eye._atualizar_audio_asas(player)
    for _ in range(eye.INTERVALO_ASAS_TICKS - 1):
        eye._atualizar_audio_asas(player)
    assert chamadas == ["flying_eye"]
    eye._atualizar_audio_asas(player)
    assert chamadas == ["flying_eye", "flying_eye"]
    player.rect.x = 2000
    for _ in range(eye.INTERVALO_ASAS_TICKS + 1):
        eye._atualizar_audio_asas(player)
    assert len(chamadas) == 2
    player.rect.x = 150
    eye.vivo = False
    eye._atualizar_audio_asas(player)
    assert len(chamadas) == 2


def test_eventos_sem_arquivos_nao_usam_som_generico(tmp_path):
    manager = AudioManager(raiz=tmp_path)
    assert manager.inicializar()
    assert not manager.play_enemy_rugido("boss_carrasco")
    assert not manager.play_enemy_asas("flying_eye")


def test_ataque_especifico_do_boss_e_encaminhado(monkeypatch):
    chamadas = []
    monkeypatch.setattr("entities.inimigo_base.audio.play_enemy_attack",
                        lambda inimigo, tipo: chamadas.append((inimigo, tipo)))
    boss = EsqueletoBoss(100, 100)
    boss.iniciar_ataque("varrido")
    assert chamadas == [("boss_carrasco", "varrido")]
    manager = AudioManager()
    pastas = []
    monkeypatch.setattr(manager, "_tocar_cascata", lambda p, *args: pastas.extend(p))
    manager.play_enemy_attack("boss_carrasco", tipo="varrido")
    assert pastas[:2] == ["sfx/inimigos/boss_carrasco/ataque/varrido", "sfx/inimigos/boss_carrasco/ataque"]
