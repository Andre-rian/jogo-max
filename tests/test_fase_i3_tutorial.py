"""Tutorial observa a fisica real e compartilha o renderer de interacao G.1."""
from collections import defaultdict
from unittest.mock import Mock, patch

import pygame
import pytest

from core.game_scene import Gamescene
from scripts.validar_bloco_celas import Percurso
from ui.prompts_teclas import PromptTeclaMundo, obter_tecla_mundo, limpar_cache


@pytest.fixture
def cena():
    return Gamescene(pygame.Surface((1280, 720)), sala_teste="bloco_celas_esquecidas")


def passo(cena, *keys, eventos=()):
    with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {k: True for k in keys})):
        cena.atualizar(eventos)


def test_spawn_entrada_real_sem_pulso_falso_e_fade(cena):
    p = Percurso(cena)
    p.repousar(180)
    t = cena.tutorial_contextual
    assert t.teclas_ativas == ("a", "d") and t.opacidade == 255
    assert all(t.prompts[k].estado == "normal" for k in t.teclas_ativas)
    identidades = {k: id(v) for k, v in t.prompts.items()}
    p.passo(pygame.K_d)
    assert t.prompts["d"].estado == "pressionado" and t.prompts["a"].estado == "normal"
    p.passo()
    assert t.prompts["d"].estado == "normal"
    p.repousar(cena.player.Double_tap + 1)
    # Caminhar apenas para a direita basta; nao exige voltar ou completar uma ordem.
    for _ in range(24):
        p.passo(pygame.K_d)
    assert "movimento" in t.concluidas
    assert 0 < t.opacidade < 255
    p.repousar(15)
    assert t.ativa is None and t.opacidade == 0
    assert identidades == {k: id(v) for k, v in t.prompts.items()}


def test_keydown_e_andar_contra_parede_nao_concluem(cena):
    p = Percurso(cena)
    p.repousar()
    passo(cena, eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)])
    assert "movimento" not in cena.tutorial_contextual.concluidas
    # Preparacao de teste junto a parede real; nao e uma captura de percurso.
    cena.player.rect.x = 64
    cena.tutorial_contextual.ocultar(cena.player)
    for _ in range(40):
        p.passo(pygame.K_a)
    assert cena.player.rect.x == 64
    assert "movimento" not in cena.tutorial_contextual.concluidas


def test_escada_s_no_topo_w_na_base_e_conclusao_por_deslocamento(cena):
    p = Percurso(cena)
    p.repousar()
    p.andar(19 * 32)
    p.repousar(12)
    assert cena.tutorial_contextual.teclas_ativas == ("s",)
    # A queda livre nao conta como uso de escada.
    p.andar(21 * 32 + 16)
    p.repousar(100)
    t = cena.tutorial_contextual
    assert "escada" not in t.concluidas and t.teclas_ativas == ("w",)
    for _ in range(5):
        p.passo(pygame.K_s)  # piso bloqueia a descida
    assert "escada" not in t.concluidas
    for _ in range(9):
        p.passo(pygame.K_w)
    assert "escada" in t.concluidas


def test_salto_fora_do_contexto_nao_ensina_pulo(cena):
    p = Percurso(cena)
    p.repousar()
    p.passo(pygame.K_SPACE)
    assert cena.player.vel.y < 0
    assert cena.tutorial_contextual.ativa != "pulo"
    p.repousar(70)
    assert "pulo" not in cena.tutorial_contextual.concluidas


def test_degrau_real_espaco_sem_stamina_nao_conclui_e_travessia_conclui(cena):
    p = Percurso(cena)
    p.repousar()
    p.andar(21 * 32 + 16)
    p.repousar(100)
    p.andar(1000)
    p.repousar(12)
    t = cena.tutorial_contextual
    assert t.ativa == "pulo" and t.teclas_ativas == ("espaco",)
    cena.player.stamina = 0
    p.passo(pygame.K_SPACE)
    assert cena.player.no_chao and "pulo" not in t.concluidas
    assert t.prompts["espaco"].estado == "pressionado"
    p.passo()
    cena.player.stamina = cena.player.stamina_max
    p.andar(40 * 32)
    p.repousar(15)
    assert "pulo" in t.concluidas and t.ativa is None


