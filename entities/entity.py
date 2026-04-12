import pygame 
from settings import Gravidade, Max_Fall_Speed, Stamina_max

class Entity(pygame.sprite.Sprite):

    #Classe base para todas as entidades do game player,inimigo, boss e ect
    #possui a responsabilidade de guarda vida,velocidade, aplicar gravidade e ect

    def __init__(self, x, y, largura, altura, hp_max):
        super().__init__()
        

        #posiçao e tamanho no mundo
        self.rect = pygame.Rect(x, y, largura, altura)
        self.no_chao = False
        self.olhando_dir = True
        #velocidade em pixeis 
        self.vel = pygame.Vector2(0,0)

        #vida 
        self.hp_max = hp_max
        self.hp = hp_max
        self.vivo = True
 
        #stamina
        self.stamina_max = Stamina_max
        self.stamina = Stamina_max
        self.stamina_delay = 0 #o contador espara pra recarrega


        #frames de invencibilidade apos ser hitado
        self.invencivel = False
        self.timer_invenc = 0
        self.Frames_ivenc = 30 #quantidade de frames de invencibilidade

    #Gravidade 
    def aplicar_gravidade(self):
        #adicionar a gravidade no jogo, sendo ela a velocida vertical,e tambem adicionar o limite dela
        if self.no_chao:
            self.vel.y = 1
        else:
            self.vel.y = min(self.vel.y + Gravidade, Max_Fall_Speed)
    
    #COLISAO
    def mover_com_colisão(self, rects_solidos):
        #move o rect pelo os eixos separadamente 

        #eixo x

        self.rect.x += int(self.vel.x)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.x > 0:      #indo para direita
                    self.rect.right = tile.left
                elif self.vel.x < 0:
                    self.rect.left = tile.right #indo para esquerda
                self.vel.x = 0 

        #eixo y
        self.no_chao = False
        self.rect.y += int(self.vel.y)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:      #caindo
                    self.rect.bottom = tile.top
                    self.no_chao = True
                    self.vel.y = 0
                elif self.vel.y < 0:    #subindo(bateu no teto)
                    self.rect.top = tile.bottom
                    self.vel.y = 0 
        if self.no_chao:
            self.vel.y = 0

    #Dano/combante
    def receber_dano(self, quantidade, frames_invenc=None):
        #Reduz o hp. se tiver invencivel = ignora. apos levar dano = frames de invecibilidade

        if self.invencivel or not self.vivo:
            
            return
        
        self.hp -= quantidade

        if self.hp <= 0:
            self.hp = 0
            self.vivo = False
        else:
            #ativar os frames de invencibilidade
            self.invencivel = True
            self.timer_invenc = frames_invenc if frames_invenc is not None else self.Frames_ivenc 

    def atualizar_invencibilidade(self):
        #conta a quantidade de frames da invencibilidade

        if self.invencivel:
            self.timer_invenc -= 1
            if self.timer_invenc <= 0:
                self.invencivel = False