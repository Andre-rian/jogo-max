import pygame
import math
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite
from settings import (
    Speed_player, player_pulo, vida_max_player, Dash_speed, Dash_duration, Dash_cooldown,
      Double_tap_window, ataque_dano, ataque_range, ataque_cooldown, Dourado, Tile_size,
      Stamina_pulo, Stamina_dash, Stamina_ataque, Stamina_recarga, Stamina_delay
)

class Player(Entity):

    #possiveis estados de maquina
    Parado = "parado"
    Correndo = "correndo"
    Pulando = "pulando"
    Caindo = "caindo"
    Dash = "Dash"
    Atacando = "atacando"
    Morto = "morto"

    def __init__(self, x, y):
        super().__init__(x, y, largura=32, altura=66, hp_max=vida_max_player)

        #estado atual da maquina de estado 
        
        self.estado = self.Parado

        #Dash
        self.em_dahs = False
        self.timer_dash = 0
        self.cooldown_dash = 0
        self.direçao_dash = 0

        #detectar duplo toque - guarda o frame do ultimo toque de cada tecla

        self._ultimo_toque = {"esquerda": -999, "direita": -999}

        self._frame_atual = 0 #contador de frames atuais

        #guarda o estado das teclas no frame anterior 
        #(detectar o momento exato do toque)`
        self._teclas_anterior = None

        #ataque
        self.atacando = False
        self.timer_ataque = 0
        self.cooldown_ataque = 0

        #invetario(bem basico)
        self.tem_espada = True
        self.tem_armadura = False 


        #checkpoin(inicial)
        self.checkpoint_pos = pygame.Vector2(x, y)
        self.checkpoint_sala = 'calabouço_1' 


        # animações
        KNIGHT = "assets/sprites/player/knight/"
        self.animacoes = {
            self.Parado:   AnimatedSprite(KNIGHT + "_Idle.png",  120, 80, velocidade=8,  escala=2),
            self.Correndo: AnimatedSprite(KNIGHT + "_Run.png",   120, 80, velocidade=6,  escala=2),
            self.Pulando:  AnimatedSprite(KNIGHT + "_Jump.png",  120, 80, velocidade=8,  escala=2),
            self.Caindo:   AnimatedSprite(KNIGHT + "_Fall.png",  120, 80, velocidade=8,  escala=2),
            self.Atacando: AnimatedSprite(KNIGHT + "_Attack.png",120, 80, velocidade=5,  escala=2),
            self.Dash:     AnimatedSprite(KNIGHT + "_Dash.png",  120, 80, velocidade=4,  escala=2),
            self.Morto:    AnimatedSprite(KNIGHT + "_Death.png", 120, 80, velocidade=8,  escala=2),
                }
        self._estado_anterior = self.Parado
        self.anim_atual = self.animacoes[self.Parado]

    #UPDATE
    def atualizar(self, rects_solidos, camera, pos_mouse_mundo):
        if not self.vivo:
            self.estado = self.Morto                                
            if self._estado_anterior != self.Morto:   #animação de morte
                self.anim_atual = self.animacoes[self.Morto]
                self.anim_atual.resetar()
                self._estado_anterior = self.estado
            
            
            if not self.anim_atual.terminou:
                    self.anim_atual.atualizar()
            return 
        


           


        self._frame_atual += 1

        teclas = pygame.key.get_pressed()
        
        self._verificar_dash(teclas)
        self._mover_horizontal(teclas)
        self._pular(teclas)
        self._atacar(pos_mouse_mundo)
        self._atualizar_stamina(teclas)

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()
        self._atualizar_estado()
        self._atualizar_times()



        #troca a animaçao se o estado mudou
        if self.estado != self._estado_anterior:
            self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Parado])
            self.anim_atual.resetar()
            self._estado_anterior = self.estado

        #avançar o frame da animaçao atual
        self.anim_atual.atualizar()


        #salvar teclas para o proximo frame
        self._teclas_anterior = teclas

    #dash - duplo toque a ou d

    def _verificar_dash(self, teclas):
        #detectar o duplo toque dentro da janela de frames
        #calcular o tempo de um clique ao outro e detectar se pode haver o dash ou nao, por isso a biblioteca math

        if self.em_dahs:
            return #se ja ta em dash, nao acontece nada
        
        if self._teclas_anterior is None:
            return #PRIMEIRO frame, nao tem um antes
        
        # detectar o momento do toque
        toque_esq = teclas[pygame.K_a] and not self._teclas_anterior[pygame.K_a]
        toque_dir = teclas[pygame.K_d] and not self._teclas_anterior[pygame.K_d]

        if toque_esq:
            intervalo = self._frame_atual - self._ultimo_toque["esquerda"]
            #intervalo > 1 evitar detectar o mesmo toque duas vezes
            
            if 1 < intervalo <= Double_tap_window and self.cooldown_dash == 0:
                self._iniciar_dash(-1)
                
            self._ultimo_toque["esquerda"] = self._frame_atual

        if toque_dir:
            intervalo = self._frame_atual - self._ultimo_toque["direita"]
            #intervalo > 1 evitar detectar o mesmo toque duas vezes
            
            if 1 < intervalo <= Double_tap_window and self.cooldown_dash == 0:
                self._iniciar_dash(1)
                
            self._ultimo_toque["direita"] = self._frame_atual
    
    def _iniciar_dash(self, direçao):
        if not self._tem_stamina(Stamina_dash):
            return #sem stamina = sem dash
        self.em_dahs = True
        self.direçao_dash = direçao
        self.timer_dash = Dash_duration
        self.cooldown_dash = Dash_cooldown
        self.vel.y = 0 #cancela a gravidade no dash
        self.olhando_dir = direçao > 0
        self._gastar_stamina(Stamina_dash)
    
    #MOVIMENTO HORIZONTAL

    def _mover_horizontal(self, teclas):
        if self.em_dahs:
            #durante o dash a velocidade é fixa
            self.vel.x = Dash_speed * self.direçao_dash
            return
        
        if teclas[pygame.K_d]:
            self.vel.x = Speed_player
            self.olhando_dir = True
        
        elif teclas[pygame.K_a]:
            self.vel.x = -Speed_player
            self.olhando_dir = False
        else:
            #friçao - desacerela gradualmente ao soltar a tecla
            self.vel.x *= 0.8
            if abs(self.vel.x) < 0.5:
                self.vel.x = 0

    #PULO
    def _pular(self, teclas):
        if self.em_dahs:
            #so pular se tiver no chao
            return
        if teclas[pygame.K_SPACE] and self.no_chao:
            if not self._tem_stamina(Stamina_pulo):
                return #sem stamina nao pula
            self.vel.y = player_pulo
            self.no_chao = False
            self._gastar_stamina(Stamina_pulo)

    #ATAQUEEEE -- clique esquerdo do mouse
    def _atacar(self, pos_mouse_mundo):
        #sem espada nao atacar(por enquanto)
        if not self.tem_espada:
            return

        if self.cooldown_ataque > 0:
            return
        
        if not self._tem_stamina(Stamina_ataque):
            return #sem stamina = sem ataque
        
        if pygame.mouse.get_pressed()[0]:   #botao esquerdo
            self.atacando = True
            self.timer_ataque = ataque_cooldown // 2
            self.cooldown_ataque = ataque_cooldown
            self._gastar_stamina(Stamina_ataque)

            #atualizar a direçao com base no mouse
            dx = pos_mouse_mundo.x - self.rect.centerx
            self.olhando_dir = dx >= 0

    def get_rect_ataque(self):
        #retorna o rect da hitbox dp ataque  enquanto esta atacando.é ele que vai verificar as hitsbox dos inimigos

        if not self.atacando:
            return None
        
        if self.olhando_dir:  #atacando para direita
            return pygame.Rect(
                self.rect.right, 
                self.rect.centery - 16,
                ataque_range, 
                32
            )
        
        else:
            return pygame.Rect(
                self.rect.left - ataque_range,
                self.rect.centery - 16,
                ataque_range,
                32
            )
        
    #recarrega stamina
    def _atualizar_stamina(self, teclas):
        #mundaça na stamina como prometido, agora ela so nao recupera se o player esta fazendo uma "ação pesada"
        
        em_acao_pesada = (self.em_dahs or
                self.atacando or
                teclas[pygame.K_SPACE])
        
        if em_acao_pesada or not self.no_chao:
            #reseta o delay enquanto esta em açao
            self.stamina_delay = Stamina_delay
        else:
            #recupera normalmente a stamina
            if self.stamina_delay > 0:
                self.stamina_delay -= 1
            else:
                #recarrega gradualmente
                self.stamina = min(
                    self.stamina_max,
                    self.stamina + Stamina_recarga
                )
        

    #verificar se tem stamina

    def _tem_stamina(self, custo):
        return self.stamina >= custo
    
    def _gastar_stamina(self, custo):
        #garante que a stamina vai ser gastar, e nao vai ficar abaixo de 0
        self.stamina = max(0, self.stamina - custo)


    #TIMES - CONTA os downs de dash e ataques

    def _atualizar_times(self):
        if self.em_dahs:
            self.timer_dash -= 1
            if self.timer_dash <= 0:
                self.em_dahs = False
                self.vel.x = 0

        #cooldowm entre dashes
        if self.cooldown_dash > 0:
            self.cooldown_dash -= 1 

        #ataque ativo

        if self.atacando:
            self.timer_ataque -= 1
            if self.timer_ataque <= 0:
                self.atacando = False

        #cooldown entres ataques

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1

    #MAQUINA DE ESTADOS 

    def _atualizar_estado(self):
        #define o estado atual com base no player

        if self.em_dahs:
            self.estado = self.Dash
        elif self.atacando:
            self.estado = self.Atacando
        elif not self.no_chao and self.vel.y > 0:
            self.estado = self.Caindo
        elif not self.no_chao and self.vel.y < 0:
            self.estado = self.Pulando
        elif abs(self.vel.x) > 0.5:
            self.estado = self.Correndo
        else:
            self.estado = self.Parado

    
    #CHECKPOINT (PROVISORIO)

    def defenir_checkpoint(self, nome_sala,x=None, y=None):
        #salva a posição atual como checkpoint

        self.checkpoint_pos.x = x if x is not None else self.rect.x 
        self.checkpoint_pos.y = y if y is not None else self.rect.y 
        self.checkpoint_sala = nome_sala

    def respawnar(self): 
        #voltar para o ultimo checkpoint com o hp cheio
        self.rect.x = int(self.checkpoint_pos.x)
        self.rect.y = int(self.checkpoint_pos.y)
        self.hp = self.hp_max
        self.vivo = True
        self.vel = pygame.Vector2(0,0)
        self.estado = self.Parado
        self.em_dahs = False 
        self.atacando = False


    #colisao
    def mover_com_colisão(self, rects_solidos):
        # chama a colisão normal da Entity
        super().mover_com_colisão(rects_solidos)
    
        # se estava em dash e bateu na parede (vel.x zerou), cancela o dash
        if self.em_dahs and self.vel.x == 0:
            self.em_dahs = False
            self.timer_dash = 0
    

    #DESENHO (placerholder geometrico ou coisa do tipo)
    def desenhar(self, tela, camera):
        sr = camera.aplicar(self.rect)

        if not self.vivo and self.estado != self.Morto:
            return

        #piscar durante invecibilidade 
        if self.invencivel and self._frame_atual % 6 < 3:
            return
        
        #centraliza a sprite visualmente sobre o rect de colisão
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        if  self.olhando_dir:
            offset_x = sr.centerx - sprite_w // 2 + 10
        else:
            offset_x = sr.centerx - sprite_w // 2 - 10
        
        
        offset_y = sr.bottom - sprite_h

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        #rastro azul do dash
        if self.em_dahs:
            rastro = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            rastro.fill((100, 180, 255, 80))
            tela.blit(rastro, sr)