import pygame
from settings import Screen_widht, Screen_height, Titulo_size


class Camera:
    def __init__(self, largura_mapa_tiles, altura_mapa_tiles):
        #isso é o offset, basicamente o mundo que ta fora da tela
        self.offset = pygame.Vector2(0, 0)

        #tamanho do mapa em pixels 
        self.mapa_largura = largura_mapa_tiles * Titulo_size
        self.mapa_altura = altura_mapa_tiles * Titulo_size

        #suavização do movimento da camera
        self.suavizaçao = 0.12 

    def atualizar(self, alvo):
        #posiçao do player
        ideal_x = alvo.centerx - Screen_widht // 2
        ideal_y = alvo.centery - Screen_height // 2
        
        #lerp, o movimento da camera durante os frames
        self.offset.x += (ideal_x - self.offset.x) * self.suavizaçao
        self.offset.y += (ideal_y - self.offset.y) * self.suavizaçao

        #travamento da camera, para nao passar do mapa
        self.offset.x = max(0, min(self.offset.x, self.mapa_largura - Screen_widht))
        self.offset.y = max(0, min(self.offset.y, self.mapa_altura - Screen_height))

    def aplicar(self, rect):
        #é oque converta a posiçao do item no mundo para o desenho na tela, usando o rect

        return rect.move(-int(self.offset.x), -int(self.offset.y))
    
    def mouse_para_mundo(self, pos_mouse):
        #bsicamente é oque converte a direçao do mouse para a direçao do ataque

        return pygame.Vector2(
            pos_mouse[0] + self.offset.x,
            pos_mouse[1] + self.offset.y
        )
    
    def atualizar_limite(self, largura_tiles, altura_tiles):
        #vai ser utilizado quando o player trocar de cenario/salar

        self.mapa_largura = largura_tiles * Titulo_size
        self.mapa_altura = altura_tiles * Titulo_size