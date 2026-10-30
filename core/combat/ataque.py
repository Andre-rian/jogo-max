from core.combat.tipos import FaseAtaque


class InstanciaAtaque:
    def __init__(self, definicao, atacante, dano_base=None, alvo=None):
        self.definicao = definicao
        self.atacante = atacante
        self.dano_base = definicao.dano.dano_base if dano_base is None else dano_base
        self.alvo_inicial = alvo
        self.tick = 0
        self.frame = 0

        self.animacao = definicao.animacao
        self.animacao.manual = True
        self.animacao.resetar()
        self.animacao.definir_frame(0)

    @property
    def fase(self):
        if self.tick >= self.definicao.duracao_animacao_ticks:
            return FaseAtaque.RECOVERY
        return self.definicao.fase_em(self.frame)

    @property
    def finalizado(self):
        return self.tick >= self.definicao.duracao_ticks

    @property
    def progresso(self):
        if self.definicao.duracao_ticks <= 0:
            return 1.0
        return min(1.0, self.tick / self.definicao.duracao_ticks)

    def janelas_ativas(self):
        if self.fase == FaseAtaque.RECOVERY:
            return ()
        return self.definicao.janelas_no_frame(self.frame)

    def avancar(self):
        if self.finalizado:
            return self.frame

        self.tick += 1
        self.frame = min(
            self.tick // max(1, self.animacao.velocidade),
            self.definicao.total_frames - 1,
        )
        self.animacao.definir_frame(self.frame)
        return self.frame

    def fase_em(self, frame):
        return self.definicao.fase_em(frame)

    def __repr__(self):
        return (
            f"InstanciaAtaque({self.definicao.nome!r}, "
            f"frame={self.frame}, tick={self.tick}, fase={self.fase.value!r})"
        )
