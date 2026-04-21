import pygame
from settings import Tile_size

class Bau:

    Frame_w = 48
    Frame_h = 32
    N_frames = 5
    Velocidade = 6 #frames de delay entre cada animação


    def __init__(self, x, y, col, linha, item="espada"):
        #col e linha do grid
        
        self.col = col
        self.linha = linha
        self.item = item

        

        self.rect = pygame.Rect(x  , y - 22, Tile_size * 1.2, Tile_size * 2)

        self.aberto = False
        self.ativo = True #false o item ja foi coletado e a animação termina

        self._frame_idx = 0
        self._contador = 0
        self._anim_tocando = False #so anima se o player pressiona E


        #carrega o spritesheet inteiro e so carrega a linha do bau selecionado
        sheet = pygame.image.load("assets/sprites/objetos/baus/Chests.png").convert_alpha()
        
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
        

        #mostra a mensagem quando o player esta perto 
        dist = abs(player.rect.centerx - self.rect.centerx)
        if dist < 10 and not self.aberto:
            hud.mostra_mensagem("pressione E para abrir")

            #player pressinou a tecla
            if teclas[pygame.K_e] and not self._anim_tocando:
                self._anim_tocando = True
                self._frame_idx = 0
                self._contador = 0

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
        if self.item == "espada":
            from entities.objetos.item import EspadaLonga
            player.equipar(EspadaLonga)
            hud.mostra_mensagem("Espada Longa encontrada")


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
        pygame.draw.rect(tela, (220, 180, 60), sr, 2)
