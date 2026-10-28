import pygame
from entities.entity import Entity
from core.combat import (
    DanoSpec,
    DefinicaoAtaque,
    HitboxSpec,
    InstanciaAtaque,
    JanelaGolpe,
    KnockbackSpec,
    ModoMovimento,
    PoliticaHit,
    construir_hitboxes,
)

class InimigoBase(Entity):

    Patrulha  = "patrulha"
    Perseguir = "perseguir"
    Atacando  = "atacando"
    Morto     = "morto"

    Duracao_morte = 60          # cada filho sobrescreve (skeleton=90, boss=120...)
    TEM_GRAVIDADE = True        # FlyingEye sobrescreve pra False
    ESTADO_PADRAO = "Patrulha"  # nome do atributo usado como fallback de animação


    #valores padroes do knockback
    KB_FORCA_X = 4
    KB_FORCA_Y = -2
    KB_FRAMES = 12
    HITSTUN_FRAMES = 14
    RECUPERACAO_HIT_FRAMES = 0  # pausa em idle depois do hitstun, antes de voltar à IA
    IMUNIDADE_STAGGER_FRAMES = 0 # SEM hiper armor
    IMUNE_DURANTE_ATAQUE = False #se true nao pode ser interrompido no meio do proprio ataqie
    USAR_IFRAMES_DANO = False #inimigos comuns não têm i-frames de dano (só hitstun/knockback)

    def __init__(self, x, y, largura, altura, hp_max, patrulha_esq=None, patrulha_dir=None, callback_morte=None):
        super().__init__(x, y, largura, altura, hp_max)

        self.callback_morte = callback_morte  # já existe na Entity, só passamos pra frente

        self.patrulha_esq = patrulha_esq
        self.patrulha_dir = patrulha_dir

        self.estado = getattr(self, self.ESTADO_PADRAO)
        self._estado_anterior = self.estado

        self.cooldown_ataq = 0
        self._cooldowns_extra = []   # filho preenche, ex: ["cooldown_bomba"] no Globin

        self._frame = 0
        self.olhando_dir = True

        self._ataque_atual = None
        self._animando_ataque = False
        self.ataque_ativo = None
        self.definicoes_ataque = {}

        self._em_hit = False
        self._timer_hit = 0
        self._em_recuperacao = False
        self._timer_recuperacao = 0
        self._imune_stagger = 0

    def atualizar(self, rects_solidos, player):
        self.atualizar_invencibilidade()
        if self._imune_stagger > 0:
            self._imune_stagger -= 1

        if not self.vivo:   
            return self._atualizar_morte()

        self._frame += 1

        if self.timer_knockback > 0:
            return self._atualizar_knockback(rects_solidos)

        #trava a ai no hitsun de verdade
        if self._em_hit:
            return self._atualizar_hitsun_parado(rects_solidos)

        if self._em_recuperacao:
            return self._atualizar_recuperacao(rects_solidos)

        resultado_especial = self._estado_especial(rects_solidos, player)
    
        if resultado_especial is not None:
            return resultado_especial

        if self._animando_ataque:
            return self._atualizar_ataque_em_curso(rects_solidos, player)

        dano_causado = self._ia(rects_solidos, player) or 0

        if self.TEM_GRAVIDADE:
            self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self._decrementar_cooldowns()

        return self._atualizar_troca_animacao(dano_causado)

    # ---------- HOOKS (cada inimigo implementa) ----------

    def _ia(self, rects_solidos, player):
        raise NotImplementedError("cada inimigo implementa sua IA de perseguir/atacar aqui")

    def _configurar_ataques(self):
        #cada filho registra suas DefinicaoAtaque em self.definicoes_ataque
        pass

    def _criar_janela(self, nome, frame_inicio, frame_fim, *, politica=PoliticaHit.UMA_VEZ,
                      canal=None, intervalo=0, hitbox=None, bloqueia_por_parede=True):
        return JanelaGolpe(
            nome=nome,
            frame_inicio=frame_inicio,
            frame_fim=frame_fim,
            hitbox=hitbox or HitboxSpec(),
            politica=politica,
            canal=canal or nome,
            intervalo=intervalo,
            bloqueia_por_parede=bloqueia_por_parede,
        )

    def _registrar_ataque(self, nome, animacao, janelas, dano, *,
                          movimento=ModoMovimento.REDUZIDO, lunge=0.0, prioridade=0):
        self.definicoes_ataque[nome] = DefinicaoAtaque(
            nome=nome,
            animacao=animacao,
            janelas=tuple(janelas),
            movimento=movimento,
            lunge=lunge,
            dano=dano,
            prioridade=prioridade,
        )

    def iniciar_ataque(self, nome, alvo=None):
        definicao = self.definicoes_ataque.get(nome)
        if definicao is None:
            return False

        self.ataque_ativo = InstanciaAtaque(definicao, self, alvo=alvo)
        self._ataque_atual = nome
        self._animando_ataque = True
        self.anim_atual = definicao.animacao
        self.anim_atual.manual = True
        self.anim_atual.definir_frame(0)
        self.estado = self.Atacando
        self._resetar_flags_ataque()
        return True

    def encerrar_ataque(self):
        self.ataque_ativo = None
        self._animando_ataque = False
        self._ataque_atual = None
        self._resetar_flags_ataque()
        if self.vivo:
            self._resetar_para_estado_atual()

    def _resetar_flags_ataque(self):
        #cada filho zera flags de spawn/dano aqui (nada de hasattr persistente)
        pass

    def _ao_tick_ataque(self, player, frame):
        #hook chamado pelo CombatSystem a cada tick da instância de ataque
        pass

    def _atualizar_hitsun_parado(self, rects_solidos):
        #empurrao ja acabou a animação - mantem a fisica normal, mas nao deixa o bixo atacar
        if self.TEM_GRAVIDADE:
            self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self._decrementar_cooldowns()
        resultado = self._atualizar_hit_flash()
        if resultado is not None:
            return resultado
        return 0
    

    def _estado_especial(self, rects_solidos, player):
        # hook opcional (ex: escudo do boss). None = não fez nada especial, segue o fluxo normal
        return None

    def _animacao_extra_hook(self):
        # hook opcional (ex: skeleton troca pra idle quando parado)
        pass

    def _offset_mask(self):
        return self._offset_desenho(self.rect)

    # ---------- DEBUG DE GOLPE ----------

    def rect_do_golpe(self):
        #rect da hitbox ativa do golpe em curso (usado pelo debug)
        if self.ataque_ativo is None:
            return None
        hitboxes = construir_hitboxes(self.ataque_ativo)
        return hitboxes[0].rect if hitboxes else None

    def rect_golpe_debug(self):
        return self.rect_do_golpe()

    def golpe_acerta(self, player):
        if self.ataque_ativo is None:
            return False
        return any(hb.colide_com(player) for hb in construir_hitboxes(self.ataque_ativo))

    def _offset_desenho(self, sr):
        # cada filho sobrescreve se o sprite precisar de ajuste manual
        sprite_w = self.anim_atual.largura
        sprite_h = self.anim_atual.altura
        return sr.centerx - sprite_w // 2, sr.bottom - sprite_h

    # ---------- SUB-ESTADOS (genéricos) ----------

    def _atualizar_morte(self):
        if not hasattr(self, "_timer_morte"):
            self._iniciar_morte()

        if not self.anim_atual.terminou:
            self.anim_atual.atualizar()

        self._timer_morte -= 1
        return 0 if self._timer_morte <= 0 else -1

    def _iniciar_morte(self):
        # callback_morte já foi disparado pelo receber_dano() da Entity, não precisa chamar de novo
        self._timer_morte = self.Duracao_morte
        self.estado = self.Morto
        self.anim_atual = self.animaçoes[self.Morto]
        self.anim_atual.resetar()

    def _atualizar_knockback(self, rects_solidos):
        self.atualizar_knockback(rects_solidos, tem_gravide=self.TEM_GRAVIDADE)  # FIX: era "tem_gravide"
        self._decrementar_cooldowns()
        resultado = self._atualizar_hit_flash()
        if resultado is not None:
            return resultado
        return 0

    def _atualizar_ataque_em_curso(self, rects_solidos, player):
        #a animação e as hitboxes são dirigidas pelo CombatSystem
        if self.TEM_GRAVIDADE:
            self.aplicar_gravidade()
        self.mover_com_colisão(rects_solidos)
        self._decrementar_cooldowns()
        return 0

    def _decrementar_cooldowns(self):
        if self.cooldown_ataq > 0:
            self.cooldown_ataq -= 1
        for nome in self._cooldowns_extra:
            valor = getattr(self, nome)
            if valor > 0:
                setattr(self, nome, valor - 1)

    def _atualizar_hit_flash(self):
        # retorna 0 se ainda travado no flash de hit, None se liberou pro fluxo normal
        if not self._em_hit:
            return None

        self._timer_hit -= 1
        if self._timer_hit <= 0:
            self._em_hit = False
            self._iniciar_recuperacao()
            self._resetar_para_estado_atual()
            return None

        self.anim_atual = self.anim_hit
        if not self.anim_hit.terminou:
            self.anim_atual.atualizar()
        return 0

    def _iniciar_recuperacao(self):
        self._em_recuperacao = self.RECUPERACAO_HIT_FRAMES > 0
        self._timer_recuperacao = self.RECUPERACAO_HIT_FRAMES if self._em_recuperacao else 0
        if self._em_recuperacao:
            #volta para idle; o movimento/IA só libera quando a recuperação acabar
            self.estado = getattr(self, self.ESTADO_PADRAO)

    def _atualizar_recuperacao(self, rects_solidos):
        if self.TEM_GRAVIDADE:
            self.aplicar_gravidade()
        self.vel.x = 0
        self.mover_com_colisão(rects_solidos)
        self._decrementar_cooldowns()

        self._timer_recuperacao -= 1
        if self._timer_recuperacao <= 0:
            self._em_recuperacao = False
            self._resetar_para_estado_atual()
        else:
            self._animacao_extra_hook()
            self.anim_atual.atualizar()
        return 0

    def _resetar_para_estado_atual(self):
        fallback = self.animaçoes[getattr(self, self.ESTADO_PADRAO)]
        self.anim_atual = self.animaçoes.get(self.estado, fallback)
        self.anim_atual.resetar()
        self._estado_anterior = self.estado

    def _atualizar_troca_animacao(self, dano_causado):
        resultado = self._atualizar_hit_flash()
        if resultado is not None:
            return resultado

        if self.estado != self._estado_anterior:
            self._resetar_para_estado_atual()

        self._animacao_extra_hook()

        self.anim_atual.atualizar()
        return dano_causado

    # COMBATE 

    def receber_evento(self, evento):
        kb = evento.knockback or KnockbackSpec()
        #o tempo mínimo de reação é do próprio inimigo; golpes mais fortes
        #podem estender, mas nunca encurtar (globin/mushroom tinham a animação
        #de "take hit" cortada pelo duracao_hit padrão do player)
        duracao_hit = 0
        if evento.stagger:
            duracao_hit = max(self.HITSTUN_FRAMES, evento.duracao_hit or 0)
        return self.receber_hit(
            evento.dano,
            evento.direcao,
            forca_x=kb.forca_x,
            forca_y=kb.forca_y,
            frames_kb=kb.frames or None,
            duracao_hit=duracao_hit,
        )

    def receber_hit(self, dano, direçao_knockback, forca_x=None, forca_y=None, frames_kb=None, duracao_hit=None):
        if getattr(self, "_escudo_ativo", False):
            return False  # só o boss usa isso

        frames_invenc = self.Frames_ivenc if self.USAR_IFRAMES_DANO else 0
        aplicado = self.receber_dano(dano, frames_invenc=frames_invenc)
        if not aplicado:
            return False

        if not self.vivo:
            self.ataque_ativo = None
            self._animando_ataque = False
            self._ataque_atual = None
            self._resetar_flags_ataque()
            if not hasattr(self, "_timer_morte"):
                self._iniciar_morte()
            return True

        #hiper armor quando está no próprio ataque
        if self._animando_ataque and self.IMUNE_DURANTE_ATAQUE:
            return True

        #hiper armor temporário após um stagger
        if self._imune_stagger > 0:
            return True

        forca_x     = self.KB_FORCA_X       if forca_x      is None else forca_x
        forca_y     = self.KB_FORCA_Y       if forca_y      is None else forca_y
        frames_kb   = self.KB_FRAMES        if frames_kb    is None else frames_kb
        duracao_hit = self.HITSTUN_FRAMES   if duracao_hit  is None else duracao_hit

        self.aplicar_knockback(direçao_knockback, forca_x, forca_y, frames_kb)
        self.ataque_ativo = None
        self._animando_ataque = False
        self._ataque_atual = None
        self._resetar_flags_ataque()

        #se o golpe interrompeu um ataque, volta para um estado neutro.
        #sem isso o inimigo podia terminar o hitstun exibindo o 1º frame do
        #ataque cancelado (principalmente enquanto o cooldown ainda está ativo)
        if self.estado == self.Atacando:
            self.estado = getattr(self, self.ESTADO_PADRAO)

        if duracao_hit > 0:
            self._em_hit = True
            self._timer_hit = duracao_hit
            self._em_recuperacao = False
            self._timer_recuperacao = 0
            self.anim_hit.resetar()
            #aplica já neste frame para o feedback aparecer mesmo durante o hitstop
            self.anim_atual = self.anim_hit

        if self.IMUNIDADE_STAGGER_FRAMES > 0:
            self._imune_stagger = frames_kb + duracao_hit + self.IMUNIDADE_STAGGER_FRAMES

        return True

    # DESENHO

    def desenhar(self, tela, camera):
        if not self.vivo and (not hasattr(self, "_timer_morte") or self._timer_morte <= 0):
            return

        sr = camera.aplicar(self.rect)

        if self.vivo and self.invencivel and self._frame % 6 < 3:
            return

        offset_x, offset_y = self._offset_desenho(sr)
        espelhado = not self.olhando_dir
        self.anim_atual.desenhar(tela, offset_x, offset_y, espelhado)

        self._desenhar_extra(tela, sr)   # FIX: faltava chamar (usado pelo escudo do boss)

        if self.hp < self.hp_max:
            self._desenhar_hp(tela, sr)

    def _desenhar_extra(self, tela, sr):
        # hook opcional (ex: contorno do escudo do boss). vazio por padrão
        pass

    def _desenhar_hp(self, tela, sr):
        bar_w = sr.width
        ratio = self.hp / self.hp_max
        pygame.draw.rect(tela, (60, 20, 20), (sr.x, sr.y - 8, bar_w, 4), border_radius=2)
        if ratio > 0:
            pygame.draw.rect(tela, (200, 40, 40), (sr.x, sr.y - 8, int(bar_w * ratio), 4), border_radius=2)