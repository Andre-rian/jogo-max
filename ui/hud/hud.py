import pygame
from settings import DEBUG
from ui.estilo import Fonte_titulo, Fonte_texto
from ui.hud.status import BarrasStatus
from ui.hud.ecos import IndicadorEcos
from ui.hud.pocao import SlotPocao
from ui.hud.mensagens import Mensagens
from ui.hud.notificacao import NotificacaoItem
from ui.hud.boss import BarraBoss
from ui.hud.debug_painel import DebugPainel


class Hud:

    def __init__(self):
        pygame.font.init()
        self.fonte_pequena  = Fonte_texto(14)
        self.fonte_media    = Fonte_titulo(18, negrito=True)
        self.fonte_mensagem = Fonte_titulo(28, negrito=True)
        self.fonte_cargas   = Fonte_titulo(16, negrito=True)

        self.mensagens = Mensagens(self.fonte_mensagem, self.fonte_media)
        self.notificacao_item = NotificacaoItem(self.fonte_media)
        self.ecos = IndicadorEcos(self.fonte_media)
        self.status = BarrasStatus(self.fonte_pequena)
        self.pocao_slot = SlotPocao(self.fonte_pequena)
        self.boss_bar = BarraBoss(self.fonte_media)
        self.debug = DebugPainel(self.fonte_pequena)

    def mostra_mensagem(self, texto, duracao=180):
        self.mensagens.mostrar(texto, duracao)

    def limpar_mensagem(self):
        self.mensagens.limpar()

    def mostrar_prompt(self, texto):
        self.mensagens.mostrar_prompt(texto)

    def limpar_prompt(self):
        self.mensagens.limpar_prompt()

    def flash_pocao(self):
        self.pocao_slot.flash()

    def mostrar_item_coletado(self, item, quantidade=1):
        self.notificacao_item.mostrar(item, quantidade)

    def atualizar(self):
        self.mensagens.atualizar()
        self.pocao_slot.atualizar()
        self.boss_bar.atualizar()

    def desenhar(self, tela, player, boss_atual=None):
        self.status.desenhar(tela, player)
        self.pocao_slot.desenhar(tela, player)
        self.mensagens.desenhar(tela)
        self.notificacao_item.desenhar(tela)
        self.ecos.desenhar(tela, player)
        if DEBUG:
            self.debug.desenhar(tela, player)
        if boss_atual:
            self.boss_bar.desenhar(tela, boss_atual)