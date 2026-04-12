

import pygame
import random
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite

class Globin(Entity):

    Patrulha = "patrulha"
    Perseguir = "perseguir"
    Atacando = "atacando"
    Morto = "morto"

    Dano_normal = 10
    Dano_dash = 15
    Dano_bomba = 20
    Vel_patrulha = 1.9
    Vel_perseguir = 3.0
    Alcance_detec = 350 #distancia maxima que o globin detecta o player
    Alcance_ataq_normal = 80 #medio - ataque normal
    Alcance_ataq_dash = 55 #perto - ataque dash
    Alcance_ataq_bomba = 200 #longe - ataque bomba
    Cooldown_ataq = 300 #frames de cooldown entre ataques, para evitar que o globin ataque toda hora sem dar chance pro player reagir
    Cooldown_bomba_max = 400 #6 segundos de cooldown para o ataque de bomba, que é o mais forte, para evitar spam

    def __init__(self, x, y, patrulha_esq, patrulha_dir):
        super().__init__(x, y, largura=30, altura=44, hp_max=40)

        self.patrulha_esq = patrulha_esq
        self.patrulha_dir = patrulha_dir

        self.estado = self.Patrulha
        self.cooldown_ataq = 0
        self._frame = 0
        self.timer_knockback = 0
        self.cooldown_bomba = 0
      

        self.vel.x = self.Vel_patrulha
        self.olhando_dir = True

        #qual o ataque atual, usado para decidir o dano e a animação

        self._ataque_atual = None # normal, dash ou bomba
        self._animando_ataque = False #trava a ia do inimigo enquanto esta na animaçao de ataque, para evitar bugs de troca de animação no meio do ataque

        #lista de bombas, para serem usadas la no game_scene, onde a logica dos projeteis fica
        self.bombas_spawnar = []



        Gob = "assets/sprites/enemies/monsters/goblin/"
        
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Gob + "Idle.png",     150, 150, velocidade=10, escala=1, n_frames=4),
            self.Perseguir: AnimatedSprite(Gob + "Run.png",      150, 150, velocidade=6,  escala=1, n_frames=8),
            self.Atacando:  AnimatedSprite(Gob + "Attack.png",   150, 150, velocidade=5,  escala=1, n_frames=8),
            self.Morto:     AnimatedSprite(Gob + "Death.png",    150, 150, velocidade=8,  escala=1, n_frames=4),
        }
        self.anim_attack2 = AnimatedSprite(Gob + "Attack2.png", 150, 150, velocidade=5, escala=1, n_frames=8)
        self.anim_attack3 = AnimatedSprite(Gob + "Attack3.png", 150, 150, velocidade=5, escala=1, n_frames=12)
        self.anim_hit = AnimatedSprite(Gob + "Take Hit.png", 150, 150, velocidade=4, escala=1, n_frames=4)

        self._estado_anterior = self.Patrulha
        self.anim_atual = self.animaçoes[self.Patrulha]
        self._em_hit = False
        self._timer_hit = 0

    def atualizar(self, rects_solidos, player):
        if not self.vivo:
            if not hasattr(self, "_timer_morte"):
                self._timer_morte = 60
                self.estado = self.Morto
                self.anim_atual = self.animaçoes[self.Morto]
                self.anim_atual.resetar()
            
            
            if not self.anim_atual.terminou:
                self.anim_atual.atualizar()

            self._timer_morte -= 1
            if self._timer_morte <= 0:
                return 0
            return -1
        
        self._frame += 1
        

        if self.timer_knockback > 0:
            self.timer_knockback -= 1
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            self.atualizar_invencibilidade()
            if self.cooldown_ataq > 0:
                self.cooldown_ataq -= 1
            
            if self.cooldown_bomba > 0:
                self.cooldown_bomba -= 1

            if self._em_hit:
                self._timer_hit -= 1
                if self._timer_hit <= 0:
                    self._em_hit = False
                    self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Patrulha])
                    self.anim_atual.resetar()
                    self._estado_anterior = self.estado
                
                else:
                    self.anim_atual = self.anim_hit
                    if not self.anim_hit.terminou:
                        self.anim_atual.atualizar()
            return 0

        #se estiver animando um ataque, trava a IA ate a animaçao acabar, para evitar bugs de troca de animaçao no meio do ataque
        if self._animando_ataque:
            self._atualizar_animaçao_ataque(player)
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            if self.cooldown_ataq > 0:
                self.cooldown_ataq -= 1
            if self.cooldown_bomba > 0:
                self.cooldown_bomba -= 1
            return 0
        


        dist = abs(player.rect.centerx - self.rect.centerx)
        

        if player.vivo and dist < self.Alcance_detec:
            if dist < self.Alcance_ataq_dash:
                if self.cooldown_ataq <= 0:
                    #muito perto, ataque dash 
                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)
                else:
                    #cooldown ativo
                    self.estado = self.Atacando
                    self.vel.x = 0
            

            elif dist < self.Alcance_ataq_normal:
                #distancia media, so ataca se tiver perto o suficiente, senao fica perseguindo
                if self.cooldown_ataq <= 0:
                    # perto o suficiente para atacar, mesmo que seja o ataque normal

                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)

                else:
                    #cooldown do ataque, mas ainda nao esta perto o suficiente para atacar, entao fica perseguindo
                    self.estado = self.Perseguir
                    direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                    self.vel.x = self.Vel_perseguir * direçao
                    self.olhando_dir = direçao > 0

            elif dist < self.Alcance_ataq_bomba:
                if self.cooldown_bomba <= 0:
                    #distancia longe, ataque bomba
                    self.estado = self.Atacando
                    self.vel.x = 0
                    self._tentar_atacar(dist, player)

                else:
                    #cooldown ativo
                    self.estado = self.Perseguir
                    direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                    self.vel.x = self.Vel_perseguir * direçao    
                    self.olhando_dir = direçao > 0
        
        else:
            self.estado = self.Patrulha
            if self.rect.left <= self.patrulha_esq:
                self.vel.x = self.Vel_patrulha
                self.olhando_dir = True
            
            elif self.rect.right >= self.patrulha_dir:
                self.vel.x = -self.Vel_patrulha
                self.olhando_dir = False

        
        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()

        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1
        
        if self.cooldown_bomba > 0:
            self.cooldown_bomba -= 1

        if self._em_hit:
            self._timer_hit -= 1
            if self._timer_hit <= 0:
                self._em_hit = False
                self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado
            else:
                self.anim_atual = self.anim_hit
                if not self.anim_hit.terminou:
                    self.anim_atual.atualizar()
            return 0
        
        else:
            if self.estado != self._estado_anterior:
                self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Patrulha])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado
        
        self.anim_atual.atualizar()
        return 0
    

    def _tentar_atacar(self, dist, player):
        if self.cooldown_ataq > 0:
            return
        
        self.cooldown_ataq = self.Cooldown_ataq
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.olhando_dir = direçao > 0

        if dist < self.Alcance_ataq_dash:
            #muito perto, ataque dash
            self._iniciar_ataque("dash", direçao)

        elif dist < self.Alcance_ataq_normal:
            #distancia media, ataque normal ou dash
            if random.random() < 0.5:
                self._iniciar_ataque("normal")
            else:
                self._iniciar_ataque("dash", direçao)
        else:
            #distancia longe, ataque bomba
            if self.cooldown_bomba <= 0:
                self._iniciar_ataque("bomba", direçao, player)
                self.cooldown_bomba = self.Cooldown_bomba_max
            else:
                #se a bomba estiver em cooldown, tenta os outros ataques
                self.estado = self.Perseguir
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0

    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        self._ataque_atual = tipo
        self._animando_ataque = True

        if tipo == "normal":
            direçao_atq = 1 if self.olhando_dir else -1
            self.vel.x = direçao_atq * self.Vel_perseguir
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()
        
        elif tipo == "dash":
            #recua para tras antes de atacar
            self.vel.x = -direçao * 4
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()

        elif tipo == "bomba":
            
            self.anim_atual = self.anim_attack3
            self.anim_atual.resetar()
            #agenda a bomba para spawnar no meio da animaçao de ataque
            self._bombar_spawnar = {
                "direçao": direçao,
                "frame_spawn": 6 ,#spawna a bomba no frame 6 da animaçao, que é quando o goblin levanta a mao pra jogar a bomba
                "spawnando": False #flag pra garantir que so spawna uma bomba por ataque

            }

    def _atualizar_animaçao_ataque(self, player):
        self.anim_atual.atualizar()

        #logica espesifica para cada ataque
        if self._ataque_atual == "normal":
            #dano no meio da animaçao
            if self.anim_atual._frame_idx == 3 and not hasattr(self, "_dano_normal_aplicado"):
                self._dano_normal_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:
                    player.receber_dano(self.Dano_normal, frames_invenc=10)
        
        elif self._ataque_atual == "dash":
            #dano no frame final da animaçao
            if self.anim_atual._frame_idx == 6 and not hasattr(self, "_dano_dash_aplicado"):
                self._dano_dash_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:
                    player.receber_dano(self.Dano_dash)
            self.vel.x *= 0.8 #diminui a velocidade do dash com o tempo

        elif self._ataque_atual == "bomba":
            #spawna a bomba no frame certo
            if not self._bombar_spawnar["spawnando"]:
                if self.anim_atual._frame_idx >= self._bombar_spawnar["frame_spawn"]:
                    self._bombar_spawnar["spawnando"] = True
                    from entities.projeteis.bomba import Bomba
                    bomba = Bomba(
                        self.rect.centerx,
                          self.rect.centery,
                            self._bombar_spawnar["direçao"],
                              self.Dano_bomba)
                    self.bombas_spawnar.append(bomba)

        #terminou a animação libera a ia
        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            #limpa as flags de dano para poder atacar de novo
            if hasattr(self, "_dano_normal_aplicado"):
                del self._dano_normal_aplicado
            if hasattr(self, "_dano_dash_aplicado"):
                del self._dano_dash_aplicado
            
            self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Patrulha])
            self.anim_atual.resetar()
            self._estado_anterior = self.estado



    def receber_hit(self, dano, direçao_knockback):
        self.receber_dano(dano)
        self.vel.x = direçao_knockback * 3
        self.vel.y = -2
        self.timer_knockback = 16
        self._animando_ataque = False #interrompe o ataque se receber hit no meio da animação
        self._ataque_atual = None



        if not self.vivo and not hasattr(self, "_timer_morte"):
            self._timer_morte = 60
            self.estado = self.Morto
            self.anim_atual = self.animaçoes[self.Morto]
            self.anim_atual.resetar()

        
        if self.vivo:
            self._em_hit = True
            self._timer_hit = 20
            self.anim_hit.resetar()


    def desenhar(self, tela, camera):
        if not self.vivo and (not hasattr(self, "_timer_morte") or self._timer_morte <= 0):
            return
        
        sr = camera.aplicar(self.rect)

        if self.vivo and self.invencivel and self._frame % 6 < 3:
            return
        
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        

        
        #ajuste manual pro sprite do globin que tem muito espaço vazio 
        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h + 72

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

    def _desenhar_hp(self, tela, sr):
        bar_w = sr.width
        ratio = self.hp / self.hp_max
        pygame.draw.rect(tela, (200, 40, 40),
                         (sr.x, sr.y - 8, int(bar_w * ratio), 4), border_radius=2)
