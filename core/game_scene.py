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
from world.niveis import spwans, Inimigos_por_sala, Conexoes, Drops_inimigos, Drops_fixos, MATERIAL_PISO
from world.niveis import SALAS_BETA, TITULOS_BETA, VIDA_INIMIGOS_BETA

from core.camera import Camera
from core.audio import audio, resolver_arma_id
from core.combat import CombatSystem
from core.combat.debug import desenhar_hitboxes_ativas, desenhar_hurtbox

from entities.projeteis.bomba import Bomba
from entities.projeteis.esporo_mushroom import EsporoMushroom
from entities.projeteis.projetil_flying_eye import ProjetilFlyingEye
from entities.projeteis.projetil_boss import ProjetilBoss

from entities.player import Player
from entities.objetos.bau import Bau
from entities.objetos.porta import Porta
from entities.objetos.drop_eco import DropEco
from entities.objetos.pocao import Pocao

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
from ui.prompts_teclas import PromptTeclaMundo
from core.interacoes import GerenciadorInteracoes
from core.tutorial_contextual import TutorialContextual
from ui.fim_beta import TelaFimBeta



# corrigi os key sensitives dos arquivos 
def _nome_arquivo_normalizado(nome):
    #remove acentos dos nomes das salas para monta os caminhos para o tmx
    nfdk = unicodedata.normalize('NFKD', nome)
    return ''.join(c for c in nfdk if not unicodedata.combining(c))


AMBIENCIA_POR_SALA = {
    "arena_chefe": "arena_boss",
    "calabouço_4": "sala_descanso",
    "calabouço_5": "arena_boss",
}

# H.1: exploração prioriza ambiência nas salas comuns. Mapa preparado para reativar música por sala.
MUSICA_POR_SALA = {
    "calabouço_1": None,
    "calabouço_2": None,
    "calabouço_3": None,
    "calabouço_4": "descanso",
    "calabouço_5": None,
}







