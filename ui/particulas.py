import math
import pygame

class ParticulaEco:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.ativo = True
        self._timer = 0

        #velocidade inicial aleatoria
        import random
        angulo = random.uniform(0, math.pi * 2)
        self.vel_x = math.cos(angulo) * random.uniform(0.3, 1)
        self.vel_y = math.sin(angulo) * random.uniform(0.3, 1)
        self.cor = random.choice([
            (100, 60, 180),
            (140, 80, 220),
            (160, 100, 255),
        ])
        self.raio = random.randint(2, 4)

    def atualizar(self, player_cx, player_cy):
        self._timer += 1

        #direçao do player
        dx = player_cx - self.x 
        dy = player_cy - self.y
        dist = math.sqrt(dx * dx + dy * dy)


        if dist < 10:
            self.ativo = False
            return
        
        #se acelera em direçao baseado na distancia
        fator = min(0.15, 60 / dist)
        self.vel_x += dx * fator * 0.05
        self.vel_y += dy * fator * 0.05


        #limita a velocidade
        spd = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        if spd > 8:
            self.vel_x = self.vel_x / spd * 3
            self.vel_y = self.vel_y / spd * 3 

        self.x += self.vel_x
        self.y += self.vel_y

        #some se demora demais para se aproxima
        if self._timer > 120:
            self.ativo = False


    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        pos = camera.aplicar(pygame.Rect(int(self.x), int(self.y), 1, 1))
        pygame.draw.circle(tela, self.cor, (pos.x , pos.y), self.raio)