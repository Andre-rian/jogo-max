from dataclasses import dataclass, field

from core.combat.tipos import JanelaGolpe, KnockbackSpec, PoliticaHit


@dataclass
class DamageEvent:
    atacante: object
    alvo: object
    fonte: object
    janela: JanelaGolpe
    dano: int
    direcao: int
    knockback: KnockbackSpec = field(default_factory=KnockbackSpec)
    hitstop: int = 0
    stagger: bool = True
    duracao_hit: int | None = None
    frames_invenc: int | None = None
    tipo: str = "melee"
    aplicado: bool = False


class RegistroDano:
    def __init__(self):
        self._acertos = {}

    def pode_acertar(self, fonte_uid, alvo_uid, janela, tick):
        chave = (fonte_uid, alvo_uid, janela.nome, janela.canal)
        ultimo = self._acertos.get(chave)
        if ultimo is None:
            return True

        if janela.politica in (PoliticaHit.UMA_VEZ, PoliticaHit.PIERCE):
            return False

        if janela.politica == PoliticaHit.PERSISTENTE:
            return True

        return tick - ultimo >= max(0, janela.intervalo)

    def registrar(self, fonte_uid, alvo_uid, janela, tick):
        chave = (fonte_uid, alvo_uid, janela.nome, janela.canal)
        self._acertos[chave] = tick

    def limpar_fonte(self, fonte_uid):
        chaves = [c for c in self._acertos if c[0] == fonte_uid]
        for chave in chaves:
            del self._acertos[chave]

    def limpar(self):
        self._acertos.clear()
