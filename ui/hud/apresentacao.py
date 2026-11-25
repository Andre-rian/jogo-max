"""Pequenos helpers visuais da HUD; sem dados ou regras de gameplay."""
import pygame

from ui.estilo import Roxo_espectral, desenhar_painel

TEXTO = (220, 224, 235)
BORDA = (107, 118, 137)


def painel(tamanho):
    superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
    desenhar_painel(superficie, superficie.get_rect(), 0, cor_borda=BORDA)
    pygame.draw.line(superficie, Roxo_espectral, (12, 6), (tamanho[0] - 13, 6))
    return superficie


def texto_em_linhas(fonte, texto, largura, cor=TEXTO):
    """Quebra por palavras; tokens longos (quantidades) mantêm todos os dígitos."""
    linhas = []
    for paragrafo in str(texto).split('\n'):
        linha = ''
        for palavra in paragrafo.split(' '):
            candidato = f'{linha} {palavra}' if linha else palavra
            if fonte.size(candidato)[0] <= largura:
                linha = candidato
                continue
            if linha:
                linhas.append(linha)
            linha = ''
            for caractere in palavra:
                if linha and fonte.size(linha + caractere)[0] > largura:
                    linhas.append(linha)
                    linha = ''
                linha += caractere
        linhas.append(linha)
    superficie = pygame.Surface((largura, len(linhas) * fonte.get_linesize()), pygame.SRCALPHA)
    for i, linha in enumerate(linhas):
        superficie.blit(fonte.render(linha, True, cor), (0, i * fonte.get_linesize()))
    return superficie
