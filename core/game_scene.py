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
        self.player.defenir_checkpoint("calabouço_1")


        self.morrendo = False
        self.timer_morto = 0
        self.duraçao_morte = 180

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

        #atualizar os espinhos
        self._checar_espinhos()

        #atuallizar o checar_morte
        self._checar_morte()

        #bloquueia os outros atualizar se o player estiver morto
        if self.morrendo:

            #camera segue o player
            self.camera.atualizar(self.player.rect)

            #hud
            self.hud.atualizar()
            return


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

    

    def _checar_morte(self):
        #dectetar se o player morreu, se sim colocar o "voce morreu" na tela tipo dark souls

        if not self.player.vivo and not self.morrendo:
            #inicia o timer de morte
            self.morrendo = True
            self.timer_morto = self.duraçao_morte

        if self.morrendo:
            self.timer_morto -= 1
            if self.timer_morto <= 0:
                #respwana  no lugar do checkpoint, que ainda vai ser aprimorado
                self._carregar_sala(self.player.checkpoint_sala)
                self.player.respawnar()
                self.player.defenir_checkpoint(self.player.checkpoint_sala)
                self.morrendo = False

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


    #sistema de dano nos espinhos para parkou
    def _checar_espinhos(self):
        for rect_dano, dano in self.mapa.rects_dano:
            if self.player.rect.colliderect(rect_dano):
                self.player.receber_dano(dano)
                break 
    
    #DESENHAR   
    
    def desenhar(self):
        self.mapa.desenhar(self.tela, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera)

        self.player.desenhar(self.tela, self.camera)

        self.hud.desenhar(self.tela, self.player)  

        #tela de morte - desenhada por cima de tudo
        if self.morrendo:
            self._desenhar_tela_morte()

    def _desenhar_tela_morte(self):
        #fade escuro com o texto voce morreu centralizado

        progresso = 1 - (self.timer_morto / self.duraçao_morte)
        alpha = int(progresso * 200) #maximo 200 de 255, pra tela nao ficar toda preta

        #superfice transparente
        overlay = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0 , alpha))
        self.tela.blit(overlay, (0, 0))

        #texto so aparece depois do fade ta na metade
        if progresso > 0.4:
            fonte = pygame.font.SysFont("Georgia", 64, bold=True)
            texto = fonte.render("VOCÊ MORREU", True, Vermelho_sangue)
            x = Screen_widht // 2 - texto.get_width() // 2
            y = Screen_height // 2 - texto.get_height() // 2
            self.tela.blit(texto, (x, y))