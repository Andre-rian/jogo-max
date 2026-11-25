"""Conclusão da campanha beta, sem atualizar o combate atrás da tela."""
import pygame
from ui.estilo import (Fonte_titulo, Fonte_texto, desenhar_botao,
                       Azul_espectral, Branco_texto, Cinza_texto)


class TelaFimBeta:
    def __init__(self, tela):
        self.tela = tela
        self.frame = 0
        w, h = tela.get_size()
        self.botao = pygame.Rect(w // 2 - 170, int(h * .73), 340, 52)

    def atualizar(self, eventos):
        self.frame += 1
        return any(
            e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)
            or e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.botao.collidepoint(e.pos)
            for e in eventos
        )

    def desenhar(self):
        self.tela.fill((11, 13, 24))
        w, h = self.tela.get_size()
        for y in (int(h * .20), int(h * .65)):
            pygame.draw.line(self.tela, Azul_espectral, (w // 4, y), (3 * w // 4, y))
        textos = (("PROFANE ECHO", Fonte_titulo(44), .31, Azul_espectral),
                  ("Fim da Beta", Fonte_titulo(30), .45, Branco_texto),
                  ("O caminho para o topo do castelo apenas começou.", Fonte_texto(19), .56, Cinza_texto))
        for texto, fonte, altura, cor in textos:
            surface = fonte.render(texto, True, cor)
            if surface.get_width() > w - 60:
                surface = pygame.transform.smoothscale(surface, (w - 60, surface.get_height()))
            self.tela.blit(surface, surface.get_rect(center=(w // 2, int(h * altura))))
        desenhar_botao(self.tela, self.botao, "Voltar ao menu principal", True, self.frame,
                       fonte_btn=Fonte_texto(19))
