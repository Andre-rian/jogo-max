# Telas sobrepostas da cena de jogo (morte e pausa).
# Desenho puro: a lógica (estado, navegação, tempo) permanece na cena.

import pygame

from settings import Screen_widht, Screen_height
from ui.estilo import (
    Fonte_titulo, Fonte_texto,
    Roxo_espectral, Roxo_profundo, Vermelho_ritual,
    Branco_texto,
    desenhar_overlay, desenhar_titulo, desenhar_linha_ornamental,
    desenhar_eco_profano, desenhar_botao, adicionar_brilho, escurecer
)


def desenhar_tela_morte(tela, progresso):
    # fade escuro com o texto "você morreu" centralizado

    alpha = int(progresso * 200)  # máximo 200 de 255, pra tela não ficar toda preta

    desenhar_overlay(tela, alpha)

    # o texto só aparece depois do fade estar na metade
    if progresso > 0.4:
        desenhar_titulo(tela, "VOCÊ MORREU",
                        Fonte_titulo(64, negrito=True), Vermelho_ritual,
                        Screen_widht // 2, Screen_height // 2 - 40,
                        espacamento=3)
        desenhar_linha_ornamental(tela, Screen_widht // 2,
                                  Screen_height // 2 + 30, 220,
                                  escurecer(Vermelho_ritual, 0.3))


def desenhar_tela_pausa(tela, frame, opçoes, opçao_selecionada, fonte_opçao=None):
    # fundo semitransparente
    desenhar_overlay(tela, 170)

    if fonte_opçao is None:
        fonte_opçao = Fonte_texto(28)

    adicionar_brilho(tela, Screen_widht // 2, 230, 240, Roxo_profundo,
                     frame, intensidade=0.25)

    # titulo
    desenhar_titulo(tela, "PAUSA", Fonte_titulo(54, negrito=True), Roxo_espectral,
                    Screen_widht // 2, 200, espacamento=4)
    desenhar_linha_ornamental(tela, Screen_widht // 2, 268, 200,
                              Roxo_espectral)
    desenhar_eco_profano(tela, Screen_widht // 2, 268, 10, frame)

    # opções
    for i, opçao in enumerate(opçoes):
        selecionado = i == opçao_selecionada
        texto = fonte_opçao.render(opçao, True, Branco_texto)
        x = Screen_widht // 2 - texto.get_width() // 2
        y = 320 + i * 50
        rect_opçao = pygame.Rect(x - 10, y - 5,
                                 texto.get_width() + 20,
                                 texto.get_height() + 10)
        desenhar_botao(tela, rect_opçao, opçao, selecionado,
                       frame, fonte_btn=fonte_opçao)