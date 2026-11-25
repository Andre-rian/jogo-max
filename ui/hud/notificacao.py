"""Notificação híbrida acima da faixa dos prompts; animação original preservada."""
import logging

import pygame

from ui.hud.apresentacao import painel, texto_em_linhas
from ui.sprites_itens import obter_sprite_de_item

logger = logging.getLogger(__name__)


class NotificacaoItem:
    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._notif_item = None
        self._notif_quantidade = 1
        self._notif_timer = 0
        self._notif_duracao = 210
        self._painel = None
        self._chave = None
        self.rect = pygame.Rect(0, 0, 0, 0)

    def mostrar(self, item, quantidade=1):
        logger.debug(f"notif recebida: item={item}, tipo={type(item)}")
        self._notif_item = item
        self._notif_quantidade = quantidade
        self._notif_timer = self._notif_duracao
        self._chave = None

    def atualizar(self):
        # Cadência histórica: esta notificação avança em desenhar, não aqui.
        pass

    def _preparar(self, largura):
        item = self._notif_item
        chave = (item.nome, getattr(item, 'id', None), getattr(item, 'icone', None),
                 self._notif_quantidade, largura)
        if chave == self._chave:
            return
        self._chave = chave
        largura_texto = max(self.fonte_media.size(item.nome)[0],
                            self.fonte_media.size(str(self._notif_quantidade))[0])
        largura = min(largura, max(340, min(largura, largura_texto + 96)))
        nome = texto_em_linhas(self.fonte_media, item.nome, max(120, largura - 96))
        quantidade = None
        if self._notif_quantidade > 1:
            quantidade = texto_em_linhas(self.fonte_media, str(self._notif_quantidade),
                                        max(60, largura - 96), (168, 178, 202))
        altura_texto = nome.get_height() + (quantidade.get_height() + 4 if quantidade else 0)
        altura = max(self.fonte_media.get_height() + 34, altura_texto + 24)
        self._painel = painel((largura, altura))
        sprite = obter_sprite_de_item(item)
        if sprite is not None:
            self._painel.blit(sprite, (12, (altura - sprite.get_height()) // 2))
        else:
            self._desenhar_icone(self._painel, getattr(item, 'icone', 'generico'),
                                 36, altura // 2, 255)
        pygame.draw.line(self._painel, (81, 94, 120), (68, 12), (68, altura - 13))
        y = (altura - altura_texto) // 2
        self._painel.blit(nome, (80, y))
        if quantidade is not None:
            self._painel.blit(quantidade, (80, y + nome.get_height() + 4))

    def desenhar(self, tela):
        if not self._notif_item or self._notif_timer <= 0:
            self.rect = pygame.Rect(0, 0, 0, 0)
            return
        self._notif_timer -= 1
        alpha = int(255 * self._notif_timer / 60) if self._notif_timer < 60 else 255
        self._preparar(min(460, tela.get_width() - 40))
        # Em 1280x720: termina em y=540; prompt começa em y=562.
        # Cresce para cima quando o nome/quantidade precisa de mais linhas.
        self.rect = self._painel.get_rect(midbottom=(tela.get_width() // 2, tela.get_height() - 180))
        self._painel.set_alpha(alpha)
        tela.blit(self._painel, self.rect)

    def _desenhar_icone(self, tela, icone, cx, cy, alpha):
        cor_arma = (int(168 * alpha / 255), int(176 * alpha / 255), int(210 * alpha / 255))
        cor_cabo = (int(130 * alpha / 255), int(104 * alpha / 255), int(70 * alpha / 255))
        cor_verde = (int(70 * alpha / 255), int(160 * alpha / 255), int(90 * alpha / 255))
        cor_pocao = (int(150 * alpha / 255), int(30 * alpha / 255), int(44 * alpha / 255))
        cor_mineral = (int(96 * alpha / 255), int(118 * alpha / 255), int(190 * alpha / 255))

        if icone == "espada":
            pygame.draw.polygon(tela, cor_arma, [
                (cx, cy - 16), (cx - 3, cy + 2), (cx + 3, cy + 2)
            ])
            pygame.draw.line(tela, cor_arma, (cx - 10, cy + 3), (cx + 10, cy + 3), 3)
            pygame.draw.line(tela, cor_cabo, (cx, cy + 3), (cx, cy + 12), 3)
            pygame.draw.circle(tela, cor_cabo, (cx, cy + 14), 3)

        elif icone == "machado":
            pygame.draw.line(tela, cor_cabo, (cx + 8, cy + 14), (cx - 6, cy - 10), 3)
            pygame.draw.polygon(tela, cor_arma, [
                (cx - 6, cy - 10), (cx - 16, cy - 4), (cx - 8, cy + 6)
            ])

        elif icone == "pocao":
            pygame.draw.ellipse(tela, cor_pocao, (cx - 10, cy - 5, 20, 18))
            pygame.draw.rect(tela, cor_pocao, (cx - 4, cy - 14, 8, 10), border_radius=2)

        elif icone == "raiz":
            pygame.draw.line(tela, cor_verde, (cx, cy + 12), (cx, cy - 4), 2)
            pygame.draw.ellipse(tela, cor_verde, (cx - 10, cy - 12, 12, 8))
            pygame.draw.ellipse(tela, cor_verde, (cx - 2, cy - 16, 12, 8))

        elif icone == "mineral":
            pygame.draw.polygon(tela, cor_mineral, [
                (cx, cy - 14), (cx + 10, cy - 4),
                (cx + 6, cy + 10), (cx - 6, cy + 10), (cx - 10, cy - 4)
            ])
            pygame.draw.polygon(tela, (int(140 * alpha / 255), int(150 * alpha / 255), int(215 * alpha / 255)), [
                (cx, cy - 14), (cx + 10, cy - 4), (cx, cy)
            ])

        else:
            pygame.draw.circle(tela, cor_arma, (cx, cy), 12, 2)
