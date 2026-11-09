from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from core.audio import AudioManager, resolver_arma_id


@pytest.fixture(autouse=True)
def limpar_mixer():
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()
        pygame.mixer.set_num_channels(24)
        pygame.mixer.set_reserved(2)
    yield
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()


def criar_arquivo(raiz, pasta):
    caminho = raiz / "assets" / "sons" / pasta
    caminho.mkdir(parents=True, exist_ok=True)
    (caminho / "hit_01.wav").write_bytes(b"")
    return caminho


def test_resolver_pasta_prioriza_inimigo_arma(tmp_path):
    criar_arquivo(tmp_path, "sfx/inimigos/skeleton/hit/espada_longa")
    criar_arquivo(tmp_path, "sfx/inimigos/skeleton/hit/_default")
    criar_arquivo(tmp_path, "sfx/materiais/osso/_default")
    criar_arquivo(tmp_path, "sfx/combate/generico")

    manager = AudioManager(raiz=tmp_path)
    assert manager.inicializar()

    assert manager.resolver_pasta("skeleton", "espada_longa", "osso") == (
        "sfx/inimigos/skeleton/hit/espada_longa"
    )
    assert manager.resolver_pasta("skeleton", "machado_guerra", "osso") == (
        "sfx/inimigos/skeleton/hit/_default"
    )
    assert manager.resolver_pasta("globin", "espada_longa", "osso") == (
        "sfx/materiais/osso/_default"
    )
    assert manager.resolver_pasta("globin", "espada_longa", "carne") == (
        "sfx/combate/generico"
    )


def test_resolver_morte_usa_pasta_de_morte(tmp_path):
    criar_arquivo(tmp_path, "sfx/inimigos/skeleton/morte")
    criar_arquivo(tmp_path, "sfx/combate/generico")

    manager = AudioManager(raiz=tmp_path)
    assert manager.inicializar()

    assert manager.resolver_pasta("skeleton", "soco", "osso", tipo="morte") == (
        "sfx/inimigos/skeleton/morte"
    )
    assert manager.resolver_pasta("globin", "soco", "carne", tipo="morte") == (
        "sfx/combate/generico"
    )


def test_play_hit_usa_fallback_generico_real():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_hit("globin", "espada_longa", "etereo")
    assert "sfx/combate/generico" in Path(manager._ativos[-1].chave).as_posix()


def test_play_swing_encontra_arma_especifica():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_swing("espada_longa")
    assert "sfx/player/armas/espada_longa" in Path(manager._ativos[-1].chave).as_posix()


def test_play_step_pedra_encontra_som_de_pedra():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_step("pedra")
    assert "sfx/player/movimento/passos/pedra" in Path(manager._ativos[-1].chave).as_posix()


def test_play_step_material_vazio_cai_para_madeira():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_step("metal")
    assert "sfx/player/movimento/passos/madeira" in Path(manager._ativos[-1].chave).as_posix()


def test_play_enemy_step_usa_pasta_do_inimigo():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_enemy_step("globin")
    assert "sfx/inimigos/globin/passos" in Path(manager._ativos[-1].chave).as_posix()


def test_play_enemy_step_cai_para_default():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_enemy_step("skeleton")
    assert "sfx/inimigos/_default/passos" in Path(manager._ativos[-1].chave).as_posix()


def test_play_land_pedra_encontra_som_de_pedra():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_land("pedra")
    assert "sfx/player/movimento/pouso/pedra" in Path(manager._ativos[-1].chave).as_posix()


def test_resolver_arma_id_mapeia_icones():
    assert resolver_arma_id(SimpleNamespace(arma_id="soco")) == "soco"
    assert resolver_arma_id(SimpleNamespace(arma_equipada=None)) == "soco"
    assert resolver_arma_id(
        SimpleNamespace(arma_equipada=SimpleNamespace(icone="espada"))
    ) == "espada_longa"
    assert resolver_arma_id(
        SimpleNamespace(arma_equipada=SimpleNamespace(icone="machado"))
    ) == "machado_guerra"


def test_play_kill_usa_morte_default():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_kill("globin", "machado_guerra", "carne")
    assert "/morte/" in Path(manager._ativos[-1].chave).as_posix()


def test_play_block_nao_usa_hit_como_fallback():
    manager = AudioManager()
    assert manager.inicializar()

    assert manager.play_block("skeleton")
    assert "block_" in Path(manager._ativos[-1].chave).name
