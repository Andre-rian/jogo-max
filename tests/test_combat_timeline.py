import pygame

from core.animated_sprite import AnimatedSprite
from core.combat import (
    DanoSpec,
    DefinicaoAtaque,
    FaseAtaque,
    InstanciaAtaque,
    JanelaGolpe,
    ModoMovimento,
    PoliticaHit,
    RegistroDano,
)


def _animacao(n_frames=4, velocidade=5):
    return AnimatedSprite(
        "assets/sprites/player/knight/_AttackNoMovement.png",
        120,
        80,
        velocidade=velocidade,
        escala=1,
        n_frames=n_frames,
    )


def _definicao(janelas, n_frames=4, velocidade=5):
    return DefinicaoAtaque(
        nome="teste",
        animacao=_animacao(n_frames, velocidade),
        janelas=tuple(janelas),
        movimento=ModoMovimento.REDUZIDO,
        dano=DanoSpec(dano_base=10),
    )


class _Dono:
    def __init__(self):
        self.anim_atual = _animacao()
        self.olhando_dir = True
        self.rect = pygame.Rect(0, 0, 30, 30)

    def _offset_mask(self):
        return self.rect.topleft

    def encerrar_ataque(self):
        self.ataque_ativo = None


def test_instancia_avanca_frames_e_janelas():
    janela = JanelaGolpe("corte", 1, 2)
    dono = _Dono()
    ataque = InstanciaAtaque(_definicao([janela]), dono)

    assert ataque.frame == 0
    assert ataque.fase == FaseAtaque.STARTUP
    assert ataque.janelas_ativas() == ()

    for _ in range(5):
        ataque.avancar()
    assert ataque.frame == 1
    assert ataque.janelas_ativas() == (janela,)
    assert ataque.fase == FaseAtaque.ACTIVE

    for _ in range(5):
        ataque.avancar()
    assert ataque.frame == 2
    assert ataque.janelas_ativas() == (janela,)

    for _ in range(5):
        ataque.avancar()
    assert ataque.frame == 3
    assert ataque.fase == FaseAtaque.RECOVERY


def test_instancia_finaliza_pela_duracao_em_ticks():
    ataque = InstanciaAtaque(_definicao([JanelaGolpe("corte", 1, 2)]), _Dono())
    assert ataque.definicao.duracao_ticks == 4 * 5

    for _ in range(ataque.definicao.duracao_ticks):
        ataque.avancar()

    assert ataque.finalizado


def test_definicao_sem_janelas_nao_quebra_fase():
    definicao = _definicao([])
    assert definicao.fase_em(0) == FaseAtaque.STARTUP
    assert definicao.primeiro_frame_ativo == 0
    assert definicao.ultimo_frame_ativo == 0

    ataque = InstanciaAtaque(definicao, _Dono())
    assert ataque.janelas_ativas() == ()
    assert ataque.fase == FaseAtaque.STARTUP


def test_registro_dano_idempotente_por_janela_e_canal():
    registro = RegistroDano()
    janela = JanelaGolpe("corte", 1, 2, politica=PoliticaHit.UMA_VEZ, canal="principal")

    assert registro.pode_acertar(1, 2, janela, tick=10)
    registro.registrar(1, 2, janela, tick=10)
    assert not registro.pode_acertar(1, 2, janela, tick=11)

    outra = JanelaGolpe("corte_2", 1, 2, politica=PoliticaHit.UMA_VEZ, canal="secundario")
    assert registro.pode_acertar(1, 2, outra, tick=11)

    registro.limpar_fonte(1)
    assert registro.pode_acertar(1, 2, janela, tick=12)


def test_registro_multi_hit_respeita_intervalo():
    registro = RegistroDano()
    janela = JanelaGolpe("aura", 1, 9, politica=PoliticaHit.MULTI_HIT, intervalo=5)

    assert registro.pode_acertar(1, 2, janela, tick=10)
    registro.registrar(1, 2, janela, tick=10)
    assert not registro.pode_acertar(1, 2, janela, tick=14)
    assert registro.pode_acertar(1, 2, janela, tick=15)
