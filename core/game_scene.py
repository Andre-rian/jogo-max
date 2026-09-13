import pygame
import sys
import logging
import unicodedata

logger = logging.getLogger(__name__)

from settings import *

from core.inventario import Inventario

from core.navegacao import hover_index

from world.tile_map import TileMap
from world.rooms import Salas
from world.niveis import spwans, Inimigos_por_sala, Conexoes, Drops_inimigos, Drops_fixos

from core.camera import Camera

from entities.projeteis.bomba import Bomba
from entities.projeteis.esporo_mushroom import EsporoMushroom
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye
from entities.projeteis.projetil_boss import ProjetilBoss

from entities.player import Player
from entities.objetos.bau import Bau
from entities.objetos.porta import Porta
from entities.objetos.drop_eco import DropEco

from entities.objetos.fogueira import Fogueira
from entities.objetos.tocha import Tocha, NOME_TILESET_TOCHA, FLAME_ROWS
from core.menu_fogueira import MenuFogueira

from entities.monsters.skeleton import Skeleton
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.skeleton_boss import EsqueletoBoss

from ui.hud import Hud
from ui.particulas import ParticulaEco
from ui.overlays import desenhar_tela_morte, desenhar_tela_pausa
from ui.estilo import Fonte_texto



# corrigi os key sensitives dos arquivos 
def _nome_arquivo_normalizado(nome):
    #remove acentos dos nomes das salas para monta os caminhos para o tmx
    nfdk = unicodedata.normalize('NFKD', nome)
    return ''.join(c for c in nfdk if not unicodedata.combining(c))







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


        #menu da fogueira
        self.menu_fogueira = MenuFogueira(self.tela, self.player, callback_descansar=self._descansar_fogueira, callback_fechar=self._fechar_menu_fogueira)


        #baus
        self.baus_abertos = set()

        #portas
        self.portas_abertas = set()

        #particulas do eco
        self.particulas_ecos = []

        #drops
        self.drops_por_sala = {} #nome_sala: [drops]

        self.drops_fixos_coletados = set() #chaves (nome_sala, linha) dos drops fixos ja coletados

        self.inventario.callback_descartar = self._descartar_item

        self.drops_ecos_por_sala = {}

        #fogueiras
        self.fogueiras_ativas = set() #guarda as posiçoes das fogueiras ativas
        self.fogueiras = []

        #inimigos
        self.inimigos_morto_por_sala = {} #salas que ja foram carregadas inimigos nao respwanams
        self.bosses_derrotados = set() #guarda os bosses que ja foram derrotados
        

        #carrega a sala
        self._dir_entrada = None
        self._entrada_lado = None  #lado da sala onde o player entrou (esquerda/direita)
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
        self._frame_pausa = 0

        #debug: mostra o que o engine considera plataforma/escada (F3 no jogo)
        self.debug_tiles = False
    

    



    #CARREGA A SALA 

    def _carregar_sala(self, nome_sala, posiçao_spwan=None, respawnando=False ):
        #carrega um novo mapa e reposiciona o player

        self.sala_atual = nome_sala

        #se existe um tmx para aquela sala usa ele, senao pular
        import os 
        caminho_tmx = f"assets/maps/{_nome_arquivo_normalizado(nome_sala)}.tmx"
        if os.path.exists(caminho_tmx):
            logger.info(f"[MAPA] carregando '{nome_sala}' via TMX: {caminho_tmx}")
            grid = TileMap.carregar_camada_tmx(caminho_tmx, "colisao")
            grid_decoracao = TileMap.carregar_camada_tmx(caminho_tmx, "decoracao")
            grid_fundo = TileMap.carregar_camada_tmx(caminho_tmx, "fundo")
            grid_escadas = TileMap.carregar_camada_tmx(caminho_tmx, "escadas")
            grid_plataformas = TileMap.carregar_camada_tmx(caminho_tmx, "plataformas")
            objetos_tmx = TileMap.carregar_objetos_tmx(caminho_tmx, "objetos")


            if grid is None:
                logger.warning(f"[MAPA] '{nome_sala}': camada 'colisao' ausente no TMX, caindo para o FALLBACK pythoi")
                grid = [linha[:] for linha in Salas[nome_sala]]
        else:
            logger.info(f"[MAPA] '{caminho_tmx}' Caminho TMX não encontrado - carregando '{nome_sala}' via PYTHON grid (Fallback)")
            grid = [linha[:] for linha in Salas[nome_sala]]
            grid_decoracao = None
            grid_fundo = None
            grid_escadas = None
            grid_plataformas = None
            objetos_tmx = None
        




    
        
        self.mapa = TileMap(grid, grid_decoracao, grid_fundo, grid_escadas, grid_plataformas)


        #tochas decorativas: uma tocha = um FOGO (linha 0 ou 2 da folha) + a HASTE
        #logo abaixo (linha seguinte). Só o fogo vira entidade (32x64 já com a haste);
        #as células do mapa que sobravam (fogo estático + haste) são removidas.
        self.tochas = []
        if grid_decoracao is not None:
            raizes = []
            for linha_idx_d, linha_d in enumerate(grid_decoracao):
                for col_idx_d, ref in enumerate(linha_d):
                    if ref is None or ref.tileset_nome != NOME_TILESET_TOCHA:
                        continue
                    if ref.linha in FLAME_ROWS:
                        raizes.append((col_idx_d, linha_idx_d, ref.linha))

            for col_idx_d, linha_idx_d, linha_folha in raizes:
                variante = "fraca" if linha_folha == 0 else "forte"
                self.tochas.append(Tocha(col_idx_d * Tile_size, linha_idx_d * Tile_size,
                                         col_idx_d, linha_idx_d, variante=variante))
                grid_decoracao[linha_idx_d][col_idx_d] = None
                if linha_idx_d + 1 < len(grid_decoracao):
                    embaixo = grid_decoracao[linha_idx_d + 1][col_idx_d]
                    if embaixo is not None and embaixo.tileset_nome == NOME_TILESET_TOCHA:
                        grid_decoracao[linha_idx_d + 1][col_idx_d] = None
        if objetos_tmx is not None:
            for obj in objetos_tmx:
                if obj["tipo"] != "tocha":
                    continue
                col_idx, linha_idx = obj["col"], obj["linha"]
                variante = obj["propriedades"].get("variante", "forte")
                self.tochas.append(Tocha(col_idx * Tile_size, linha_idx * Tile_size,
                                         col_idx, linha_idx, variante=variante))





        #ajusta os baus da sala
        self.baus = []

        if objetos_tmx is not None:
            logger.info(f"[MAPA] '{nome_sala}': baús via Objetc Layer do tiled")
            for obj in objetos_tmx:
                if obj["tipo"] != "bau":
                    continue

                col_idx, linha_idx = obj["col"],  obj["linha"]
                if (col_idx, linha_idx) in self.baus_abertos:
                    continue

                try:
                    id_item = int(obj["propriedades"].get("id_item", 1))
                except (TypeError, ValueError):
                    logger.warning(f"[MAPA] baú em ({col_idx},{linha_idx}) com id_item inválido, usando 1")    
                    id_item = 1


                bau = Bau(
                col_idx * Tile_size,
                linha_idx * Tile_size,
                col_idx, linha_idx,
                id_item=id_item        
                )
                bau.callback_aberto = self._registrar_bau_aberto
                self.baus.append(bau)
 

        else:
            for linha_idx, linha in enumerate(Salas[nome_sala]):
                    for col_idx, tile in enumerate(linha):
                        if tile == 6:
                            if (col_idx, linha_idx) in self.baus_abertos:
                                continue
                            
                            bau = Bau(
                                col_idx * Tile_size,
                                linha_idx * Tile_size,
                                col_idx, linha_idx,
                                id_item=1
                            )
                            bau.callback_aberto = self._registrar_bau_aberto
                            self.baus.append(bau)




        #ajusta as portas na sala
        self.portas = []
        if objetos_tmx is not None:
            for obj in objetos_tmx:
                if obj["tipo"] != "porta":
                    continue

                col_idx, linha_idx = obj["col"], obj["linha"]
                porta = Porta(
                    col_idx * Tile_size,
                    linha_idx * Tile_size,
                    col_idx, linha_idx
                )
                if (col_idx, linha_idx) in self.portas_abertas:
                    porta.aberta = True

                self.portas.append(porta)






        #ajusta as fogueiras nas salas

        self.fogueiras = []
        for linha_idx, linha in enumerate(Salas[nome_sala]):
            for col_idx, tile in enumerate(linha):
                if tile == 9:
                    fogueira = Fogueira(
                        col_idx * Tile_size,
                        linha_idx * Tile_size,
                        col_idx, linha_idx,
                        callback_descanso=self._descansar_fogueira
                    )
                    fogueira._callback_abrir_menu = self._abrir_menu_fogueira
                    logger.debug(f"setado na fogueira id={id(fogueira)}, col={fogueira.col}")
                    self.fogueiras.append(fogueira)

        for fogueira in self.fogueiras:
            if (fogueira.col, fogueira.linha) in self.fogueiras_ativas:
                fogueira.ativa = True
        


        self.drops = self.drops_por_sala.get(nome_sala, [])




        #drop fixos da sala
        from entities.objetos.drop import Drop

        for dados in Drops_fixos.get(nome_sala, []):
            id_item, col_drop, lin_drop = dados 

            #chave unica para cada item fixo
            chave = (nome_sala, col_drop, lin_drop)
            if chave not in self.drops_fixos_coletados:
                if not nome_sala in self.drops_por_sala:
                    self.drops_por_sala[nome_sala] = []

                #evita duplica se a sala ja foi carregada antes
                ja_existe = any(
                    d.rect.centerx == col_drop * Tile_size and
                    d.rect.centery == lin_drop * Tile_size
                    for d in self.drops_por_sala[nome_sala]
                )

                if not ja_existe:
                    drop = Drop(col_drop * Tile_size, lin_drop * Tile_size, id_item)
                    drop.chave_fixa = chave #marca o drop como fixo 
                    drop.callback_coletado = self._registrar_drop_fixo_coletado
                    self.drops_por_sala[nome_sala].append(drop)
                
                self.drops = self.drops_por_sala.get(nome_sala, [])


       #limpa os projeteis ao trocar de sala
        self.projeteis = []

        #ecos que ficam no chao ao morrer
        drop_eco = self.drops_ecos_por_sala.get(nome_sala)
        self.drops_ecos = [drop_eco] if drop_eco and drop_eco.ativo else []







        #ajuste da camera para o mapa novo
        self.largura_mapa = len(grid[0]) * Tile_size
        self.altura_mapa = len(grid) * Tile_size
        self.camera = Camera(self.largura_mapa, self.altura_mapa)

    #posiçao do spwan
        spwans_tmx = {}
        if objetos_tmx is not None:
            for obj in objetos_tmx:
                if obj["tipo"] != "spwan":
                    continue
                nome_spwan =  obj["propriedades"].get("nome") or "default"
                spwans_tmx[nome_spwan] = (obj["col"], obj["linha"])



        
        if not respawnando:
            if posiçao_spwan is not None:
                col, linha = posiçao_spwan
            else:
                col, linha = self._resolver_spwan(nome_sala, grid, spwans_tmx)
                print(f"[SANITY] spawn bruto={spwans_tmx}, resolvido=({col},{linha})")
            self.player.rect.x = col * Tile_size
            self.player.rect.y = linha * Tile_size
            self.player.vel.xy = (0, 0)

        #resetar o time do cooldown ao trocar de sala
        self._cooldown_transiçao = 30



        self.inimigos = []
        self.boss_atual = None

        _tipos_inimigos = {
            "skeleton": Skeleton,
            "globin": Globin,
            "mushroom": Mushroom,
            "flying_eye": FlyingEye,
            "esqueleto_boss": EsqueletoBoss,
        }

        if objetos_tmx is not None:
            mortos = self.inimigos_morto_por_sala.get(nome_sala, [])

            for obj in objetos_tmx:
                if obj["tipo"] != "inimigo":
                    continue

                tipo = obj["propriedades"].get("tipo")
                classe = _tipos_inimigos.get(tipo)
                if not classe:
                    logger.warning(
                        f"[MAPA] tipo de inimigo '{tipo}' desconhecido no objeto id={obj['id']}, ignorando"
                    )
                    continue

                indice = obj["id"] #id nativo do tiled
                col_idx, linha_idx = obj["col"], obj["linha"]
                x, y = col_idx * Tile_size, linha_idx * Tile_size

                if tipo == "esquelo_boss":
                    if self.sala_atual in self.bosses_derrotados:
                        continue

                    boss = EsqueletoBoss(x, y, callback_morte=self._abrir_parede_boss)
                    boss._indice_spawn = indice
                    self.inimigos.append(boss)
                    self.boss_atual = boss
                    continue

                if indice in mortos:
                    continue

                try:
                    pat_esq = int(obj["propriedades"].get("patrulha_esq", 0))
                    pat_dir = int(obj["propriedades"].get("patrulha_dir", 0))
                except (TypeError, ValueError):
                    logger.warning(f"[MAPA] patrulha inválida no objeto inimigo id={indice}, usando 0/0")
                    pat_esq, pat_dir = 0, 0

                inimigo = classe(x, y, pat_esq, pat_dir)
                inimigo._indice_spawn = indice

                tabela = Drops_inimigos.get(tipo, [])
                if tabela:
                    inimigo.callback_morte = self._fazer_callback_drop_inimigo(tabela, self.sala_atual)

                self.inimigos.append(inimigo)
        else:
            self._spwanar_inimigos(nome_sala)  # fallback python, comportamento atual intacto

     
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

    def _fazer_callback_drop_inimigo(self, drops, sala):
        def _callback(ix, iy):
            import random
            from entities.objetos.drop import Drop
            for chance, id_item in drops:
                if random.random() < chance:
                    drop = Drop(ix, iy, id_item)
                    if sala not in self.drops_por_sala:
                        self.drops_por_sala[sala] = []
                    self.drops_por_sala[sala].append(drop)
                    self.drops = self.drops_por_sala[self.sala_atual]
        return _callback










    def _resolver_spwan(self, nome_sala, grid, spwans_tmx):
        #define a posiçao inicial do player ao entrar numa sala
        #prioriza o spwan do TMX (default ou o do lado onde se entra), 
        #depois o lado da entrada com a config de fallback
        # em qualquer caso valida a posição final contra a grade de colisao
        # pra garantir que o player nasça de pé, nunca enterrado

        lado = getattr(self, "_entrada_lado", None)

        if spwans_tmx:
            if lado is not None and lado in spwans_tmx:
                return spwans_tmx[lado]
            if spwans_tmx.get("default") is not None:
                return spwans_tmx["default"]
            else:
                logger.warning(
                    f"[SPAWN] '{nome_sala}': TMX tem spawns mas nenhum bate com "
                    f"lado='{lado}' nem 'default', usando fallback de grade"
                )
                col, linha = self._spwanar_fallback(nome_sala, grid, lado)
        else:
            logger.warning(
                f"[SPAWN] '{nome_sala}': sem spawns no TMX (layer 'objetos' ausente "
                f"ou sem objeto tipo 'spwan'), usando fallback de grade"
            )
            col, linha = self._spwanar_fallback(nome_sala, grid, lado)

                        
        col_final, linha_final = self._spwan_fallback_grid(nome_sala, grid, lado)
                
        if (col_final, linha_final) != (col, linha):
            logger.info(
                f"[SPAWN] '{nome_sala}': posiçao bruta ({col},{linha}) ajustada "
                f"para ({col_final},{linha_final}) pelo _spawn_seguro"
            )
        else:
            logger.info(f"[SPAWN] '{nome_sala}': posiçao resolvida ({col_final},{linha_final})")

        return col_final, linha_final


    def _spwan_fallback_grid(self, nome_sala, grid, lado):
        # spwan vindo da grade pythob
        
        ponto = spwans.get(nome_sala, (2, 10))
        if lado == "esquerda":
            return 2, ponto[1]
        if lado == "direita":
            return len(grid[0]) -3, ponto[1]
        return ponto 


    def _spawn_seguro(self, col, linha, grid, max_ajuste=8):
        # garante que o bloco 2x2 do player (64x64) nasça numa área livre
        # com chão sólido embaixo - nunca enterrado, nunca dentro de parede,
        # nunca flutuando sobre um buraco.
        # aceita tanto grade TMX (celulas TileRef/None) quanto grade fallback
        # python (celulas int, onde 0 = vazio).
        altura_mapa = len(grid)
        largura_mapa = len(grid[0]) if altura_mapa else 0

        def _solido(c, l):
            if l < 0 or l >= altura_mapa or c < 0 or c >= largura_mapa:
                return True  # fora do mapa conta como parede, nunca spawna pra fora
            valor = grid[l][c]
            if valor is None:
                return False
            if isinstance(valor, int):
                return valor != 0
            return True  # TileRef presente na camada de colisao = solido

        def _bloco_livre(c, l):
            # player ocupa colunas c,c+1 e linhas l,l+1 (2x2 tiles = 64x64)
            return not any(_solido(c + dc, l + dl) for dc in (0, 1) for dl in (0, 1))

        def _tem_chao(c, l):
            # ha solo logo abaixo do bloco (linha l+2)?
            return _solido(c, l + 2) or _solido(c + 1, l + 2)

        col = max(0, min(col, largura_mapa - 2))
        linha_original = linha

        # 1) se nasceu enterrado ou dentro de parede, sobe ate o bloco ficar livre
        ajustes = 0
        while not _bloco_livre(col, linha) and ajustes < max_ajuste:
            linha -= 1
            ajustes += 1

        # 2) se ficou flutuando sem chao embaixo (ex: caiu num buraco), desce ate achar piso
        ajustes = 0
        while _bloco_livre(col, linha) and not _tem_chao(col, linha) and ajustes < max_ajuste:
            linha += 1
            ajustes += 1

        if not _bloco_livre(col, linha):
            logger.warning(
                f"[SPAWN] não foi possível achar um bloco livre perto de "
                f"col={col}, linha={linha_original} (tentativas esgotadas); "
                f"usando ({col},{linha}) mesmo assim"
            )

        return col, linha


    def _registrar_drop_fixo_coletado(self, chave):
        if chave:
            self.drops_fixos_coletados.add(chave)










    #ATUALIZAR  
    def atualizar(self, eventos): 
        teclas = pygame.key.get_pressed()

        #F3 liga/desliga o debug de plataforma/escada
        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F3:
                self.debug_tiles = not self.debug_tiles

        if self.menu_fogueira.aberto:
            self.menu_fogueira.atualizar(eventos)
            return


        if self.pausado:
            self._atualizar_pausa(eventos)
            

        rects_solidos = self.mapa.rects_solidos + self.parede_boss + [p.rect for p in self.portas if not p.aberta]
        
        if self.inventario.aberto:
            self.inventario.atualizar(eventos, self.player)

        #atuallizar o checar_morte
        self._checar_morte()

        #bloquueia os outros atualizar se o player estiver morto
        if self.morrendo:
            #atualizar o player
            self.player.atualizar(rects_solidos, self.camera,
                                  rects_plataforma=self.mapa.rects_plataforma,
                                  rects_escada=self.mapa.rects_escada)

            #camera segue o player
            self._atualizar_zoom_camera()
            self.camera.atualizar(self.player.rect)

            #hud
            self.hud.atualizar()
            return

        #atualizar o player
        self.player.atualizar(rects_solidos, self.camera,
                              rects_plataforma=self.mapa.rects_plataforma,
                              rects_escada=self.mapa.rects_escada)

        #atualizar a transiçao de cena
        self._checar_transiçao()

        #atualizar os baus
        teclas = pygame.key.get_pressed()
        for bau in self.baus:
            bau.atualizar(self.player, teclas, self.mapa, self.hud)

        for drop in self.drops:
            drop.atualizar(self.player, teclas, self.hud)

        for drop in self.drops_ecos:
            drop.atualizar(self.player, teclas, self.hud)
        self.drops_ecos = [d for d in self.drops_ecos if d.ativo]
        

        for fogueira in self.fogueiras:
            fogueira.atualizar(self.player, teclas, self.hud, self.sala_atual, self.fogueiras_ativas)

        for porta in self.portas:
            porta.atualizar(self.player, teclas, self.hud, self.portas_abertas)

        for tocha in self.tochas:
            tocha.atualizar()

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
        vivos = []
        for in_ in self.inimigos:
            if in_.vivo or (hasattr(in_, "_timer_morte") and in_._timer_morte > 0):
                vivos.append(in_)
            else:
                if hasattr(in_, "_indice_spawn"):
                    if self.sala_atual not in self.inimigos_morto_por_sala:
                        self.inimigos_morto_por_sala[self.sala_atual] = []

                    self.inimigos_morto_por_sala[self.sala_atual].append(in_._indice_spawn)

                if in_.ecos_drop > 0:
                    self.player.ecos += in_.ecos_drop
                    #spwanar as particulas 
                    for _ in range(in_.ecos_drop // 3): #quantidade propocional aos ecos
                        self.particulas_ecos.append(ParticulaEco(in_.rect.centerx, in_.rect.centery))

        player_cx = self.player.rect.centerx
        player_cy = self.player.rect.centery
        
        for p in self.particulas_ecos:
            p.atualizar(player_cx, player_cy)
        
        self.particulas_ecos = [p for p in self.particulas_ecos if p.ativo]
        self.inimigos = vivos
        
        
        #camera segue o player
        self._atualizar_zoom_camera()
        self.camera.atualizar(self.player.rect)

        #atualizar os projeteis
        for proj in self.projeteis:
            proj.atualizar(rects_solidos, self.player)

        #remove os projeteis inativos depois de atualizar
        self.projeteis = [p for p in self.projeteis if p.ativo]


        #hud
        self.hud.atualizar()


    def _atualizar_zoom_camera(self):
        #aproxima a camera no dia a dia; em luta de boss ela desaproxima
        lutando = self.boss_atual is not None and self.boss_atual.vivo
        self.camera.zoom_alvo = ZOOM_BOSS if lutando else ZOOM_PADRAO


    def _atualizar_pausa(self, eventos):


        pos_mouse = pygame.mouse.get_pos()
        fonte_opçao = Fonte_texto(28)

        itens_com_rect = []
        
        #houver com mouse
        for i, opçao in enumerate(self.opçoes_pause):
            texto = fonte_opçao.render(opçao, True, (255, 255, 255))
            x = Screen_widht // 2 - texto.get_width() // 2
            y = 320 + i * 50
            rect_opçao = pygame.Rect(x - 10, y - 5, texto.get_width() + 20, texto.get_height() + 10)
            itens_com_rect.append((i, rect_opçao))


        indice_houver = hover_index(eventos, pos_mouse, itens_com_rect)   
        if indice_houver is not None:
            self.opçoes_selecionadas = indice_houver

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
        mortos = self.inimigos_morto_por_sala.get(nome_sala, [])

        for i, dados in enumerate(Inimigos_por_sala.get(nome_sala, [])):
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
                boss._indice_spawn = i  #marca o boss com um indice para rastrear se ele morreu
                self.inimigos.append(boss)
                self.boss_atual = boss

            else:
                if i in mortos:
                    continue

                _, col_in, lin_in, pat_esq, pat_dir = dados
                x = col_in * Tile_size
                y = lin_in * Tile_size
                inimigo = classe(x, y, pat_esq, pat_dir)
                inimigo._indice_spawn = i  #marca o inimigo com um indice para rastrear se ele morreu

                tabela = Drops_inimigos.get(tipo, [])
                if tabela:
                    def _fazer_callback(drops, sala):
                        def _callback(ix, iy):
                            import random
                            from entities.objetos.drop import Drop
                            for chance, id_item in drops:
                                if random.random() < chance:
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
        self.inimigos_morto_por_sala.clear()

        #curar o player e recarregar as poções
        self.player.hp = self.player.hp_max
        self.player.pocao.recarregar()


        #respwna os inimigos da sala atual
        self._spwanar_inimigos(self.sala_atual)

    def _fechar_menu_fogueira(self):
        self.menu_fogueira.aberto = False
        self.pausado = False


    def _abrir_menu_fogueira(self):
        logger.info("abrindo menu fogueira")
        self.menu_fogueira.abrir()
        


    def _verificar_combante(self):
        #checa se o player acertou algum inimigo
        rect_ataque = self.player.get_rect_ataque()
        if rect_ataque is None:
            return

        for inimigo in self.inimigos:
            if not inimigo.vivo:
                continue

            if inimigo in self.player._alvos_atingidos:
                continue #o inimigo ja foi acertado por esse golpe
            
            if inimigo.colide_mask_com_rect(rect_ataque):
                direçao = 1 if self.player.olhando_dir else -1
                inimigo.receber_hit(self.player.calcular_dano(), direçao)
                self.player._alvos_atingidos.add(inimigo)
    

    def _registrar_bau_aberto(self, col, linha):
        self.baus_abertos.add((col, linha))    



    

    def _checar_morte(self):
        #dectetar se o player morreu, se sim colocar o "voce morreu" na tela tipo dark souls

        if not self.player.vivo and not self.morrendo:
            #inicia o timer de morte
            self.morrendo = True
            self.timer_morto = self.duraçao_morte


            #cria o drop dos ecos no lugar da morte
            if self.player.ecos > 0:
                #remove se ja haver um 
                self.drops_ecos_por_sala.clear()
                #criar um novo

                drop = DropEco(self.player.rect.centerx, self.player.rect.bottom, self.player.ecos)
                self.drops_ecos_por_sala[self.sala_atual] = drop
                self.drops_ecos = [drop]
                self.player.ecos_perdidos = self.player.ecos
                self.player.ecos = 0

        if self.morrendo:
            self.timer_morto -= 1
            if self.timer_morto <= 0:
                #respwana  no lugar do checkpoint, que ainda vai ser aprimorado
                
                self.player.respawnar()
                self._carregar_sala(self.player.checkpoint_sala, respawnando=True)
                

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
                self._entrada_lado = "esquerda"  # entrando na proxima sala pela esquerda
                self._carregar_sala(proxima)
                self._dir_entrada = "direita"
                self._cooldown_transiçao = 60
                return

        # esquerda
        elif self.player.rect.left <= 0:
            proxima = conexoes_sala.get("esquerda")
            if proxima:
                self._entrada_lado = "direita"  # entrando na proxima sala pela direita
                self._carregar_sala(proxima)
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
        self.drops_fixos_coletados= dados.get("drops_fixos_coletados", set())
        self.baus_abertos = dados.get("baus_abertos", set())
        self.player.ecos = dados.get("ecos", 0)
        
        drop_eco_data = dados.get("drop_eco")

        if drop_eco_data:
            from entities.objetos.drop_eco import DropEco
            drop = DropEco(drop_eco_data["x"], drop_eco_data["y"], drop_eco_data["quantidade"])
            self.drops_ecos_por_sala[drop_eco_data["sala"]] = drop

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
        self._carregar_sala(dados["checkpoint_sala"], respawnando=True)
        self.player.respawnar()   
    
    
    
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
        self._frame_pausa += 1

        #a cena do mundo é desenhada numa superficie do tamanho da area visivel
        #(Screen / zoom) e depois escalada pra tela - é isso que aproxima a camera
        vw = max(1, int(round(Screen_widht / self.camera.zoom)))
        vh = max(1, int(round(Screen_height / self.camera.zoom)))
        vista = pygame.Surface((vw, vh))
        vista.fill((0, 0, 0))

        self.mapa.desenhar(vista, self.camera)

        for tocha in self.tochas:
            tocha.desenhar(vista, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(vista, self.camera)


            if DEBUG:
                #debug dos rects dos inimigos
                sr_inimigo = self.camera.aplicar(inimigo.rect)
                pygame.draw.rect(vista, (255, 0, 0), sr_inimigo, 2)

                #mostra a mask (azul)
                if getattr(inimigo, "mask", None) and hasattr(inimigo, "_mask_pos"):
                    mx, my = inimigo._mask_pos
                    pontos = inimigo.mask.outline(2)
                    if pontos:
                        pontos_tela = [self.camera.aplicar(pygame.Rect(mx + px, my + py, 1, 1)).topleft for px, py in pontos]
                        pygame.draw.polygon(vista, (0, 200, 255), pontos_tela, 1)

                #DEBUG: contorno real da mask do player
                if getattr(self.player, "mask", None) and hasattr(self.player, "_mask_pos"):
                    mx, my = self.player._mask_pos
                    pontos = self.player.mask.outline(2)
                    if pontos:
                        pontos_tela = [self.camera.aplicar(pygame.Rect(mx + px, my + py, 1, 1)).topleft for px, py in pontos]
                        pygame.draw.polygon(vista, (0, 200, 255), pontos_tela, 1)

        if DEBUG:
            for r in self.parede_boss:
                pygame.draw.rect(vista, (255, 80, 0), self.camera.aplicar(r), 2)



        for proj in self.projeteis:
            proj.desenhar(vista, self.camera)

        for p in self.particulas_ecos:
            p.desenhar(vista, self.camera)

        for porta in self.portas:
            porta.desenhar(vista, self.camera)

        self.player.desenhar(vista, self.camera)
        sr_player = self.camera.aplicar(self.player.rect)

        if self.debug_tiles:
            #verde = o que o engine considera plataforma one-way
            for r in self.mapa.rects_plataforma:
                sr = self.camera.aplicar(r)
                over = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
                over.fill((0, 255, 0, 60))
                vista.blit(over, sr)
                pygame.draw.rect(vista, (0, 255, 0), sr, 2)
            #amarelo = celulas de escada
            for r in self.mapa.rects_escada:
                sr = self.camera.aplicar(r)
                over = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
                over.fill((255, 220, 0, 45))
                vista.blit(over, sr)
                pygame.draw.rect(vista, (255, 220, 0), sr, 2)
            #marcador magenta nos pes = esta de pe em uma plataforma (pronto p/ S+Espaço)
            if self.player._sobre_plataforma:
                pe = pygame.Rect(self.player.rect.centerx - 3, self.player.rect.bottom - 3, 6, 6)
                pygame.draw.rect(vista, (255, 0, 255), self.camera.aplicar(pe))

        for bau in self.baus:
            bau.desenhar(vista, self.camera)  

        for drop in self.drops:
            drop.desenhar(vista, self.camera)

        for drop in self.drops_ecos:
            drop.desenhar(vista, self.camera)

        for fogueira in self.fogueiras:
            fogueira.desenhar(vista, self.camera)

        if DEBUG:
            pygame.draw.rect(vista, (0, 255, 0), sr_player, 2)

        #escala a cena do mundo para a tela (com zoom aplicado)
        pygame.transform.scale(vista, (Screen_widht, Screen_height), self.tela)

        #a partir daqui tudo é desenhado na resolução nativa (HUD, menus...)
        if self.menu_fogueira.aberto:
            self.menu_fogueira.desenhar()

        self.inventario.desenhar(self.player)

        self.hud.desenhar(self.tela, self.player, self.boss_atual)  

        #overlay de debug (F3): estado de plataformas/escadas direto na tela
        if self.debug_tiles:
            linhas_info = []
            if self.player._sobre_plataforma:
                linhas_info.append("SOBRE PLATAFORMA -> S+espaco (ou seta+espaco) para descer")
            if self.player._timer_atravessar > 0:
                linhas_info.append("DESCENDO PELA PLATAFORMA...")
            if self.player._escalando:
                linhas_info.append("ESCALANDO (W sobe / S desce)")
            if not linhas_info:
                linhas_info.append("F3: plat=verde escada=amarelo (nenhuma condicao ativa)")
            fonte_debug = pygame.font.SysFont(None, 24)
            for i, msg in enumerate(linhas_info):
                txt = fonte_debug.render(msg, True, (255, 255, 255), (0, 0, 0))
                self.tela.blit(txt, (10, 8 + i * 26))  

        #tela de morte - desenhada por cima de tudo
        if self.morrendo:
            progresso = 1 - (self.timer_morto / self.duraçao_morte)
            desenhar_tela_morte(self.tela, progresso)


        #tela de menu
        if self.pausado:
            desenhar_tela_pausa(self.tela, self._frame_pausa,
                                self.opçoes_pause, self.opçoes_selecionadas)