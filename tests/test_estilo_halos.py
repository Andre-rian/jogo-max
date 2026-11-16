import pygame

from settings import Screen_height, Screen_widht
from ui import estilo


def _brilho(tela, x, y):
    return sum(tela.get_at((x, y))[:3])


def test_halo_com_alpha_tem_queda_gradual():
    tela = pygame.Surface((240, 240))
    tela.fill((0, 0, 0))

    estilo.adicionar_brilho(tela, 120, 120, 100, estilo.Roxo_profundo, 0,
                            intensidade=1.0, alpha_real=True)

    valores = [_brilho(tela, 120 + dx, 120) for dx in (0, 30, 60, 85)]

    assert valores == sorted(valores, reverse=True)
    assert valores[0] > valores[-1]
    assert len(set(valores)) >= 3


def test_halo_central_continua_em_y_470(monkeypatch):
    def fundo_preto():
        surf = pygame.Surface((Screen_widht, Screen_height))
        surf.fill((0, 0, 0))
        return surf

    monkeypatch.setattr(estilo, "_construir_fundo", fundo_preto)
    monkeypatch.setattr(estilo, "_desenhar_particulas", lambda *args: None)
    estilo._cache.pop("fundo", None)

    tela = pygame.Surface((Screen_widht, Screen_height))
    estilo.desenhar_fundo(tela, 0)

    centro = _brilho(tela, 640, 470)
    perto = _brilho(tela, 640, 450)
    meio = _brilho(tela, 640, 350)
    borda = _brilho(tela, 640, 300)
    fora = _brilho(tela, 640, 239)

    assert centro > perto > meio > borda
    assert borda > fora
    assert fora == 0

    estilo._cache.pop("fundo", None)
