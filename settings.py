import pygame

#constantes globaid

#janela do game
Telacheia_normal = False
Screen_widht = 1280
Screen_height = 720
FPS = 60
Titulo = "Profane Echo"

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
    
    def __init__(self, tile_id, solid, color, damage = 0 , lethal = False, folhas_variantes=None):
        self.title_id = tile_id 

        self.solid = solid

        self.color = color

        self.damage = damage

        self.lethal = lethal

        self.folhas_variantes_path = folhas_variantes

        self._variantes = None # lista de surface, cortadas sobe demanda

        
                
    def on_enter(self, player):
        
        if self.damage > 0:
            player.take_damage(self.damage)

    def _carregar_variantes(self):
        folha = pygame.image.load(self.folhas_variantes_path).convert_alpha()
        cols = folha.get_width() // Tile_size
        rows = folha.get_height() // Tile_size
        variantes = []
        for r in range(rows):
            for c in range(cols):
                pedaco = folha.subsurface((c * Tile_size, r * Tile_size, Tile_size, Tile_size))
                variantes.append(pedaco)
        return variantes








    def draw(self, tela, rect, col=0, linha=0):
        if self.folhas_variantes_path:
            if self._variantes is None:
                self._variantes = self._carregar_variantes()
            indice = (col * 7 + linha * 13) % len(self._variantes) # escolha determinística
            tela.blit(self._variantes[indice], rect)
        else:
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
    
    def draw(self, tela, rect, col=0, linha=0):
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

    def draw(self, tela, rect, col=0, linha=0):

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
    1: Tile(tile_id=1, solid=True, color=Stone_gray, folhas_variantes="assets/tileset/calabouco/parede_variantes.png"), #parede do calabouço
    2: Tile(tile_id=2, solid=True, color=(60, 60, 68), folhas_variantes="assets/tileset/calabouco/chao_variantes.png"), #chao calabouço
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
