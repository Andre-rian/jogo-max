"""Barra híbrida do chefe: estado visual isolado por identidade e presença."""
import pygame

from ui.hud.apresentacao import painel, texto_em_linhas
from ui.hud.trilho_status import obter_trilho

COR_VIDA = (184, 51, 65)
COR_ATRASADA = (191, 126, 144)


class BarraBoss:
    def __init__(self, fonte_media):
        self.fonte_media = fonte_media
        self._boss = None
        self._boss_hp_display = 0
        self._boss_hp_real = 0
        self._boss_hp_anterior = 0
        self._boss_ultimo_dano = 0
        self._boss_timer_dano = 0
        self._chave = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.interior = pygame.Rect(0, 0, 0, 0)

    def atualizar(self):
        if self._boss_hp_display > self._boss_hp_real:
            self._boss_hp_display = max(self._boss_hp_real, self._boss_hp_display - 2)
        if self._boss_timer_dano > 0:
            self._boss_timer_dano -= 1
            if self._boss_timer_dano == 0:
                self._boss_ultimo_dano = 0

    def _preparar(self, boss, largura):
        dano = f'-{self._boss_ultimo_dano}' if self._boss_timer_dano > 0 else ''
        chave = (boss.nome, dano, largura, self.fonte_media.get_height())
        if chave == self._chave:
            return
        self._chave = chave
        nome = texto_em_linhas(self.fonte_media, boss.nome, largura - 144)
        texto_dano = texto_em_linhas(self.fonte_media, dano, 100, COR_ATRASADA) if dano else None
        altura = max(64, 44 + max(nome.get_height(), texto_dano.get_height() if texto_dano else 0))
        self._painel = painel((largura, altura))
        self._painel.blit(nome, (16, 12))
        if texto_dano:
            self._painel.blit(texto_dano, (largura - 116, 12))
        self._trilho = obter_trilho(largura - 32, 10)
        self._painel.blit(self._trilho, (16, altura - 28))

    def desenhar(self, tela, boss):
        if boss is None:
            self._boss = None
            self._boss_hp_display = self._boss_hp_real = self._boss_hp_anterior = 0
            self._boss_ultimo_dano = self._boss_timer_dano = 0
            self.rect = pygame.Rect(0, 0, 0, 0)
            self.interior = pygame.Rect(0, 0, 0, 0)
            return

        if boss is not self._boss:
            self._boss = boss
            # Não simula dano ao apresentar um chefe já ferido ou reapresentado.
            self._boss_hp_display = self._boss_hp_anterior = boss.hp
            self._boss_ultimo_dano = self._boss_timer_dano = 0
        self._boss_hp_real = boss.hp
        if boss.hp < self._boss_hp_anterior:
            self._boss_ultimo_dano += self._boss_hp_anterior - boss.hp
            self._boss_timer_dano = 120
        # Cura observada não deixa a camada atrasada atrás da vida atual.
        self._boss_hp_display = max(boss.hp, self._boss_hp_display)
        self._boss_hp_anterior = boss.hp

        self._preparar(boss, min(max(480, self.fonte_media.get_height()*22), tela.get_width() - 40))
        self.rect = self._painel.get_rect(midbottom=(tela.get_width() // 2, tela.get_height() - 20))
        tela.blit(self._painel, self.rect)
        self.interior = pygame.Rect(self.rect.x + 19, self.rect.bottom - 25,
                                    self.rect.width - 38, 10)
        for valor, cor in ((self._boss_hp_display, COR_ATRASADA), (boss.hp, COR_VIDA)):
            proporcao = max(0, min(1, valor / boss.hp_max)) if boss.hp_max > 0 else 0
            largura = int(self.interior.width * proporcao)
            if largura:
                pygame.draw.rect(tela, cor, (self.interior.x, self.interior.y,
                                             largura, self.interior.height))
