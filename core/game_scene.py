import pygame
import sys
from settings import *
from core.inventario import Inventario
from world.tile_map import Tilemap
from world.rooms import Salas, spwans, Inimigos_por_sala, Conexoes, Drops_inimigos
from core.camera_player import Camera
from entities.projeteis.bomba import Bomba
from entities.projeteis.esporo_mushroom import EsporoMushroom
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye
from entities.projeteis.projetil_boss import ProjetilBoss
from entities.player import Player
from entities.objetos.bau import Bau

from entities.objetos.fogueira import Fogueira
from entities.monsters.skeleton import Skeleton
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.skeleton_boss import EsqueletoBoss
from ui.hud import Hud


class Gamescene:
    #centraliza toda a logica do jogo, mapa, inimigo e etc, para alivar e organiza o arquivo main.py
    
    def __init__(self, tela):
        self.tela = tela 
        self.hud = Hud()


        #cria o hud e reeutilizar ele em outras salas
        self.player = Player(0, 0)


        self._save_callback = None 


        #inventario
        self.inventario = Inventario(self.tela)


        #drops
        self.drops_por_sala = {} #nome_sala: [drops]

        self.inventario.callback_descartar = self._descartar_item

        #fogueiras
        self.fogueiras_ativas = set() #guarda as posiçoes das fogueiras ativas
        self.fogueiras = []

        #inimigos
        self.salas_visitadas = set() #salas que ja foram carregadas inimigos nao respwanams
        self.bosses_derrotados = set() #guarda os bosses que ja foram derrotados
        

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
        self._menu_callback = None #sera setado no main
        self.opçoes_pause = ["Continuar", "Inventário", "Salvar", "Menu principal", "Sair"]
        self.opçoes_selecionadas = 0
    #CARREGA A SALA 

    def _carregar_sala(self, nome_sala, posiçao_spwan= None):
        #carrega um novo mapa e reposiciona o player

        self.sala_atual = nome_sala

        #monta o tilemap com o grid das salas
        grid = Salas[nome_sala]
        self.mapa = Tilemap(grid)





        #ajusta os baus da sala
        self.baus = []
        for linha_idx, linha in enumerate(Salas[nome_sala]):
            for col_idx, tile in enumerate(linha):
                if tile == 6:
                    self.baus.append(Bau(
                        col_idx * Tile_size,
                        linha_idx * Tile_size,
                        col_idx, linha_idx,
                        id_item=1 #espada longa
                    ))

        #ajusta as fogueiras nas salas

        self.fogueiras = []
        for linha_idx, linha in enumerate(Salas[nome_sala]):
            for col_idx, tile in enumerate(linha):
                if tile == 9:
                    self.fogueiras.append(Fogueira(
                        col_idx * Tile_size,
                        linha_idx * Tile_size,
                        col_idx, linha_idx,
                        callback_descanso=self._descansar_fogueira
                    ))

        for fogueira in self.fogueiras:
            if (fogueira.col, fogueira.linha) in self.fogueiras_ativas:
                fogueira.ativa = True


        self.drops = self.drops_por_sala.get(nome_sala, [])

        #drop fixos da sala
        from entities.objetos.drop import Drop
        from world.rooms import Drops_fixos
        
        for dados in Drops_fixos.get(nome_sala, []):
            id_item, col_drop, lin_drop = dados 

            #chave unica para cada item fixo
            chave = (nome_sala, col_drop, lin_drop)
            if chave not in self.drops_fixos_coletados:
                if not nome_sala in self.drops_por_sala:
                    self.drops_por_sala[nome_sala] = []
                


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



        #criar os inimigos na sala
        if nome_sala not in self.salas_visitadas:
            self.salas_visitadas.add(nome_sala)
            self._spwanar_inimigos(nome_sala)
        else:
            self.inimigos = []
            self.boss_atual = None          #referencia do boss para passa para o hud, para criar a barra de vida
    
    
         #lista de rects da parede que some apos a derrota do boss
        
        #montar os rects da parede do boss
        self.parede_boss = []
        if self.sala_atual not in self.bosses_derrotados:
            for linha_idx, linha in enumerate(Salas[nome_sala]):
                for col_idx, tile in enumerate(linha):
                    if tile == 8:
                        self.parede_boss.append(pygame.Rect(
                            col_idx * Tile_size,
                            linha_idx * Tile_size,
                            Tile_size, Tile_size
                        ))

    
    #ATUALIZAR  
    def atualizar(self, eventos): 
        teclas = pygame.key.get_pressed()
        pos_mouse = pygame.mouse.get_pos()
        pos_mouse_mundo = self.camera.mouse_para_mundo(pos_mouse)

        if self.pausado:
            self._atualizar_pausa(eventos)
            

        rects_solidos = self.mapa.rect_solidos + self.parede_boss
        
        if self.inventario.aberto:
            self.inventario.atualizar(eventos, self.player)

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
        teclas = pygame.key.get_pressed()
        for bau in self.baus:
            bau.atualizar(self.player, teclas, self.mapa, self.hud)

        for drop in self.drops:
            drop.atualizar(self.player, teclas, self.hud)
        

        for fogueira in self.fogueiras:
            fogueira.atualizar(self.player, teclas, self.hud, self.sala_atual, self.fogueiras_ativas)

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


        pos_mouse = pygame.mouse.get_pos()
        fonte_opçao = pygame.font.SysFont("Georgia", 30)
        
        #houver com mouse
        for i, opçao in enumerate(self.opçoes_pause):
            texto = fonte_opçao.render(opçao, True, (255, 255, 255))
            x = Screen_widht // 2 - texto.get_width() // 2
            y = 320 + i * 50
            rect_opçao = pygame.Rect(x - 10, y - 5, texto.get_width() + 20, texto.get_height() + 10)
            if rect_opçao.collidepoint(pos_mouse):
                self.opçoes_selecionadas = i



        #navega o menu com as setas e confirma com enter
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_UP:
                    self.opçoes_selecionadas = (self.opçoes_selecionadas - 1) % len(self.opçoes_pause)
                
                elif evento.key == pygame.K_DOWN:
                    self.opçoes_selecionadas = (self.opçoes_selecionadas + 1) % len(self.opçoes_pause)

                elif evento.key == pygame.K_RETURN:
                    self._confirma_opçao_pausa()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: #clique esquerdo
                    self._confirma_opçao_pausa()


    def _confirma_opçao_pausa(self):
        opçao = self.opçoes_pause[self.opçoes_selecionadas]

        if opçao == "Continuar":
            self.pausado = False
        elif opçao == "Salvar":
            if self._save_callback:
                self._save_callback()
        elif opçao == "Menu principal":
            if self._menu_callback:
                self._menu_callback()
        elif opçao == "Inventário":
             self.inventario.abrir()
             self.pausado = False

        elif opçao == "Sair":
            pygame.quit()
            sys.exit()



    def _spwanar_inimigos(self, nome_sala):
        #tipos dos inimigos
        _tipos_inimigos = {
            "skeleton" : Skeleton,
            "globin" : Globin,
            "mushroom" : Mushroom,
            "flying_eye": FlyingEye,
            "esqueleto_boss": EsqueletoBoss,

        }

        self.inimigos = []
        self.boss_atual = None

        for dados in Inimigos_por_sala.get(nome_sala, []):
            tipo = dados[0]
            classe = _tipos_inimigos.get(tipo)
            if not classe:
                continue


            if tipo == "esqueleto_boss":
                
                if self.sala_atual in self.bosses_derrotados:
                    continue #boss ja morreu, nao respwana

                _, col_in, lin_in = dados       # só 3 valores, sem patrulha
                x = col_in * Tile_size
                y = lin_in * Tile_size
                boss = EsqueletoBoss(x, y, callback_morte=self._abrir_parede_boss)
                self.inimigos.append(boss)
                self.boss_atual = boss

            else:
                _, col_in, lin_in, pat_esq, pat_dir = dados
                x = col_in * Tile_size
                y = lin_in * Tile_size
                inimigo = classe(x, y, pat_esq, pat_dir)

                tabela = Drops_inimigos.get(tipo, [])
                if tabela:
                    def _fazer_callback(drops, sala):
                        def _callback(ix, iy):
                            import random
                            from entities.objetos.drop import Drop
                            print(f"callback morte chamado em {ix}, {iy}")
                            for chance, id_item in drops:
                                if random.random() < chance:
                                    print(f"dropando id_item={id_item}, drops={drops}")
                                    drop = Drop(ix, iy, id_item)
                                    if sala not in self.drops_por_sala:
                                        self.drops_por_sala[sala] = []

                                    self.drops_por_sala[sala].append(drop)
                                    
                                    self.drops = self.drops_por_sala[self.sala_atual]
                        return _callback
                    
                    inimigo.callback_morte = _fazer_callback(tabela, self.sala_atual)
                
                self.inimigos.append(inimigo) 




    def _descansar_fogueira(self):
        #reseta os inimigos das salas ja visitadas
        self.salas_visitadas.clear()

        #respwna os inimigos da sala atual
        self._spwanar_inimigos(self.sala_atual)




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
    

    def _abrir_parede_boss(self, x, y):
        self.parede_boss = []
        self.boss_atual = None
        self.bosses_derrotados.add(self.sala_atual)
        self.hud.mostra_mensagem("O caminho esta livre")


        from entities.objetos.drop import Drop
        
        drop = Drop(x, y, id_item=3)

        if self.sala_atual not in self.drops_por_sala:
            self.drops_por_sala[self.sala_atual] = []

        self.drops_por_sala[self.sala_atual].append(drop)
        self.drops = self.drops_por_sala[self.sala_atual]


    def _descartar_item(self, id_item):
        from entities.objetos.drop import Drop
        
        drop = Drop(self.player.rect.centerx, self.player.rect.bottom, id_item)

        if self.sala_atual not in self.drops_por_sala:
            self.drops_por_sala[self.sala_atual] = []

        self.drops_por_sala[self.sala_atual].append(drop)
        self.drops = self.drops_por_sala[self.sala_atual]
        
        self.drops.append(drop)

    def alternar_pausa(self):
        self.pausado = not self.pausado
        self.opçoes_selecionadas = 0 #reseta ao sair do menu
    
    def carregar_save(self, dados):
        self.fogueiras_ativas = dados["fogueiras_ativas"]
        self.bosses_derrotados = dados["bosses_derrotados"]
        if "inventario" in dados:
            self.player.inventario = dados["inventario"]
            
            #reequipar a arma se tiver
            if self.player.inventario["mao_direita"]:
                pass
        
        

        self.player.defenir_checkpoint(
            dados["checkpoint_sala"],
            x=dados["checkpoint_x"],
            y=dados["checkpoint_y"]
        )
        #carrega a sala do checkpoint
        self._carregar_sala(dados["checkpoint_sala"], posiçao_spwan=(dados["checkpoint_x"] // Tile_size,
                                                                     dados["checkpoint_y"] // Tile_size))   
    
    
    
    def salvar(self, save_manager, slot):
        #verificar se tem inimigo por perto, so pode salvar se nao estiver em combate
        for inimigo in self.inimigos:
            if inimigo.vivo:
                dist = abs(inimigo.rect.centerx - self.player.rect.centerx)
                if dist < 300:
                    self.hud.mostra_mensagem("Não é possivel salvar em combate")
                    return False
                

        save_manager.salvar(slot, self)
        self.hud.mostra_mensagem("Jogo salvo")
        return True
    
    #DESENHAR   
    
    def desenhar(self):
        self.mapa.desenhar(self.tela, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera)


            #debug do ngc do globin
            sr_inimigo = self.camera.aplicar(inimigo.rect)
            pygame.draw.rect(self.tela, (255, 0, 0), sr_inimigo, 2)

        for r in self.parede_boss:
            pygame.draw.rect(self.tela, (255, 80, 0), self.camera.aplicar(r), 2)


  

        for proj in self.projeteis:
            proj.desenhar(self.tela, self.camera)

        self.player.desenhar(self.tela, self.camera)
        sr_player = self.camera.aplicar(self.player.rect)

        for bau in self.baus:
            bau.desenhar(self.tela, self.camera)  

        for drop in self.drops:
            drop.desenhar(self.tela, self.camera)

        for fogueira in self.fogueiras:
            fogueira.desenhar(self.tela, self.camera)


        

        pygame.draw.rect(self.tela, (0, 255, 0), sr_player, 2)

        self.inventario.desenhar(self.player)

        self.hud.desenhar(self.tela, self.player, self.boss_atual)  

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