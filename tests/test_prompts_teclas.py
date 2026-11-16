import pygame

from ui.estilo import Branco_texto, Fonte_texto
from ui.prompts_teclas import criar_prompt, obter_tecla


def test_escalas_de_prompt_arredondam_dimensoes():
    assert obter_tecla("enter").get_size() == (24, 16)
    assert obter_tecla("enter", 1.25).get_size() == (30, 20)
    assert obter_tecla("enter", 1.5).get_size() == (36, 24)


def test_escala_usa_nearest_neighbor_sem_cores_novas():
    base = obter_tecla("seta_cima")
    escalada = obter_tecla("seta_cima", 1.5)

    cores_base = {
        tuple(base.get_at((x, y)))
        for y in range(base.get_height())
        for x in range(base.get_width())
    }
    cores_escalada = {
        tuple(escalada.get_at((x, y)))
        for y in range(escalada.get_height())
        for x in range(escalada.get_width())
    }
    assert cores_escalada <= cores_base


def test_padding_e_fundo_aumentam_area_do_prompt():
    fonte = Fonte_texto(18)
    simples = criar_prompt(["enter"], "confirmar", fonte, Branco_texto)
    ajustado = criar_prompt(
        ["enter"], "confirmar", fonte, Branco_texto,
        escala=1.25,
        padding=(5, 3),
        cor_fundo=(10, 10, 14, 80),
        espaco_texto=9,
    )
    assert ajustado.get_width() > simples.get_width()
    assert ajustado.get_height() > simples.get_height()
    assert ajustado.get_at((5, 5)).a > 0


def test_desenhar_prompts_aceita_escala_e_padding():
    tela = pygame.Surface((1280, 720), pygame.SRCALPHA)
    fonte = Fonte_texto(18)
    from ui.prompts_teclas import desenhar_prompts

    desenhar_prompts(
        tela,
        [(["seta_cima", "seta_baixo"], "navegar"), (["enter"], "selecionar")],
        640,
        670,
        fonte,
        Branco_texto,
        escala=1.5,
        padding=(5, 3),
        cor_fundo=(10, 10, 14, 80),
    )
