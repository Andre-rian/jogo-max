import pygame
import logging
from settings import Tile_size, DEBUG
from core.recursos import carregar_imagem

logger = logging.getLogger(__name__)


class Porta:

    def __init__(self, x, y, col, linha):

        self.col = col
        self.linha = linha

        self.rect = pygame.Rect(x, y, Tile_size, Tile_size * 2)

        #area de interaçao maior que a hitbox: a porta é sólida no mapa (player é
        #bloqueado na frente dela e nunca sobrepõe o rect), então a interação aceita
        #o player encostado (~1 tile além da porta).
        self.interacao = self.rect.inflate(Tile_size * 2, Tile_size * 2)

        self.aberta = False

        #carrega as duas imagens estaticasd (sem spritesheet, sem frames)
        img_fechada = carregar_imagem("assets/sprites/objetos/portas/porta_fechada.png")
        img_aberta = carregar_imagem("assets/sprites/objetos/portas/porta_aberta.png")


        #escala mantendo a proproçao de cada imagem
        self._img_fechada = self._escalar_por_largura(img_fechada, Tile_size)
        self._img_aberta = self._escalar_por_largura(img_aberta, Tile_size)


    @staticmethod
    def _escalar_por_largura(img, largura_alvo):
        propocao = largura_alvo / img.get_width()
        altura_alvo = int(img.get_height() * propocao)
        return pygame.transform.scale(img, (largura_alvo, altura_alvo))


    def atualizar(self, player, teclas, hud, portas_abertas):
        colide = player.rect.colliderect(self.interacao)

        if colide:
            if not self.aberta:
                hud.mostrar_prompt("Pressione E para abrir")
            else:
                hud.mostrar_prompt("Pressione E para Fechar")

            if teclas[pygame.K_e] and player.cooldown_interaçao <= 0:
                self.aberta = not self.aberta
                player.cooldown_interaçao = 30


                if self.aberta:
                    portas_abertas.add((self.col, self.linha))
                    logger.debug(f"porta ({self.col},{self.linha}) aberta")

                else:
                    portas_abertas.discard((self.col, self.linha))
                    logger.debug(f"porta ({self.col},{self.linha}) fechada")

                hud.limpar_prompt()
        else:
            hud.limpar_prompt()

    def desenhar(self, tela, camera):
        sr = camera.aplicar(self.rect)
        img = self._img_aberta if self.aberta else self._img_fechada

        #ancora pela base do react, ja que as imagems tem altura diferentes
        destino = img.get_rect(midbottom=sr.midbottom)
        tela.blit(img, destino)

        #debug
        if DEBUG:
            pygame.draw.rect(tela, (120, 90, 60), sr, 1)

