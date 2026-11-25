"""Contrato do mapa experimental e percurso real de ida/volta (sem saves)."""
from pathlib import Path
from unittest.mock import Mock
import xml.etree.ElementTree as ET

import pygame
import pytest

from core.game_scene import Gamescene
from scripts.validar_bloco_celas import Percurso
from settings import Screen_widht, Screen_height, ZOOM_PADRAO
from world.niveis import Conexoes
from world.tile_map import TileMap
from world.validacao_tiled import validar_mapa_tmx


MAPA = Path("assets/maps/bloco_celas_esquecidas.tmx")


@pytest.fixture
def cena():
    return Gamescene(pygame.Surface((Screen_widht, Screen_height)),
                     sala_teste="bloco_celas_esquecidas")


def test_contrato_tmx_e_referencias():
    assert validar_mapa_tmx(str(MAPA)) == []
    root = ET.parse(MAPA).getroot()
    largura, altura = int(root.get("width")), int(root.get("height"))
    assert root.get("tilewidth") == root.get("tileheight") == "32"
    assert 3 <= largura * 32 / (Screen_widht / ZOOM_PADRAO) <= 5
    for nome in ("fundo", "colisao", "plataformas", "escadas", "decoracao", "decoracao_fundo"):
        grid = TileMap.carregar_camada_tmx(str(MAPA), nome)
        assert len(grid) == altura and all(len(row) == largura for row in grid)
    # Carrega cada sprite realmente usado, detectando recortes fora da folha.
    for layer in root.findall("layer"):
        grid = TileMap.carregar_camada_tmx(str(MAPA), layer.get("name"))
        refs = {r.gid: r for row in grid for r in row if r}
        for ref in refs.values():
            assert Path(ref.imagem_path).is_file()
            assert ref.get_surface().get_size() == (32, 32)
    ids = [obj.get("id") for grupo in root.findall("objectgroup") for obj in grupo]
    assert len(ids) == len(set(ids))


def test_percurso_real_entrada_saida_retorno_e_desvios(cena):
    resultado = Percurso(cena).executar()
    assert len(resultado["marcos"]) == 8
    assert resultado["saltos_e_drops"] >= 4
    assert cena.player.rect.bottom == 384
    assert cena.player.rect.x < 400


def test_spawn_nomeado_retorno_sem_combate_e_sem_gravacao(cena):
    assert cena.player.rect.topleft == (352, 320)
    assert not cena.inimigos and not cena.portas
    assert [b.id_item for b in cena.baus] == [9]
    assert Conexoes["bloco_celas_esquecidas"]["direita"] == "antigo_arsenal_guardas"
    # O modo experimental continua isolado, apesar da conexão da campanha.
    cena.player.rect.right = 125 * 32
    cena._checar_transiçao()
    assert cena.sala_atual == "bloco_celas_esquecidas"
    assert cena.player.checkpoint_sala == "bloco_celas_esquecidas"
    cena._entrada_lado = "direita"
    cena._carregar_sala("bloco_celas_esquecidas")
    assert cena.player.rect.topleft == (3808, 768)
    assert cena.player.rect.collidelist(cena.mapa.rects_solidos) == -1
    saves = Mock()
    assert cena.salvar(saves, 1) is False
    saves.salvar.assert_not_called()
    cena.player.respawnar()
    assert cena.player.rect.topleft == (352, 320)


@pytest.mark.parametrize("zoom", [1.0, ZOOM_PADRAO, 1.8])
def test_camera_zoom_e_render_nas_extremidades(cena, zoom):
    camera = cena.camera
    camera.zoom = camera.zoom_alvo = zoom
    for x, y in ((352, 320), (3904, 768), (2549, 320), (0, 0)):
        for _ in range(80):
            camera.atualizar(pygame.Rect(x, y, 38, 64))
        assert 0 <= camera.offset.x <= cena.largura_mapa - Screen_widht / zoom
        assert 0 <= camera.offset.y <= cena.altura_mapa - Screen_height / zoom
        cena.desenhar()


def test_modo_temporario_descarta_slot_e_retorna_ao_fluxo_normal(monkeypatch):
    # Importar main não deve abrir logs ou trocar o interpretador neste teste.
    monkeypatch.setenv("PROFANE_VENV_ATIVO", "1")
    monkeypatch.setattr("logging_config.configurar_logging", lambda: None)
    from main import Jogo
    jogo = Jogo.__new__(Jogo)
    jogo.tela = pygame.Surface((Screen_widht, Screen_height))
    jogo.teste_celas = True
    jogo.modo_teste_combate = False
    jogo.menu = Mock()
    jogo.save_manager = Mock()
    jogo._iniciar_jogo(1, {"save": "nao deve ser lido"})
    assert jogo.slot_atual is None
    assert jogo.scene._save_callback is None
    assert jogo.scene.sala_atual == "bloco_celas_esquecidas"
    jogo._salvar_emergencia()
    jogo.save_manager.salvar.assert_not_called()
    jogo._voltar_menu()
    assert not jogo.teste_celas
    jogo._iniciar_jogo(1, None)
    assert jogo.scene.sala_atual == "bloco_celas_esquecidas"
    assert jogo.scene.sala_teste is None
    assert jogo.scene._save_callback is not None
