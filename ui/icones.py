# Ícones dos itens desenhados no inventário (desenho puro).

import pygame

from ui.estilo import Roxo_espectral, Azul_espectral, Azul_claro, Branco_texto


def desenhar_icone_item(tela, item, cx, cy, sx, sy, slot_size, fonte_pequena):
    if item.icone == "espada":
        # lamina longa apontando para baixo
        pygame.draw.polygon(tela, (170, 176, 200), [
            (cx,      cy + 22),  # ponta
            (cx - 3,  cy - 4),   # base esquerda
            (cx + 3,  cy - 4),   # base direita
        ])
        # detalhe central da lamina
        pygame.draw.line(tela, (120, 130, 165),
                         (cx, cy + 22), (cx, cy - 4), 1)
        # guarda longa
        pygame.draw.line(tela, Roxo_espectral,
                         (cx - 12, cy - 5), (cx + 12, cy - 5), 3)
        # ponta da guarda esquerda
        pygame.draw.circle(tela, Azul_claro,
                           (cx - 12, cy - 5), 2)
        # ponta da guarda direita
        pygame.draw.circle(tela, Azul_claro,
                           (cx + 12, cy - 5), 2)
        # cabo
        pygame.draw.line(tela, (120, 90, 60),
                         (cx, cy - 5), (cx, cy - 16), 4)
        # punho redondo
        pygame.draw.circle(tela, (100, 80, 55),
                           (cx, cy - 18), 4)
        pygame.draw.circle(tela, (150, 130, 100),
                           (cx, cy - 18), 4, 1)

    elif item.icone == "machado":
        # cabo
        pygame.draw.line(tela, (140, 110, 70),
                         (cx + 8, cy + 14), (cx - 6, cy - 10), 3)
        # lamina
        pygame.draw.polygon(tela, (180, 172, 150), [
            (cx - 6, cy - 10),
            (cx - 16, cy - 4),
            (cx - 8, cy + 6),
        ])

    elif item.icone == "pocao":
        pygame.draw.ellipse(tela, (160, 30, 42),
                            (cx - 10, cy - 5, 20, 18))
        pygame.draw.rect(tela, (190, 180, 190),
                         (cx - 4, cy - 14, 8, 10), border_radius=2)
        cargas_txt = fonte_pequena.render(
            str(item.cargas if item.cargas is not None else item.quantidade),
            True, Branco_texto)
        tela.blit(cargas_txt, (sx + slot_size - 16, sy + slot_size - 18))

    elif item.icone == "raiz":
        # haste
        pygame.draw.line(tela, (100, 160, 80),
                         (cx, cy + 12), (cx, cy - 4), 2)
        # folhas
        pygame.draw.ellipse(tela, (80, 180, 60),
                            (cx - 10, cy - 12, 12, 8))
        pygame.draw.ellipse(tela, (80, 180, 60),
                            (cx - 2, cy - 16, 12, 8))
        cargas_txt = fonte_pequena.render(
            str(item.quantidade), True, Branco_texto)
        tela.blit(cargas_txt, (sx + slot_size - 16, sy + slot_size - 18))

    else:  # generico
        pygame.draw.circle(tela, Azul_espectral, (cx, cy), 12, 2)
        pygame.draw.line(tela, Roxo_espectral,
                         (cx, cy - 8), (cx, cy + 8), 2)