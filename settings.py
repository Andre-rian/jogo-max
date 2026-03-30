import pygame

#constantes globaid

#janela do game'
Screen_widht = 1280
Screen_height = 720
FPS = 60
Titulo = "Knight tales"

#Titulo
Titulo_size = 48


#fisica player

Gravidade = 0.6

Max_Fall_Speed = 18

Speed_player = 4

player_pulo = -14

Dash_speed = 14

Dash_duration = 12

Dash_cooldown = 45

Double_tap_window = 18


#combante

vida_max_player = 100

ataque_dano = 25

ataque_range = 70

ataque_cooldown = 30

inimigo_knockback = 8

#cores 


Preto = (0, 0, 0)
Branco = (255, 255, 255)
Cinza_escuro = (30,  30,  35)
Stone_gray = (80,  80,  90)
stone_light  = (110, 110, 120)
Torch_Orange = (200, 130, 50)
Vermelho_sangue = (160, 20,  20)
Dourado = (220, 180, 60)


#Classe do tile

class Tile:
    def __init__(self, tile_id, solid, color, damage = 0 , lethal = False):
        self.title_id = tile_id 

        self.solid = solid

        self.color = color

        self.damage = damage

        self.lethal = lethal
        
    def on_enter(self, player):
        
        if self.damage > 0:
            player.take_damage(self.damage)

    def drawn(self, tela, rect):

        pygame.draw(tela, self.color, rect)

        