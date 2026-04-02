import pygame
from settings import Tile_size, Registro_ID, Tile_vazio

class Tilemap:
    #calcula a fisica dos blocos, danos e desenha na tela

    def __init__(self, grid):
        self.grid = grid
        self.linhas = len(grid)
        self.colunas = len(grid[0]) if self.linhas > 0 else 0

        #calcula o rect de colisao dos blocos 

        self.rect_solidos = self._calcular_rects_solidos()
        self.rects_dano = self._calcular_rects_dano()

        #pré calculo

    def _calcular_rects_solidos(self):
        #percorre a lista de grid e criar um pygame.rect para cada tile que bloqueia passagem solid=True
        
        rects = []
        for linha_i, linha in enumerate(self.grid):
            for col_i, tile_id in enumerate(linha):
                tile = Registro_ID.get(tile_id)
                if tile and tile.solid:
                    rects.append(pygame.Rect(
                        col_i * Tile_size,
                        linha_i * Tile_size,
                        Tile_size,
                        Tile_size
                    ))
        return rects
    
    def _calcular_rects_dano(self):
        #cria os rects para tile que geram dano, tipo os espinhos
        rects = []
        for linha_i, linha in enumerate(self.grid):
            for col_i, tile_id in enumerate(linha):
                tile = Registro_ID.get(tile_id)
                if tile and tile.damage > 0:
                    rects.append((
                        pygame.Rect(
                            col_i  * Tile_size,
                            linha_i * Tile_size,
                            Tile_size,
                            Tile_size
                        ),
                        tile.damage   # guarda o dano junto com o rect
                    ))
        return rects

    #desenhar
    def desenhar(self, tela, camera):
        #desenhar apenas os tiles vivisives pela a camera, para evita sobrecarregamento no progama

        #calcular a quantidade de tiles na tela
        cam_x = int(camera.offset.x)
        cam_y = int(camera.offset.y)

        col_inicio = max(0, cam_x // Tile_size)
        col_fim = min(self.colunas, col_inicio + tela.get_width() // Tile_size + 2)

        linha_inicio = max(0, cam_y // Tile_size)
        linha_fim = min(self.linhas, linha_inicio + tela.get_height() // Tile_size + 2)

        #desenhar só a quantidade na tela 
        for linha_i in range(linha_inicio, linha_fim):
            for col_i in range(col_inicio, col_fim):
                
                tile_id = self.grid[linha_i][col_i]

                if tile_id == Tile_vazio:
                    continue #o tile vazio não desenhar nada

                tile = Registro_ID.get(tile_id)
                if tile is None:
                    continue

                #posiçao no mundo
                rect_mundo = pygame.Rect(
                    col_i * Tile_size,
                    linha_i * Tile_size,
                    Tile_size,
                    Tile_size
                )

                #converte para a posição na tela usando a camera
                rect_tela = camera.aplicar(rect_mundo)

                #o tile sabe se desenhar - cada tipo tem seu visual
                tile.draw(tela, rect_tela)
    
    #consulta uteis

    def get_tile(self, col, linha):
        if 0 <= linha < self.linhas and 0 <= col < self.colunas:
            return self.grid[linha][col]
        return 1 #fora do mapa= parede
    
    def remover_tile(self, col, linha):
        #remove um tile do mapa exemplo: um bau aberto ou uma parede quebrada

        if 0 <= linha < self.linhas and 0 <= col < self.colunas:
            self.grid[linha][col] = Tile_vazio

            #recalcular as colisoes pois o mapa mudou
            self.rect_solidos = self._calcular_rects_solidos()
            self.rects_dano = self._calcular_rects_dano()