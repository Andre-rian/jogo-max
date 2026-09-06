import logging
import pygame
from settings import Tile_size, DEBUG
from entities.objetos.item import get_item
from core.recursos import carregar_imagem, criar_placeholder

logger = logging.getLogger(__name__)

class Bau:


    Frame_w = 48
    Frame_h = 32
    N_frames = 5
    Velocidade = 6 #frames de delay entre cada animação


    def __init__(self, x, y, col, linha, id_item=1):
        #col e linha do grid
        
        self.col = col
        self.linha = linha
        self.id_item = id_item 
        self.item = get_item(id_item)

        self.callback_aberto = None

        self.rect = pygame.Rect(x  , y - 22, Tile_size * 1.2, Tile_size * 2)

        #area de interaçao com folga de meio tile - aceita o player encostado
        self.interacao = self.rect.inflate(Tile_size // 2, Tile_size // 2)

        self.aberto = False
        self.ativo = True #false o item ja foi coletado e a animação termina

        self._frame_idx = 0
        self._contador = 0
        self._anim_tocando = False #so anima se o player pressiona E


        #carrega o spritesheet inteiro e so carrega a linha do bau selecionado
        sheet = carregar_imagem("assets/sprites/objetos/baus/Chests.png")
        if sheet.get_width() < self.Frame_w or sheet.get_height() < self.Frame_h * 2:
            logger.warning(
                f"[Bau] spritesheet de baú muito pequena ({sheet.get_width()}x{sheet.get_height()}) "
                "— usando placeholder magenta"
            )
            sheet = criar_placeholder((self.Frame_w, self.Frame_h * 2))
        
        self._frames_fechado = []
        self._frames_aberto = []

        for i in range(self.N_frames):
            #linha 0 - fechado
            frame = sheet.subsurface(pygame.Rect(
                i * self.Frame_w, 0,
                self.Frame_w, self.Frame_h
            ))
            self._frames_fechado.append(frame)
            
            #linha 1 - aberto
            frame_aberto = sheet.subsurface(pygame.Rect(
                i * self.Frame_w, self.Frame_h,
                self.Frame_w, self.Frame_h
            ))
            self._frames_aberto.append(frame_aberto)
        
        
        
        tamanho = (Tile_size * 1.7, Tile_size * 1.7)
        self._frames_fechado = [pygame.transform.scale(f, tamanho) for f in self._frames_fechado]
        self._frames_aberto = [pygame.transform.scale(f, tamanho) for f in self._frames_aberto]
        
    def atualizar(self, player, teclas, mapa, hud):
        if not self.ativo:
            return
        

        #mostra a mensagem apenas enquanto o player colide com a hitbox do bau
        colide = player.rect.colliderect(self.interacao)
        if colide and not self.aberto:
            hud.mostrar_prompt("pressione E para abrir")

            #player pressinou a tecla
            if teclas[pygame.K_e] and not self._anim_tocando and player.cooldown_interaçao <= 0:
                self._anim_tocando = True
                self._frame_idx = 0
                self._contador = 0
                self.cooldown_interaçao = 30
        else:
            hud.limpar_prompt()

        #tocar a animação antes de abrir
        if self._anim_tocando:
            self._contador += 1
            if self._contador >= self.Velocidade:
                self._contador = 0
                self._frame_idx += 1


                #chegou no ultimo frame - abre o bau
                if self._frame_idx >= self.N_frames:
                    self._frame_idx = self.N_frames - 1
                    self._anim_tocando = False
                    self.aberto = True
                    self._dar_item(player, hud)
                    mapa.remover_tile(self.col, self.linha)

    def _dar_item(self, player, hud):
            
        player.adicionar_ao_inventario(self.item)
        hud.limpar_prompt()
        hud.mostrar_item_coletado(self.item)
        if self.callback_aberto:
            self.callback_aberto(self.col, self.linha)

    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        sr = camera.aplicar(self.rect)

        if self.aberto:
            frame = self._frames_aberto[self.N_frames - 1]

        elif self._anim_tocando:
            frame = self._frames_fechado[self._frame_idx]

        else:
            frame = self._frames_fechado[0]

        tela.blit(frame, sr)

        #debug
        if DEBUG:
            pygame.draw.rect(tela, (220, 180, 60), sr, 2)
