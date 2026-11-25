import pygame
import pytest

import ui.moldura_menu_lygame as moldura
from ui.prompts_teclas import obter_tecla


ESTADOS = {
    "vazio": (False, False),
    "ocupado": (False, True),
    "selecionado_vazio": (True, False),
    "selecionado_ocupado": (True, True),
}


@pytest.fixture(autouse=True)
def cache_limpo():
    moldura.limpar_cache()
    yield
    moldura.limpar_cache()


def test_moldura_lygame_disponivel_e_desenha_estados_distintos(tmp_path, monkeypatch):
    # Testa composição/paletas em qualquer clone, sem exigir o pack restrito.
    for nome in ('Frame1Empty.png', 'Frame1.png'):
        origem = pygame.Surface((16, 16), pygame.SRCALPHA)
        if nome == 'Frame1.png':
            origem.fill((32, 32, 35))
        pygame.draw.rect(origem, (200, 187, 162), origem.get_rect(), 5)
        pygame.image.save(origem, tmp_path / nome)
    monkeypatch.setattr(moldura, '_DIR_UI', str(tmp_path))
    assert moldura.disponivel()

    centros = {}
    for nome, (selecionado, ocupado) in ESTADOS.items():
        tela = pygame.Surface((500, 110))
        assert moldura.desenhar_moldura_slot(
            tela, (0, 0, 500, 110), selecionado, ocupado
        )
        centros[nome] = tuple(tela.get_at((250, 55))[:3])

    assert len(set(centros.values())) == len(ESTADOS)


def test_moldura_lygame_retorna_falso_sem_asset(monkeypatch):
    monkeypatch.setattr(moldura, "_obter_estado", lambda estado: None)
    tela = pygame.Surface((500, 110))
    assert not moldura.desenhar_moldura_slot(tela, (0, 0, 500, 110))


def test_prompt_enter_usa_recorte_e_delete_tem_fallback():
    assert obter_tecla("enter").get_size() == (24, 16)
    assert obter_tecla("delete").get_width() > 16