class Gamescene:
    #centraliza toda a logica do jogo, mapa, inimigo e etc, para alivar e organiza o arquivo main.py
    
    def __init__(self, tela, modo_teste_combate=False, sala_teste=None):
        self.tela = tela 
        self.modo_teste_combate = modo_teste_combate
        self.sala_teste = sala_teste
        self.hud = Hud()


        #cria o hud e reeutilizar ele em outras salas
        self.player = Player(0, 0)
        # O cavaleiro da beta já atende ao requisito da primeira espada (DEX 10).
        # Não altera a arma nem o perfil de combate dos inimigos.
        self.player.destreza = max(self.player.destreza, 10)


        self._save_callback = None 


        #inventario
        self.inventario = Inventario(self.tela)


        #menu da fogueira
        self.menu_fogueira = MenuFogueira(self.tela, self.player, callback_descansar=self._descansar_fogueira, callback_fechar=self._fechar_menu_fogueira)
        self.boss_batalha_ativa = False

        #interacoes e prompt de tecla no mundo (G.1)
        self.interacoes = GerenciadorInteracoes()
        self.prompt_interacao_mundo = PromptTeclaMundo("e", escala=1.0)
        self._alvo_interacao_atual = None


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
        self.fim_beta = None
        self._conclusao_beta_timer = None
        sala_inicial = sala_teste or SALAS_BETA[0]
        if sala_inicial in SALAS_BETA and not modo_teste_combate:
            self.player.pocao = Pocao(cargas_iniciais=0)
        self._carregar_sala(sala_inicial)
        self.player.defenir_checkpoint(sala_inicial)


        self.morrendo = False
        self.timer_morto = 0
        self.duracao_morte = 180

        #projeteis  
        self.projeteis = []

        #combate centralizado (hitboxes/hurtboxes por máscara)
        self.combate = CombatSystem()
        self.debug_combate = False




        #menu de pausa
        self.pausado = False
        self._menu_callback = None #sera setado no main
        self.opcoes_pause = ["Continuar", "Inventário", "Salvar", "Menu principal", "Sair"]
        self.ACOES_PAUSA = ["continuar", "inventario", "salvar", "menu_principal", "sair"]
        self.opcao_pausa_selecionada = 0
        self._frame_pausa = 0

        #debug: mostra o que o engine considera plataforma/escada (F3 no jogo)
        self.debug_tiles = False

        if self.modo_teste_combate:
            self._iniciar_arena_teste()

    def _iniciar_arena_teste(self):
        #arena rapida para validar o combate sem depender do progresso do save
        self.modo_teste_combate = True
        self.morrendo = False
        self.timer_morto = 0
        self.pausado = False
        self.inventario.fechar()
        self.menu_fogueira.aberto = False

        self._carregar_sala("calabouço_1")
        self._configurar_arena_teste()
        self.hud.mostra_mensagem("MODO TESTE DE COMBATE - F6 reinicia | F4 hitboxes", 300)

    def _configurar_arena_teste(self):
        #area aberta no canto superior direito do calabouco_1
        chao = 12 * Tile_size
        px, py = 25 * Tile_size, 10 * Tile_size

        self.player.defenir_checkpoint(self.sala_atual, x=px, y=py)
        self.player.respawnar()
        self.player.hp = self.player.hp_max
        self.player.stamina = self.player.stamina_max
        self.player.pocao = Pocao()
        self.player.ecos = 0

        from entities.objetos.item import get_item
        espada = get_item(1)
        if espada is not None:
            self.player.equipar(espada)
            if espada.id not in self.player.inventario["equipamentos"]:
                self.player.inventario["equipamentos"].append(espada.id)

        self.inimigos = []
        self.boss_atual = None
        self.projeteis = []
        self.particulas_ecos = []
        self.drops = []
        self.drops_ecos = []
        self.parede_boss = []
        self.inimigos_morto_por_sala.pop(self.sala_atual, None)

        _tipos_inimigos = {
            "skeleton": Skeleton,
            "globin": Globin,
            "mushroom": Mushroom,
            "flying_eye": FlyingEye,
            "esqueleto_boss": EsqueletoBoss,
        }
        arena = (
            ("skeleton", 29 * Tile_size, chao - 48, 160, 320),
            ("globin", 32 * Tile_size, chao - 44, 160, 320),
            ("mushroom", 35 * Tile_size, chao - 60, 160, 320),
            ("flying_eye", 42 * Tile_size, 8 * Tile_size, 100, 200),
            ("esqueleto_boss", 38 * Tile_size, chao - 90),
        )

        for dados in arena:
            tipo = dados[0]
            classe = _tipos_inimigos[tipo]
            x, y = dados[1], dados[2]
            if tipo == "esqueleto_boss":
                inimigo = classe(x, y, callback_morte=self._abrir_parede_boss)
                self.boss_atual = inimigo
                self._tocar_entrada_boss(inimigo)
            else:
                inimigo = classe(x, y, dados[3], dados[4])
            self.inimigos.append(inimigo)

        self._atualizar_audio_sala()

    #CARREGA A SALA 

    def _carregar_sala(self, nome_sala, posiçao_spwan=None, respawnando=False ):
        #carrega um novo mapa e reposiciona o player

        self.sala_atual = nome_sala
        self.player.material_piso = MATERIAL_PISO.get(nome_sala, "pedra")

        self._limpar_estado_interacao()

        # Dicas pertencem a esta entrada de sala, nunca ao save.
        self.tutorial_contextual = None

        parar_mundo = getattr(audio, "stop_world_sfx", None)
        if parar_mundo is not None:
            parar_mundo()

        #se existe um tmx para aquela sala usa ele, senao pular
        import os 
        caminho_tmx = f"assets/maps/{_nome_arquivo_normalizado(nome_sala)}.tmx"
        grid_decoracao_fundo = None
        if os.path.exists(caminho_tmx):
            logger.info(f"[MAPA] carregando '{nome_sala}' via TMX: {caminho_tmx}")
            grid = TileMap.carregar_camada_tmx(caminho_tmx, "colisao")
            grid_decoracao = TileMap.carregar_camada_tmx(caminho_tmx, "decoracao", obrigatoria=False)
            grid_fundo = TileMap.carregar_camada_tmx(caminho_tmx, "fundo", obrigatoria=False)
            grid_escadas = TileMap.carregar_camada_tmx(caminho_tmx, "escadas", obrigatoria=False)
            grid_plataformas = TileMap.carregar_camada_tmx(caminho_tmx, "plataformas", obrigatoria=False)
            grid_decoracao_fundo = TileMap.carregar_camada_tmx(caminho_tmx, "decoracao_fundo", obrigatoria=False)
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
        




    
        
        self.mapa = TileMap(grid, grid_decoracao, grid_fundo, grid_escadas, grid_plataformas,
                            grid_decoracao_fundo)
        self.passagens = []
        for obj in objetos_tmx or []:
            if obj["tipo"] == "transicao":
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                lado = obj["propriedades"].get("lado")
                if rect.width > 0 and rect.height > 0 and lado in ("esquerda", "direita"):
                    self.passagens.append((rect, lado))
                    self.mapa.aberturas_passagens.append(rect)


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
                try:
                    id_item = int(obj["propriedades"].get("id_item", 1))
                except (TypeError, ValueError):
                    logger.warning(f"[MAPA] baú em ({col_idx},{linha_idx}) com id_item inválido, usando 1")    
                    id_item = 1

                primeira_espada = nome_sala == "antigo_arsenal_guardas" and id_item == 1
                if primeira_espada and self._possui_espada():
                    continue
                if self._objeto_registrado(self.baus_abertos, col_idx, linha_idx):
                    # A espada perdida pode ser recuperada no arsenal, inclusive após load.
                    if not primeira_espada or any(
                        d.ativo and d.id_item == 1 for d in self.drops_por_sala.get(nome_sala, [])
                    ):
                        continue


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
                            if self._objeto_registrado(self.baus_abertos, col_idx, linha_idx):
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
        posicoes_fogueira = set()

        def _adicionar_fogueira(col_idx, linha_idx):
            chave = (col_idx, linha_idx)
            if chave in posicoes_fogueira:
                return
            fogueira = Fogueira(
                col_idx * Tile_size,
                linha_idx * Tile_size,
                col_idx, linha_idx,
                callback_descanso=self._descansar_fogueira
            )
            fogueira._callback_abrir_menu = self._abrir_menu_fogueira
            posicoes_fogueira.add(chave)
            self.fogueiras.append(fogueira)

        if objetos_tmx is not None:
            for obj in objetos_tmx:
                if obj.get("tipo") != "fogueira":
                    continue
                _adicionar_fogueira(obj["col"], obj["linha"])

        for linha_idx, linha in enumerate(Salas.get(nome_sala, [])):
            for col_idx, tile in enumerate(linha):
                if tile == 9:
                    _adicionar_fogueira(col_idx, linha_idx)

        for fogueira in self.fogueiras:
            if self._objeto_registrado(self.fogueiras_ativas, fogueira.col, fogueira.linha):
                fogueira.ativa = True
        


        self.drops = self.drops_por_sala.get(nome_sala, [])




        #drop fixos da sala
        from entities.objetos.drop import Drop

        for dados in Drops_fixos.get(nome_sala, []):
            id_item, col_drop, lin_drop = dados 
            frasco = id_item == 2 and nome_sala in SALAS_BETA
            if frasco and self.player.pocao.cargas_max >= 3:
                continue

            #chave unica para cada item fixo
            chave = (nome_sala, col_drop, lin_drop)
            if chave not in self.drops_fixos_coletados:
                if not nome_sala in self.drops_por_sala:
                    self.drops_por_sala[nome_sala] = []

                #evita duplica se a sala ja foi carregada antes
                ja_existe = any(
                    d.chave_fixa == chave
                    for d in self.drops_por_sala[nome_sala]
                )

                if not ja_existe:
                    drop = Drop(col_drop * Tile_size, lin_drop * Tile_size, id_item)
                    drop.frasco = frasco
                    drop.chave_fixa = chave #marca o drop como fixo 
                    drop.callback_coletado = self._registrar_drop_fixo_coletado
                    self.drops_por_sala[nome_sala].append(drop)
                
                self.drops = self.drops_por_sala.get(nome_sala, [])

        # Inclui pickups restaurados de saves anteriores, que usavam o centro flutuante.
        for drop in self.drops:
            if drop.ativo:
                drop.apoiar(self.mapa.rects_solidos + self.mapa.rects_plataforma)

       #limpa os projeteis ao trocar de sala
        self.projeteis = []

        #ecos que ficam no chao ao morrer
        drop_eco = self.drops_ecos_por_sala.get(nome_sala)
        self.drops_ecos = [drop_eco] if drop_eco and drop_eco.ativo else []







        #ajuste da camera para o mapa novo
        self.largura_mapa = len(grid[0]) * Tile_size
        self.altura_mapa = len(grid) * Tile_size
        self.camera = Camera(self.largura_mapa, self.altura_mapa)
        self.boss_batalha_ativa = False

    #posiçao do spwan
        spwans_tmx = {}
        if objetos_tmx is not None:
            for obj in objetos_tmx:
                if obj["tipo"] not in {"spawn", "spwan"}:
                    continue
                nome_spwan = obj.get("nome") or obj["propriedades"].get("nome") or "default"
                spwans_tmx[nome_spwan] = (obj["col"], obj["linha"])



        
        if not respawnando:
            if posiçao_spwan is not None:
                col, linha = posiçao_spwan
            else:
                col, linha = self._resolver_spwan(nome_sala, grid, spwans_tmx)
            self.player.rect.x = col * Tile_size
            self.player.rect.y = linha * Tile_size
            self.player.vel.xy = (0, 0)
            self.player._escalando = False
            self.player._escada_lock = None
            self.player.encerrar_ataque()

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
                if obj.get("tipo") != "inimigo":
                    continue

                props = obj.get("propriedades", {})
                tipo = props.get("tipo", props.get("type"))
                tipo = str(tipo).strip().lower() if tipo is not None else ""
                classe = _tipos_inimigos.get(tipo)
                if not classe:
                    logger.warning(
                        f"[MAPA] tipo de inimigo '{tipo}' desconhecido no objeto id={obj.get('id')}, ignorando"
                    )
                    continue

                indice = obj["id"] #id nativo do tiled
                col_idx, linha_idx = obj["col"], obj["linha"]
                x, y = col_idx * Tile_size, linha_idx * Tile_size

                if tipo == "esqueleto_boss":
                    if self.sala_atual in self.bosses_derrotados:
                        continue

                    boss = EsqueletoBoss(x, y, callback_morte=self._abrir_parede_boss)
                    if nome_sala in SALAS_BETA:
                        boss.hp = boss.hp_max = VIDA_INIMIGOS_BETA[tipo]
                    boss._indice_spawn = indice
                    self.inimigos.append(boss)
                    self.boss_atual = boss
                    self.boss_batalha_ativa = False
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
                if nome_sala in SALAS_BETA:
                    inimigo.hp = inimigo.hp_max = VIDA_INIMIGOS_BETA[tipo]
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
            for linha_idx, linha in enumerate(Salas.get(nome_sala, [])):
                for col_idx, tile in enumerate(linha):
                    if tile == 8:
                        self.parede_boss.append(pygame.Rect(
                            col_idx * Tile_size,
                            linha_idx * Tile_size,
                            Tile_size, Tile_size
                        ))

        self._atualizar_audio_sala()
        if nome_sala in SALAS_BETA:
            self.tutorial_contextual = TutorialContextual(self.mapa, self.player)
            self.hud.mostra_mensagem(TITULOS_BETA[nome_sala])
        # Evita uma panorâmica desde (0,0) a cada passagem/respawn.
        for _ in range(90):
            self.camera.atualizar(self.player.rect)

    def _objeto_registrado(self, registros, col, linha):
        if (self.sala_atual, col, linha) in registros:
            return True
        # Pares antigos continuam pertencendo somente à campanha antiga.
        return self.sala_atual not in SALAS_BETA and (col, linha) in registros

    def _possui_espada(self):
        inv = self.player.inventario
        return inv["mao_direita"] == 1 or 1 in inv["equipamentos"]

    def _contexto_musical_sala(self):
        menu = getattr(self, "menu_fogueira", None)
        boss = getattr(self, "boss_atual", None)
        if boss is not None and boss.vivo and getattr(self, "boss_batalha_ativa", False):
            return "boss", "batalha_chefe_ativa"
        if menu is not None and menu.aberto:
            return "descanso", "menu_fogueira_aberto"
        contexto_sala = MUSICA_POR_SALA.get(self.sala_atual)
        if contexto_sala == "descanso":
            return "descanso", "sala_descanso"
        if contexto_sala:
            return contexto_sala, f"musica_sala_{self.sala_atual}"
        return None, "exploracao_prioriza_ambiencia"

    def _atualizar_audio_sala(self, forcar=False, motivo_extra=""):
        ambiencia = AMBIENCIA_POR_SALA.get(self.sala_atual, "calabouco")
        set_sala = getattr(audio, "set_contexto_sala", None)
        if set_sala is not None:
            set_sala(self.sala_atual, ambiencia)
        tocar_ambiente = getattr(audio, "play_ambiente", None)
        if tocar_ambiente is not None:
            tocar_ambiente(ambiencia)
        tocar_tochas = getattr(audio, "play_tochas", None)
        if tocar_tochas is not None:
            tocar_tochas(bool(getattr(self, "tochas", [])))

        contexto, motivo = self._contexto_musical_sala()
        if motivo_extra:
            motivo = f"{motivo}:{motivo_extra}"
        if contexto is None:
            stop = getattr(audio, "stop_music", None)
            if stop is not None:
                try:
                    stop(fade_ms=800, motivo=motivo)
                except TypeError:
                    if getattr(audio, "_musica_contexto", None) not in (None, "menu"):
                        stop()
            return
        tocar_musica = getattr(audio, "play_music", None)
        if tocar_musica is not None:
            fade_ms = 1200 if contexto == "descanso" else 800
            try:
                tocar_musica(contexto, origem="game_scene", fade_ms=fade_ms, fade_out_ms=800, motivo=motivo)
            except TypeError:
                tocar_musica(contexto)

    def _fazer_callback_drop_inimigo(self, drops, sala):
        def _callback(ix, iy):
            import random
            from entities.objetos.drop import Drop
            for chance, id_item in drops:
                if random.random() < chance:
                    drop = Drop(ix, iy, id_item)
                    drop.apoiar(self.mapa.rects_solidos + self.mapa.rects_plataforma)
                    if sala not in self.drops_por_sala:
                        self.drops_por_sala[sala] = []
                    self.drops_por_sala[sala].append(drop)
                    self.drops = self.drops_por_sala[self.sala_atual]
        return _callback










    def _resolver_spwan(self, nome_sala, grid, spwans_tmx):
        # Define posição inicial; prioriza spawns TMX e valida com _spawn_seguro.
        # Convenção oficial: spawn nomeado "default"/"esquerda"/"direita".
        lado = getattr(self, "_entrada_lado", None)

        if spwans_tmx:
            spawns_norm = {str(k).strip().lower(): v for k, v in spwans_tmx.items()}
            lado_norm = str(lado).strip().lower() if lado is not None else None
            if lado_norm and lado_norm in spawns_norm:
                col, linha = spawns_norm[lado_norm]
            elif "default" in spawns_norm:
                col, linha = spawns_norm["default"]
            elif len(spawns_norm) == 1:
                col, linha = next(iter(spawns_norm.values()))
            else:
                logger.warning(
                    f"[SPAWN] '{nome_sala}': TMX tem spawns mas nenhum bate com "
                    f"lado='{lado}' (disponíveis: {list(spawns_norm.keys())}), usando fallback de grade"
                )
                col, linha = self._spwan_fallback_grid(nome_sala, grid, lado)
        else:
            col, linha = self._spwan_fallback_grid(nome_sala, grid, lado)

        col_final, linha_final = self._spawn_seguro(col, linha, grid)
        if (col_final, linha_final) != (col, linha):
            logger.info(
                f"[SPAWN] '{nome_sala}': posição bruta ({col},{linha}) ajustada "
                f"para ({col_final},{linha_final})"
            )
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


    def _contexto_suprime_interacao(self):
        return (
            bool(getattr(self, "pausado", False))
            or bool(getattr(self, "morrendo", False))
            or bool(getattr(self, "inventario", None) and self.inventario.aberto)
            or bool(getattr(self, "menu_fogueira", None) and self.menu_fogueira.aberto)
        )


    def _selecionar_alvo_interacao(self, teclas):
        contexto = {
            'baus': getattr(self, 'baus', []),
            'drops': getattr(self, 'drops', []),
            'drops_ecos': getattr(self, 'drops_ecos', []),
            'fogueiras': getattr(self, 'fogueiras', []),
            'portas': getattr(self, 'portas', []),
            'pausado': bool(getattr(self, 'pausado', False)),
            'inventario_aberto': bool(getattr(self, 'inventario', None) and self.inventario.aberto),
            'menu_fogueira_aberto': bool(getattr(self, 'menu_fogueira', None) and self.menu_fogueira.aberto),
            'morrendo': bool(getattr(self, 'morrendo', False)),
            'suprimido': False,
        }
        gerenciador = getattr(self, 'interacoes', None)
        if gerenciador is None:
            self._alvo_interacao_atual = None
            return None
        alvo = gerenciador.atualizar(self.player, self.hud, teclas, contexto)
        self._alvo_interacao_atual = alvo
        return alvo

    def _limpar_estado_interacao(self):
        self._alvo_interacao_atual = None
        hud = getattr(self, 'hud', None)
        if hud is not None:
            try:
                hud.limpar_prompt_interacao()
            except Exception:
                try:
                    hud.limpar_prompt()
                except Exception:
                    pass

    def atualizar(self, eventos): 
        if getattr(self, "fim_beta", None) is not None:
            if self.fim_beta.atualizar(eventos) and self._menu_callback:
                self._menu_callback()
            return
        if getattr(self, "_conclusao_beta_timer", None) is not None:
            self._conclusao_beta_timer -= 1
            for inimigo in self.inimigos:
                if not inimigo.vivo:
                    inimigo.atualizar(self.mapa.rects_solidos, self.player)
            if self._conclusao_beta_timer <= 0:
                self.fim_beta = TelaFimBeta(self.tela)
                if self._save_callback:
                    self._save_callback()
            return
        teclas = pygame.key.get_pressed()
        tutorial = getattr(self, "tutorial_contextual", None)
        if tutorial and (self._contexto_suprime_interacao() or not self.player.vivo):
            tutorial.ocultar(self.player)

        #F3 liga/desliga o debug de plataforma/escada
        reiniciar_teste = False
        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F3:
                self.debug_tiles = not self.debug_tiles
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F4:
                self.debug_combate = not self.debug_combate
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F6 and self.modo_teste_combate:
                reiniciar_teste = True
            if (ev.type == pygame.KEYDOWN and ev.key == pygame.K_i
                    and not self.menu_fogueira.aberto and not self.morrendo):
                if self.inventario.aberto:
                    self.inventario.fechar()
                else:
                    self.inventario.abrir()

        if reiniciar_teste:
            self._iniciar_arena_teste()
            return

        if self.menu_fogueira.aberto:
            self._limpar_estado_interacao()
            self.menu_fogueira.atualizar(eventos)
            return


        if self.pausado:
            self._limpar_estado_interacao()
            self._atualizar_pausa(eventos)
            return
            

        rects_solidos = self.mapa.rects_solidos + self.parede_boss + [p.rect for p in self.portas if not p.aberta]
        
        if self.inventario.aberto:
            self._limpar_estado_interacao()
            self.inventario.atualizar(eventos, self.player)
            return

        #hitstop: congela o mundo por alguns frames após um acerto confirmado
        if not self.pausado and self.combate.consumir_hitstop():
            self.hud.atualizar()
            return

        #atuallizar o checar_morte
        self._checar_morte()

        #bloquueia os outros atualizar se o player estiver morto
        if self.morrendo:
            self._limpar_estado_interacao()
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

        self._atualizar_estado_batalha_chefe()

        #atualizar o player
        self.player.atualizar(rects_solidos, self.camera,
                              rects_plataforma=self.mapa.rects_plataforma,
                              rects_escada=self.mapa.rects_escada)

        #atualizar a transiçao de cena
        sala_antes = self.sala_atual
        self._checar_transiçao()
        if self.sala_atual != sala_antes:
            return  # Os sólidos deste frame pertencem à sala anterior.

        #interacoes: selecao deterministica + prompt no mundo (G.1)
        teclas = pygame.key.get_pressed()
        alvo_interacao = self._selecionar_alvo_interacao(teclas)

        for bau in self.baus:
            bau.atualizar(self.player, teclas, self.mapa, self.hud,
                          selecionado=(bau is alvo_interacao))

        for drop in self.drops:
            drop.atualizar(self.player, teclas, self.hud,
                           selecionado=(drop is alvo_interacao))

        for drop in self.drops_ecos:
            drop.atualizar(self.player, teclas, self.hud,
                           selecionado=(drop is alvo_interacao))
        self.drops_ecos = [d for d in self.drops_ecos if d.ativo]

        for fogueira in self.fogueiras:
            fogueira.atualizar(self.player, teclas, self.hud, self.sala_atual,
                               self.fogueiras_ativas,
                               selecionado=(fogueira is alvo_interacao))

        for porta in self.portas:
            porta.atualizar(self.player, teclas, self.hud, self.portas_abertas,
                            selecionado=(porta is alvo_interacao))

        # atualiza animacao do prompt (estado/deslocamento discreto e press real)
        if hasattr(self, "prompt_interacao_mundo"):
            tecla_prompt = getattr(alvo_interacao, "tecla_prompt", "e") if alvo_interacao else "e"
            self.prompt_interacao_mundo.tecla = tecla_prompt
            pressionada = bool(alvo_interacao and teclas[pygame.K_e]
                               and alvo_interacao.disponivel_para_prompt(self.player))
            self.prompt_interacao_mundo.atualizar(pressionada=pressionada)
        # revalida alvo apos execucao/consumo (evita sprite preso)
        if alvo_interacao is not None and not getattr(alvo_interacao, "ativo", True):
            self._limpar_estado_interacao()
        elif alvo_interacao is not None and not alvo_interacao.disponivel_para_prompt(self.player):
            # mantem oculto se nao mais disponivel; proximo frame re-seleciona
            self._alvo_interacao_atual = None
            try:
                self.hud.limpar_prompt_interacao()
            except Exception:
                self.hud.limpar_prompt()

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


        #atualizar os projeteis (posição do frame antes de resolver o combate)
        for proj in self.projeteis:
            proj.atualizar(rects_solidos, self.player)

        #as máscaras refletem a posição final do frame
        self.player.atualizar_mask()
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.atualizar_mask()

        #resolver todo o combate do frame (player, inimigos e projéteis)
        eventos_combate = self.combate.resolver(
            self.player, self.inimigos, self.projeteis, rects_solidos
        )
        self._processar_audio_combate(eventos_combate)

        #coleta projéteis spawnados pelos hooks de ataque neste frame
        for inimigo in self.inimigos:
            if getattr(inimigo, "bombas_spawnar", None):
                self.projeteis.extend(inimigo.bombas_spawnar)
                inimigo.bombas_spawnar.clear()
            if getattr(inimigo, "esporos_spawnar", None):
                self.projeteis.extend(inimigo.esporos_spawnar)
                inimigo.esporos_spawnar.clear()
            if getattr(inimigo, "projeteis_spawnar", None):
                self.projeteis.extend(inimigo.projeteis_spawnar)
                inimigo.projeteis_spawnar.clear()

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

        #remove os projeteis inativos depois de atualizar
        self.projeteis = [p for p in self.projeteis if p.ativo]
        
        #camera segue o player
        self._atualizar_zoom_camera()
        self.camera.atualizar(self.player.rect)

        #hud
        self.hud.atualizar()

        tutorial = getattr(self, "tutorial_contextual", None)
        if tutorial:
            if self.sala_atual == "antigo_arsenal_guardas" and self.player.tem_arma_equipada:
                if self.player.atacando:
                    tutorial.concluir("ataque")
                elif "ataque" not in tutorial.concluidas:
                    tutorial.solicitar("ataque", ("k",))
            tutorial.atualizar(
                self.player, teclas, suprimido=self._contexto_suprime_interacao(),
                interacao=getattr(self, "_alvo_interacao_atual", None) is not None,
            )


    def _atualizar_zoom_camera(self):
        #aproxima a camera no dia a dia; em luta de boss ela desaproxima
        lutando = self.boss_atual is not None and self.boss_atual.vivo and self.boss_batalha_ativa
        self.camera.zoom_alvo = ZOOM_BOSS if lutando else ZOOM_PADRAO


    def _atualizar_pausa(self, eventos):

        pos_mouse = pygame.mouse.get_pos()
        fonte_opcao = Fonte_texto(28)

        itens_com_rect = []
        for i, opcao in enumerate(self.opcoes_pause):
            texto = fonte_opcao.render(opcao, True, (255, 255, 255))
            x = Screen_widht // 2 - texto.get_width() // 2
            y = 320 + i * 50
            rect_opcao = pygame.Rect(x - 10, y - 5, texto.get_width() + 20, texto.get_height() + 10)
            itens_com_rect.append((i, rect_opcao))

        indice_houver = hover_index(eventos, pos_mouse, itens_com_rect)
        if indice_houver is not None and indice_houver != self.opcao_pausa_selecionada:
            self.opcao_pausa_selecionada = indice_houver
            audio.play_sfx("ui_move")

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_UP:
                    novo = (self.opcao_pausa_selecionada - 1) % len(self.opcoes_pause)
                    if novo != self.opcao_pausa_selecionada:
                        self.opcao_pausa_selecionada = novo
                        audio.play_sfx("ui_move")

                elif evento.key == pygame.K_DOWN:
                    novo = (self.opcao_pausa_selecionada + 1) % len(self.opcoes_pause)
                    if novo != self.opcao_pausa_selecionada:
                        self.opcao_pausa_selecionada = novo
                        audio.play_sfx("ui_move")

                elif evento.key == pygame.K_RETURN:
                    self._ativar_opcao_pausa()

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for indice, rect_opcao in itens_com_rect:
                    if rect_opcao.collidepoint(pos_mouse):
                        self.opcao_pausa_selecionada = indice
                        self._ativar_opcao_pausa()
                        break


    def _abrir_inventario_por_pausa(self):
        self._fechar_pausa(tocar_som=False)
        self.inventario.abrir()
        self._inventario_aberto_por_pausa = True
        try:
            if not self.inventario.aberto:
                audio.play_sfx("ui_error")
                log.warning("[pausa] Inventario.abrir() nao manteve estado aberto")
        except Exception:
            log.exception("[pausa] falha ao validar abertura do inventario")

    def _ativar_opcao_pausa(self):
        opcao = self.opcoes_pause[self.opcao_pausa_selecionada]
        acoes = getattr(self, "ACOES_PAUSA", None)
        acao = acoes[self.opcao_pausa_selecionada] if acoes and self.opcao_pausa_selecionada < len(acoes) else opcao
        if acao in ("inventario", "Invent?rio", "Invent?rio"):
            self._abrir_inventario_por_pausa()
            return
        if acao in ("salvar", "Salvar"):
            if self._save_callback:
                self._save_callback()
            else:
                audio.play_sfx("ui_error")
            return
        if acao in ("continuar", "Continuar"):
            self._fechar_pausa()
            return
        if acao in ("menu_principal", "Menu principal"):
            audio.play_sfx("ui_confirm")
            self._fechar_pausa(tocar_som=False)
            if self._menu_callback:
                self._menu_callback()
            return
        if acao in ("sair", "Sair"):
            audio.play_sfx("ui_confirm")
            self._fechar_pausa(tocar_som=False)
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        audio.play_sfx("ui_confirm")


    def _confirma_opcao_pausa(self):
        self._confirmar_opcao_pausa()

    def _confirmar_opcao_pausa(self):
        # compatibilidade: acao unificada sem recursao
        self._ativar_opcao_pausa()

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
                self.boss_batalha_ativa = False

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
        audio.play_sfx("campfire_rest")
        #reseta os inimigos das salas ja visitadas
        self.inimigos_morto_por_sala.clear()

        #curar o player e recarregar as poções
        self.player.hp = self.player.hp_max
        self.player.stamina = getattr(self.player, "stamina_max", 0)
        self.player.pocao.recarregar()


        #respwna os inimigos da sala atual
        if self.sala_atual in SALAS_BETA:
            self._carregar_sala(self.sala_atual, respawnando=True)
        else:
            self._spwanar_inimigos(self.sala_atual)

    def _fechar_menu_fogueira(self):
        self.menu_fogueira.aberto = False
        self.pausado = False
        self._atualizar_audio_sala()


    def _abrir_menu_fogueira(self):
        logger.info("abrindo menu fogueira")
        self.menu_fogueira.abrir()
        self._atualizar_audio_sala()
        


    def _registrar_bau_aberto(self, col, linha):
        self.baus_abertos.add((self.sala_atual, col, linha))
        if self.sala_atual == "antigo_arsenal_guardas" and self._possui_espada():
            if not self.player.tem_arma_equipada:
                from entities.objetos.item import get_item
                self.inventario._tentar_equipar(get_item(1), self.player)



    

    def _processar_audio_combate(self, eventos):
        for evento in eventos:
            alvo = evento.alvo
            atacante = evento.atacante

            if alvo is self.player:
                if evento.aplicado and self.player.vivo:
                    audio.play_sfx("player_hurt")
                continue

            if atacante is not self.player:
                continue

            inimigo = getattr(alvo, "SOM_ID", "_default")
            material = getattr(alvo, "MATERIAL", "_default")
            arma = resolver_arma_id(atacante)

            if getattr(alvo, "_escudo_ativo", False) and not evento.aplicado:
                if hasattr(audio, "play_block"):
                    audio.play_block(inimigo)
                else:
                    audio.play_sfx("block")
            elif not getattr(alvo, "vivo", False):
                if hasattr(audio, "play_hit"):
                    audio.play_hit(inimigo, arma, material, kill=True)
                else:
                    audio.play_sfx("enemy_death")
            elif evento.aplicado:
                if hasattr(audio, "play_hit"):
                    audio.play_hit(inimigo, arma, material)
                else:
                    audio.play_sfx("hit")

    def _checar_morte(self):
        #dectetar se o player morreu, se sim colocar o "voce morreu" na tela tipo dark souls

        if not self.player.vivo and not self.morrendo:
            #inicia o timer de morte
            self.morrendo = True
            self.timer_morto = self.duracao_morte
            audio.play_sfx("player_death")


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
                if self.modo_teste_combate:
                    self._configurar_arena_teste()

                self.morrendo = False

    #verificar passagem
    def _checar_transiçao(self):    
        #verificar se o player saiu pela borda da sala e carrega a nova, se existir conexao é claro

        #proteçao anti bug de teleporte da transiçao de fase
        conexoes_sala = Conexoes.get(self.sala_atual, {})
        if self.sala_teste or self.modo_teste_combate:
            return
        if self.sala_atual in SALAS_BETA:
            self._cooldown_transiçao = max(0, self._cooldown_transiçao - 1)
            self.player.rect.clamp_ip(pygame.Rect(0, 0, self.largura_mapa, self.altura_mapa))
            if self.boss_batalha_ativa:
                return
            for rect, lado in self.passagens:
                movendo_para_passagem = self.player.vel.x > 0 if lado == "direita" else self.player.vel.x < 0
                if not movendo_para_passagem or not rect.collidepoint(self.player.rect.center):
                    continue
                if self._cooldown_transiçao and lado == self._entrada_lado:
                    continue
                proxima = conexoes_sala.get(lado)
                if proxima:
                    self._entrada_lado = "esquerda" if lado == "direita" else "direita"
                    self._carregar_sala(proxima)
                    self._dir_entrada = lado
                    self._cooldown_transiçao = 12
                    return
            return  # Paredes/bordas comuns da beta nunca são gatilhos.
        limite_direita = self.largura_mapa

        # cooldown só bloqueia a direção de onde o player veio
        if hasattr(self, "_cooldown_transiçao") and self._cooldown_transiçao > 0:
            self._cooldown_transiçao -= 1
            if self._dir_entrada == "direita" and self.player.rect.left <= 0:
                return  # bloqueia só esquerda
            if self._dir_entrada == "esquerda" and self.player.rect.right >= self.largura_mapa:
                return  # bloqueia só direita

        # direita
        if self.player.rect.right >= limite_direita:
            proxima = conexoes_sala.get("direita")
            if proxima:
                self._entrada_lado = "esquerda"  # entrando na proxima sala pela esquerda
                self._carregar_sala(proxima)
                self._dir_entrada = "direita"
                self._cooldown_transiçao = 60
                return
            self.player.rect.right = min(self.player.rect.right, self.largura_mapa)

        # esquerda
        elif self.player.rect.left <= 0:
            proxima = conexoes_sala.get("esquerda")
            if proxima:
                self._entrada_lado = "direita"  # entrando na proxima sala pela direita
                self._carregar_sala(proxima)
                self._dir_entrada = "esquerda"
                self._cooldown_transiçao = 60
                return
            self.player.rect.left = max(0, self.player.rect.left)

    #sistema de dano nos espinhos para parkou
    def _checar_espinhos(self):
        for rect_dano, dano in self.mapa.rects_dano:
            if self.player.rect.colliderect(rect_dano):
                self.player.receber_dano(dano)
                break 
    

    def _tocar_entrada_boss(self, boss):
        tocar = getattr(audio, "play_enemy_entrada", None)
        if tocar is not None:
            tocar(boss.SOM_ID)

    def _atualizar_estado_batalha_chefe(self):
        boss = getattr(self, "boss_atual", None)
        if boss is None or not boss.vivo:
            if getattr(self, "boss_batalha_ativa", False):
                self.boss_batalha_ativa = False
                self._atualizar_audio_sala(motivo_extra="chefe_inativo")
            return
        if getattr(self, "boss_batalha_ativa", False):
            return
        # H.1: batalha do chefe só começa quando jogador realmente entra no encontro.
        # Reaproveita detecção de aggro/entrada do boss (Alcance_detec/rugido emitido).
        dist = abs(self.player.rect.centerx - boss.rect.centerx)
        detectado = dist < getattr(boss, "Alcance_detec", 0)
        aggro = bool(getattr(boss, "_rugido_emitido", False)) or getattr(boss, "estado", None) in ("Perseguir", "Atacando")
        if self.player.vivo and (detectado or aggro):
            self.boss_batalha_ativa = True
            if self.sala_atual == "arena_chefe":
                self.parede_boss = [r.copy() for r, lado in self.passagens if lado == "esquerda"]
            self._tocar_entrada_boss(boss)
            self._atualizar_audio_sala(motivo_extra="batalha_chefe_iniciada")

    def _abrir_parede_boss(self, x, y):
        self.parede_boss = []
        self.boss_atual = None
        self.boss_batalha_ativa = False
        self.bosses_derrotados.add(self.sala_atual)
        self._atualizar_audio_sala(motivo_extra="chefe_derrotado")
        tocar_mecanismo = getattr(audio, "play_mecanismo", None)
        if tocar_mecanismo is not None:
            tocar_mecanismo()
        self.hud.mostra_mensagem("O caminho esta livre")

        if self.sala_atual == "arena_chefe":
            self._conclusao_beta_timer = 120
            self.projeteis.clear()
            self.player.encerrar_ataque()
            self.player.vel.xy = (0, 0)
            self._limpar_estado_interacao()
            return


        from entities.objetos.drop import Drop
        
        drop = Drop(x, y, id_item=3)

        if self.sala_atual not in self.drops_por_sala:
            self.drops_por_sala[self.sala_atual] = []

        self.drops_por_sala[self.sala_atual].append(drop)
        self.drops = self.drops_por_sala[self.sala_atual]


    def _descartar_item(self, id_item):
        from entities.objetos.drop import Drop
        
        drop = Drop(self.player.rect.centerx, self.player.rect.bottom, id_item)
        drop.apoiar(self.mapa.rects_solidos + self.mapa.rects_plataforma)

        if self.sala_atual not in self.drops_por_sala:
            self.drops_por_sala[self.sala_atual] = []

        self.drops_por_sala[self.sala_atual].append(drop)
        self.drops = self.drops_por_sala[self.sala_atual]
        

    def _fechar_pausa(self, tocar_som=True):
        if not self.pausado:
            return
        self.pausado = False
        if tocar_som:
            audio.play_sfx("ui_pause_close")

    def alternar_pausa(self):
        if getattr(self, "fim_beta", None) is not None or getattr(self, "_conclusao_beta_timer", None) is not None:
            return
        if self.pausado:
            self._fechar_pausa()
        else:
            self.pausado = True
            self.opcao_pausa_selecionada = 0 #reseta ao sair do menu
            audio.play_sfx("ui_pause_open")
    
    def carregar_save(self, dados):
        estado = dados.get("estado_jogador", {})
        # Formatos anteriores não registravam capacidade: conservam seus três frascos.
        self.player.pocao.cargas_max = max(0, min(3, estado.get("pocoes_max", 3)))
        self.player.pocao.cargas = self.player.pocao.cargas_max
        self.inimigos_morto_por_sala = estado.get("inimigos_mortos", {})
        from entities.objetos.drop import Drop
        for sala, drops in estado.get("drops", {}).items():
            self.drops_por_sala[sala] = []
            for registro in drops:
                drop = Drop(registro["x"], registro["y"], registro["id_item"])
                drop.frasco = registro.get("frasco", False)
                if registro.get("chave_fixa"):
                    drop.chave_fixa = tuple(registro["chave_fixa"])
                    drop.callback_coletado = self._registrar_drop_fixo_coletado
                self.drops_por_sala[sala].append(drop)
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
        estado = dados.get("estado_jogador", {})
        if not estado and self.sala_atual not in SALAS_BETA:
            self.player.destreza = Player.DESTREZA_INICIAL
        for atributo, valor in estado.get("atributos", {}).items():
            if atributo in ("vigor", "resistencia", "forca", "destreza", "nivel"):
                setattr(self.player, atributo, valor)
        if estado:
            p = self.player
            p.hp_max = p.HP_BASE + p.vigor * p.HP_POR_VIGOR
            p.stamina_max = p.STAMINA_BASE + p.resistencia * p.STAMINA_POR_RES
            p.hp = max(1, min(p.hp_max, estado.get("hp", p.hp_max)))
            p.stamina = max(0, min(p.stamina_max, estado.get("stamina", p.stamina_max)))
            p.pocao.cargas = max(0, min(p.pocao.cargas_max, estado.get("pocoes", p.pocao.cargas_max)))
            checkpoint = estado.get("checkpoint")
            if checkpoint:
                p.defenir_checkpoint(checkpoint[0], x=checkpoint[1], y=checkpoint[2])
        # Saves antigos mantêm sua campanha e o ponto salvo como checkpoint.
        for _ in range(90):
            self.camera.atualizar(self.player.rect)
        if "arena_chefe" in self.bosses_derrotados and self.sala_atual in SALAS_BETA:
            self.fim_beta = TelaFimBeta(self.tela)
    
    
    
    def salvar(self, save_manager, slot):
        if getattr(self, "sala_teste", None):
            self.hud.mostra_mensagem("Teste de mapa: progresso temporário")
            return False
        #verificar se tem inimigo por perto, so pode salvar se nao estiver em combate
        for inimigo in self.inimigos:
            if inimigo.vivo:
                dist = abs(inimigo.rect.centerx - self.player.rect.centerx)
                if dist < 300:
                    audio.play_sfx("ui_error")
                    self.hud.mostra_mensagem("Não é possivel salvar em combate")
                    return False
                

        if save_manager.salvar(slot, self) is False:
            self.hud.mostra_mensagem("Não foi possível salvar")
            return False
        audio.play_sfx("ui_save")
        self.hud.mostra_mensagem("Jogo salvo")
        return True
    
    #DESENHAR   
    
    def desenhar(self):
        if self.fim_beta is not None:
            self.fim_beta.desenhar()
            return
        self._frame_pausa += 1

        #a cena do mundo é desenhada numa superficie do tamanho da area visivel
        #(Screen / zoom) e depois escalada pra tela - é isso que aproxima a camera
        vw = max(1, int(round(Screen_widht / self.camera.zoom)))
        vh = max(1, int(round(Screen_height / self.camera.zoom)))
        vista = pygame.Surface((vw, vh))
        vista.fill((0, 0, 0))

        self.mapa.desenhar(vista, self.camera)

        if self.sala_atual == "arena_chefe" and self.boss_batalha_ativa:
            for parede in self.parede_boss:
                pygame.draw.rect(vista, (67, 57, 105), self.camera.aplicar(parede))

        for tocha in self.tochas:
            tocha.desenhar(vista, self.camera)

        for inimigo in self.inimigos:
            inimigo.desenhar(vista, self.camera)


            if DEBUG:
                #debug: rect lógico do inimigo (vermelho) — hitbox real de combate
                sr_inimigo = self.camera.aplicar(inimigo.rect)
                pygame.draw.rect(vista, (255, 0, 0), sr_inimigo, 2)

                #debug: zona de conexão do golpe em curso — verde se conecta no player, laranja se não
                zona = inimigo.rect_golpe_debug()
                if zona is not None:
                    cor_zona = (0, 255, 0) if zona.colliderect(self.player.rect) else (255, 150, 0)
                    pygame.draw.rect(vista, cor_zona, self.camera.aplicar(zona), 2)

        if DEBUG:
            #debug: rect lógico do player (verde) e hitbox do ataque (amarelo)
            pygame.draw.rect(vista, (0, 255, 0), self.camera.aplicar(self.player.rect), 2)
            rect_ataque_debug = self.player.get_rect_ataque()
            if rect_ataque_debug is not None:
                pygame.draw.rect(vista, (255, 230, 0), self.camera.aplicar(rect_ataque_debug), 2)

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

        # Interacao tem prioridade exclusiva sobre dicas de exploracao.
        desenhou_interacao = False
        # prompt de interacao no mundo (sprite de tecla sobre a cabeca do player)
        if (not self._contexto_suprime_interacao() and
                getattr(self, "_alvo_interacao_atual", None) is not None and
                hasattr(self, "prompt_interacao_mundo")):
            alvo = self._alvo_interacao_atual
            try:
                disponivel = alvo.disponivel_para_prompt(self.player)
            except Exception:
                disponivel = False
            if disponivel:
                ax = self.player.rect.centerx
                ay = self.player.rect.top - 4
                self.prompt_interacao_mundo.desenhar(vista, self.camera, ax, ay, visivel=True)
                desenhou_interacao = True

        tutorial = getattr(self, "tutorial_contextual", None)
        if (tutorial and not desenhou_interacao and not self._contexto_suprime_interacao()
                and self.player.vivo):
            tutorial.desenhar(vista, self.camera, self.player)

        if DEBUG:
            pygame.draw.rect(vista, (0, 255, 0), sr_player, 2)

        if self.debug_combate:
            desenhar_hurtbox(vista, self.camera, self.player)
            desenhar_hitboxes_ativas(vista, self.camera, self.player)
            for inimigo in self.inimigos:
                desenhar_hurtbox(vista, self.camera, inimigo)
                desenhar_hitboxes_ativas(vista, self.camera, inimigo)
            for proj in self.projeteis:
                for hitbox in proj.hitboxes_ativas():
                    pygame.draw.rect(vista, (255, 0, 255), self.camera.aplicar(hitbox.rect), 1)

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
            progresso = 1 - (self.timer_morto / self.duracao_morte)
            desenhar_tela_morte(self.tela, progresso)


        #tela de menu
        if self.pausado:
            desenhar_tela_pausa(self.tela, self._frame_pausa,
                                self.opcoes_pause, self.opcao_pausa_selecionada)
