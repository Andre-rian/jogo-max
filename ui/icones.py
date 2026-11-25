# Ícones dos itens desenhados no inventário (desenho puro).

import pygame

from ui.estilo import Roxo_espectral, Azul_espectral, Azul_claro, Branco_texto
from ui.sprites_itens import obter_fallback, obter_sprite_de_item


ICONS_COM_CONTAGEM = {"pocao", "raiz", "atadura", "cinzas", "lasca_umbrita"}


def _desenhar_contagem(tela, item, sx, sy, slot_size, fonte_pequena):
    icone = getattr(item, "icone", None)
    if icone not in ICONS_COM_CONTAGEM:
        return
    if icone == "pocao":
        valor = item.cargas if item.cargas is not None else item.quantidade
    else:
        valor = item.quantidade
    txt = fonte_pequena.render(str(valor), True, Branco_texto)
    tela.blit(txt, (sx + slot_size - 16, sy + slot_size - 18))


def desenhar_icone_item(tela, item, cx, cy, sx, sy, slot_size, fonte_pequena):
    sprite = obter_sprite_de_item(item)
    if sprite is None:
        sprite = obter_fallback()
    if sprite is not None:
        if sprite.get_width() > slot_size or sprite.get_height() > slot_size:
            sprite = pygame.transform.scale(sprite, (slot_size, slot_size))
        tela.blit(sprite, (sx + (slot_size - sprite.get_width()) // 2,
                           sy + (slot_size - sprite.get_height()) // 2))
        _desenhar_contagem(tela, item, sx, sy, slot_size, fonte_pequena)
        return

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