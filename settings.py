import pygame

#constantes globaid

#janela do game
Telacheia_normal = False
Screen_widht = 1280
Screen_height = 720
FPS = 60
Titulo = "Knight tales"

#Titulo
Tile_size = 32


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

    def draw(self, tela, rect):

        pygame.draw.rect(tela, self.color, rect)


#tiles especiais,vão herda as caracteristicas de tile original
class Espinho(Tile):

    def __init__(self):
        super().__init__(
            tile_id=4,
            solid=False,
            color=(120, 20, 20),
            damage=20
        )
    
    def draw(self, tela, rect):
        
        pts = [
            (rect.centerx, rect.top + 4),
            (rect.right - 4, rect.bottom - 4),
            (rect.left + 4, rect.bottom - 4)]
        
        pygame.draw.polygon(tela, self.color, pts)

class Torcha(Tile):

    def __init__(self):

        super().__init__(
            tile_id=7,
            solid=False,
            color= Torch_Orange
        )

    def draw(self, tela, rect):

        #cabo da torcha
        pygame.draw.rect(tela, (100, 70, 30),
                          (rect.centerx - 3, rect.centery, 6, 16 ))

        #fogo da tocha
        pygame.draw.ellipse(tela, Torch_Orange, (rect.centerx - 7, rect.top + 8, 14, 18 ))

        pygame.draw.ellipse(tela, (255, 220, 80), (rect.centerx - 4, rect.top + 11, 8, 11 ))


#Registros = dicionarios de todos os ids/tile

#chave id =bau()
Registro_ID = {
    0: None, #nao desenhar nada
    1: Tile(tile_id=1, solid=True, color=Stone_gray), #parede do calabouço
    2: Tile(tile_id=2, solid=True, color=(60, 60, 68)), #chao calabouço
    3: Tile(tile_id=3, solid=False, color=(80, 60, 30)), #escada
    4: Espinho(), #espinho
    5: Tile(tile_id=5, solid=True, color=(90, 55, 20)), #porta
    6: None, #bau
    7: Torcha(), #torcha
    9: None, #fogueira

}


#Ids em ordem numerica pra não esquecer
Tile_vazio = 0
Tile_parede = 1
Tile_chão = 2
Tile_escada = 3
Tile_espinho = 4
Tile_porta = 5
Tile_bau = 6
Tile_torcha = 7
Tile_fogueira = 9
