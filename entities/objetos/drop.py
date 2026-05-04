import pygame
from entities.objetos.item import get_item

class Drop:

    Raio = 12
    Alcance_coleta = 50


    def __init__(self, x, y, id_item):
        self.id_item = id_item
        self.item = get_item(id_item)
        self.ativo = True

        #rect para centralizar o ponto do drop
        self.rect = pygame.Rect(0, 0, self.Raio * 2, self.Raio * 2)
        self.rect.centerx = x
        self.rect.centery = y

        self._timer = 0


    def atualizar(self, player, teclas, hud):
        if not self.ativo:
            return
        
        self._timer += 1

        dist = abs(player.rect.centerx - self.rect.centerx)
        if dist < self.Alcance_coleta:
            hud.mostra_mensagem(f"E -- Pegar {self.item.nome}")

            if teclas[pygame.K_e] and player.cooldown_interaçao <= 0:
                print(f"coletando {self.item.nome}, ativo={self.ativo}")
                player.adicionar_ao_inventario(self.item)
                hud.mostra_mensagem(f" {self.item.nome} coletado!")
                self.ativo = False
                player.cooldown_interaçao = 30

    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        sr = camera.aplicar(self.rect)

        #pulso do item, cresce e dimunui levemente
        pulso = abs((self._timer % 60) - 30) / 30 
        raio = int(self.Raio + pulso * 4)

        pygame.draw.circle(tela, (255, 215, 0), sr.center, raio)
        pygame.draw.circle(tela, (180, 140, 0), sr.center, raio, 2)