@pytest.mark.parametrize("contexto", ["pausa", "inventario", "fogueira", "morte"])
def test_suprime_estado_e_desenho_sem_conclusoes_ocultas(cena, contexto):
    Percurso(cena).repousar(12)
    t = cena.tutorial_contextual
    if contexto == "pausa":
        cena.pausado = True
    elif contexto == "inventario":
        cena.inventario.aberto = True
    elif contexto == "fogueira":
        cena.menu_fogueira.aberto = True
    else:
        cena.player.vivo = False
    passo(cena)
    assert t.ativa is None and not t.teclas_ativas and t.opacidade == 0
    assert not t.concluidas
    with patch.object(t, "desenhar") as desenho:
        cena.desenhar()
        desenho.assert_not_called()


def test_interacao_real_tem_prioridade_e_retoma_tutorial(cena):
    # Instancia do objeto real somente na fixture; nenhum objeto e adicionado ao mapa.
    from entities.objetos.bau import Bau
    p = Percurso(cena)
    p.repousar(12)
    bau = Bau(cena.player.rect.x, cena.player.rect.y + 22, 11, 10)
    cena.baus.append(bau)
    p.passo()
    assert cena._alvo_interacao_atual is bau
    assert cena.tutorial_contextual.ativa is None
    with patch.object(cena.prompt_interacao_mundo, "desenhar") as e, patch.object(cena.tutorial_contextual, "desenhar") as tutorial:
        cena.desenhar()
        e.assert_called_once()
        tutorial.assert_not_called()
    cena.baus.clear()
    p.passo()
    assert cena.tutorial_contextual.teclas_ativas == ("a", "d")


def test_troca_sala_limpa_e_nova_sessao_restaura(cena):
    cena.tutorial_contextual.concluir("movimento")
    cena._carregar_sala("calabouço_1")
    assert cena.tutorial_contextual is None
    cena._carregar_sala("bloco_celas_esquecidas")
    assert not cena.tutorial_contextual.concluidas
    nova = Gamescene(pygame.Surface((1280, 720)), sala_teste="bloco_celas_esquecidas")
    passo(nova)
    assert nova.tutorial_contextual.teclas_ativas == ("a", "d")
    saves = Mock()
    assert nova.salvar(saves, 1) is False
    saves.salvar.assert_not_called()


def test_percurso_independente_do_controlador(cena):
    cena.tutorial_contextual = None
    resultado = Percurso(cena).executar()
    assert resultado["frames"] == 3290 and len(resultado["marcos"]) == 8


@pytest.mark.parametrize("zoom", [1.0, 1.35, 1.8])
def test_mesmo_renderer_posiciona_grupo_acima_do_player(cena, zoom):
    p = Percurso(cena)
    p.repousar(12)
    camera = cena.camera
    camera.zoom = zoom
    camera.offset.xy = (80, 40)
    vista = pygame.Surface((round(1280 / zoom), round(720 / zoom)), pygame.SRCALPHA)
    assert cena.tutorial_contextual.desenhar(vista, camera, cena.player)
    r = vista.get_bounding_rect()
    assert r.width == 35 and r.height <= 16
    assert abs(r.centerx - (cena.player.rect.centerx - 80)) <= 1
    assert r.bottom <= cena.player.rect.top - 40
    assert all(isinstance(p, PromptTeclaMundo) for p in cena.tutorial_contextual.prompts.values())


def test_extensao_ataque_e_explicita_e_sem_sons(cena):
    p = Percurso(cena)
    with patch("core.game_scene.audio.play_sfx") as som:
        p.repousar(180)
        assert "k" not in cena.tutorial_contextual.teclas_ativas
        t = cena.tutorial_contextual
        t.solicitar("ataque", ("k",))
        passo(cena)
        assert t.teclas_ativas == ("k",)
        t.concluir("ataque")
        passo(cena)
        assert "k" not in t.teclas_ativas
        som.assert_not_called()


@pytest.mark.parametrize("nome", ["a", "d", "w", "s", "e", "k", "espaco"])
def test_sprites_normais_e_pressionados_distintos_sem_fallback(nome):
    limpar_cache()
    with patch("ui.prompts_teclas._criar_fallback", side_effect=AssertionError("recorte invalido")):
        normal = obter_tecla_mundo(nome)
        press = obter_tecla_mundo(nome, "pressionado")
        assert normal.get_size() == press.get_size() == ((48, 16) if nome == "espaco" else (16, 16))
        assert pygame.image.tobytes(normal, "RGBA") != pygame.image.tobytes(press, "RGBA")
