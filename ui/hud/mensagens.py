"""Mensagens e prompts existentes, protegidos por painéis de alto contraste."""
import pygame

from ui.hud.apresentacao import painel, texto_em_linhas


class Mensagens:
    def __init__(self, fonte_mensagem, fonte_prompt):
        self.fonte_mensagem = fonte_mensagem
        self.fonte_prompt = fonte_prompt
        self._mensagem = ''
        self._timer_mensagem = 0
        self._prompt = None
        self._cache = {}
        self.rect_prompt = pygame.Rect(0, 0, 0, 0)
        self.rect_mensagem = pygame.Rect(0, 0, 0, 0)

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

    def _preparar(self, tipo, fonte, texto, limite):
        chave = (texto, limite)
        anterior = self._cache.get(tipo)
        if anterior is not None and anterior[0] == chave:
            return anterior[1]
        largura = min(limite, max(24, fonte.size(texto)[0]))
        renderizado = texto_em_linhas(fonte, texto, largura)
        superficie = painel((largura + 32, max(fonte.get_height()+16, renderizado.get_height() + 16)))
        superficie.blit(renderizado, (16, 8))
        # Somente os dois conteúdos atuais ficam em cache.
        self._cache[tipo] = (chave, superficie)
        return superficie

    def desenhar(self, tela):
        self.rect_prompt = pygame.Rect(0, 0, 0, 0)
        self.rect_mensagem = pygame.Rect(0, 0, 0, 0)
        limite = min(max(360, int(self.fonte_mensagem.get_height()*18)), tela.get_width() - 72)
        # Prompts de interacao sao renderizados como sprites no mundo (G.1).

        if self._timer_mensagem <= 0:
            return
        msg = self._preparar('mensagem', self.fonte_mensagem, self._mensagem, limite)
        msg.set_alpha(min(255, self._timer_mensagem * 5))
        self.rect_mensagem = msg.get_rect(midtop=(tela.get_width() // 2, tela.get_height() // 2 - 100))
        tela.blit(msg, self.rect_mensagem)
