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
        self.player.tem_espada = False 
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
        self.largura_mapa = len(grid[0]) * Tile_size
        self.altura_mapa = len(grid) * Tile_size
        self.camera = Camera(self.largura_mapa, self.altura_mapa)

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

        #atualizar a transiçao de cena
        self._checar_transiçao()

        #atualizar os baus
        self._checar_bau()

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
    
    def _checar_bau(self):
        #se o player encosta(provisorio) no bau:recebe o item , bau some, hud mostar a mensagem'
        teclas = pygame.key.get_pressed()

        for rect_bau, col, linha in self.mapa.rects_bau:
            if self.player.rect.colliderect(rect_bau):
                #esta perto do bau
                self.hud.mostra_mensagem("pressione E para abrir") #provisorio
                
                   
            if teclas[pygame.K_e]:
                self.player.tem_espada = True
                self.mapa.remover_tile(col, linha)
                self.hud.mostra_mensagem("espada encontrada")
                break




    #verificar passagem
    def _checar_transiçao(self):
        #verificar se o player saiu pela borda da sala e carrega a nova, se existir conexao é claro
        conexoes_sala = Conexoes.get(self.sala_atual, {})




        #direita
        if self.player.rect.right >= self.largura_mapa:
            proxima = conexoes_sala.get("direita")
            if proxima:
                #entra pela a esquerda da nova sala
                linha_spwan = spwans[proxima][1]
                self._carregar_sala(proxima, posiçao_spwan=(1, linha_spwan))

        #esquerda
        elif self.player.rect.left <= 0:
            proxima = conexoes_sala.get("esquerda")
            if proxima:
                #entra pela a direita da nova sala
                grid = Salas[proxima]
                ultima_col = len(grid[0]) - 2 # -2 para nao spwana dentro da parede
                linha_spwan = spwans[proxima][1]
                self._carregar_sala(proxima, posiçao_spwan=(ultima_col, linha_spwan))



    
    #DESENHAR   
    
    def desenhar(self):
        self.mapa.desenhar(self.tela, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera)

        self.player.desenhar(self.tela, self.camera)

        self.hud.desenhar(self.tela, self.player)  