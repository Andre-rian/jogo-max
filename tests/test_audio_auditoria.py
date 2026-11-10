from pathlib import Path
from types import SimpleNamespace
import wave

import pygame
import pytest

from core.audio import AudioManager
from core.game_scene import Gamescene
from entities.monsters.mushroom import Mushroom
from entities.projeteis.bomba import Bomba


@pytest.fixture(autouse=True)
def limpar_audio():
    pygame.mixer.stop()
    pygame.mixer.music.stop()
    yield
    pygame.mixer.stop()
    pygame.mixer.music.stop()


def som_teste(tmp_path, caminho):
    p = tmp_path / "assets/sons" / caminho
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setparams((1, 2, 44100, 0, "NONE", "not compressed"))
        w.writeframes(b"\x01\x01" * 44100)
    return p


def manager(raiz=None):
    m = AudioManager(raiz=raiz, agora_ms=lambda: 0)
    assert m.inicializar()
    return m


def test_impacto_nao_e_bloqueado_pelo_disparo_no_mesmo_tick():
    m = manager()
    assert m.play_projectile("olho", "disparo")
    assert m.play_projectile("olho", "impacto")
    assert {r.grupo for r in m._ativos} == {"projectile_olho_disparo", "projectile_olho_impacto"}


def test_bomba_nao_emite_voo_depois_de_explodir(monkeypatch):
    chamadas = []
    falso = SimpleNamespace(play_projectile=lambda tipo, fase: chamadas.append((tipo, fase)))
    monkeypatch.setattr("entities.projeteis.projetil.audio", falso)
    monkeypatch.setattr("entities.projeteis.bomba.audio", falso)
    bomba = Bomba(0, 0, 1)
    bomba._iniciar_explosao()
    bomba._iniciar_explosao()
    for _ in range(10):
        bomba.atualizar([], SimpleNamespace(vivo=False))
    assert chamadas == [("bomba", "disparo"), ("bomba", "impacto")]


def test_esporo_nao_dispara_ataque_comum_junto(monkeypatch):
    chamadas = []
    m = AudioManager()
    monkeypatch.setattr(m, "_tocar_cascata", lambda pastas, *a, **kw: chamadas.append(pastas))
    monkeypatch.setattr("entities.inimigo_base.audio", m)
    Mushroom(100, 100, 0, 500)._iniciar_ataque("esporo")
    assert len(chamadas) == 1
    assert chamadas[0][0] == "sfx/inimigos/mushroom/esporo"


def test_eco_fallback_e_sempre_coleta_de_eco():
    m = manager()
    m._indice.pop("sfx/interacao/eco_profano")
    assert m.play_eco_profano()
    assert m._ativos[-1].chave == "eco_pickup"


def test_cooldown_do_eco_nao_dispara_fallback_extra():
    m = manager()
    assert m.play_eco_profano()
    assert not m.play_eco_profano()
    assert len(m._ativos) == 1
    assert m._ativos[0].grupo == "eco_profano"


def test_arquivo_ruim_nao_descarta_variacao_valida(tmp_path, monkeypatch):
    pasta = "sfx/player/armas/soco"
    valido = som_teste(tmp_path, f"{pasta}/bom.wav")
    ruim = valido.with_name("a_ruim.wav")
    ruim.write_bytes(b"arquivo corrompido")
    m = manager(tmp_path)
    monkeypatch.setattr(m, "_escolher_arquivo", lambda pasta, arquivos: arquivos[0])
    assert m.play_swing("soco")
    assert Path(m._ativos[-1].chave) == valido


def test_swing_novo_interrompe_cauda_sem_ficar_mudo():
    m = manager()
    assert m.play_swing("espada_longa")
    assert m.play_swing("espada_longa")
    assert len([r for r in m._ativos if r.grupo == "swing"]) == 1


def test_configuracao_de_evento_estatico_e_aplicada():
    m = manager()
    m._config["eventos"]["player_hurt"]["volume"] = 0.2
    assert m.play_sfx("player_hurt")
    assert pygame.mixer.Channel(1).get_volume() == pytest.approx(0.8 * 0.9 * 0.2, abs=0.01)


def test_ui_alterna_variacoes_sem_repeticao_imediata(tmp_path):
    arquivos = {
        som_teste(tmp_path, f"sfx/ui/confirmar/confirmar_{n:02}.wav")
        for n in (1, 2)
    }
    m = manager(tmp_path)
    tocados = []
    for _ in range(3):
        assert m.play_sfx("ui_confirm")
        tocados.append(pygame.mixer.Channel(0).get_sound())
        m.stop_all_sfx()
    assert tocados[0] is not tocados[1]
    assert tocados[0] is tocados[2]
    assert arquivos <= {Path(k) for k in m._sons}


def test_ui_variante_valida_substitui_original_ruim_sem_tocar_outra_acao(tmp_path):
    original = som_teste(tmp_path, "sfx/ui/pausa/pausa_abrir_01.wav")
    original.write_bytes(b"audio corrompido")
    valido = som_teste(tmp_path, "sfx/ui/pausa/pausa_abrir_02.wav")
    som_teste(tmp_path, "sfx/ui/pausa/pausa_fechar_01.wav")
    m = manager(tmp_path)
    assert m.play_sfx("ui_pause_open", ajuste=0.5)
    assert pygame.mixer.Channel(0).get_sound() is m._sons[str(valido)]
    assert pygame.mixer.Channel(0).get_volume() == pytest.approx(0.8 * 0.7 * 0.5, abs=0.01)
    m.stop_all_sfx()
    assert m.play_sfx("ui_pause_close")
    assert pygame.mixer.Channel(0).get_sound() is not m._sons[str(valido)]


