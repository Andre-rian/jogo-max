import pygame
from settings import DEBUG
from core.audio import audio
from entities.projeteis.projetil import Projetil
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, Hitbox, JanelaGolpe, KnockbackSpec, PoliticaHit

class Bomba(Projetil):

    #frames de spritesheet
    N_frames_voando = 9 #frames da bomba voando 0 a 8
    N_frames_explosao = 10  #frames da explosao 9-18
    Raio_explosao = 80 #area de dano em pixels

    def __init__(self, x, y, direcao, dano=20):
        #direçao -1 = esquerda, 1 = direita
        
        super().__init__(x, y, vel_x=direcao * 4, vel_y=-6, dano=dano, tem_gravidade=True, gravidade=0.2, frames_invenc=30)

        self.rect = pygame.Rect(x, y, 20, 20)
        self.direcao = direcao
        self.explodindo = False
        self._timer_delay = 20 #esperar os 20 frames para checar a colisao com o chao ou player, evita que a bomba exploda no spawn

        Gob = "assets/sprites/enemies/monsters/goblin/"
        self.anim_voando = AnimatedSprite(
            Gob + "Bomb_sprite.png", 
            frame_width=100, frame_height=100,
            velocidade=4, escala=1,
            n_frames=self.N_frames_voando
        ) 
        #explosao usa a mesma spritesheet, mas começa no frame 9
        #o animatedsprite le do frame 0, por isso o offset

        self.anim_explosao = AnimatedSprite(
            Gob + "Bomb_sprite.png", 
            frame_width=100, frame_height=100,
            velocidade=4, escala=1,
            n_frames=19 #carrega todos os frames
        )

        #pula direto ao frame 9 ao explodir
        self.anim_explosao.definir_frame(self.N_frames_voando)

        self.anim_atual = self.anim_voando

        self._janela_explosao = JanelaGolpe(
            nome="explosao",
            frame_inicio=0,
            frame_fim=10_000,
            politica=PoliticaHit.UMA_VEZ,
            canal="explosao",
            bloqueia_por_parede=False,
        )


    def atualizar(self, rects_solidos, player):
        if not self.ativo:
            return
        
        if self.explodindo:
            self._atualizar_explosao(player)
            return
        
        #fisica da bomba
        self.vel.y = min(self.vel.y + self.gravidade, 15)
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        if self._timer_delay > 0:
            self._timer_delay -= 1
        else:
            if player.vivo and self.rect.colliderect(player.rect):
                self._iniciar_explosao()
                


        #colisao com o chao
        for tile in rects_solidos:
            if self.rect.colliderect(tile):
                self.rect.bottom = tile.top
                self._iniciar_explosao()
                return

        self.anim_voando.atualizar()


    def _iniciar_explosao(self):
        if self.explodindo:
            return

        self.explodindo = True
        self.vel = pygame.Vector2(0, 0) #para a bomba no ar
        self.anim_explosao.definir_frame(self.N_frames_voando) #começa a animação de explosão
        audio.play_sfx("bomb_explosion")


    def _atualizar_explosao(self, player):
        self.anim_explosao.atualizar()
        #desativa a bomba depois da explosao
        if self.anim_explosao.terminou:
            self.ativo = False

    def dano_spec(self):
        return DanoSpec(
            dano_base=self.dano,
            knockback=KnockbackSpec(forca_x=7, forca_y=-3, frames=16),
            stagger=True,
            duracao_hit=14,
            frames_invenc=self.frames_invenc,
        )

    def hitboxes_ativas(self):
        if not self.ativo or not self.explodindo:
            return ()

        area = pygame.Rect(0, 0, self.Raio_explosao * 2, 160)
        area.centerx = self.rect.centerx
        area.bottom = self.rect.bottom
        return [
            Hitbox.de_rect(
                area,
                self.dano_spec(),
                self._janela_explosao,
                self,
                self.direcao or 1,
            )
        ]

    def ao_acertar(self, player, evento):
        #a explosao continua ativa mesmo depois de acertar
        pass

    def desenhar(self, tela, camera):
        if not self.ativo:
            return
        
        sr = camera.aplicar(self.rect)

        #debug para conferir a hitbox da explosao
        if DEBUG:
            pygame.draw.rect(tela, (255, 165, 0), sr, 2)  # laranja para a bomba        
        if self.explodindo:
            #centraliza a explosao na posiçao da bomba
            sprite_w = self.anim_explosao.largura
            sprite_h = self.anim_explosao.altura
            offset_x = sr.centerx - sprite_w // 2
            offset_y = sr.bottom - sprite_h // 2
            self.anim_explosao.desenhar(tela, offset_x, offset_y)
        else:
            sprite_w = self.anim_voando.largura
            sprite_h = self.anim_voando.altura
            offset_x = sr.centerx - sprite_w // 2
            offset_y = sr.bottom - sprite_h // 2
            self.anim_voando.desenhar(tela, offset_x, offset_y)

            
