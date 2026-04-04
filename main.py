import pygame
import sys
from settings import Screen_widht, Screen_height, FPS, Titulo, Telacheia_normal, Tile_size, ataque_dano
from core.camera_player import Camera
from world.tile_map import Tilemap
from world.rooms import Salas, spwans, Inimigos_por_sala
from entities.player import Player
from ui.hud import Hud
from entities.enemy import Enemy









class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(Titulo)

        self.tela_cheia = Telacheia_normal
        self.screen = self.Criar_janela()
        self.clock = pygame.time.Clock()

        #carrega sala 1
        grid = Salas['calabouço_2']
        self.mapa = Tilemap(grid)
        self.camera = Camera(len(grid[0]), len(grid))

        #rect temporario simulando o player
        spwan = spwans['calabouço_2']
        self.player = Player(
            spwan[0] * Tile_size,
            spwan[1] * Tile_size
        )
        self.inimigos = self._carregar_inimigos('calabouço_2')

        #adicionar o hud na tela
        self.hud = Hud()


    def Criar_janela(self):

        if self.tela_cheia:
            info = pygame.display.Info()
            largura = info.current_w
            altura = info.current_h
            return pygame.display.set_mode(
                (largura, altura),
                pygame.NOFRAME | pygame.SCALED
            )

        else:
            return pygame.display.set_mode(
                (Screen_widht, Screen_height), pygame.SCALED)
        

    def _Mudar_telacheia(self):

        self.tela_cheia = not self.tela_cheia
        self.screen = self.Criar_janela()

    def _carregar_inimigos(self, nome_sala):
        inimigos = []
        for col, linha, pat_esq, pat_dir in Inimigos_por_sala.get(nome_sala, []):
            e = Enemy(
                col * Tile_size,
                linha * Tile_size,
                pat_esq,
                pat_dir
            )
            inimigos.append(e)
        return inimigos

    def _verificar_combate(self):
        rect_atq = self.player.get_rect_ataque()
        if not rect_atq:
            return
        for inimigo in self.inimigos:
            if not inimigo.vivo:
                continue
            if rect_atq.colliderect(inimigo.rect):
                #knoback na direçao do ataque
                knockback = 1 if self.player.olhando_dir else -1 
                inimigo.receber_hit(ataque_dano, knockback)





    def rodar(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._Mudar_telacheia() 
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            #teclas temporarias
            pos_mouse_mundo = self.camera.mouse_para_mundo(pygame.mouse.get_pos())


            #atualizar a camera
            self.player.atualizar(
                self.mapa.rect_solidos,
                self.camera,
                pos_mouse_mundo
            )
            for inimigo in self.inimigos:
                inimigo.atualizar(self.mapa.rect_solidos, self.player)

            self._verificar_combate()
            self.hud.atualizar()
            self.camera.atualizar(self.player.rect)
            self.screen.fill((22, 20, 28))
            self.mapa.desenhar(self.screen, self.camera)


            #desenhar
            pos_tela = self.camera.aplicar(self.player.rect)
            self.player.desenhar(self.screen, self.camera)
            for inimigo in self.inimigos:
                inimigo.desenhar(self.screen, self.camera)
            self.hud.desenhar(self.screen, self.player)
            
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Jogo().rodar()