def test_porta_usa_variante_integrada_e_preserva_acao_fechar(monkeypatch):
    m = manager()
    monkeypatch.setattr(m, "_escolher_arquivo", lambda pasta, arquivos: arquivos[-1])
    assert m.play_sfx("door_open")
    assert m._ativos[-1].chave.endswith("portas_abrir_02.wav")
    assert m.play_sfx("door_close")
    assert m._ativos[-1].chave == "door_close"


def test_loops_nao_reiniciam_e_param_se_destino_ficar_vazio(tmp_path):
    som_teste(tmp_path, "ambiencia/sala/teste.wav")
    som_teste(tmp_path, "sfx/mundo/tochas/teste.wav")
    m = manager(tmp_path)
    assert m.play_ambiente("sala")
    primeiro = m._ativos[-1]
    assert m.play_ambiente("sala")
    assert m._ativos[-1] is primeiro
    assert m.play_tochas()
    assert pygame.mixer.Channel(2).get_busy()
    assert pygame.mixer.Channel(3).get_busy()
    assert not m.play_ambiente("inexistente")
    assert not pygame.mixer.Channel(2).get_busy()
    m.play_tochas(False)
    assert not pygame.mixer.Channel(3).get_busy()


def test_musica_troca_sem_ocupar_canal_da_interface(tmp_path, monkeypatch):
    som_teste(tmp_path, "musica/menu/teste.wav")
    som_teste(tmp_path, "musica/boss/teste.wav")
    m = manager(tmp_path)
    chamadas = []
    play_real = pygame.mixer.music.play
    def play(*args, **kwargs):
        chamadas.append(kwargs)
        return play_real(*args, **kwargs)
    monkeypatch.setattr(pygame.mixer.music, "play", play)
    assert m.play_music("menu")
    assert m.play_music("menu")
    assert len(chamadas) == 1
    assert not pygame.mixer.Channel(0).get_busy()
    assert m.play_music("boss")
    assert len(chamadas) == 2
    assert m._musica_contexto == "boss"
    m.set_master_volume(0.4)
    volume = pygame.mixer.music.get_volume()
    m.set_sfx_volume(0)
    assert pygame.mixer.music.get_volume() == volume
    assert not m.play_music("inexistente")
    assert not pygame.mixer.music.get_busy()


def test_troca_de_sala_encerra_sons_do_mundo_e_preserva_ui():
    m = manager()
    assert m.play_sfx("ui_confirm")
    assert m.play_swing("soco")
    assert m.play_ambiente("arena_boss")
    m.stop_world_sfx()
    assert pygame.mixer.Channel(0).get_busy()
    assert all(r.categoria == "ui" for r in m._ativos)
    assert not pygame.mixer.Channel(2).get_busy()


def test_pausa_nao_continua_atualizacao_do_mundo():
    chamadas = []
    cena = SimpleNamespace(menu_fogueira=SimpleNamespace(aberto=False), pausado=True,
                           _atualizar_pausa=lambda ev: chamadas.append("pausa"))
    Gamescene.atualizar(cena, [])  # sem mapa/player: acessá-los significaria que o mundo avançou
    assert chamadas == ["pausa"]


def test_contexto_musical_da_sala(monkeypatch):
    chamadas = []
    monkeypatch.setattr("core.game_scene.audio", SimpleNamespace(play_music=chamadas.append))
    cena = SimpleNamespace(sala_atual="calabouço_1", boss_atual=None,
                           menu_fogueira=SimpleNamespace(aberto=False))
    Gamescene._atualizar_audio_sala(cena)
    cena.boss_atual = SimpleNamespace(vivo=True)
    Gamescene._atualizar_audio_sala(cena)
    cena.boss_atual.vivo = False
    Gamescene._atualizar_audio_sala(cena)
    cena.menu_fogueira.aberto = True
    Gamescene._atualizar_audio_sala(cena)
    assert chamadas == ["exploracao", "boss", "exploracao", "descanso"]


def test_boss_tmx_dispara_entrada_e_nao_usa_construtor_de_patrulha(monkeypatch):
    from world.tile_map import TileMap

    chamadas = []
    monkeypatch.setattr("core.game_scene.audio", SimpleNamespace(play_enemy_entrada=chamadas.append))
    objeto = dict(tipo="inimigo", id=999, col=10, linha=10,
                  propriedades={"tipo": "esqueleto_boss"})
    carregar = TileMap.carregar_objetos_tmx
    monkeypatch.setattr("core.game_scene.TileMap.carregar_objetos_tmx",
                        lambda *args: [o for o in carregar(*args) if o["tipo"] != "inimigo"] + [objeto])
    cena = Gamescene(pygame.display.get_surface())
    assert cena.boss_atual is not None
    assert chamadas == ["boss_carrasco"]
    cena.bosses_derrotados.add(cena.sala_atual)
    cena._carregar_sala(cena.sala_atual)
    assert cena.boss_atual is None
    assert chamadas == ["boss_carrasco"]


def test_audio_desligado_nao_decodifica_cascata_ou_background(monkeypatch):
    monkeypatch.setenv("PROFANE_AUDIO", "0")
    m = AudioManager()
    assert not m.inicializar()
    monkeypatch.setattr(m, "_carregar_som", lambda _: pytest.fail("não deve carregar"))
    assert not m.play_swing("soco")
    assert not m.play_eco_profano()
    assert not m.play_music("menu")
    assert not m.play_ambiente("arena_boss")
