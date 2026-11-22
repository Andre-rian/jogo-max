"""Contador de Ecos com arte D.1, efeito existente e painel ancorado à direita."""
from functools import lru_cache
from pathlib import Path

import pygame

from core.recursos import carregar_imagem
from ui.estilo import Branco_texto, Roxo_espectral, desenhar_eco_profano, desenhar_painel

CAMINHO_ECO = (Path(__file__).resolve().parents[2]
               / 'assets/sprites/itens/ecos/eco_profano.png')


@lru_cache(maxsize=1)
def _obter_icone():
    imagem = carregar_imagem(str(CAMINHO_ECO), converter_alfa=False)
    return imagem if imagem.get_size() == (24, 24) else None


class IndicadorEcos:
    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._frame_hud = 0
        self._icone = _obter_icone()
        self._efeito = pygame.Surface((64, 64), pygame.SRCALPHA)
        self._chave = None
        self._painel = None
        self._linhas = []

    def _preparar_painel(self, quantidade, largura_tela):
        limite = min(max(220, self.fonte_media.get_height() * 12), largura_tela - 40)
        chave = (quantidade, limite, self.fonte_media.get_height())
        if chave == self._chave:
            return
        self._chave = chave
        largura_texto = max(1, limite - 80)
        linhas = ['']
        for digito in str(quantidade):
            if linhas[-1] and self.fonte_media.size(linhas[-1] + digito)[0] > largura_texto:
                linhas.append('')
            linhas[-1] += digito
        self._linhas = [self.fonte_media.render(linha, True, Branco_texto) for linha in linhas]
        largura = min(limite, max(196, 80 + max(s.get_width() for s in self._linhas)))
        altura = max(64, 24 + len(linhas) * self.fonte_media.get_linesize())
        self._painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        desenhar_painel(self._painel, self._painel.get_rect(), 0, cor_borda=(107, 118, 137))
        pygame.draw.line(self._painel, Roxo_espectral, (68, 8), (largura - 12, 8))
        y = (altura - len(linhas) * self.fonte_media.get_linesize()) // 2
        for texto in self._linhas:
            self._painel.blit(texto, (largura - 12 - texto.get_width(), y))
            y += self.fonte_media.get_linesize()

    def desenhar(self, tela, player):
        # Mesma cadência anterior: o efeito avança uma vez por desenho.
        self._frame_hud += 1
        self._preparar_painel(player.ecos, tela.get_width())
        rect = self._painel.get_rect(bottomright=(tela.get_width() - 20, tela.get_height() - 20))
        tela.blit(self._painel, rect)
        self._efeito.fill((0, 0, 0, 0))
        desenhar_eco_profano(self._efeito, 32, 32, 15, self._frame_hud, alpha_real=True)
        if self._icone is not None:
            # Troca somente o núcleo procedural; halo e fragmentos continuam.
            self._efeito.fill((0, 0, 0, 0), (20, 20, 24, 24))
            self._efeito.blit(self._icone, (20, 20))
        tela.blit(self._efeito, (rect.x + 4, rect.centery - 32))
