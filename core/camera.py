import pygame
from settings import Screen_widht, Screen_height, Tile_size, ZOOM_PADRAO, ZOOM_SUAVIZAÇÃO


class Camera:
    def __init__(self, largura_mapa_px, altura_mapa_px):
        #isso é o offset, basicamente o mundo que ta fora da tela
        self.offset = pygame.Vector2(0, 0)

        #tamanho do mapa em pixels 
        self.mapa_largura = largura_mapa_px
        self.mapa_altura = altura_mapa_px

        #suavização do movimento da camera
        self.suavizaçao = 0.12 

        #zoom: quanto maior, mais proximo do player
        self.zoom = ZOOM_PADRAO
        self.zoom_alvo = ZOOM_PADRAO


    def atualizar(self, alvo):
        #ease do zoom em direçao ao alvo (ex: boss)
        self.zoom += (self.zoom_alvo - self.zoom) * ZOOM_SUAVIZAÇÃO

        #tamanho da area visivel do mundo, dependendo do zoom
        vw = Screen_widht / self.zoom
        vh = Screen_height / self.zoom

        #posiçao do player
        ideal_x = alvo.centerx - vw / 2
        ideal_y = alvo.centery - vh / 2

        #lerp, o movimento da camera durante os frames
        self.offset.x += (ideal_x - self.offset.x) * self.suavizaçao
        self.offset.y += (ideal_y - self.offset.y) * self.suavizaçao

        #travamento da camera, para nao passar do mapa
        if self.mapa_largura <= vw:
            self.offset.x = (self.mapa_largura - vw) / 2
        else:
            self.offset.x = max(0, min(self.offset.x, self.mapa_largura - vw))


        if self.mapa_altura <= vh:
            self.offset.y = (self.mapa_altura - vh) / 2
        else:
            self.offset.y = max(0, min(self.offset.y, self.mapa_altura - vh))

    def aplicar(self, rect):
        #é oque converta a posiçao do item no mundo para o desenho na tela, usando o rect

        return rect.move(-int(self.offset.x), -int(self.offset.y))
    
    def mouse_para_mundo(self, pos_mouse):
        #bsicamente é oque converte a direçao do mouse para a direçao do ataque
        #para isso divide o mouse pelo zoom, já que a cena é desenhada escalada

        return pygame.Vector2(
            pos_mouse[0] / self.zoom + self.offset.x,
            pos_mouse[1] / self.zoom + self.offset.y
        )
    
    def atualizar_limite(self, largura_px, altura_px):
        #vai ser utilizado quando o player trocar de cenario/salar

        self.mapa_largura = largura_px
        self.mapa_altura = altura_px