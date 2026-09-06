import pygame

class AnimatedSprite:
    #carrega um spriteshet, fatia em frames e anima automaticamente.

    def __init__(self, caminho, frame_width, frame_height, velocidade=8, escala=1, n_frames=None, loop=True):

        """
        caminho = caminho para a spritesheet
        frame_width = largura de cada frame no spritesheet original
        frame_height = altura de cada frame no spritesheet original
        velocidade = quantos frames de jogo por animação   (menor = animaçao mais rapida)
        escala = fator de escala (2 dobro de tamanho)
        loop = se True, a animação volta pro frame 0 ao terminar (andar, parado, etc).
               se False, ela trava no último frame ao terminar (ataques, golpes, etc).
        """
        self.velocidade = velocidade
        self.escala = escala
        self.loop = loop
        self._contador = 0
        self._frame_idx = 0
        
        #carrega e fatia o spritesheet
        self.frames = self._carregar_frames(caminho, frame_width, frame_height, escala, n_frames)


    def _carregar_frames(self, caminho, fw, fh, escala, n_frames=None):
        
        sheet = pygame.image.load(caminho).convert_alpha()


        if n_frames is None:
            n_frames = sheet.get_width() // fw

        
        frames = []
        for i in range(n_frames):
            #recorta o frame do spritesheet
            frame = sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh))

            #aplicar escala se necessaria
            if escala != 1:
                novo_w = int(fw * escala)
                novo_h = int(fh * escala)
                frame = pygame.transform.scale(frame, (novo_w, novo_h))

            frames.append(frame)
        return frames
    

    def atualizar(self):
        #avançar o frame de animaçao baseado na velocidade

        #se nao é loop e ja chegou no ultimo frame, fica parado nele
        if not self.loop and self._frame_idx == len(self.frames) - 1:
            return

        self._contador += 1
        if self._contador >= self.velocidade:
            self._contador = 0
            if self.loop:
                self._frame_idx = (self._frame_idx + 1) % len(self.frames)
            else:
                self._frame_idx = min(self._frame_idx + 1, len(self.frames) - 1)

    def resetar(self):
        #voltar ao primeiro frame , chamado quando a animaçao é trocada
        self._contador = 0
        self._frame_idx = 0

    def desenhar(self, tela, x, y, espelhado=False):
        #desenhar o frame na posiçao atual x e y, o espelhado=false é para mover a direçao que a sprite esta olhando
        
        frame = self.frames[self._frame_idx]

        if espelhado:
            frame = pygame.transform.flip(frame, True, False)
        
        tela.blit(frame, (x, y))

    @property
    def frame_atual(self):
        #retorna o frame atual como surface util para o metodo mask
        return self.frames[self._frame_idx]
    
    @property
    def terminou(self):
        #verificar se a animação ja terminou
        if not self.loop:
            return self._frame_idx == len(self.frames) - 1
        return self._frame_idx == len(self.frames) - 1 and self._contador >= self.velocidade - 1

    @property
    def largura(self):
        return self.frames[0].get_width()
    
    @property

    def altura(self):
        return self.frames[0].get_height()