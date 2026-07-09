import pygame
import math
import random

class DropEco:

    Alcance_coleta = 60

    def __init__(self, x, y, quantidade):
        self.x = float(x)
        self.y = float(y)
        self.quantidade = quantidade
        self.ativo = True


        self.rect = pygame.Rect(int(x) - 16, int(y) - 16, 32, 32)

        self._timer = 0
        self._fragmentos = []

        #gera os fragmentos obitidos
        for i in range(6):
            angulo = (i / 6) * math.pi * 2
            vel = random.uniform(0.01, 0.03)
            dist = random.uniform(10, 18)
            cor = random.choice([
                (100, 60, 180),
                (140, 80, 220),
                (160, 100, 255),
                (80, 40, 140)
            ])
            self._fragmentos.append({
                "angulo": angulo,
                "vel": vel,             
                "dist": dist,
                "cor": cor,
                "raio": random.randint(2, 4)
            })

        #particulas subindo
        self._particulas = []

    def atualizar(self, player, teclas, hud):
        if not self.ativo:
            return
        
        self._timer += 1
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        #atulizar o movimentos dos fragementos em obita
        for f in self._fragmentos:
            f["angulo"] += f["vel"]

        # spwana as particulas subindo
        if self._timer * 8 == 0:
            self._particulas.append({
                "x": self.x + random.uniform(-8, 8),
                "y": self.y,
                "vel_y": random.uniform(-0.3, -0.8),
                "alpha": 255,
                "cor": random.choice([(100, 60, 180), (140, 80, 220)]),
            })

        #atualizar as particulas 
        for p in self._particulas:
            p["y"] += p["vel_y"]
            p["alpha"] -= 4
        self._particulas = [p for p in self._particulas if p["alpha"] > 0]


        #checar a coleta
        dist = abs(player.rect.centerx - self.rect.centerx)
        if dist < self.Alcance_coleta:
            hud.mostra_mensagem("E - para recupera Ecos perdidos")
            if teclas[pygame.K_e] and player.cooldown_interaçao <= 0:
                player.ecos += self.quantidade
                player.cooldown_interaçao = 30
                self.ativo = False
        

    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        sr = camera.aplicar(self.rect)
        cx = sr.centerx
        cy = sr.centery


        #pulsar o chao abaixo

        pulso = abs((self._timer % 90) - 45) / 45
        raio_nucleo = int(10 + pulso * 3)

        #escure o chao abaixo
        sombra = pygame.Surface((60, 20), pygame.SRCALPHA)
        sombra.fill((20, 0, 40, 80))
        tela.blit(sombra, (cx - 30, cy + 10))


        #nucleo vazio escuro
        pygame.draw.circle(tela, (10, 0, 20), (cx, cy), raio_nucleo)
        pygame.draw.circle(tela, (80, 40, 120), (cx, cy), raio_nucleo, 1)


        #fragmentos obitandos
        for f in self._fragmentos:
            fx = int(cx + math.cos(f["angulo"]) * f["dist"])
            fy = int(cy + math.sin(f["angulo"]) * f["dist"])
            
            pygame.draw.circle(tela, f["cor"], (fx, fy), f["raio"])

        #particulas subindo
        for p in self._particulas:
            pos = camera.aplicar(pygame.Rect(int(p["x"]), int(p["y"]), 1, 1))
            alpha_cor = tuple(int(c * p["alpha"] / 255) for c in p["cor"])
            pygame.draw.circle(tela, alpha_cor, (pos.x, pos.y), 2)

