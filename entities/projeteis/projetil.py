import pygame
from core.animated_sprite import AnimatedSprite

class Projetil:
    #classe base para todos os projeteis do jogo
    def __init__(self, x, y, vel_x, vel_y, dano, tem_gravidade=False, gravidade = 0.4):
        self.rect = pygame.Rect(x, y, 20, 20)  # Tamanho base, cada inimigo pode ter um tamanho diferente
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.dano = dano
        self.tem_gravidade = tem_gravidade
        self.ativo = True  # Para controlar se o projétil ainda está ativo ou deve ser removido
        self.gravidade = gravidade
        

    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return
        
        if self.tem_gravidade:
            self.vel.y = min(self.vel.y + self.gravidade, 15)  # Limite de velocidade de queda

        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        #colisao com as paredes
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self._ao_colidir_mundo(tile)
                return
            
        #colisao com o player
        if player.vivo and self.rect.colliderect(player.rect):
            self._ao_colidir_player(player)
    

    def _ao_colidir_mundo(self, tile):
        #conportamento padrao, se colidir = desetivar
        self.ativo = False

    def _ao_colidir_player(self, player):
        #comportamento padrao, se colidir = dano e desativar
        player.receber_dano(self.dano)
        self.ativo = False

    
    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        sr = camera.aplicar(self.rect)

        #placerholder, cada filho implementar a sua sprite
        pygame.draw.circle(tela, (255, 0, 0), sr.center, 6)
