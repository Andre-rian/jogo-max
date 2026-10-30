from core.combat.colisao import construir_hitboxes
from core.combat.dano import DamageEvent, RegistroDano


class CombatSystem:
    def __init__(self):
        self.registro = RegistroDano()
        self.eventos = []
        self.frame = 0
        self.hitstop = 0
        self._uid = 0

    def resolver(self, player, inimigos, projeteis, rects_solidos=None):
        self.frame += 1
        self.eventos.clear()

        self._resolver_ataque_do_player(player, inimigos, rects_solidos or ())
        self._resolver_ataques_dos_inimigos(player, inimigos, rects_solidos or ())
        self._resolver_projeteis(player, projeteis)
        self._avancar_ataques(player, inimigos)

        return self.eventos

    def consumir_hitstop(self):
        if self.hitstop <= 0:
            return False
        self.hitstop -= 1
        return True

    def _uid_fonte(self, fonte):
        uid = getattr(fonte, "_combate_uid", None)
        if uid is None:
            self._uid += 1
            uid = self._uid
            try:
                fonte._combate_uid = uid
            except AttributeError:
                pass
        return uid

    def _parede_entre(self, atacante, alvo, rects_solidos):
        if not rects_solidos:
            return False
        inicio = atacante.rect.center
        fim = alvo.rect.center
        for tile in rects_solidos:
            if tile.clipline(inicio, fim):
                return True
        return False

    def _resolver_ataque_do_player(self, player, inimigos, rects_solidos):
        ataque = getattr(player, "ataque_ativo", None)
        if ataque is None or not player.vivo:
            return

        fonte_uid = self._uid_fonte(ataque)
        for hitbox in construir_hitboxes(ataque):
            for inimigo in list(inimigos):
                if not getattr(inimigo, "vivo", False):
                    continue
                if hitbox.janela.bloqueia_por_parede and self._parede_entre(
                    player, inimigo, rects_solidos
                ):
                    continue
                if not hitbox.colide_com(inimigo):
                    continue
                if not self.registro.pode_acertar(
                    fonte_uid, id(inimigo), hitbox.janela, self.frame
                ):
                    continue

                evento = DamageEvent(
                    atacante=player,
                    alvo=inimigo,
                    fonte=ataque,
                    janela=hitbox.janela,
                    dano=hitbox.dano.calcular(),
                    direcao=1 if inimigo.rect.centerx >= player.rect.centerx else -1,
                    knockback=hitbox.dano.knockback,
                    hitstop=hitbox.dano.hitstop,
                    stagger=hitbox.dano.stagger,
                    duracao_hit=hitbox.dano.duracao_hit,
                    frames_invenc=hitbox.dano.frames_invenc,
                    tipo="melee",
                )
                evento.aplicado = bool(inimigo.receber_evento(evento))
                self.eventos.append(evento)
                if evento.aplicado:
                    self.registro.registrar(
                        fonte_uid, id(inimigo), hitbox.janela, self.frame
                    )
                    if evento.hitstop > 0:
                        self.hitstop = max(self.hitstop, evento.hitstop)

    def _resolver_ataques_dos_inimigos(self, player, inimigos, rects_solidos):
        if not player.vivo:
            return

        for inimigo in list(inimigos):
            if not getattr(inimigo, "vivo", False):
                continue
            ataque = getattr(inimigo, "ataque_ativo", None)
            if ataque is None:
                continue

            fonte_uid = self._uid_fonte(ataque)
            for hitbox in construir_hitboxes(ataque):
                if not player.vivo:
                    break
                if hitbox.janela.bloqueia_por_parede and self._parede_entre(
                    inimigo, player, rects_solidos
                ):
                    continue
                if not hitbox.colide_com(player):
                    continue
                if not self.registro.pode_acertar(
                    fonte_uid, id(player), hitbox.janela, self.frame
                ):
                    continue

                evento = DamageEvent(
                    atacante=inimigo,
                    alvo=player,
                    fonte=ataque,
                    janela=hitbox.janela,
                    dano=hitbox.dano.calcular(),
                    direcao=1 if player.rect.centerx >= inimigo.rect.centerx else -1,
                    knockback=hitbox.dano.knockback,
                    hitstop=hitbox.dano.hitstop,
                    stagger=hitbox.dano.stagger,
                    duracao_hit=hitbox.dano.duracao_hit,
                    frames_invenc=hitbox.dano.frames_invenc,
                    tipo="melee",
                )
                evento.aplicado = bool(player.receber_evento(evento))
                self.eventos.append(evento)
                if evento.aplicado:
                    self.registro.registrar(
                        fonte_uid, id(player), hitbox.janela, self.frame
                    )
                    if evento.hitstop > 0:
                        self.hitstop = max(self.hitstop, evento.hitstop)

    def _resolver_projeteis(self, player, projeteis):
        if not player.vivo:
            return

        for projetil in list(projeteis):
            if not getattr(projetil, "ativo", False):
                continue

            fonte_uid = self._uid_fonte(projetil)
            for hitbox in projetil.hitboxes_ativas():
                if not player.vivo:
                    break
                if not hitbox.colide_com(player):
                    continue
                if not self.registro.pode_acertar(
                    fonte_uid, id(player), hitbox.janela, self.frame
                ):
                    continue

                evento = DamageEvent(
                    atacante=projetil,
                    alvo=player,
                    fonte=projetil,
                    janela=hitbox.janela,
                    dano=hitbox.dano.calcular(),
                    direcao=1 if player.rect.centerx >= projetil.rect.centerx else -1,
                    knockback=hitbox.dano.knockback,
                    hitstop=hitbox.dano.hitstop,
                    stagger=hitbox.dano.stagger,
                    duracao_hit=hitbox.dano.duracao_hit,
                    frames_invenc=hitbox.dano.frames_invenc,
                    tipo="projetil",
                )
                evento.aplicado = bool(player.receber_evento(evento))
                self.eventos.append(evento)
                if evento.aplicado:
                    self.registro.registrar(
                        fonte_uid, id(player), hitbox.janela, self.frame
                    )
                    projetil.ao_acertar(player, evento)
                    if evento.hitstop > 0:
                        self.hitstop = max(self.hitstop, evento.hitstop)

    def _avancar_ataques(self, player, inimigos):
        ataque = getattr(player, "ataque_ativo", None)
        if ataque is not None:
            if player.vivo:
                self._chamar_hook(player, ataque, player)
                ataque.avancar()
                if ataque.finalizado:
                    player.encerrar_ataque()
                    self.registro.limpar_fonte(self._uid_fonte(ataque))
            else:
                player.encerrar_ataque()

        for inimigo in list(inimigos):
            ataque = getattr(inimigo, "ataque_ativo", None)
            if ataque is None:
                continue

            if getattr(inimigo, "vivo", False):
                self._chamar_hook(inimigo, ataque, player)
                ataque.avancar()
                if ataque.finalizado:
                    inimigo.encerrar_ataque()
                    self.registro.limpar_fonte(self._uid_fonte(ataque))
            else:
                inimigo.encerrar_ataque()

    def _chamar_hook(self, dono, ataque, player):
        hook = getattr(dono, "_ao_tick_ataque", None)
        if hook is not None:
            hook(player, ataque.frame)
