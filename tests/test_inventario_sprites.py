import os

import pygame
import pytest

from core.inventario import Inventario
from entities.objetos.item import get_item
from entities.objetos.pocao import Pocao
from entities.player import Player
from ui import sprites_itens
from ui.icones import desenhar_icone_item

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PASTA_ITENS = os.path.join(RAIZ, "assets", "sprites", "itens")


class AudioFalso:
    def __init__(self):
        self.chamadas = []

    def play_sfx(self, nome):
        self.chamadas.append(nome)


class ItemSemSprite:
    id = 999
    icone = None


@pytest.fixture(autouse=True)
def cache_limpo():
    sprites_itens.limpar_cache()
    yield
    sprites_itens.limpar_cache()


@pytest.fixture
def audio_falso(monkeypatch):
    falso = AudioFalso()
    monkeypatch.setattr("core.inventario.audio", falso)
    return falso


def tecla(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def test_arquivos_finais_sao_24x24_com_alpha():
    caminhos = [
        os.path.join(PASTA_ITENS, "equipamentos", "espada_longa.png"),
        os.path.join(PASTA_ITENS, "equipamentos", "machado_guerra.png"),
        os.path.join(PASTA_ITENS, "consumiveis", "pocao_vida.png"),
        os.path.join(PASTA_ITENS, "consumiveis", "raiz_amarga.png"),
        os.path.join(PASTA_ITENS, "materiais", "umbrita.png"),
        os.path.join(PASTA_ITENS, "_default", "item_desconhecido.png"),
    ]
    for caminho in caminhos:
        assert os.path.isfile(caminho), caminho
        imagem = pygame.image.load(caminho).convert_alpha()
        assert imagem.get_size() == (24, 24)
        assert pygame.mask.from_surface(imagem).count() > 0


def test_sprites_mapeados_por_id_real_1_a_5():
    for item_id in (1, 2, 3, 4, 5):
        sprite = sprites_itens.obter_sprite_item(item_id)
        assert sprite is not None
        assert sprite.get_size() == (48, 48)


def test_umbrita_id_5_usa_sprite_integrado():
    sprite = sprites_itens.obter_sprite_item(5)
    assert sprite is not None
    assert sprites_itens.obter_sprite_de_item(get_item(5)) is sprite


def test_pocao_sem_id_usa_sprite_do_id_2():
    pocao = Pocao()
    assert sprites_itens.obter_sprite_de_item(pocao) is not None
    assert sprites_itens.obter_sprite_de_item(pocao) is sprites_itens.obter_sprite_item(2)


def test_item_sem_sprite_usa_fallback():
    assert sprites_itens.obter_sprite_item(999) is None
    fallback = sprites_itens.obter_fallback()
    assert fallback is not None
    assert fallback.get_size() == (48, 48)
    assert sprites_itens.obter_sprite_de_item(ItemSemSprite()) is None


def test_desenhar_icone_com_sprite_e_com_fallback():
    fonte = pygame.font.Font(None, 12)
    for item in (get_item(1), get_item(5), ItemSemSprite()):
        tela = pygame.Surface((60, 60), pygame.SRCALPHA)
        desenhar_icone_item(tela, item, 30, 30, 0, 0, 60, fonte)
        assert pygame.mask.from_surface(tela).count() > 0


def test_inventario_vazio_desenha_sem_erro():
    tela = pygame.Surface((1280, 720), pygame.SRCALPHA)
    inventario = Inventario(tela)
    player = Player(100, 300)
    player.pocao = None
    inventario.aberto = True

    for aba in range(len(inventario.abas)):
        inventario.aba_atual = aba
        assert inventario._itens_da_aba(player) == []
        inventario.desenhar(player)


def test_quatro_itens_quantidades_e_abas():
    inventario = Inventario(None)
    player = Player(100, 300)
    player.inventario["mao_direita"] = 1
    player.inventario["equipamentos"] = [3]
    player.inventario["itens"] = {"4": 2}
    player.inventario["materiais"] = {"5": 4}

    inventario.aba_atual = 0
    equipamentos = inventario._itens_da_aba(player)
    assert [item.id for item in equipamentos] == [1, 3]

    inventario.aba_atual = 1
    itens = inventario._itens_da_aba(player)
    assert itens[0] is player.pocao
    raiz = next(item for item in itens if getattr(item, "id", None) == 4)
    assert raiz.quantidade == 2

    inventario.aba_atual = 3
    materiais = inventario._itens_da_aba(player)
    umbrita = next(item for item in materiais if item.id == 5)
    assert umbrita.quantidade == 4


def test_troca_de_aba_e_selecao(audio_falso):
    inventario = Inventario(None)
    player = Player(100, 300)
    player.inventario["equipamentos"] = [1, 3]
    inventario.abrir()
    inventario._ignorar_frame_abertura = False

    inventario.atualizar([tecla(pygame.K_TAB)], player)
    assert inventario.aba_atual == 1
    assert inventario.slot_selecionado == 0

    inventario.aba_atual = 0
    inventario.slot_selecionado = 0
    inventario.atualizar([tecla(pygame.K_RIGHT)], player)
    assert inventario.slot_selecionado == 1


def test_equipar_arma_pelo_inventario(audio_falso):
    inventario = Inventario(None)
    player = Player(100, 300)
    player.inventario["equipamentos"] = [1]

    inventario._tentar_equipar(get_item(1), player)

    assert player.inventario["mao_direita"] == 1
    assert 1 not in player.inventario["equipamentos"]


def test_precarregamento_popula_cache():
    Inventario(None)
    for item_id in (1, 2, 3, 4, 5):
        assert sprites_itens.obter_sprite_item(item_id) is not None
