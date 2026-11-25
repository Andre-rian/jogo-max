"""Dano inicial/progressão e composição visual local, sem saves pessoais."""
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import patch

import pygame
import pytest

from core.game_scene import Gamescene
from entities.objetos.fogueira import Fogueira
from entities.objetos.item import get_item
from save_manager import Savemaneger
from scripts.validar_dano_ecofoco import jogador, medir_danos, medir_impacto
from world.niveis import SALAS_BETA


@pytest.fixture
def cena():
    return jogador(pygame.Surface((1280, 720)))


def test_dano_real_nivel_dez_sem_bonus_duplicado_em_todos_os_alvos(cena):
    r = medir_danos(cena.tela)
    for tipo in ("skeleton", "globin", "mushroom", "flying_eye", "boss_carrasco"):
        assert r["alvos"][tipo]["normal"] == 25
    assert r["alvos"]["combo_chefe"] == [40, 40]
    assert r["hp_max_jogador"] == 200


@pytest.mark.parametrize("forca,destreza,dano", [(10, 10, 25), (15, 10, 27), (10, 15, 27), (15, 15, 29), (20, 20, 33)])
def test_progressao_altera_dano_aplicado_ao_chefe(cena, forca, destreza, dano):
    cena.player.forca, cena.player.destreza = forca, destreza
    cena._carregar_sala(SALAS_BETA[3])
    assert medir_impacto(cena, cena.boss_atual) == [dano]
    assert cena.player.hp_max == 200


@pytest.mark.parametrize("atributo", ["forca", "destreza"])
def test_progressao_nao_regride_e_preserva_incrementos_do_escalonamento(cena, atributo):
    p = cena.player
    danos = []
    for valor in range(10, 51):
        setattr(p, atributo, valor)
        danos.append(p.calcular_dano("normal"))
    assert danos == sorted(danos)
    assert danos[-1] - danos[0] == 16  # 40 pontos no escalonamento C


def test_dano_base_da_arma_continua_sendo_respeitado(cena):
    arma = get_item(1)
    arma.dano += 10  # contrato de entrada: simula melhoria, sem criar sistema de upgrades
    with patch("entities.player.get_item", return_value=arma):
        assert cena.player.calcular_dano("normal") == 35
        assert cena.player.calcular_dano("combo") == 56
    assert get_item(1).dano == 25


def test_nivel_isolado_nao_da_bonus_e_requisitos_soco_e_pesado_preservados(cena):
    p = cena.player
    for nivel in (1, 10, 20):
        p.nivel = nivel
        assert p.calcular_dano("normal") == p.calcular_dano("pesado") == 25
    p.destreza = 9
    assert p.calcular_dano("normal") == 10  # penalidade existente por requisitos
    p.inventario["mao_direita"] = None
    assert p.calcular_dano("normal") == 5


@pytest.mark.parametrize("frames,esperado", [(1, 25), (17, 40)])
def test_toque_curto_e_ataque_segurado_usam_danos_distintos(cena, frames, esperado):
    p = cena.player
    for _ in range(frames):
        p._atacar(defaultdict(bool, {pygame.K_k: True}))
    p._atacar(defaultdict(bool))
    assert p.ataque_ativo.dano_base == esperado


