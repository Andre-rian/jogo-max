import pygame
import math
import random
from entities.objetos.item import Arma, get_item, Consumivel, Material, Chave
from entities.entity import Entity
from core.animated_sprite import AnimatedSprite
from entities.objetos.poçao import Pocao
from settings import Dourado, Tile_size

class Player(Entity):

    #possiveis estados de maquina
    Parado = "parado"
    Correndo = "correndo"
    Pulando = "pulando"
    Caindo = "caindo"
    Dash = "Dash"
    Atacando = "atacando"
    Bebendo = "bebendo"
    Pegando = "pegando"
    Morto = "morto"

    #status base
    HP_BASE = 50
    STAMINA_BASE = 30
    VIGOR_INICIAL = 10
    RESISTENCIA_INICIAL = 10
    FORCA_INICIAL = 10
    DESTREZA_INICIAL = 9
    HP_INICIAL = 10
    HP_POR_VIGOR = 15
    STAMINA_POR_RES = 10

    #fisica
    Speed         = 4
    Pulo          = -14
    Dash_speed    = 14
    Dash_duration = 12
    Dash_cooldown = 45
    Double_tap    = 18

    # combate
    Ataque_range    = 70
    Ataque_cooldown = 30
    Knockback       = 8

    #combo
    Hold_combo_frames = 15 #quanto tempo tem que segura o clique pra virar combo
    Stamina_combo = 20
    Multiplicador_combo = 1.6


    # stamina
    Stamina_pulo    = 20
    Stamina_dash    = 30
    Stamina_ataque  = 10
    Stamina_recarga = 0.4
    Stamina_delay   = 30

    def __init__(self, x, y):
        hp_inicial = self.HP_BASE + (self.VIGOR_INICIAL * self.HP_POR_VIGOR)
        super().__init__(x, y, largura=32, altura=66, hp_max=hp_inicial)

        
        
        
        #stamina
        self.stamina_max = self.STAMINA_BASE + (self.RESISTENCIA_INICIAL * self.STAMINA_POR_RES)
        self.stamina = self.stamina_max        
        
        #graus de escalonamento
        self._graus = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}
        
        
        #estado atual da maquina de estado 
        
        self.estado = self.Parado


        #stamina
        self.buff_stamina_duracao = 0
        self.buff_stamina_valor = 1.0



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
        self._alvos_atingidos = set()  #controla quem ja levou o swing

        #controle de combo
        self._segurando_ataque = False
        self._timer_hold = 0
        self._tier_ataque = "normal"        #normal ou pesado, combo usado no calculo de dano

        #bebendo
        self._bebendo = False
        self.timer_bebida = 0

        #pegando item do chao
        self._pegando = False
        self.timer_pegando = 0

        #interaçao (evita pressionar E em multiplos objetos ao mesmo tempo)
        self.cooldown_interaçao = 0

        #invetario(bem basico)
        self.inventario = {
                "mao_direita" : None,   # arma equipada
                "mao_esquerda": None,   # escudo — futuro
                "armadura"    : None,   # armadura — futuro
                "equipamentos": [],     #parte do inventario que fica os equipaveis 
                "itens"       : {},     # consumíveis no inventário               -dicionario da lista de ids
                "chaves"      : [],      # itens de progressão                    -lista de ids  
                "materiais"   : {}      # materias de fabricação/ upgrades        -dict da lista de ids
                        }   
        

        #sistema do inventario/ simbolo nos itens novos
        self.itens_novos = set() #id dos itens que o player nao interagiu no inventario

        #ecos profanos 
        self.ecos = 0
        self.ecos_perdidos = 0  #guarda os ecos perdidos quando o player morrre

        #atributos
        self.nivel = 1
        self.vigor = self.VIGOR_INICIAL
        self.resistencia = self.RESISTENCIA_INICIAL
        self.forca = self.FORCA_INICIAL
        self.destreza = self.DESTREZA_INICIAL



        #poçoes
        self.pocao = Pocao()

        #checkpoin(inicial)
        self.checkpoint_pos = pygame.Vector2(x, y)
        self.checkpoint_sala = 'calabouço_1' 


        # animações
        KNIGHT = "assets/sprites/player/knight/"
        self.animacoes = {
            self.Parado:   AnimatedSprite(KNIGHT + "_Idle.png",  120, 80, velocidade=8,  escala=2, loop=True),
            self.Correndo: AnimatedSprite(KNIGHT + "_Run.png",   120, 80, velocidade=6,  escala=2, loop=True),
            self.Pulando:  AnimatedSprite(KNIGHT + "_Jump.png",  120, 80, velocidade=8,  escala=2, loop=True),
            self.Caindo:   AnimatedSprite(KNIGHT + "_Fall.png",  120, 80, velocidade=8,  escala=2, loop=True),
            self.Atacando: AnimatedSprite(KNIGHT + "_Attack.png",120, 80, velocidade=5,  escala=2, loop=False),
            self.Dash:     AnimatedSprite(KNIGHT + "_Dash.png",  120, 80, velocidade=4,  escala=2, loop=False),
            self.Morto:    AnimatedSprite(KNIGHT + "_Death.png", 120, 80, velocidade=8,  escala=2, loop=False),
                }
        
        self.animacoes_ataque = {

                        "espada": {
                    "normal": {
                        "parado":    AnimatedSprite(KNIGHT + "_AttackNoMovement.png",     120, 80, velocidade=5, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "_Attack.png",               120, 80, velocidade=5, escala=2),
                    },
                    "pesado": {
                        "parado":    AnimatedSprite(KNIGHT + "_Attack2NoMovement.png",    120, 80, velocidade=5, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "_Attack2.png",              120, 80, velocidade=5, escala=2),
                    },
                    "combo": {
                        "parado":    AnimatedSprite(KNIGHT + "_AttackComboNoMovement.png",120, 80, velocidade=4, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "_AttackCombo2hit.png",      120, 80, velocidade=4, escala=2),
                    },
                },
                "machado": {
                    "normal": {
                        "parado":    AnimatedSprite(KNIGHT + "Attack_Axe.png",          76, 80, velocidade=12, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "Attack_Axe.png",          76, 80, velocidade=12, escala=2),
                    },
                    "pesado": {
                        "parado":    AnimatedSprite(KNIGHT + "Attack2_Axe.png",      106, 80, velocidade=12, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "Attack2_Axe.png",      106, 80, velocidade=12, escala=2),
                    },
                    "combo": {
                        "parado":    AnimatedSprite(KNIGHT + "Attack_Combo_Axe.png", 56, 80, velocidade=12, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "Attack_Combo_Axe.png", 56, 80, velocidade=12, escala=2),
                    },
                },
                None: {  # sem arma - soco
                    "normal": {
                        "parado":    AnimatedSprite(KNIGHT + "_Attack_Punho.png", 120, 80, velocidade=15, escala=2),
                        "movimento": AnimatedSprite(KNIGHT + "_Attack_Punho.png", 120, 80, velocidade=15, escala=2),
                    },
                },
            }
        #animaçoes pocao
        self.anim_pocao_parado = AnimatedSprite(KNIGHT + "knight_poçao.png", 30, 78, velocidade=14, escala=2)
        self.anim_pocao_movimento = AnimatedSprite(KNIGHT + "knight_poçao_movimento.png",  32, 80, velocidade=14, escala=2)

        #animaçao pegando item
        self.anim_pegando_item = AnimatedSprite(KNIGHT + "Pegando_item.png", 46, 80, velocidade=8, escala=2)

        self._estado_anterior = self.Parado
        self.anim_atual = self.animacoes[self.Parado]

    def equipar(self, item):
        
        if isinstance(item, Arma):
            self.inventario["mao_direita"] = item.id
            print(f"Equipado: {item.nome} ID: {item.id}" )



    @property
    def arma_equipada(self):
        id_ = self.inventario["mao_direita"]
        return get_item(id_) if id_ else None
    
    @property
    def tem_arma_equipada(self):
        
        return self.inventario["mao_direita"] is not None


    def adicionar_ao_inventario(self, item):
        if isinstance(item, Arma):

            self.inventario["equipamentos"].append(item.id)
            self.itens_novos.add(item.id)
        
        
        elif isinstance(item, Consumivel):

            id_ = str(item.id)

            if id_ in self.inventario["itens"]:
                self.inventario["itens"][id_] += 1
                
            else:    
                self.inventario["itens"][id_] = 1
            
            self.itens_novos.add(item.id)
        
        
        elif isinstance(item, Chave):
            self.inventario["chaves"].append(item.id)
            self.itens_novos.add(item.id)
        
        
        elif isinstance(item, Material):
            id_ = str(item.id)

            print(f"adicionando material id={item.id}, materiais atual={self.inventario['materiais']}")
            
            if id_ in self.inventario["materiais"]:
                
                self.inventario["materiais"][id_] += 1

            else:
                self.inventario["materiais"][id_] = 1
                
            self.itens_novos.add(item.id)



    #UPDATE
    def atualizar(self, rects_solidos, camera):
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
        self._atacar(teclas)
        self._usar_pocao(teclas)
        self._atualizar_stamina(teclas)

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self.atualizar_invencibilidade()
        self._atualizar_estado()
        self._atualizar_times()



        #troca a animaçao se o estado mudou
        if self.estado != self._estado_anterior:

            if self.estado not in (self.Atacando, self.Bebendo, self.Pegando):
                self.anim_atual = self.animacoes.get(self.estado, self.animacoes[self.Parado])
                self.anim_atual.resetar()
            self._estado_anterior = self.estado

        #avançar o frame da animaçao atual
        self.anim_atual.atualizar()

        #mask pro combate melhorado
        self.atualizar_mask()


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
            
            if 1 < intervalo <= self.Double_tap and self.cooldown_dash == 0:
                self._iniciar_dash(-1)
                
            self._ultimo_toque["esquerda"] = self._frame_atual

        if toque_dir:
            intervalo = self._frame_atual - self._ultimo_toque["direita"]
            #intervalo > 1 evitar detectar o mesmo toque duas vezes
            
            if 1 < intervalo <= self.Double_tap and self.cooldown_dash == 0:
                self._iniciar_dash(1)
                
            self._ultimo_toque["direita"] = self._frame_atual
    
    def _iniciar_dash(self, direçao):
        if not self._tem_stamina(self.Stamina_dash):
            return #sem stamina = sem dash
        self.em_dahs = True
        self.direçao_dash = direçao
        self.timer_dash = self.Dash_duration
        self.cooldown_dash = self.Dash_cooldown
        self.vel.y = 0 #cancela a gravidade no dash
        self.olhando_dir = direçao > 0
        self._gastar_stamina(self.Stamina_dash)
    
    #MOVIMENTO HORIZONTAL

    def _mover_horizontal(self, teclas):
        if self.recebendo_knockback:
            return  #se ta no knockback nao consegue se mexer
        
        if self._pegando:
            self.vel.x = 0 #ttrava a movimentaçao durante a animaçao
            return
        
        if self.em_dahs:
            #durante o dash a velocidade é fixa
            self.vel.x = self.Dash_speed * self.direçao_dash
            return
        
        if teclas[pygame.K_d]:
            self.vel.x = self.Speed
            self.olhando_dir = True
        
        elif teclas[pygame.K_a]:
            self.vel.x = -self.Speed
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
            if not self._tem_stamina(self.Stamina_pulo):
                return #sem stamina nao pula
            self.vel.y = self.Pulo
            self.no_chao = False
            self._gastar_stamina(self.Stamina_pulo)

    #ATAQUEEEE -- clique esquerdo do mouse
    def _atacar(self, teclas):
        if self._pegando or self._bebendo:
            return
        
        pressionado = teclas[pygame.K_k]

        if pressionado and not self._segurando_ataque:
            if self.cooldown_ataque > 0 or not self._tem_stamina(self.Stamina_ataque):
                return
            self._segurando_ataque = True
            self._timer_hold = 0

        elif pressionado and self._segurando_ataque:
            self._timer_hold += 1
            #deixa reajusta a direçao do golpe enquanto carrega
            # direção do golpe fica travada em olhando_dir (sem mirar) — cima/baixo fica pra quando tiver sprite

            

        elif not pressionado and self._segurando_ataque:
            virou_combo = self._timer_hold >= self.Hold_combo_frames
            self._disparar_ataque(combo=virou_combo)
            self._segurando_ataque = False
            self._timer_hold = 0




    def _disparar_ataque(self, combo):
        tipo_arma = self.arma_equipada.icone if self.arma_equipada else None
        set_arma = self.animacoes_ataque.get(tipo_arma, self.animacoes_ataque[None])

        if combo and "combo" in set_arma:
            tier = "combo"
        
        else:
            opcoes = [t for t in ("normal", "pesado") if t in set_arma]
            tier = random.choice(opcoes) if opcoes else "normal"

        variante = "parado" if abs(self.vel.x) < 0.5 else "movimento"
        anim = set_arma[tier][variante]

        self._tier_ataque = tier
        self.atacando = True
        self._alvos_atingidos = set()   #outro golpe
        self.anim_atual = anim
        self.anim_atual.resetar()

        n_frames = len(anim.frames)
        duracao = n_frames * anim.velocidade
        self.timer_ataque = duracao
        self.cooldown_ataque = duracao + 10 #pequeno intervalo entre golpes

        custo = self.Stamina_combo if tier == "combo" else self.Stamina_ataque
        self._gastar_stamina(custo)





    def get_rect_ataque(self):
        #retorna o rect da hitbox dp ataque  enquanto esta atacando.é ele que vai verificar as hitsbox dos inimigos

        if not self.atacando:
            return None
        
        if self.olhando_dir:  #atacando para direita
            return pygame.Rect(
                self.rect.right, 
                self.rect.centery - 16,
                self.Ataque_range, 
                32
            )
        
        else:
            return pygame.Rect(
                self.rect.left - self.Ataque_range,
                self.rect.centery - 16,
                self.Ataque_range,
                32
            )
    
    def calcular_dano(self):

        arma = self.arma_equipada
        dano = 5 if not arma else arma.dano #soquinho se nao tiver uma arma
        
        if arma:
            #penalidade se nao bate os requisitos da arma
            if not arma.pode_equipar(self):
                dano = int(dano * 0.4)
            else:

                #bonus do escalonamento
                for atributo, grau in arma.escalonamento.items():
                    multiplicador = self._graus[grau]

                    if atributo == "forca":
                        dano += int(self.forca * multiplicador)

                    elif atributo == "destreza":
                        dano += int(self.destreza * multiplicador)
        
        if self._tier_ataque == "combo":
            dano = int(dano * self.Multiplicador_combo)

        return dano




    #recarrega stamina
    def _atualizar_stamina(self, teclas):
        #mundaça na stamina como prometido, agora ela so nao recupera se o player esta fazendo uma "ação pesada"
        
        em_acao_pesada = (self.em_dahs or
                self.atacando or
                self._pegando or 
                teclas[pygame.K_SPACE])
        
        if em_acao_pesada or not self.no_chao:
            #reseta o delay enquanto esta em açao
            self.stamina_delay = self.Stamina_delay
        else:
            #recupera normalmente a stamina
            if self.stamina_delay > 0:
                self.stamina_delay -= 1
            else:
                #recarrega gradualmente
                velocidade = self.Stamina_recarga * self.buff_stamina_valor if self.buff_stamina_duracao > 0 else self.Stamina_recarga
                self.stamina = min(
                    self.stamina_max,
                    self.stamina + velocidade
                )


        #decrementa o buff da stamina
        if self.buff_stamina_duracao > 0:
            self.buff_stamina_duracao -= 1

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

        #pegando item
        if self._pegando:
            self.timer_pegando -= 1
            if self.timer_pegando <= 0:
                self._pegando = False
        
        #bebendo poçoes
        if self._bebendo:
            self.timer_bebida -= 1
            if self.timer_bebida <= 0:
                self._bebendo = False


        #cooldown de interações 
        if self.cooldown_interaçao > 0:
            self.cooldown_interaçao -= 1

    def _usar_pocao(self, teclas):
        self.pocao.atualizar()
        
        if self._pegando or self._bebendo or self.atacando or self.em_dahs:
            return
    
        
        
        
        if teclas[pygame.K_f]:
            sucesso = self.pocao.usar(self)
            if sucesso:
                self._iniciar_bebida()




    #funçao do player exucutar a animação de beber poção
    def _iniciar_bebida(self):
        variante = "parado" if abs(self.vel.x) < 0.5 else "movimento"
        anim = self.anim_pocao_parado if variante == "parado" else self.anim_pocao_movimento
        self._bebendo = True
        self.anim_atual = anim
        self.anim_atual.resetar()            
        n_frames = len(anim.frames)
        self.timer_bebida = n_frames * anim.velocidade

    
    #funçao chamada pelo o drop para iniciar a animação de pegar os itens
    def iniciar_pegar_item(self):
        if self.atacando or self._bebendo or self.em_dahs or self._pegando:
            return


        #NOVO: cancela qualquer ataque sendo carregado — sem isso, ele "sobra"
        #e dispara sozinho assim que a animação de pegar item terminar

        self._segurando_ataque = False
        self._timer_hold = 0

        self._pegando = True
        self.vel.x = 0
        self.anim_atual = self.anim_pegando_item
        self.anim_atual.resetar()
        n_frames = len(self.anim_atual.frames)
        self.timer_pegando = n_frames * self.anim_atual.velocidade




    #MAQUINA DE ESTADOS 

    def _atualizar_estado(self):
        #define o estado atual com base no player

        if self.em_dahs:
            self.estado = self.Dash
        elif self._pegando:
            self.estado = self.Pegando
        elif self._bebendo:
            self.estado = self.Bebendo

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
        print(f"checkpoint definido: sala={nome_sala}, x={self.checkpoint_pos.x}, y={self.checkpoint_pos.y}")

    def respawnar(self): 
        #voltar para o ultimo checkpoint com o hp cheio

        self.rect.x = int(self.checkpoint_pos.x)
        self.rect.y = int(self.checkpoint_pos.y)
        self.hp = self.hp_max
        self.vivo = True
        self.vel = pygame.Vector2(0,0)
        self.estado = self.Parado
        print(f"respawnando em: x={self.checkpoint_pos.x}, y={self.checkpoint_pos.y}")
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

    def _offset_mask(self):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        if self.olhando_dir:
            offset_x = self.rect.centerx - sprite_w // 2 + 10
        else:
            offset_x = self.rect.centerx - sprite_w // 2 - 10
        offset_y = self.rect.bottom - sprite_h
        return offset_x, offset_y

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