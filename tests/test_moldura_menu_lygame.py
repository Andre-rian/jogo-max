import pygame

import ui.moldura_menu_lygame as moldura
from ui.prompts_teclas import obter_tecla


ESTADOS = {
    "vazio": (False, False),
    "ocupado": (False, True),
    "selecionado_vazio": (True, False),
    "selecionado_ocupado": (True, True),
}


def test_moldura_lygame_disponivel_e_desenha_estados_distintos():
    moldura.limpar_cache()
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
