import pygame
import random
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite
from entities.projeteis.projetil_boss import ProjetilBoss




class EsqueletoBoss(Entity):
    
    Patrulha = "patrulha"
    Perseguir = "perseguir"
    Atacando = "atacando"
    Morto = "Morto"


    Dano_normal             = 25
    Dano_varrido            = 30
    Dano_projetil           = 20
    
    Vel_perseguir           = 1.8
    
    Alcance_detec           = 400
    Alcance_ataq_normal     = 90
    Alcance_ataq_varrido    = 120
    Alcance_ataq_projetil   = 160
    Alcance_escudo          = 150
    
    Cooldown_ataq           = 150
    Cooldown_projetil_max   = 280
    Cooldown_escudo_max     = 350
    Duracao_escudo_max      = 90



    def __init__(self, x, y, callback_morte=None):
        super().__init__(x, y, largura=50, altura=90, hp_max=300)

        self._callback_morte = callback_morte


        self.estado             = self.Perseguir
        
        
        self.cooldown_ataq      = 0
        self.cooldown_projetil  = random.randint(0, self.Cooldown_projetil_max)
        self.cooldown_escudo    = random.randint(0, self.Cooldown_escudo_max)
        
        
        self._duracao_escudo    = 0
        self._escudo_ativo      = False
        
        
        self._frame             = 0
        self.timer_knockback    = 0


        self.vel.x          = 0
        self.olhando_dir    = True


        self._ataque_atual = None
        self._animando_ataque = False 
        self.projeteis_spawnar = []

        Boss_skeleton = "assets/sprites/enemies/monsters/esqueletos/"

        self.animaçoes = {
            self.Patrulha: AnimatedSprite(Boss_skeleton + "Idle.png", 150, 150, velocidade=8, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Boss_skeleton + "Walk.png", 150, 150, velocidade=8, escala=2, n_frames=4),
            self.Atacando: AnimatedSprite(Boss_skeleton + "Attack.png", 150, 150, velocidade=6, escala=2, n_frames=8),
            self.Morto: AnimatedSprite(Boss_skeleton + "Death.png", 150, 150, velocidade=8, escala=2, n_frames=4),
            

        }
        self.anim_attack2 = AnimatedSprite(Boss_skeleton + "Attack2.png", 150, 150, velocidade=6, escala=2, n_frames=8)
        self.anim_attack3 = AnimatedSprite(Boss_skeleton + "Attack3.png", 150, 150, velocidade=6, escala=2, n_frames=6)        
        self.anim_shield = AnimatedSprite(Boss_skeleton + "Shield.png", 150, 150, velocidade=8, escala=2, n_frames=4)
        self.anim_hit = AnimatedSprite(Boss_skeleton + "Take Hit.png", 150, 150, velocidade=10, escala=2, n_frames=4)

        self._estado_anterior = self.Perseguir
        self.anim_atual = self.animaçoes[self.Perseguir]
        self._em_hit = False
        self._timer_hit = 0


    #propriedades para o hud
    @property
    def nome(self):
        return "Carrasco Esquelético"
    

    #Atualizar
    def atualizar(self, rects_solidos, player):
        self.projeteis_spawnar.clear()


        #morte
        if not self.vivo:
            if not hasattr(self, "_timer_morte"):
                self._timer_morte = 120
                self.estado = self.Morto
                self.anim_atual = self.animaçoes[self.Morto]
                self.anim_atual.resetar()
                if self._callback_morte:
                    self._callback_morte(self.rect.centerx, self.rect.bottom)
            
            
            if not self.anim_atual.terminou:
                self.anim_atual.atualizar()
                
            self._timer_morte -= 1
            if self._timer_morte <= 0:
                return 0
            return -1
        self._frame += 1


        #knockback
        if self.timer_knockback > 0:
            self.timer_knockback -= 1
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            self.atualizar_invencibilidade()
            if self.cooldown_ataq    > 0: self.cooldown_ataq    -= 1
            if self.cooldown_projetil> 0: self.cooldown_projetil-= 1
            if self.cooldown_escudo  > 0: self.cooldown_escudo  -= 1

            if self._em_hit:
                self._timer_hit -= 1
                if self._timer_hit <= 0:
                    self._em_hit    = False
                    self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Perseguir])
                    self.anim_atual.resetar()
                    self._estado_anterior = self.estado
                else:
                    self.anim_atual = self.anim_hit
                    if not self.anim_hit.terminou:
                        self.anim_hit.atualizar()
            return 0


        #escudo ativo, trava tudo e bloqueia o dano
        if self._escudo_ativo:
            self._duracao_escudo -= 1
            self.anim_atual = self.anim_shield
            self.anim_shield.atualizar()
            if self.cooldown_escudo > 0: self.cooldown_escudo -= 1
            if self._duracao_escudo <= 0:
                self._escudo_ativo = False
                self.estado = self.Perseguir
                self.anim_atual = self.animaçoes[self.Perseguir]
                self.anim_atual.resetar()
                self._estado_anterior = self.Perseguir
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            return 0 
        
        #animando ataque
        if self._animando_ataque:
            self._atualizar_animaçao_ataque(player)
            self.aplicar_gravidade()
            self.mover_com_colisão(rects_solidos)
            if self.cooldown_ataq > 0: self.cooldown_ataq -= 1
            if self.cooldown_projetil > 0: self.cooldown_projetil -= 1
            if self.cooldown_escudo > 0: self.cooldown_escudo -= 1 
            return 0
        
        #ia
        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.vivo and dist < self.Alcance_detec:




            if dist < self.Alcance_ataq_normal:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)

            
            elif dist < self.Alcance_ataq_varrido:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)

            
            elif dist < self.Alcance_ataq_projetil and self.cooldown_projetil <= 0:
                self.estado = self.Atacando
                self.vel.x = 0
                self._tentar_atacar(dist, player)


            elif self.cooldown_escudo <= 0 and dist < self.Alcance_escudo:
                self._escudo_ativo = True
                self._duracao_escudo = self.Duracao_escudo_max
                self.cooldown_escudo = self.Cooldown_escudo_max
                self.vel.x = 0


            else:
                self.estado = self.Perseguir
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0
        
        
        else:
            self.estado = self.Patrulha
            self.vel.x = 0

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()


        if self.cooldown_ataq    > 0: self.cooldown_ataq    -= 1
        if self.cooldown_projetil> 0: self.cooldown_projetil-= 1
        if self.cooldown_escudo  > 0: self.cooldown_escudo  -= 1


        if self._em_hit:
            self._timer_hit -= 1
            if self._timer_hit <= 0:
                self._em_hit = False
                self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Perseguir])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

            else:
                self.anim_atual = self.anim_hit
                if not self.anim_hit.terminou:
                    self.anim_hit.atualizar()
            return 0
        
        else:
            if self.estado != self._estado_anterior:
                self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Perseguir])
                self.anim_atual.resetar()
                self._estado_anterior = self.estado

        self.anim_atual.atualizar()
        return 0 
    

    #funçao de tentar atacar basicamente igual a dos outros inimigos
    def _tentar_atacar(self, dist, player):
        if self.cooldown_ataq > 0:
            return
        
        self.cooldown_ataq = self.Cooldown_ataq
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1 
        self.olhando_dir = direçao > 0


        if dist < self.Alcance_ataq_normal:
            self._iniciar_ataque("normal")


        elif dist < self.Alcance_ataq_varrido:
            self._iniciar_ataque("varrido")

        else:
            if self.cooldown_projetil <= 0:
                self._iniciar_ataque("projetil", direçao, player)
                self.cooldown_projetil = self.Cooldown_projetil_max
            else:
                direçao = 1 if player.rect.centerx > self.rect.centerx else -1
                self.estado = self.Perseguir
                self.vel.x = self.Vel_perseguir * direçao
                self.olhando_dir = direçao > 0

    

    #função iniciar ataque
    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        self._ataque_atual = tipo
        self._animando_ataque = True

        if tipo == "normal":
            self.anim_atual = self.animaçoes[self.Atacando]
            self.anim_atual.resetar()


        elif tipo == "varrido":
            self.anim_atual = self.anim_attack2
            self.anim_atual.resetar()


        elif tipo == "projetil":
            self._projetil_info = {
            "direçao"    : direçao,
            "frame_spawn": 3,        
            "spawnando"  : False     
                }
            
            self.anim_atual = self.anim_attack3
            self.anim_atual.resetar()


    #atualizar animação de ataque
    def _atualizar_animaçao_ataque(self, player):
        self.anim_atual.atualizar()

        if self._ataque_atual == "normal":
            if self.anim_atual._frame_idx == 4 and not hasattr(self, "_dano_normal_aplicado"):

                self._dano_normal_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                if dist < self.Alcance_ataq_normal:

                    direçao_kb = 1 if player.rect.centerx > self.rect.centerx else -1
                    player.receber_dano(self.Dano_normal, frames_invenc=20)
                    player.vel.x = direçao_kb * 5
                    player.vel.y = -4



        elif self._ataque_atual == "varrido":
            if self.anim_atual._frame_idx == 4 and not hasattr(self, "_dano_varrido_aplicado"):
                self._dano_varrido_aplicado = True
                dist = abs(player.rect.centerx - self.rect.centerx)
                
                
                if dist < self.Alcance_ataq_varrido:
                    
                    direçao_kb   = 1 if player.rect.centerx > self.rect.centerx else -1
                    player.receber_dano(self.Dano_varrido, frames_invenc=30)
                    player.vel.x = direçao_kb * 8
                    player.vel.y = -4




        elif self._ataque_atual == "projetil":
            if not self._projetil_info["spawnando"]:


                if self.anim_atual._frame_idx >= self._projetil_info["frame_spawn"]:
                    self._projetil_info["spawnando"] = True
                    
                    p = ProjetilBoss(
                        self.rect.centerx,
                        self.rect.centery  - 35,
                        self._projetil_info["direçao"],
                        self.Dano_projetil
                    )
                    self.projeteis_spawnar.append(p)

        if self.anim_atual.terminou:
            self._animando_ataque = False
            self._ataque_atual = None
            if hasattr(self, "_dano_normal_aplicado"): del self._dano_normal_aplicado
            if hasattr(self, "_dano_varrido_aplicado"): del self._dano_varrido_aplicado
            
            
            self.anim_atual = self.animaçoes.get(self.estado, self.animaçoes[self.Perseguir])
            self.anim_atual.resetar()
            self._estado_anterior = self.estado


    #receber o hit
    def receber_hit(self, dano, direçao_knockback):
        if self._escudo_ativo:
            #nao toma dano com o escudo ativo
            return
            
        self.receber_dano(dano)
        self.vel.x = direçao_knockback * 3
        self.vel.y = -2 
        self.timer_knockback = 16
        self._animando_ataque = False
        self._ataque_atual = None


        if not self.vivo and not hasattr(self, "_timer_morte"):
            self._timer_morte = 120 
            self.estado = self.Morto
            self.anim_atual = self.animaçoes[self.Morto]
            self.anim_atual.resetar()
            if self._callback_morte:
                self._callback_morte(self.rect.centerx, self.rect.bottom)

        if self.vivo:
            self._em_hit = True
            self._timer_hit = 20
            self.anim_hit.resetar()


    #desenhar
    def desenhar(self, tela, camera):
        if not self.vivo and (not hasattr(self, "_timer_morte") or self._timer_morte <= 0):
            return

        sr = camera.aplicar(self.rect)

        if self.vivo and self.invencivel and self._frame % 6 < 3:
            return

        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura

        offset_x = sr.centerx - sprite_w // 2
        offset_y = sr.centery - sprite_h + 143

        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        if self._escudo_ativo:
            pygame.draw.rect(tela, (0, 150, 255), sr, 3)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

    def _desenhar_hp(self, tela, sr):
        bar_w = sr.width
        ratio = self.hp / self.hp_max
        pygame.draw.rect(tela, (60, 20, 20),
                         (sr.x, sr.y - 8, bar_w, 4), border_radius=2)
        if ratio > 0:
            pygame.draw.rect(tela, (200, 40, 40),
                             (sr.x, sr.y - 8, int(bar_w * ratio), 4), border_radius=2)              
        
            