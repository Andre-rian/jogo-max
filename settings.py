import pygame

# constantes globais

# janela do game
Telacheia_normal = False
Screen_widht = 1280
Screen_height = 720
FPS = 60
Titulo = "Profane Echo"

# Titulo
Tile_size = 32

# camera
ZOOM_PADRAO = 1.35      # mais proximo do player
ZOOM_BOSS = 1.0         # em luta contra o boss, desaproxima (mostra mais da arena)
ZOOM_SUAVIZAÇÃO = 0.08


# fisica player

Gravidade = 0.6

Max_Fall_Speed = 18

Speed_player = 4

player_pulo = -14

Dash_speed = 14

Dash_duration = 12

Dash_cooldown = 45

Double_tap_window = 18


# combate

ataque_range = 70

ataque_cooldown = 30

inimigo_knockback = 8


# cores legadas (ainda usadas por main/tiles/player)
Preto = (0, 0, 0)
Branco = (255, 255, 255)
Cinza_escuro = (30, 30, 35)
Stone_gray = (80, 80, 90)
stone_light = (110, 110, 120)
Torch_Orange = (200, 130, 50)
Vermelho_sangue = (160, 20, 20)
Dourado = (220, 180, 60)


# debug
DEBUG = False