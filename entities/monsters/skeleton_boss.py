import pygame
import random
from entities.inimigo_base import InimigoBase
from core.animated_sprite import AnimatedSprite
from core.combat import DanoSpec, KnockbackSpec, ModoMovimento, ReacaoDano
from entities.projeteis.projetil_boss import ProjetilBoss


class EsqueletoBoss(InimigoBase):

    ESTADO_PADRAO = "Perseguir"   
    Duracao_morte = 120

    Dano_normal           = 25
    Dano_varrido          = 30
    Dano_projetil         = 20


    # boss resiste à guarda: 3 golpes quebram, sem imunidade de stagger
    KB_FORCA_X = 2
    KB_FORCA_Y = 0
    KB_FRAMES = 6
    IMUNIDADE_STAGGER_FRAMES = 0
    IMUNE_DURANTE_ATAQUE = True
    USAR_IFRAMES_DANO = False

    GUARDA_GOLPES_PARA_QUEBRAR = 3
    GUARDA_TIMEOUT_TICKS = 180
    GUARDA_FLASH_TICKS = 6
    Cooldown_apos_quebra = 45  # ~0.75 s para o Boss voltar a pressionar
    Recomposicao_apos_quebra = 10  # ~0.17 s de postura antes de decidir de novo

    Vel_perseguir         = 1.8

    Alcance_detec         = 400
    Alcance_ataq_normal   = 90
    Alcance_ataq_varrido  = 120
    Alcance_ataq_projetil = 160
    Alcance_escudo        = 150

    #alcance real dos golpes por distância de borda (gap)
    Alcance_conectar          = 30
    Alcance_conectar_varrido  = 50

    #cooldowns independentes: a espada não bloqueia escudo nem projétil
    Cooldown_ataq         = 90   # espada (normal/varrido)
    Cooldown_projetil_max = 180
    Cooldown_escudo_max   = 120
    Duracao_escudo_max    = 90

    #loop de decisão e pressão
    Decisao_ticks = 8
    Distancia_pressao = 80
    Distancia_recuo = 60
    Chance_escudo = 0.15

    def __init__(self, x, y, callback_morte=None):
        super().__init__(x, y, largura=50, altura=90, hp_max=300,
                          callback_morte=callback_morte)

        self.cooldown_projetil = random.randint(0, self.Cooldown_projetil_max)
        self.cooldown_escudo   = random.randint(0, self.Cooldown_escudo_max)
        self._cooldowns_extra  = ["cooldown_projetil", "cooldown_escudo"]

        self._duracao_escudo = 0
        self._escudo_ativo   = False

        self._guarda_golpes = 0
        self._guarda_timer = 0
        self._guarda_ultimo_golpe = None
        self._quebra_ativa = False

        self._tempo_decisao = 0
        self._micro_dir = 0

        self.projeteis_spawnar = []

        Boss_skeleton = "assets/sprites/enemies/monsters/esqueletos/"
        self.animaçoes = {
            self.Patrulha:  AnimatedSprite(Boss_skeleton + "Idle.png",   150, 150, velocidade=8, escala=2, n_frames=4),
            self.Perseguir: AnimatedSprite(Boss_skeleton + "Walk.png",   150, 150, velocidade=8, escala=2, n_frames=4),
            self.Atacando:  AnimatedSprite(Boss_skeleton + "Attack.png", 150, 150, velocidade=6, escala=2, n_frames=8, loop=False),
            self.Morto:     AnimatedSprite(Boss_skeleton + "Death.png",  150, 150, velocidade=8, escala=2, n_frames=4, loop=False),
        }
        self.anim_attack2 = AnimatedSprite(Boss_skeleton + "Attack2.png", 150, 150, velocidade=6, escala=2, n_frames=8, loop=False)
        self.anim_attack3 = AnimatedSprite(Boss_skeleton + "Attack3.png", 150, 150, velocidade=6, escala=2, n_frames=6, loop=False)
        self.anim_shield  = AnimatedSprite(Boss_skeleton + "Shield.png",  150, 150, velocidade=8, escala=2, n_frames=4)
        self.anim_hit     = AnimatedSprite(Boss_skeleton + "Take Hit.png", 150, 150, velocidade=8, escala=2, n_frames=4, loop=False)
        self.anim_atual   = self.animaçoes[self.Perseguir]

        self.ecos_drop = 150

        self._configurar_ataques()

    def _configurar_ataques(self):
        dano_normal = DanoSpec(
            dano_base=self.Dano_normal,
            knockback=KnockbackSpec(forca_x=5, forca_y=-2, frames=14),
            hitstop=3,
            duracao_hit=12,
            frames_invenc=20,
        )
        dano_varrido = DanoSpec(
            dano_base=self.Dano_varrido,
            knockback=KnockbackSpec(forca_x=8, forca_y=-2, frames=16),
            hitstop=5,
            duracao_hit=16,
            frames_invenc=30,
        )
        self._registrar_ataque(
            "normal",
            self.animaçoes[self.Atacando],
            [self._criar_janela("golpe", 6, 7)],
            dano_normal,
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )
        self._registrar_ataque(
            "varrido",
            self.anim_attack2,
            [self._criar_janela("varrido", 6, 7)],
            dano_varrido,
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )
        self._registrar_ataque(
            "projetil",
            self.anim_attack3,
            [],
            DanoSpec(),
            movimento=ModoMovimento.TRAVADO,
            recuperacao_ticks=12,
        )

    def _resetar_flags_ataque(self):
        self._projetil_spawnado = False
        self._projetil_direcao = 1

    @property
    def nome(self):
        return "Carrasco Esquelético"

    def atualizar(self, rects_solidos, player):
        if self._guarda_golpes > 0:
            self._guarda_timer += 1
            if self._guarda_timer >= self.GUARDA_TIMEOUT_TICKS:
                self._resetar_guarda()
        return super().atualizar(rects_solidos, player)

    def _resetar_guarda(self):
        self._guarda_golpes = 0
        self._guarda_timer = 0
        self._guarda_ultimo_golpe = None

    def _reacao_ao_dano(self, dano, direcao, evento, duracao_hit, knockback):
        if evento is None:
            return super()._reacao_ao_dano(
                dano, direcao, evento, duracao_hit, knockback
            )

        #durante o hitstun da quebra o dano entra, mas não conta para a próxima guarda
        if self._quebra_ativa or self._em_hit:
            return ReacaoDano()

        chave = (evento.fonte, evento.janela.nome, evento.janela.canal)
        if chave == self._guarda_ultimo_golpe:
            return ReacaoDano()

        self._guarda_ultimo_golpe = chave
        self._guarda_golpes += 1
        self._guarda_timer = 0

        if self._guarda_golpes < self.GUARDA_GOLPES_PARA_QUEBRAR:
            #primeiro e segundo golpes: só o flash dourado, sem stagger nem interrupção
            return ReacaoDano(
                flash_guarda=self.GUARDA_FLASH_TICKS,
                interrompe_ataque=False,
            )

        #terceiro golpe: quebra a guarda e interrompe o ataque em andamento
        atacando = self._animando_ataque
        self._quebra_ativa = True
        self._guarda_golpes = 0
        self._guarda_timer = 0
        #a quebra cancela o ataque; sem encurtar o cooldown o Boss ficaria
        #tempo demais parado e pareceria menos agressivo que antes
        self.cooldown_ataq = min(self.cooldown_ataq, self.Cooldown_apos_quebra)
        return ReacaoDano(
            knockback=KnockbackSpec(forca_x=self.KB_FORCA_X, forca_y=0, frames=self.KB_FRAMES),
            duracao_hit=16 if atacando else 24,
            invencibilidade_stagger=0,
            animacao=self.anim_hit,
            interrompe_ataque=True,
            ignora_hyper_armor=True,
            flash_guarda=self.GUARDA_FLASH_TICKS,
            recuperacao=self.Recomposicao_apos_quebra,
        )

    def _ao_terminar_hit(self):
        self._quebra_ativa = False
        self._tempo_decisao = 0

    def _iniciar_recuperacao(self, duracao=None):
        super()._iniciar_recuperacao(duracao)
        if self._em_recuperacao:
            #recomposição de guarda usa a pose de idle, não a de caminhada
            self.estado = self.Patrulha

    def _ao_terminar_recuperacao(self):
        self._tempo_decisao = 0

    #escudo

    def _estado_especial(self, rects_solidos, player):
        if not self._escudo_ativo:
            return None

        self._duracao_escudo -= 1
        self.anim_atual = self.anim_shield
        self.anim_shield.atualizar()

        #o escudo não congela os outros cooldowns; senão ele vira uma pausa
        if self.cooldown_escudo > 0:
            self.cooldown_escudo -= 1
        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1
        if self.cooldown_projetil > 0:
            self.cooldown_projetil -= 1

        if self._duracao_escudo <= 0:
            self._escudo_ativo = False
            self.estado = self.Perseguir
            self._tempo_decisao = 0
            self._resetar_para_estado_atual()

        self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        return 0

    # IA 

    def _ia(self, rects_solidos, player):
        dist = abs(player.rect.centerx - self.rect.centerx)

        if not player.vivo or dist >= self.Alcance_detec:
            self.estado = self.Patrulha
            self.vel.x = 0
            return 0

        if self._tempo_decisao <= 0:
            self._tempo_decisao = self.Decisao_ticks
            if self._tentar_acao_agressiva(dist, player):
                return 0
            self._micro_dir = random.choice((-1, 0, 1))
        else:
            self._tempo_decisao -= 1

        self._pressionar(dist, player)
        return 0

    def _tentar_acao_agressiva(self, dist, player):
        if self.cooldown_ataq <= 0 and dist < self.Alcance_ataq_varrido:
            self._iniciar_ataque("normal" if dist < self.Alcance_ataq_normal else "varrido")
            self.cooldown_ataq = self.Cooldown_ataq
            return True

        if self._deve_levantar_escudo(dist, player):
            self._levantar_escudo()
            return True

        if self.cooldown_projetil <= 0 and self.Alcance_ataq_normal <= dist < self.Alcance_ataq_projetil:
            direçao = 1 if player.rect.centerx > self.rect.centerx else -1
            self.olhando_dir = direçao > 0
            self._iniciar_ataque("projetil", direçao, player)
            self.cooldown_projetil = self.Cooldown_projetil_max
            return True

        return False

    def _deve_levantar_escudo(self, dist, player):
        if self.cooldown_escudo > 0 or dist >= self.Alcance_escudo:
            return False
        #a espada continua sendo a prioridade; o escudo cobre a abertura
        if self.cooldown_ataq <= 0 and dist < self.Alcance_ataq_varrido:
            return False
        ameaca = getattr(player, "ataque_ativo", None) is not None
        return ameaca or random.random() < self.Chance_escudo

    def _levantar_escudo(self):
        self._escudo_ativo = True
        self._duracao_escudo = self.Duracao_escudo_max
        self.cooldown_escudo = self.Cooldown_escudo_max
        self.vel.x = 0

    def _pressionar(self, dist, player):
        self.estado = self.Perseguir
        direçao = 1 if player.rect.centerx > self.rect.centerx else -1
        self.olhando_dir = direçao > 0

        if dist > self.Distancia_pressao:
            #longe acelera; perto da faixa de ataque entra pisando curto
            fator = 1.0 if dist > self.Alcance_ataq_varrido else 0.45
            self.vel.x = self.Vel_perseguir * fator * direçao
        elif dist < self.Distancia_recuo:
            #recupera espaço para a espada sem recuar demais
            self.vel.x = -self.Vel_perseguir * 0.35 * direçao
        else:
            #micro-ajustes vendem o "cavaleiro pressionando"
            self.vel.x = self.Vel_perseguir * 0.2 * self._micro_dir

    def _iniciar_ataque(self, tipo, direçao=1, player=None):
        if not self.iniciar_ataque(tipo, player):
            return
        self.vel.x = 0
        self._projetil_direcao = direçao
        self._tempo_decisao = 0

    def _ao_tick_ataque(self, player, frame):
        if self._ataque_atual == "projetil" and frame >= 3 and not self._projetil_spawnado:
            self._projetil_spawnado = True
            p = ProjetilBoss(
                self.rect.centerx,
                self.rect.centery - 35,
                self._projetil_direcao,
                self.Dano_projetil,
            )
            self.projeteis_spawnar.append(p)



    def _offset_desenho(self, sr):
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        return sr.centerx - sprite_w // 2, sr.centery - sprite_h + 143

    def _desenhar_extra(self, tela, sr):
        if self._escudo_ativo:
            pygame.draw.rect(tela, (0, 150, 255), sr, 3)