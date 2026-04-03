import pygame
from entities.entity import Entity
from settings import Gravidade, Max_Fall_Speed

class Enemy(Entity):

    #estados do inimigo

    Patrulha = "patrulha"
    Perseguir = "perseguir"
    Atacando = "atacando"