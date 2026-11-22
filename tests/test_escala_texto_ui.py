import pygame
from ui.estilo import definir_escala_texto, obter_escala_texto, versao_escala_texto, Fonte_texto
from ui.hud.hud import Hud
from entities.player import Player


def test_escala_texto_global_muda_fonte_e_versao():
    definir_escala_texto(1.0)
    v1 = versao_escala_texto()
    h1 = Fonte_texto(20).get_height()
    definir_escala_texto(1.5)
    v2 = versao_escala_texto()
    h2 = Fonte_texto(20).get_height()
    assert obter_escala_texto() == 1.5
    assert v2 > v1
    assert h2 > h1
    definir_escala_texto(1.0)


def test_hud_recria_fontes_ao_mudar_escala():
    definir_escala_texto(1.0)
    hud = Hud()
    h1 = hud.fonte_pequena.get_height()
    definir_escala_texto(1.5)
    player = Player(100, 300)
    tela = pygame.display.get_surface() or pygame.display.set_mode((1280, 720))
    hud.desenhar(tela, player)
    h2 = hud.fonte_pequena.get_height()
    assert h2 > h1
    definir_escala_texto(1.0)
