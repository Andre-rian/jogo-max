import pygame 
from settings import Gravidade, Max_Fall_Speed

class Entity(pygame.sprite.Sprite):

    #Classe base para todas as entidades do game player,inimigo, boss e ect
    #possui a responsabilidade de guarda vida,velocidade, aplicar gravidade e ect

    def __init__(self, x, y, largura, altura, hp_max):
        super().__init__()
        

        #posiçao e tamanho no mundo
        self.rect = pygame.Rect(x, y, largura, altura)
        self.no_chao = False
        self.olhando_dir = True
        #velocidade em pixeis 
        self.vel = pygame.Vector2(0,0)

        #vida 
        self.hp_max = hp_max
        self.hp = hp_max
        self.vivo = True
 
        #stamina
        self.stamina_max = 0
        self.stamina = 0
        self.stamina_delay = 0 #o contador espara pra recarrega

        #ecos profanos
        self.ecos_drop = 0


        self.callback_morte = None #setado por quem  spwana o inimigo

        #frames de invencibilidade apos ser hitado
        self.invencivel = False
        self.timer_invenc = 0
        self.Frames_ivenc = 30 #quantidade de frames de invencibilidade


        #knockback
        self.timer_knockback = 0
        self.recebendo_knockback = False

        #mask, começando a implementaçõa 
        self.mask = None


    #Gravidade 
    def aplicar_gravidade(self):
        #adicionar a gravidade no jogo, sendo ela a velocida vertical,e tambem adicionar o limite dela
        if self.no_chao:
            self.vel.y = 1
        else:
            self.vel.y = min(self.vel.y + Gravidade, Max_Fall_Speed)
    
    def atualizar_mask(self):
        #gera o mask a partir do frame atual da animação
        if getattr(self, "anim_atual", None):
            self.mask = pygame.mask.from_surface(self.anim_atual.frame_atual)



    #COLISAO
    def mover_com_colisão(self, rects_solidos):
        #move o rect pelo os eixos separadamente 

        #eixo x

        self.rect.x += int(self.vel.x)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.x > 0:      #indo para direita
                    self.rect.right = tile.left
                elif self.vel.x < 0:
                    self.rect.left = tile.right #indo para esquerda
                self.vel.x = 0 

        #eixo y
        self.no_chao = False
        self.rect.y += int(self.vel.y)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:      #caindo
                    self.rect.bottom = tile.top
                    self.no_chao = True
                    self.vel.y = 0
                elif self.vel.y < 0:    #subindo(bateu no teto)
                    self.rect.top = tile.bottom
                    self.vel.y = 0 
        if self.no_chao:
            self.vel.y = 0

    #Dano/combante
    def receber_dano(self, quantidade, frames_invenc=None):
        #Reduz o hp. se tiver invencivel = ignora. apos levar dano = frames de invecibilidade

        if self.invencivel or not self.vivo:
            
            return
        
        self.hp -= quantidade

        if self.hp <= 0:
            self.hp = 0
            self.vivo = False
            if self.callback_morte:
                self.callback_morte(self.rect.centerx, self.rect.bottom)
        else:
            #ativar os frames de invencibilidade
            self.invencivel = True
            self.timer_invenc = frames_invenc if frames_invenc is not None else self.Frames_ivenc 

    def atualizar_invencibilidade(self):
        #conta a quantidade de frames da invencibilidade

        if self.invencivel:
            self.timer_invenc -= 1
            if self.timer_invenc <= 0:
                self.invencivel = False

    def aplicar_knockback(self, direçao, forca_x=3, forca_y=2, frames=16):
        #aplicar a gravide à entidade : -1 0u 1
        
        self.vel.x = direçao * forca_x
        self.vel.y = forca_y
        self.timer_knockback = frames
        self.recebendo_knockback = True


    def atualizar_knockback(self, rects_solidos, tem_gravide=True):
        self.timer_knockback -= 1

        if tem_gravide:
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
        else:
            #inimigos que voam
            self.rect.x += int(self.vel.x)
            self.rect.y += int(self.vel.y)
            self.vel.x *= 0.85
            self.vel.y *= 0.85

        self.atualizar_invencibilidade()

        if self.timer_knockback <= 0:
            self.recebendo_knockback = False


    def _offset_mask(self):
        #hook: por padrão a mask fica alinhada ao rect. quem desenha fora do rect (a maioria) sobrescreve isso
        return self.rect.x, self.rect.y
    

    def atualizar_mask(self):
        if getattr(self, "anim_atual", None):
            self.mask = pygame.mask.from_surface(self.anim_atual.frame_atual)
            self._mask_pos = self._offset_mask() #guarda onde a mask realmente está no mundo





    def colide_mask_com_rect(self, outro_rect):
        #testa a colisao entre o metodo mask e uma coliso simples tipo a do cenario

        if self.mask is None:
            return self.rect.colliderect(outro_rect)


        mx, my = getattr(self, "_mask_pos", self.rect.topleft)    
        mask_rect = pygame.mask.Mask((outro_rect.width, outro_rect.height), fill=True)
        offset = (outro_rect.x - mx, outro_rect.y - my)
        return self.mask.overlap(mask_rect, offset) is not None
    

    def colide_mask_com_mask(self, outro):
        #testa a colisao de pixel entre duas entidades (inimigo vs player)
        if self.mask is None or outro.mask is None:
            return self.rect.colliderect(outro.rect)
        

        mx, my = getattr(self, "_mask_pos", self.rect.topleft)
        ox, oy = getattr(outro, "_mask_pos", outro.rect.topleft)
        offset = (ox - mx, oy - my)
        return self.mask.overlap(outro.mask, offset) is not None
    