def test_ecofoco_interacao_descanso_evolucao_e_persistencia(cena, tmp_path, monkeypatch):
    cena._carregar_sala(SALAS_BETA[2])
    cena.inimigos.clear()
    p = cena.player
    foco = cena.fogueiras[0]
    p.rect.midbottom = foco.rect.midbottom
    p.vel.xy = (0, 0)
    p.ecos = 100000
    p.pocao.obter_frasco()
    p.pocao.cargas = 0
    p.hp = 50
    with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {pygame.K_e: True})):
        cena.atualizar([])
    assert foco.ativa and cena.menu_fogueira.aberto
    checkpoint = (p.checkpoint_sala, tuple(p.checkpoint_pos))

    def tecla(key):
        with patch("pygame.key.get_pressed", return_value=defaultdict(bool)):
            cena.atualizar([pygame.event.Event(pygame.KEYDOWN, key=key)])

    tecla(pygame.K_DOWN)
    tecla(pygame.K_RETURN)
    tecla(pygame.K_DOWN)
    tecla(pygame.K_DOWN)  # Força
    for _ in range(5):
        tecla(pygame.K_RIGHT)
    tecla(pygame.K_DOWN)  # Destreza
    for _ in range(5):
        tecla(pygame.K_RIGHT)
    tecla(pygame.K_RETURN)
    assert (p.nivel, p.forca, p.destreza) == (20, 15, 15)
    assert p.calcular_dano("normal") == 29 and p.hp_max == 200
    tecla(pygame.K_ESCAPE)
    tecla(pygame.K_UP)
    tecla(pygame.K_RETURN)
    assert not cena.menu_fogueira.aberto
    assert p.pocao.cargas == 1 and p.hp == 200
    assert (p.checkpoint_sala, tuple(p.checkpoint_pos)) == checkpoint
    monkeypatch.setattr("save_manager.CAMINHO_DB", str(tmp_path / "ecofoco.db"))
    db = Savemaneger()
    try:
        assert db.salvar(1, cena)
        nova = Gamescene(cena.tela)
        nova.carregar_save(db.carregar(1))
        assert nova.fogueiras[0].ativa
        assert nova.player.calcular_dano("normal") == 29
        assert (nova.player.checkpoint_sala, tuple(nova.player.checkpoint_pos)) == checkpoint
    finally:
        db.fechar()


@pytest.mark.parametrize("ativa", [False, True])
def test_luz_nao_apaga_textura_nem_forma_disco_opaco(ativa):
    foco = Fogueira(100, 100, 3, 3)
    foco.ativa = ativa
    foco._frame = 120
    camera = SimpleNamespace(aplicar=lambda r: r.copy())
    a, b = pygame.Surface((250, 200)), pygame.Surface((250, 200))
    a.fill((40, 60, 80))
    b.fill((140, 160, 180))
    foco.desenhar(a, camera)
    foco.desenhar(b, camera)
    # Fora da chama e do suporte, o fundo mantém contraste e recebe luz sutil.
    for x in (98, 100, 132, 134):
        for y in (96, 100, 104, 108, 112):
            escuro, claro = a.get_at((x, y)), b.get_at((x, y))
            assert min(claro[i] - escuro[i] for i in range(3)) >= 85
            assert max(abs(escuro[i] - (40, 60, 80)[i]) for i in range(3)) <= 15


def test_mascara_suave_zerada_na_borda_e_cache_sem_crescimento_por_frame():
    luz = Fogueira._obter_luz(44, 60, 26)
    assert max(luz.get_at((x, 0)).a for x in range(44)) == 0
    assert max(luz.get_at((0, y)).a for y in range(60)) == 0
    assert max(luz.get_at((x, y)).a for y in range(60) for x in range(44)) <= 26
    assert 20 <= luz.get_at((22, 30)).a <= 26
    assert luz.get_at((12, 30)).a < luz.get_at((22, 30)).a
    foco = Fogueira(100, 100, 3, 3)
    camera = SimpleNamespace(aplicar=lambda r: r.copy())
    tela = pygame.Surface((250, 200))
    for ativa in (False, True):
        foco.ativa = ativa
        foco.desenhar(tela, camera)
    cache = dict(Fogueira._cache_luz_suave)
    particula = foco._sprite_particula
    for frame in range(180):
        foco._frame = frame
        foco.desenhar(tela, camera)
    assert cache == Fogueira._cache_luz_suave
    assert foco._sprite_particula is particula


def test_pulso_lento_estados_distintos_e_render_sem_avancar_animacao():
    foco = Fogueira(100, 100, 3, 3)
    camera = SimpleNamespace(aplicar=lambda r: r.copy())

    def render(frame, ativa):
        foco._frame, foco.ativa = frame, ativa
        tela = pygame.Surface((250, 200))
        tela.fill((20, 20, 20))
        foco.desenhar(tela, camera)
        return pygame.image.tobytes(tela, "RGB")

    assert render(45, True) == render(45, True)
    assert render(45, True) != render(135, True)
    assert render(45, True) != render(45, False)
