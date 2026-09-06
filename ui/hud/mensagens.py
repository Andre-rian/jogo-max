import pygame
from settings import Screen_widht, Screen_height
from ui.estilo import Azul_claro, Cinza_texto

# Mensagens do HUD:
# - mensagem central temporizada (ex.: "Jogo salvo") que some sozinha;
# - prompt contextual (ex.: "pressione E para abrir") que só aparece enquanto
#   o player está interagindo com um objeto e é limpo ao sair.

class Mensagens:

    def __init__(self, fonte_mensagem, fonte_prompt):
        self.fonte_mensagem = fonte_mensagem
        self.fonte_prompt = fonte_prompt
        self._mensagem = ""
        self._timer_mensagem = 0
        self._prompt = None

    def mostrar(self, texto, duracao=180):
        self._mensagem = texto
        self._timer_mensagem = duracao

    def limpar(self):
        self._timer_mensagem = 0

    def mostrar_prompt(self, texto):
        self._prompt = texto

    def limpar_prompt(self):
        self._prompt = None

    def atualizar(self):
        if self._timer_mensagem > 0:
            self._timer_mensagem -= 1

    def desenhar(self, tela):
        if self._prompt is not None:
            prompt = self.fonte_prompt.render(self._prompt, True, Cinza_texto)
            x = Screen_widht // 2 - prompt.get_width() // 2
            y = Screen_height - 150
            tela.blit(prompt, (x, y))

        if self._timer_mensagem <= 0:
            return
        alpha = min(255, self._timer_mensagem * 5)
        msg = self.fonte_mensagem.render(self._mensagem, True, Azul_claro)
        msg.set_alpha(alpha)
        x = Screen_widht // 2 - msg.get_width() // 2
        y = Screen_height // 2 - 100
        tela.blit(msg, (x, y))