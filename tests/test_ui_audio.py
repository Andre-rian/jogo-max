from types import SimpleNamespace

import pygame
import pytest

from core.game_scene import Gamescene
from core.inventario import Inventario
from core.menu import MenuInicial
from core.menu_fogueira import MenuFogueira
from entities.objetos.item import get_item
from entities.player import Player


class AudioFalso:
    def __init__(self):
        self.chamadas = []

    def play_sfx(self, chave, ajuste=1.0):
        self.chamadas.append(chave)
        return True


class HudFalso:
    def mostra_mensagem(self, texto, duracao=180):
        pass


class SaveManagerFalso:
    def __init__(self, slots=None):
        self.slots = slots or {1: None, 2: None, 3: None}
        self.deletados = []

    def listar_slots(self):
        return self.slots

    def deletar(self, slot):
        self.deletados.append(slot)
        self.slots[slot] = None


def tecla(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


@pytest.fixture
def audio_falso(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr("core.menu.audio", falso)
    monkeypatch.setattr("core.inventario.audio", falso)
    monkeypatch.setattr("core.menu_fogueira.audio", falso)
    monkeypatch.setattr("core.game_scene.audio", falso)
    return falso


def test_menu_inicial_navega_confirma_e_volta(audio_falso):
    menu = MenuInicial(None, SaveManagerFalso())
    iniciados = []
    menu.callback_iniciar = lambda slot, dados: iniciados.append(slot)

    menu.atualizar([tecla(pygame.K_UP)])
    assert audio_falso.chamadas == []

    menu.atualizar([tecla(pygame.K_DOWN)])
    assert audio_falso.chamadas == ["ui_move"]

    menu.atualizar([tecla(pygame.K_RETURN)])
    assert audio_falso.chamadas == ["ui_move", "ui_confirm"]
    assert iniciados == [2]

    menu.atualizar([tecla(pygame.K_DELETE)])
    assert audio_falso.chamadas[-1] == "ui_error"


def test_menu_inicial_delete_pede_confirmacao(audio_falso):
    menu = MenuInicial(None, SaveManagerFalso(slots={1: {"hp": 1}, 2: None, 3: None}))

    menu.atualizar([tecla(pygame.K_DELETE)])
    assert audio_falso.chamadas == ["ui_confirm"]
    assert menu.estado == "confirmar_delete"

    menu.atualizar([tecla(pygame.K_ESCAPE)])
    assert audio_falso.chamadas == ["ui_confirm", "ui_back"]
    assert menu.estado == "selecionar"


def test_pausa_abre_fecha_e_navega(audio_falso):
    cena = Gamescene.__new__(Gamescene)
    cena.pausado = False
    cena.opçoes_selecionadas = 2

    Gamescene.alternar_pausa(cena)
    assert cena.pausado is True
    assert cena.opçoes_selecionadas == 0
    assert audio_falso.chamadas == ["ui_pause_open"]

    Gamescene.alternar_pausa(cena)
    assert cena.pausado is False
    assert audio_falso.chamadas == ["ui_pause_open", "ui_pause_close"]


def test_pausa_continuar_e_salvar(audio_falso):
    cena = Gamescene.__new__(Gamescene)
    cena.pausado = True
    cena.opçoes_pause = ["Continuar", "Salvar"]
    cena.opçoes_selecionadas = 0
    cena.inventario = SimpleNamespace(abrir=lambda: None)
    cena._save_callback = None
    cena._menu_callback = None

    cena._confirma_opçao_pausa()
    assert cena.pausado is False
    assert audio_falso.chamadas == ["ui_pause_close"]


def test_salvar_toca_sucesso_e_erro(audio_falso):
    player = Player(100, 300)
    cena = SimpleNamespace(
        inimigos=[],
        player=player,
        hud=HudFalso(),
    )
    save_manager = SimpleNamespace(salvar=lambda slot, cena: None)

    assert Gamescene.salvar(cena, save_manager, 1) is True
    assert audio_falso.chamadas == ["ui_save"]

    cena.inimigos = [
        SimpleNamespace(vivo=True, rect=pygame.Rect(player.rect.centerx + 10, 0, 10, 10))
    ]
    assert Gamescene.salvar(cena, save_manager, 1) is False
    assert audio_falso.chamadas == ["ui_save", "ui_error"]


def test_inventario_abre_fecha_e_navega(audio_falso):
    inventario = Inventario(None)
    player = Player(100, 300)
    player.inventario["equipamentos"].append(get_item(1).id)

    inventario.abrir()
    inventario._ignorar_frame_abertura = False
    assert audio_falso.chamadas == ["ui_inventory_open"]

    inventario.atualizar([tecla(pygame.K_TAB)], player)
    assert audio_falso.chamadas == ["ui_inventory_open", "ui_move"]

    inventario.atualizar([tecla(pygame.K_ESCAPE)], player)
    assert audio_falso.chamadas == [
        "ui_inventory_open",
        "ui_move",
        "ui_inventory_close",
    ]


def test_inventario_contexto_confirma_e_volta(audio_falso):
    inventario = Inventario(None)
    player = Player(100, 300)
    inventario.aberto = True
    inventario._ignorar_frame_abertura = False
    inventario.menu_contexto = {
        "item": get_item(1),
        "x": 0,
        "y": 0,
        "opcoes": ["Desequipar"],
    }

    inventario.atualizar([tecla(pygame.K_RETURN)], player)
    assert audio_falso.chamadas == ["ui_confirm"]
    assert inventario.menu_contexto is None

    inventario.menu_contexto = {
        "item": get_item(1),
        "x": 0,
        "y": 0,
        "opcoes": ["Desequipar"],
    }
    inventario.atualizar([tecla(pygame.K_ESCAPE)], player)
    assert audio_falso.chamadas == ["ui_confirm", "ui_back"]
    assert inventario.menu_contexto is None


def test_inventario_acao_invalida_toca_erro(audio_falso):
    inventario = Inventario(None)
    player = Player(100, 300)

    inventario._executar_opcao("Descartar", get_item(1), player)
    assert audio_falso.chamadas == ["ui_error"]


def test_menu_fogueira_navega_confirma_e_volta(audio_falso):
    player = Player(100, 300)
    menu = MenuFogueira(None, player, None, None)
    menu.abrir()

    menu._input_menu(tecla(pygame.K_DOWN))
    assert audio_falso.chamadas == ["ui_move"]

    menu._input_menu(tecla(pygame.K_RETURN))
    assert audio_falso.chamadas == ["ui_move", "ui_confirm"]
    assert menu.estado == MenuFogueira.LEVEL_UP

    menu._input_level_up(tecla(pygame.K_ESCAPE))
    assert audio_falso.chamadas[-1] == "ui_back"
    assert menu.estado == MenuFogueira.MENU_PRINCIPAL

    menu._input_menu(tecla(pygame.K_ESCAPE))
    assert audio_falso.chamadas[-1] == "ui_back"
    assert menu.aberto is False


def test_level_up_menu_fogueira_toca_som_e_erro(audio_falso):
    player = Player(100, 300)
    player.ecos = 100000
    menu = MenuFogueira(None, player, None, None)

    menu.pendente["vigor"] = 1
    menu._confirmar_level_up()
    assert audio_falso.chamadas == ["level_up"]

    menu._confirmar_level_up()
    assert audio_falso.chamadas == ["level_up", "ui_error"]
