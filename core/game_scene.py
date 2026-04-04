import pygame
from settings import *
from world.tile_map import Tilemap
from world.rooms import Salas, spwans, Inimigos_por_sala, Conexoes
from core.camera_player import Camera
from entities.player import Player
from entities.enemy import Enemy
from ui.hud import Hud


class Gamescene:
    #centraliza toda a logica do jogo, mapa, inimigo e etc, para alivar e organiza o arquivo main.py
    
    def __init__(self, tela):
        self.tela = tela 
        self.hud = Hud()
        #cria o hud e reeutilizar ele em outras salas
        self.player = Player(0, 0)
        self.player.tem_espada = True #temporario enquanto nao adiciono uma forma de obter a espada

        #carrega a sala
        self._carregar_sala("calabouço_2")


    #CARREGA A SALA 

    def _carregar_sala(self, nome_sala, posiçao_spwan= None):
        #carrega um novo mapa e reposiciona o player

        self.sala_atual = nome_sala

        #monta o tilemap com o grid das salas
        grid = Salas[nome_sala]
        self.mapa = Tilemap(grid)

        #ajuste da camera para o mapa novo
        largura_mapa = len(grid[0]) * Tile_size
        altura_mapa = len(grid) * Tile_size
        self.camera = Camera(largura_mapa, altura_mapa)

        #posiçao do spwan
        if posiçao_spwan is None:
            col, linha = spwans[nome_sala]
        else:
            col, linha = posiçao_spwan

        self.player.rect.x = col * Tile_size
        self.player.rect.y = linha * Tile_size
        self.player.vel.xy = (0, 0) #isso zerar a velocida ao trocar de sala

        #criar os inimigos na sala
        self.inimigos = []
        for dados in Inimigos_por_sala.get(nome_sala, []):
            col_in, lin_in, pat_esq, pat_dir = dados
            x = col_in * Tile_size
            y = lin_in * Tile_size
            self.inimigos.append(Enemy(x, y, pat_esq, pat_dir))

    
    #ATUALIZAR  
    def atualizar(self, eventos):
        teclas = pygame.key.get_pressed()
        pos_mouse = pygame.mouse.get_pos()
        pos_mouse_mundo = self.camera.mouse_para_mundo(pos_mouse)

        rects_solidos = self.mapa.rect_solidos

        #atualizar o player
        self.player.atualizar(rects_solidos, self.camera, pos_mouse_mundo)

        #atualizar inimigos
        for inimigo in self.inimigos:
            inimigo.atualizar(rects_solidos, self.player)

        #verificar combante
        self._verificar_combante()

        #camera segue o player
        self.camera.atualizar(self.player.rect)

        #hud
        self.hud.atualizar()


    def _verificar_combante(self):
        #checa se o player acertou algum inimigo
        rect_ataque = self.player.get_rect_ataque()
        if rect_ataque is None:
            return

        for inimigo in self.inimigos:
            if not inimigo.vivo:
                continue
            
            if rect_ataque.colliderect(inimigo.rect):
                direçao = 1 if self.player.olhando_dir else -1
                inimigo.receber_hit(ataque_dano, direçao)
    
        #remove os inimigos mortos da lista inimigos
        self.inimigos = [in_ for in_ in self.inimigos if in_.vivo ]

    #DESENHAR   
    
    def desenhar(self):
        self.mapa.desenhar(self.tela, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera)

        self.player.desenhar(self.tela, self.camera)

        self.hud.desenhar(self.tela, self.player)  