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


def desenhar_tela_pausa(tela, frame, opcoes, opcao_selecionada, fonte_opcao=None):
    # fundo escurecido com vinheta + leve brilho central
    desenhar_overlay(tela, 185)

    if fonte_opcao is None:
        fonte_opcao = Fonte_texto(28)
    fonte_titulo = Fonte_titulo(54, negrito=True)

    # Painel central sutil para leitura
    largura_painel = min(Screen_widht - 120, 560)
    altura_opcao = max(44, fonte_opcao.get_height() + 18)
    espacamento = max(altura_opcao + 8, int(altura_opcao * 1.16))
    altura_painel = min(Screen_height - 120, 170 + len(opcoes) * espacamento)
    painel = pygame.Rect(Screen_widht // 2 - largura_painel // 2,
                         Screen_height // 2 - altura_painel // 2,
                         largura_painel, altura_painel)

    # sem halo grande; apenas realce de borda/painel no desenho abaixo

    # painel
    from ui.estilo import desenhar_painel, Cinza_texto_escuro
    desenhar_painel(tela, painel, frame, cor_borda=Roxo_espectral)

    y_titulo = painel.top + 18
    desenhar_titulo(tela, "PAUSA", fonte_titulo, Roxo_espectral,
                    painel.centerx, y_titulo, espacamento=4)
    y_linha = y_titulo + fonte_titulo.get_height() + 10
    desenhar_linha_ornamental(tela, painel.centerx, y_linha, min(180, painel.width // 3),
                              Roxo_espectral)
    desenhar_eco_profano(tela, painel.centerx, y_linha, 6, frame,
                         alpha_real=True, intensidade_halo=0.0, raio_halo=0)

    y_base = y_linha + 34
    for i, opcao in enumerate(opcoes):
        selecionado = i == opcao_selecionada
        bw = min(painel.width - 80, 360)
        bh = altura_opcao
        bx = painel.centerx - bw // 2
        by = y_base + i * espacamento
        rect_opcao = pygame.Rect(bx, by, bw, bh)
        desenhar_botao(tela, rect_opcao, opcao, selecionado,
                       frame, fonte_btn=fonte_opcao, brilho=False)