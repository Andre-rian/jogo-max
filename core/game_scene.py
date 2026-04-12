import pygame
import sys
from settings import *
from world.tile_map import Tilemap
from world.rooms import Salas, spwans, Inimigos_por_sala, Conexoes
from core.camera_player import Camera
from entities.projeteis.bomba import Bomba
from entities.projeteis.esporo_mushroom import EsporoMushroom
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye
from entities.player import Player
from entities.monsters.skeleton import Skeleton
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.flying_eye import FlyingEye
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
        self._dir_entrada = None
        self._carregar_sala("calabouço_1")
        self.player.defenir_checkpoint("calabouço_1")


        self.morrendo = False
        self.timer_morto = 0
        self.duraçao_morte = 180

        #projeteis  
        self.projeteis = []

        #menu de pausa
        self.pausado = False
        self.opçoes_pause = ["Continuar", "Salvar", "Sair"]
        self.opçoes_selecionadas = 0
    #CARREGA A SALA 

    def _carregar_sala(self, nome_sala, posiçao_spwan= None):
        #carrega um novo mapa e reposiciona o player

        self.sala_atual = nome_sala

        #monta o tilemap com o grid das salas
        grid = Salas[nome_sala]
        self.mapa = Tilemap(grid)

       #limpa os projeteis ao trocar de sala
        self.projeteis = []

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

        #resetar o time do cooldown ao trocar de sala
        self._cooldown_transiçao = 30

        #tipos dos inimigos
        _tipos_inimigos = {
            "skeleton" : Skeleton,
            "globin" : Globin,
            "mushroom" : Mushroom,
            "flying_eye": FlyingEye,

        }

        #criar os inimigos na sala
        self.inimigos = []
        for dados in Inimigos_por_sala.get(nome_sala, []):
            tipo, col_in, lin_in, pat_esq, pat_dir = dados
            x = col_in * Tile_size
            y = lin_in * Tile_size
            classe = _tipos_inimigos.get(tipo)
            if classe:
                self.inimigos.append(classe(x, y, pat_esq, pat_dir))

    
    #ATUALIZAR  
    def atualizar(self, eventos): 
        teclas = pygame.key.get_pressed()
        pos_mouse = pygame.mouse.get_pos()
        pos_mouse_mundo = self.camera.mouse_para_mundo(pos_mouse)

        if self.pausado:
            self._atualizar_pausa(eventos)
            return

        rects_solidos = self.mapa.rect_solidos

        #atuallizar o checar_morte
        self._checar_morte()

        #bloquueia os outros atualizar se o player estiver morto
        if self.morrendo:

            #atualizar o player
            self.player.atualizar(rects_solidos, self.camera, pos_mouse_mundo)

            #camera segue o player
            self.camera.atualizar(self.player.rect)

            #hud
            self.hud.atualizar()
            return

        #atualizar o player
        self.player.atualizar(rects_solidos, self.camera, pos_mouse_mundo)

        #atualizar a transiçao de cena
        self._checar_transiçao()

        #atualizar os baus
        self._checar_bau()

        #atualizar os espinhos
        self._checar_espinhos()






        #atualizar inimigos
        for inimigo in self.inimigos:
            inimigo.atualizar(rects_solidos, self.player)
            #pega as bombas spawnadas pelos globins e adiciona na lista de projeteis da sala
            if hasattr(inimigo, "bombas_spawnar") and inimigo.bombas_spawnar:
                self.projeteis.extend(inimigo.bombas_spawnar)
                inimigo.bombas_spawnar.clear()
            if hasattr(inimigo, "esporos_spawnar") and inimigo.esporos_spawnar:
                self.projeteis.extend(inimigo.esporos_spawnar)
                inimigo.esporos_spawnar.clear()
            if hasattr(inimigo, "projeteis_spawnar") and inimigo.projeteis_spawnar:
                self.projeteis.extend(inimigo.projeteis_spawnar)
                inimigo.projeteis_spawnar.clear()


        #verificar combante
        self._verificar_combante()

        #remove os imimigos mortos depois de tudo atualiza
        self.inimigos = [    in_ for in_ in self.inimigos
            if in_.vivo or (hasattr(in_, "_timer_morte") and in_._timer_morte > 0)
            ]
        #camera segue o player
        self.camera.atualizar(self.player.rect)

        #atualizar os projeteis
        for proj in self.projeteis:
            proj.atualizar(rects_solidos, self.player)

        #remove os projeteis inativos depois de atualizar
        self.projeteis = [p for p in self.projeteis if p.ativo]


        #hud
        self.hud.atualizar()


    def _atualizar_pausa(self, eventos):
        #navega o menu com as setas e confirma com enter
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_UP:
                    self.opçoes_selecionadas = (self.opçoes_selecionadas - 1) % len(self.opçoes_pause)
                
                elif evento.key == pygame.K_DOWN:
                    self.opçoes_selecionadas = (self.opçoes_selecionadas + 1) % len(self.opçoes_pause)

                elif evento.key == pygame.K_RETURN:
                    self._confirma_opçao_pausa()


    def _confirma_opçao_pausa(self):
        opçao = self.opçoes_pause[self.opçoes_selecionadas]

        if opçao == "Continuar":
            self.pausado = False
        elif opçao == "Salvar":
            self.hud.mostra_mensagem("sistema de saves em breve")
        elif opçao == "Sair":
            pygame.quit()
            sys.exit()

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

        #proteçao anti bug de teleporte da transiçao de fase
        conexoes_sala = Conexoes.get(self.sala_atual, {})

        # cooldown só bloqueia a direção de onde o player veio
        if hasattr(self, "_cooldown_transiçao") and self._cooldown_transiçao > 0:
            self._cooldown_transiçao -= 1
            if self._dir_entrada == "direita" and self.player.rect.left <= 0:
                return  # bloqueia só esquerda
            if self._dir_entrada == "esquerda" and self.player.rect.right >= self.largura_mapa:
                return  # bloqueia só direita

        # direita
        if self.player.rect.right >= self.largura_mapa:
            proxima = conexoes_sala.get("direita")
            if proxima:
                linha_spwan = spwans[proxima][1]
                self._carregar_sala(proxima, posiçao_spwan=(2, linha_spwan))
                self._dir_entrada = "direita"
                self._cooldown_transiçao = 60
                return

        # esquerda
        elif self.player.rect.left <= 0:
            proxima = conexoes_sala.get("esquerda")
            if proxima:
                grid = Salas[proxima]
                ultima_col = len(grid[0]) - 3
                linha_spwan = spwans[proxima][1]
                self._carregar_sala(proxima, posiçao_spwan=(ultima_col, linha_spwan))
                self._dir_entrada = "esquerda"
                self._cooldown_transiçao = 60
                return

    #sistema de dano nos espinhos para parkou
    def _checar_espinhos(self):
        for rect_dano, dano in self.mapa.rects_dano:
            if self.player.rect.colliderect(rect_dano):
                self.player.receber_dano(dano)
                break 
    


    def alternar_pausa(self):
        self.pausado = not self.pausado
        self.opçoes_selecionadas = 0 #reseta ao sair do menu
    #DESENHAR   
    
    def desenhar(self):
        self.mapa.desenhar(self.tela, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera)


            #debug do ngc do globin
            sr_inimigo = self.camera.aplicar(inimigo.rect)
            pygame.draw.rect(self.tela, (255, 0, 0), sr_inimigo, 2)


        for proj in self.projeteis:
            proj.desenhar(self.tela, self.camera)

        self.player.desenhar(self.tela, self.camera)
        sr_player = self.camera.aplicar(self.player.rect)
        pygame.draw.rect(self.tela, (0, 255, 0), sr_player, 2)
        self.hud.desenhar(self.tela, self.player)  

        #tela de morte - desenhada por cima de tudo
        if self.morrendo:
            self._desenhar_tela_morte()


        #tela de menu
        if self.pausado:
            self._desenhar_pausa()



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

    def _desenhar_pausa(self):
        #fundo semitrasnparente
        overlay = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0 , 160))
        self.tela.blit(overlay, (0, 0))


        fonte_titulo = pygame.font.SysFont("Georgia", 48, bold=True)
        fonte_opçao = pygame.font.SysFont("Georgia", 30)

        #titulo
        titulo = fonte_titulo.render("PAUSA", True, Dourado)
        self.tela.blit(titulo, (Screen_widht // 2 - titulo.get_width() // 2, 220))
        

        #opçoes
        for i, opçao in enumerate(self.opçoes_pause):
            selecionado = i == self.opçoes_selecionadas
            cor = Dourado if selecionado else Branco
            texto = fonte_opçao.render(opçao, True, cor)
            x = Screen_widht // 2 - texto.get_width() // 2
            y = 320 + i * 50

            #seta indicando a opçao selecionada
            if selecionado:
                seta = fonte_opçao.render("▶", True, Dourado)
                self.tela.blit(seta, (x - 30, y))

            self.tela.blit(texto, (x, y))