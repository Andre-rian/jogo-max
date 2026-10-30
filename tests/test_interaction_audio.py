from types import SimpleNamespace

import pygame
import pytest

from core.game_scene import Gamescene
from core.inventario import Inventario
from core.menu_fogueira import MenuFogueira
from entities.objetos import bau as bau_module
from entities.objetos import drop as drop_module
from entities.objetos import drop_eco as drop_eco_module
from entities.objetos import fogueira as fogueira_module
from entities.objetos import porta as porta_module
from entities.objetos.bau import Bau
from entities.objetos.drop import Drop
from entities.objetos.drop_eco import DropEco
from entities.objetos.fogueira import Fogueira
from entities.objetos.item import get_item
from entities.objetos.porta import Porta
from entities.player import Player


class AudioFalso:
    def __init__(self):
        self.chamadas = []

    def play_sfx(self, chave, ajuste=1.0):
        self.chamadas.append(chave)
        return True


class HudFalso:
    def mostrar_prompt(self, texto):
        pass

    def limpar_prompt(self):
        pass

    def mostra_mensagem(self, texto, duracao=180):
        pass

    def mostrar_item_coletado(self, item, quantidade=None):
        pass


@pytest.fixture
def audio_falso(monkeypatch):
    falso = AudioFalso()
    for modulo in (
        bau_module,
        drop_module,
        drop_eco_module,
        fogueira_module,
        porta_module,
    ):
        monkeypatch.setattr(modulo, "audio", falso)
    monkeypatch.setattr("core.inventario.audio", falso)
    monkeypatch.setattr("core.menu_fogueira.audio", falso)
    monkeypatch.setattr("core.game_scene.audio", falso)
    return falso


def jogador_no_rect(rect):
    return SimpleNamespace(
        rect=rect.copy(),
        cooldown_interaçao=0,
        inventory=None,
    )


def test_bau_toca_abertura_e_coleta(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(bau_module, "audio", falso)
    bau = Bau(100, 300, 0, 0, 1)
    player = jogador_no_rect(bau.interacao)
    player.adicionar_ao_inventario = lambda item: None
    hud = HudFalso()

    bau.atualizar(player, {pygame.K_e: True}, SimpleNamespace(remover_tile=lambda c, l: None), hud)
    assert falso.chamadas == ["chest_open"]

    bau._dar_item(player, hud)
    assert falso.chamadas == ["chest_open", "item_pickup"]


def test_drop_toca_coleta_apos_adicionar(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(drop_module, "audio", falso)
    drop = Drop(100, 100, 5)
    player = jogador_no_rect(drop.interacao)
    player.inventario = {"materiais": {}, "itens": {}}
    player.adicionar_ao_inventario = lambda item: None
    player.iniciar_pegar_item = lambda: None

    drop.atualizar(player, {pygame.K_e: True}, HudFalso())

    assert falso.chamadas == ["item_pickup"]
    assert drop.ativo is False


def test_drop_eco_toca_coleta(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(drop_eco_module, "audio", falso)
    drop = DropEco(100, 100, 50)
    player = jogador_no_rect(drop.interacao)
    player.ecos = 0

    drop.atualizar(player, {pygame.K_e: True}, HudFalso())

    assert falso.chamadas == ["eco_pickup"]
    assert player.ecos == 50


def test_fogueira_acende_uma_vez(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(fogueira_module, "audio", falso)
    fogueira = Fogueira(100, 300, 0, 0)
    player = jogador_no_rect(fogueira.interacao)
    player.defenir_checkpoint = lambda *args, **kwargs: None
    ativas = set()
    hud = HudFalso()

    fogueira.atualizar(player, {pygame.K_e: True}, hud, "sala", ativas)
    player.cooldown_interaçao = 0
    fogueira.atualizar(player, {pygame.K_e: True}, hud, "sala", ativas)

    assert falso.chamadas == ["campfire_light"]


def test_porta_toca_abrir_e_fechar(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr(porta_module, "audio", falso)
    porta = Porta(100, 300, 0, 0)
    player = jogador_no_rect(porta.interacao)
    abertas = set()
    hud = HudFalso()

    porta.atualizar(player, {pygame.K_e: True}, hud, abertas)
    player.cooldown_interaçao = 0
    porta.atualizar(player, {pygame.K_e: True}, hud, abertas)

    assert falso.chamadas == ["door_open", "door_close"]


def test_equipar_arma_toca_uma_vez(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr("core.inventario.audio", falso)
    inventario = Inventario(None)
    player = Player(100, 300)
    espada = get_item(1)
    player.inventario["equipamentos"].append(espada.id)

    inventario._tentar_equipar(espada, player)
    inventario._tentar_equipar(espada, player)

    assert falso.chamadas == ["equip_weapon"]
    assert player.inventario["mao_direita"] == espada.id


def test_level_up_valido_toca_som(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr("core.menu_fogueira.audio", falso)
    player = Player(100, 300)
    player.ecos = 100000
    menu = MenuFogueira(None, player, None, None)
    menu.pendente["vigor"] = 1

    menu._confirmar_level_up()
    assert falso.chamadas == ["level_up"]

    menu._confirmar_level_up()
    assert falso.chamadas == ["level_up", "ui_error"]


def test_descansar_fogueira_toca_som():
    falso = AudioFalso()
    cena = SimpleNamespace(
        inimigos_morto_por_sala={"sala": [1]},
        player=SimpleNamespace(
            hp=1,
            hp_max=10,
            pocao=SimpleNamespace(recarregar=lambda: None),
        ),
        sala_atual="sala",
        _spwanar_inimigos=lambda sala: None,
    )
    import core.game_scene as game_scene_module

    original = game_scene_module.audio
    game_scene_module.audio = falso
    try:
        Gamescene._descansar_fogueira(cena)
    finally:
        game_scene_module.audio = original

    assert falso.chamadas == ["campfire_rest"]
