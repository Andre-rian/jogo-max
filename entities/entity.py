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

        #plataformas one-way: True quando os pés estão apoiados em uma
        self._sobre_plataforma = False

        #durante drop, linha (row) que o solid deve ignorar ate o player descer abaixo dela
        self._drop_linha_top = None
        self._drop_linha_baixo = 0


    #Gravidade 
    def aplicar_gravidade(self):
        #adicionar a gravidade no jogo, sendo ela a velocida vertical,e tambem adicionar o limite dela
        if self.no_chao:
            self.vel.y = 1
        else:
            self.vel.y = min(self.vel.y + Gravidade, Max_Fall_Speed)
    
    #COLISAO
    def mover_com_colisão(self, rects_solidos, rects_plataforma=None):
        #move o rect pelo os eixos separadamente 

        #eixo x

        self.rect.x += int(self.vel.x)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                #resolve pela penetração mínima (face mais próxima), NÃO pela direção
                #da velocidade: senão, preso em um lado contrário ao movimento (ex.:
                #respawn/teletransporte dentro de uma parede), o player é LANÇADO pro
                #outro lado da tile e atravessa as colisões no caminho
                saida_esq = self.rect.right - tile.left
                saida_dir = tile.right - self.rect.left
                if saida_esq <= saida_dir:
                    self.rect.right = tile.left
                else:
                    self.rect.left = tile.right
                self.vel.x = 0
                #resolve só o 1º solido por frame (evita cascata de 32px por tile)
                break 

        #eixo y
        self.no_chao = False
        self._sobre_plataforma = False
        pe_anterior = self.rect.bottom
        self.rect.y += int(self.vel.y)

        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:      #caindo
                    #1) durante o drop (timer>0) deixa passar tudo
                    #2) apos o timer, ainda ignora o solid da MESMA row da plataforma
                    #   ate o player ter descido abaixo dela (senão é jogado de volta)
                    ignorar_solid = self._atravessando()
                    if (not ignorar_solid and self._drop_linha_top is not None
                            and tile.top == self._drop_linha_top
                            and self.rect.top < self._drop_linha_baixo):
                        ignorar_solid = True
                    if ignorar_solid:
                        continue
                    #também por penetração mínima: cair de lado com um canto preso
                    #numa parede não pode "puxar" o player para cima/para o outro lado
                    saida_topo = self.rect.bottom - tile.top
                    saida_baixo = tile.bottom - self.rect.top
                    if saida_topo <= saida_baixo:
                        self.rect.bottom = tile.top
                        self.no_chao = True
                    else:
                        self.rect.top = tile.bottom
                    self.vel.y = 0
                    break
                elif self.vel.y < 0:    #subindo(bateu no teto)
                    #plataforma one-way na subida: sólido da MESMA row da plataforma (a
                    #parede que a ladeia) não bloqueia enquanto o player cruza a horizontal
                    #da plataforma. Assim o pulo vindo de baixo passa pelo vão e sobe limpo,
                    #podendo pousar em cima. Teto de verdade (outra row) continua bloqueando.
                    if rects_plataforma and self._solido_na_row_da_plataforma(tile, rects_plataforma):
                        continue
                    self.rect.top = tile.bottom
                    self.vel.y = 0
                    break 

        if rects_plataforma and self.vel.y >= 0 and not self._atravessando():
            #plataforma one-way: segura só vindo de cima. pula por baixo e desce (drop) ignoram
            #usar sobreposição horizontal + proximidade vertical (nao colliderect): detecta
            #tambem quando o player é segurado pelo solido ao lado e fica em edge-touch (ex: 288)
            for plat in rects_plataforma:
                dentro_x = self.rect.right > plat.left and self.rect.left < plat.right
                if dentro_x and self.rect.bottom >= plat.top and pe_anterior - 1 <= plat.top:
                    self.rect.bottom = plat.top
                    self.no_chao = True
                    self._sobre_plataforma = True
                    self.vel.y = 0

        if self.no_chao:
            self.vel.y = 0

        #se o player desceu além da row do drop, pode voltar a colidir com solidos normais
        if self._drop_linha_top is not None and self.rect.top >= self._drop_linha_baixo:
            self._drop_linha_top = None

    def _atravessando(self):
        #entidades que podem descer atraves de plataformas (player) sobrescrevem
        return False

    def _solido_na_row_da_plataforma(self, tile, rects_plataforma):
        #o sólido está na mesma row de uma plataforma one-way E o player a cruza na horizontal?
        for plat in rects_plataforma:
            if tile.top == plat.top and self.rect.right > plat.left and self.rect.left < plat.right:
                return True
        return False

    def distancia_horizontal(self, outro):
        #distancia em px entre as bordas dos rects (0 se as faixas X se sobrepoem).
        #medir por bordas (e nao por centros) evita o "alcance fantasma" que embutia
        #metade da largura de cada hitbox nos golpes corpo-a-corpo
        return max(0, max(self.rect.left - outro.rect.right,
                          outro.rect.left - self.rect.right))

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
    