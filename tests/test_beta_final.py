"""Contratos da campanha integrada, persistência e regressões de demonstração."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import Mock, patch
import json
import sqlite3

import pygame
import pytest

from core.game_scene import Gamescene
from entities.objetos.item import get_item
from save_manager import Savemaneger
from scripts.validar_beta_final import PartidaBeta
from world.niveis import SALAS_BETA
from world.validacao_tiled import validar_mapa_tmx, validar_conexoes


@pytest.fixture
def cena():
    return Gamescene(pygame.Surface((1280, 720)))


def passo(cena, *keys, eventos=()):
    with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {k: True for k in keys})):
        cena.atualizar(list(eventos))


def test_partida_completa_teclado_fisica_ia_combate_e_save_temporario():
    resultado = PartidaBeta(pygame.Surface((1280, 720))).executar()
    assert resultado["inimigos_derrotados"] == [
        "Skeleton", "Globin", "Globin", "Skeleton", "Mushroom", "FlyingEye", "EsqueletoBoss"]
    assert resultado["marcos"][-1]["nome"] == "05_fim_beta"


@pytest.mark.parametrize("sala", SALAS_BETA)
@pytest.mark.parametrize("lado", [None, "esquerda", "direita"])
def test_tmx_spawns_e_camera_sem_intersecoes(cena, sala, lado):
    assert not validar_mapa_tmx(f"assets/maps/{sala}.tmx")
    assert not validar_conexoes()
    cena._entrada_lado = lado
    cena._carregar_sala(sala)
    assert cena.player.rect.collidelist(cena.mapa.rects_solidos) == -1
    for inimigo in cena.inimigos:
        assert inimigo.rect.collidelist(cena.mapa.rects_solidos) == -1
    for zoom in (1.0, 1.35, 1.8):
        cena.camera.zoom = cena.camera.zoom_alvo = zoom
        for _ in range(80):
            cena.camera.atualizar(cena.player.rect)
        assert 0 <= cena.camera.offset.x <= max(0, cena.largura_mapa - 1280 / zoom)
        assert 0 <= cena.camera.offset.y <= max(0, cena.altura_mapa - 720 / zoom)
        cena.desenhar()


@pytest.mark.parametrize("sala,col,topo", [
    ("antigo_arsenal_guardas", 38, 15),
    ("corredores_profundos", 23, 14), ("corredores_profundos", 62, 13),
])
def test_escadas_novas_sobem_descem_e_abandonam_animacao(cena, sala, col, topo):
    cena._carregar_sala(sala)
    # Posicionamento da fixture isola cada escada; física e inputs permanecem reais.
    cena.inimigos.clear()
    p = cena.player
    p.rect.midbottom = (col * 32 + 16, 640)
    frames = set()
    for _ in range(85):
        passo(cena, pygame.K_w)
        if p._escalando:
            assert p.estado == p.Escalando and p.anim_atual is p.animacoes[p.Escalando]
            assert p.rect.centerx == col * 32 + 16
            frames.add(p.anim_atual.frame_index)
    assert len(frames) > 1 and p.rect.bottom <= topo * 32
    for _ in range(85):
        passo(cena, pygame.K_s)
    for _ in range(15):
        passo(cena, pygame.K_d)
    assert p.rect.bottom == 640 and not p._escalando
    assert p.anim_atual is not p.animacoes[p.Escalando]


def test_espada_requisitos_e_recuperacao_sem_equipamentos_duplicados(cena):
    cena._carregar_sala(SALAS_BETA[1])
    espada = get_item(1)
    assert espada.pode_equipar(cena.player)
    bau = next(b for b in cena.baus if b.id_item == 1)
    bau._dar_item(cena.player, cena.hud)
    assert cena.player.arma_id == "espada_longa"
    assert cena.player.calcular_dano("normal") >= espada.dano
    cena.player.adicionar_ao_inventario(espada)
    assert cena.player.inventario["equipamentos"].count(1) == 0
    cena._carregar_sala(SALAS_BETA[1])
    assert not any(b.id_item == 1 for b in cena.baus)
    cena.inventario._executar_opcao("Desequipar", espada, cena.player)
    cena.inventario._executar_opcao("Descartar", espada, cena.player)
    assert sum(d.id_item == 1 and d.ativo for d in cena.drops) == 1
    # Se um save antigo não possuir a arma nem o drop, o baú volta a oferecê-la.
    cena.drops_por_sala.clear()
    cena._carregar_sala(SALAS_BETA[1])
    assert sum(b.id_item == 1 for b in cena.baus) == 1


def test_consumiveis_curam_consumem_chave_string_e_descarte_remove_uma_unidade(cena):
    p = cena.player
    for _ in range(2):
        p.adicionar_ao_inventario(get_item(2))
    p.hp = 50
    assert get_item(2).usar(p, p.inventario)
    assert p.hp == 130 and p.inventario["itens"]["2"] == 1
    p.adicionar_ao_inventario(get_item(4))
    p.adicionar_ao_inventario(get_item(4))
    cena.inventario._executar_opcao("Descartar", get_item(4), p)
    assert p.inventario["itens"]["4"] == 1
    assert len(cena.drops) == 1
    assert get_item(4).usar(p, p.inventario)
    assert "4" not in p.inventario["itens"] and p.buff_stamina_duracao > 0
    p.hp = 20
    for _ in range(3):
        p.pocao.obter_frasco()
    cena.inventario._executar_opcao("Usar", p.pocao, p)
    assert p.hp == 100 and p.pocao.cargas == 2
    assert not cena.inventario._opcao_contexto_valida("Descartar", p.pocao, p)
    cena.inventario._executar_opcao("Descartar", p.pocao, p)
    assert p.pocao.cargas == 2


def test_baus_e_ecofocos_nao_compartilham_coordenadas_entre_salas(cena):
    cena.baus_abertos = {("antigo_arsenal_guardas", 27, 13), (27, 13)}
    cena.fogueiras_ativas = {("antigo_arsenal_guardas", 105, 19), (105, 19)}
    cena._carregar_sala("corredores_profundos")
    assert any(b.col == 27 for b in cena.baus)
    assert not cena.fogueiras[0].ativa
    cena._registrar_bau_aberto(27, 13)
    cena._carregar_sala("corredores_profundos")
    assert not cena.baus


def test_salvar_load_preserva_atributos_checkpoint_drops_e_consumidos(cena, tmp_path, monkeypatch):
    monkeypatch.setattr("save_manager.CAMINHO_DB", str(tmp_path / "save.db"))
    db = Savemaneger()
    try:
        cena._carregar_sala("corredores_profundos")
        cena.player.rect.topleft = (3359, 576)
        cena.player.defenir_checkpoint("corredores_profundos")
        cena.player.vigor += 2
        cena.player.hp_max += 30
        cena.player.nivel += 2
        cena.player.pocao.obter_frasco()
        cena._descartar_item(4)
        drop = cena.drops[0]
        assert cena.salvar(db, 1)
        nova = Gamescene(cena.tela)
        nova.carregar_save(db.carregar(1))
        assert nova.player.vigor == cena.player.vigor
        assert nova.player.nivel == cena.player.nivel
        assert nova.player.pocao.cargas == 1
        assert nova.player.pocao.cargas_max == 1
        assert nova.player.hp_max == cena.player.hp_max
        assert sum(d.id_item == 4 for d in nova.drops) == 2  # fixo + descarte
        assert len(nova.drops) == len(cena.drops)
        assert nova.player.checkpoint_pos == cena.player.checkpoint_pos
        assert nova.drops[0].rect == drop.rect
    finally:
        db.fechar()


def test_schema_antigo_migra_sem_perder_slot_ou_mudar_campanha(cena, tmp_path, monkeypatch):
    caminho = tmp_path / "legado.db"
    db = sqlite3.connect(caminho)
    db.execute("CREATE TABLE saves (slot INTEGER PRIMARY KEY, checkpoint_sala TEXT, checkpoint_x INTEGER, checkpoint_y INTEGER, fogueiras_ativas TEXT, bosses_derrotados TEXT, inventario TEXT, drops_fixos_coletados TEXT, baus_abertos TEXT, ecos INTEGER, drop_eco TEXT, data_hora TEXT)")
    db.execute("INSERT INTO saves VALUES (1, 'calabouço_4', 64, 320, '[]', '[]', ?, '[]', '[]', 123, 'null', '24/11/2026')",
               (json.dumps(cena.player.inventario),))
    db.commit()
    db.close()
    monkeypatch.setattr("save_manager.CAMINHO_DB", str(caminho))
    manager = Savemaneger()
    try:
        dados = manager.carregar(1)
        assert dados["ecos"] == 123 and dados["estado_jogador"] == {}
        cena.carregar_save(dados)
        assert cena.sala_atual == "calabouço_4" and cena.player.ecos == 123
        assert cena._contexto_musical_sala()[0] == "descanso"
        assert cena.player.destreza == cena.player.DESTREZA_INICIAL
    finally:
        manager.fechar()


def test_musica_so_no_encontro_e_fim_congela_combate(cena):
    cena._carregar_sala("arena_chefe")
    assert cena._contexto_musical_sala()[0] is None
    boss = cena.boss_atual
    cena.player.rect.x = boss.rect.x - 180
    with patch("core.game_scene.audio.play_music") as music:
        cena._atualizar_estado_batalha_chefe()
        assert cena._contexto_musical_sala()[0] == "boss"
        assert any(c.args[0] == "boss" for c in music.call_args_list)
    assert cena.parede_boss
    with patch("core.game_scene.audio.stop_music") as stop:
        # Fixture de derrota; o teste de percurso aplica dano real com a espada.
        boss.receber_dano(boss.hp)
        assert stop.called
    with patch.object(cena.combate, "resolver") as combater:
        for _ in range(125):
            passo(cena, pygame.K_k)
        assert cena.fim_beta is not None
        assert not cena.projeteis and not cena.parede_boss
        combater.assert_not_called()
    cena._menu_callback = Mock()
    passo(cena, eventos=[pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=cena.fim_beta.botao.center)])
    cena._menu_callback.assert_called_once()


def test_inventario_pausa_mundo_e_f6_normal_nao_entra_na_arena_teste(cena):
    passo(cena, eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F6)])
    assert not cena.modo_teste_combate and cena.sala_atual == SALAS_BETA[0]
    passo(cena, eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)])
    rect = cena.player.rect.copy()
    for _ in range(30):
        passo(cena, pygame.K_d)
    assert cena.inventario.aberto and cena.player.rect == rect


@pytest.mark.parametrize("origem", [1, 2, 3])
def test_transicao_retorna_por_spawn_correto_antes_do_encontro(cena, origem):
    cena._carregar_sala(SALAS_BETA[origem])
    cena._cooldown_transiçao = 0
    portal = next(rect for rect, lado in cena.passagens if lado == "esquerda")
    cena.player.rect.center = portal.center
    cena.player.vel.x = -3
    cena._checar_transiçao()
    assert cena.sala_atual == SALAS_BETA[origem - 1]
    assert cena.player.rect.collidelist(cena.mapa.rects_solidos) == -1
    assert cena.player.rect.x >= cena.largura_mapa - 288


def test_salvar_falha_nao_mostra_sucesso(cena):
    manager = Mock()
    manager.salvar.return_value = False
    with patch("core.game_scene.audio.play_sfx") as som:
        assert cena.salvar(manager, 1) is False
        assert not any(c.args == ("ui_save",) for c in som.call_args_list)


@pytest.mark.parametrize("olhando_dir", [True, False])
def test_escudo_direcional_preservado_na_arena(cena, olhando_dir):
    cena._carregar_sala("arena_chefe")
    boss = cena.boss_atual
    boss.olhando_dir = olhando_dir
    boss._escudo_ativo = True
    frente = -1 if olhando_dir else 1
    assert not boss.receber_hit(10, frente)
    assert boss.receber_hit(10, -frente)
    assert boss.hp == boss.hp_max - 10


def test_novo_jogo_e_retorno_real_ao_menu_principal(monkeypatch):
    monkeypatch.setenv("PROFANE_VENV_ATIVO", "1")
    monkeypatch.setattr("logging_config.configurar_logging", lambda: None)
    from main import Jogo
    jogo = Jogo.__new__(Jogo)
    jogo.tela = pygame.Surface((1280, 720))
    jogo.teste_celas = jogo.modo_teste_combate = False
    jogo.menu = Mock()
    jogo.save_manager = Mock()
    jogo._iniciar_jogo(None, None)
    assert jogo.estado == "jogo" and jogo.scene.sala_atual == SALAS_BETA[0]
    jogo.scene._carregar_sala("arena_chefe")
    boss = jogo.scene.boss_atual
    boss.receber_dano(boss.hp)
    for _ in range(125):
        passo(jogo.scene)
    assert jogo.scene.fim_beta is not None
    passo(jogo.scene, eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    assert jogo.estado == "menu" and jogo.scene is None and jogo.slot_atual is None
    assert jogo.menu.tela_menu == "principal"
