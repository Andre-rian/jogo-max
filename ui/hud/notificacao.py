import pygame
import logging
from settings import Screen_widht, Screen_height
from ui.estilo import Fonte_texto

logger = logging.getLogger(__name__)

class NotificacaoItem:

    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._notif_item = None
        self._notif_quantidade = 1
        self._notif_timer = 0
        self._notif_duracao = 210 #3.5 segundos de duracao

    def mostrar(self, item, quantidade=1):
        logger.debug(f"notif recebida: item={item}, tipo={type(item)}")
        self._notif_item = item
        self._notif_quantidade = quantidade
        self._notif_timer = self._notif_duracao

    def atualizar(self):
        pass

    def desenhar(self, tela):
        if not self._notif_item or self._notif_timer <= 0:
            return

        self._notif_timer -= 1

        #saida suave nos ultimos 60 frames
        if self._notif_timer < 60:
            alpha = int(255 * (self._notif_timer / 60))
        else:
            alpha = 255

        item = self._notif_item
        w, h = 340, 64
        x = Screen_widht // 2 - w // 2
        y = Screen_height - 120

        #fundo
        painel = pygame.Surface((w, h), pygame.SRCALPHA)
        painel.fill((22, 22, 27, int(200 * alpha / 255)))
        tela.blit(painel, (x, y))

        #bordas bonitinhas
        cor_borda = (int(90 * alpha / 255), int(112 * alpha / 255), int(168 * alpha / 255))
        pygame.draw.rect(tela, cor_borda, (x, y, w, h), 1)
        pygame.draw.line(tela, cor_borda, (x + 10, y), (x + w - 10, y), 1)
        pygame.draw.line(tela, cor_borda, (x + 10, y + h), (x + w - 10, y + h), 1)

        #icone do item
        cx = x + 36
        cy = y + h // 2
        icone = getattr(item, "icone", "generico")
        self._desenhar_icone(tela, icone, cx, cy, alpha)

        #linha que separa
        cor_linha = (int(52 * alpha / 255), int(70 * alpha / 255), int(110 * alpha / 255))
        pygame.draw.line(tela, cor_linha, (x + 64, y + 8), (x + 64, y + h - 8))

        #nome do item
        cor_nome = (int(160 * alpha / 255), int(174 * alpha / 255), int(222 * alpha / 255))
        nome_txt = self.fonte_media.render(item.nome, True, cor_nome)
        tela.blit(nome_txt, (x + 80, y + h // 2 - nome_txt.get_height() // 2))

        #quantidade
        if self._notif_quantidade > 1:
            cor_qtd = (int(140 * alpha / 255), int(140 * alpha / 255), int(160 * alpha / 255))
            qtd_txt = self.fonte_media.render(str(self._notif_quantidade), True, cor_qtd)
            tela.blit(qtd_txt, (x + w - qtd_txt.get_width() - 16, y + h // 2 - qtd_txt.get_height() // 2))

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