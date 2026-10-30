import pygame

def mouse_mouveu(eventos):
    #retorna true se o mouse se mouveu nesse frame
    return any(e.type == pygame.MOUSEMOTION for e in eventos)


def hover_index(eventos, pos_mouse, itens_com_rect):

    #itens_com_rect: lista de (indice, rect).So calcula/retorna um indice se o mouse de fato se moveu neste frame; caso contrario retorna None (deixa a selecao como o teclado deixou).

    if not mouse_mouveu(eventos):
        return None
    for indice, rect in itens_com_rect:
        if rect.collidepoint(pos_mouse):
            return indice
    return None


def navegar_1d(atual, delta, minimo, maximo, wrap=False):
    """ 
    move "atuaL" por "delta" dentro do minimo, maximo. 
    wrap = true faz o valor  dar a voltar (o MenuFogueira faz isso com %)
    """

    novo = atual + delta
    total = maximo - minimo + 1
    if wrap:
        return minimo + (novo - minimo) % total
    return max(minimo, min(maximo, novo))