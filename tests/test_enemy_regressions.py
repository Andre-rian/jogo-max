import pygame

from core.combat import CombatSystem, JanelaGolpe, KnockbackSpec, construir_hitboxes
from core.combat.dano import DamageEvent
from entities.entity import Entity
from entities.monsters.flying_eye import FlyingEye
from entities.monsters.globin import Globin
from entities.monsters.mushroom import Mushroom
from entities.monsters.skeleton import Skeleton
from entities.monsters.skeleton_boss import EsqueletoBoss
from entities.player import Player


def _evento(alvo, duracao_hit=12, fonte=None, janela="teste"):
    return DamageEvent(
        atacante=None,
        alvo=alvo,
        fonte=fonte,
        janela=JanelaGolpe(janela, 0, 1),
        dano=1,
        direcao=1,
        knockback=KnockbackSpec(forca_x=0, forca_y=0, frames=1),
        duracao_hit=duracao_hit,
        stagger=True,
    )


def test_hitstun_nao_encurta_a_reacao_de_globin_e_mushroom():
    for classe in (Globin, Mushroom):
        inimigo = classe(100, 100, 0, 500)

        inimigo.receber_evento(_evento(inimigo, duracao_hit=12))

        assert inimigo._em_hit
        assert inimigo._timer_hit == max(inimigo.hitstun_padrao, 12)


def test_flying_eye_knockback_nao_atravessa_parede():
    eye = FlyingEye(100, 100, 0, 500)
    parede = pygame.Rect(160, 0, 32, 400)

    eye.receber_hit(1, 1, forca_x=20, forca_y=0, frames_kb=10, duracao_hit=1)
    for _ in range(10):
        eye._atualizar_knockback([parede])

    assert eye.rect.right <= parede.left


def test_flying_eye_ataque_nao_atravessa_parede():
    eye = FlyingEye(100, 100, 0, 500)
    player = Player(300, 100)
    parede = pygame.Rect(160, 0, 32, 400)

    eye._iniciar_ataque("dash", player)
    for _ in range(20):
        eye._atualizar_ataque_em_curso([parede], player)

    assert eye.rect.right <= parede.left


def test_animacao_de_hit_completa_antes_de_voltar_ao_estado():
    player = Player(5000, 300)
    alvos = [
        (Globin, (100, 300, 0, 500)),
        (Mushroom, (100, 300, 0, 500)),
        (Skeleton, (100, 300, 0, 500)),
        (FlyingEye, (100, 300, 0, 500)),
    ]

    for classe, args in alvos:
        inimigo = classe(*args)
        inimigo.receber_evento(_evento(inimigo))

        vistos = set()
        for _ in range(inimigo.hitstun_padrao + 2):
            inimigo.atualizar([], player)
            if inimigo.anim_atual is inimigo.anim_hit:
                vistos.add(inimigo.anim_atual.frame_index)

        assert max(vistos) == len(inimigo.anim_hit.frames) - 1
        assert inimigo.anim_atual is not inimigo.animaçoes[inimigo.Atacando]


def test_hit_durante_ataque_nao_deixa_pose_de_ataque():
    player = Player(120, 300)
    alvos = [
        (Globin, (100, 300, 0, 500)),
        (Mushroom, (100, 300, 0, 500)),
        (Skeleton, (100, 300, 0, 500)),
    ]

    for classe, args in alvos:
        inimigo = classe(*args)
        inimigo.iniciar_ataque("normal", player)
        inimigo.cooldown_ataq = 120

        inimigo.receber_evento(_evento(inimigo))
        for _ in range(inimigo.hitstun_padrao + 4):
            inimigo.atualizar([], player)

        assert inimigo.estado != inimigo.Atacando
        assert inimigo.anim_atual is not inimigo.animaçoes[inimigo.Atacando]


def test_mesmo_golpe_so_aplica_uma_vez_com_hitbox_em_contato():
    player = Player(200, 300)
    inimigo = Skeleton(240, 300, 0, 500)
    inimigo.rect.midbottom = (player.rect.centerx + 40, player.rect.bottom)
    player.olhando_dir = True
    player._disparar_ataque(combo=False)

    sistema = CombatSystem()
    acertos = 0
    for _ in range(60):
        player.atualizar_mask()
        inimigo.atualizar_mask()
        for evento in sistema.resolver(player, [inimigo], [], []):
            if evento.aplicado:
                acertos += 1

    assert acertos == 1


def test_inimigo_morto_nao_se_move_nem_ataca():
    player = Player(120, 300)
    inimigo = Globin(100, 300, 0, 500)
    inimigo.hp = 1

    inimigo.receber_evento(_evento(inimigo))
    assert not inimigo.vivo

    posicao = inimigo.rect.topleft
    for _ in range(10):
        inimigo.atualizar([], player)

    assert inimigo.rect.topleft == posicao
    assert inimigo.ataque_ativo is None
    assert not inimigo._animando_ataque


def test_recuperacao_pos_hit_mantem_inimigo_parado_antes_de_voltar_a_ia():
    player = Player(480, 300)
    inimigo = Globin(300, 300, 0, 500)
    inimigo.cooldown_ataq = 999
    for atributo in ("cooldown_bomba", "cooldown_esporo"):
        if hasattr(inimigo, atributo):
            setattr(inimigo, atributo, 999)

    inimigo.receber_evento(_evento(inimigo))
    for _ in range(200):
        if inimigo._em_recuperacao:
            break
        inimigo.atualizar([], player)

    assert inimigo._em_recuperacao
    assert inimigo.estado == getattr(inimigo, inimigo.ESTADO_PADRAO)

    x = inimigo.rect.x
    for _ in range(inimigo.RECUPERACAO_HIT_FRAMES - 1):
        inimigo.atualizar([], player)
        assert inimigo.rect.x == x
        assert not inimigo._animando_ataque

    assert inimigo._em_recuperacao
    x = inimigo.rect.x
    inimigo.atualizar([], player)
    assert not inimigo._em_recuperacao
    assert inimigo.rect.x == x


def test_mushroom_nao_tem_pausa_artificial_apos_o_hitstun():
    player = Player(5000, 300)
    inimigo = Mushroom(100, 300, 0, 500)
    inimigo.receber_evento(_evento(inimigo))

    for _ in range(inimigo.hitstun_padrao + 2):
        inimigo.atualizar([], player)
        if not inimigo._em_hit:
            break

    assert not inimigo._em_recuperacao
    assert inimigo._timer_retomada == inimigo.RETOMADA_FRAMES


def test_mushroom_retoma_perseguicao_em_dois_estagios():
    player = Player(300, 300)
    inimigo = Mushroom(100, 300, 0, 500)
    inimigo.receber_evento(_evento(inimigo))

    for _ in range(500):
        inimigo.atualizar([], player)
        if inimigo._timer_retomada > 0:
            break

    assert inimigo._timer_retomada == inimigo.RETOMADA_FRAMES

    velocidades = []
    for _ in range(inimigo.RETOMADA_FRAMES):
        inimigo.atualizar([], player)
        velocidades.append(inimigo.vel.x)

    assert velocidades == [inimigo.Vel_patrulha] * inimigo.RETOMADA_FRAMES

    inimigo.atualizar([], player)
    assert inimigo.vel.x == inimigo.Vel_perseguir


def test_mushroom_knockback_nao_desliza_no_hitstun():
    player = Player(5000, 300)
    inimigo = Mushroom(100, 300, 0, 500)
    inimigo.receber_hit(1, 1, forca_x=4, forca_y=0, frames_kb=5, duracao_hit=20)

    for _ in range(5):
        inimigo.atualizar([], player)

    assert inimigo.timer_knockback == 0
    assert inimigo.vel.x == 0

    x = inimigo.rect.x
    for _ in range(5):
        inimigo.atualizar([], player)
        assert inimigo.rect.x == x


def test_ataques_de_inimigos_tem_recuperacao_explicita():
    inimigos = [
        Globin(0, 0, 0, 100),
        Mushroom(0, 0, 0, 100),
        Skeleton(0, 0, 0, 100),
        FlyingEye(0, 0, -50, 50),
        EsqueletoBoss(0, 0),
    ]

    for inimigo in inimigos:
        for nome, definicao in inimigo.definicoes_ataque.items():
            assert definicao.recuperacao_ticks > 0, (type(inimigo).__name__, nome)
            assert definicao.duracao_ticks > definicao.duracao_animacao_ticks


def test_recuperacao_nao_mantem_hitbox_ativa():
    player = Player(200, 300)
    inimigo = Globin(100, 300, 0, 500)
    inimigo._iniciar_ataque("normal", 1, player)
    ataque = inimigo.ataque_ativo

    for _ in range(ataque.definicao.duracao_animacao_ticks):
        ataque.avancar()

    assert ataque.fase.value == "recovery"
    assert ataque.janelas_ativas() == ()
    assert construir_hitboxes(ataque) == []


def test_globin_normal_limita_lunge_e_acerta_no_range_da_ia():
    player = Player(300, 300)
    chao = pygame.Rect(0, player.rect.bottom, 640, 32)
    inimigo = Globin(
        player.rect.centerx - Globin.Alcance_ataq_normal,
        player.rect.bottom - 44,
        0,
        600,
    )
    inimigo.rect.midbottom = (
        player.rect.centerx - Globin.Alcance_ataq_normal,
        player.rect.bottom,
    )
    inimigo.olhando_dir = True
    inimigo._iniciar_ataque("normal", 1, player)

    sistema = CombatSystem()
    x_inicial = inimigo.rect.centerx
    acertos = 0
    deslocamento = 0
    viu_ataque = False
    for _ in range(90):
        player.atualizar_mask()
        inimigo.atualizar([chao], player)
        inimigo.atualizar_mask()
        for evento in sistema.resolver(player, [inimigo], [], [chao]):
            if evento.aplicado:
                acertos += 1
        if inimigo.ataque_ativo is not None:
            viu_ataque = True
            deslocamento = max(deslocamento, abs(inimigo.rect.centerx - x_inicial))
        elif viu_ataque:
            break

    assert acertos == 1
    assert deslocamento <= 30


def test_flying_eye_mordida_acerta_de_perto_e_limita_lunge():
    for distancia in (10, 55):
        player = Player(300, 300)
        inimigo = FlyingEye(
            player.rect.centerx - distancia,
            player.rect.centery,
            0,
            600,
        )
        inimigo.rect.center = (player.rect.centerx - distancia, player.rect.centery)
        inimigo.olhando_dir = True
        inimigo._iniciar_ataque("mordida", player)

        sistema = CombatSystem()
        x_inicial = inimigo.rect.centerx
        acertos = 0
        deslocamento = 0
        viu_ataque = False
        for _ in range(80):
            player.atualizar_mask()
            inimigo.atualizar([], player)
            inimigo.atualizar_mask()
            for evento in sistema.resolver(player, [inimigo], [], []):
                if evento.aplicado:
                    acertos += 1
            if inimigo.ataque_ativo is not None:
                viu_ataque = True
                deslocamento = max(deslocamento, abs(inimigo.rect.centerx - x_inicial))
            elif viu_ataque:
                break

        assert acertos == 1, distancia
        assert deslocamento <= 30, distancia


def test_flying_eye_usa_mordida_de_perto_e_dash_na_distancia_media():
    player = Player(300, 300)

    perto = FlyingEye(player.rect.centerx - 30, player.rect.centery, 0, 600)
    perto.rect.center = (player.rect.centerx - 30, player.rect.centery)
    perto.cooldown_ataq = 0
    perto._ia([], player)
    assert perto._ataque_atual == "mordida"

    medio = FlyingEye(player.rect.centerx - 100, player.rect.centery, 0, 600)
    medio.rect.center = (player.rect.centerx - 100, player.rect.centery)
    medio.cooldown_ataq = 0
    medio._ia([], player)
    assert medio._ataque_atual == "dash"


def test_mushroom_knockback_curto_de_8_pixels():
    player = Player(5000, 300)
    inimigo = Mushroom(100, 300, 0, 500)
    x_inicial = inimigo.rect.x

    inimigo.receber_hit(1, 1)

    for _ in range(inimigo.KB_FRAMES + 2):
        inimigo.atualizar([], player)

    assert inimigo.rect.x - x_inicial == 8


def test_boss_guarda_quebra_no_terceiro_golpe_sem_imunidade():
    boss = EsqueletoBoss(100, 100)
    boss.receber_evento(_evento(boss, fonte=object(), janela="golpe_1"))

    assert not boss._em_hit
    assert boss._guarda_golpes == 1
    assert boss._flash_reacao_timer > 0

    boss.receber_evento(_evento(boss, fonte=object(), janela="golpe_2"))
    assert not boss._em_hit
    assert boss._guarda_golpes == 2

    boss.receber_evento(_evento(boss, fonte=object(), janela="golpe_3"))
    assert boss._em_hit
    assert boss._timer_hit == 24
    assert boss._guarda_golpes == 0
    assert boss._quebra_ativa


def test_boss_terceiro_golpe_durante_ataque_interrompe_com_16_ticks():
    player = Player(120, 300)
    boss = EsqueletoBoss(100, 300)
    boss.iniciar_ataque("normal", player)

    for i in range(3):
        boss.receber_evento(_evento(boss, fonte=object(), janela=f"golpe_{i}"))

    assert boss._em_hit
    assert boss._timer_hit == 16
    assert boss.ataque_ativo is None
    assert not boss._animando_ataque
    assert boss.cooldown_ataq <= boss.Cooldown_apos_quebra


def test_boss_hits_durante_hitstun_da_quebra_nao_contam():
    boss = EsqueletoBoss(100, 100)
    for i in range(3):
        boss.receber_evento(_evento(boss, fonte=object(), janela=f"golpe_{i}"))

    hp_antes = boss.hp
    boss.receber_evento(_evento(boss, fonte=object(), janela="golpe_extra"))

    assert boss.hp < hp_antes
    assert boss._guarda_golpes == 0
    assert boss._em_hit


def test_boss_guarda_reseta_apos_timeout_e_deduplica_mesma_janela():
    player = Player(5000, 300)
    boss = EsqueletoBoss(100, 100)
    fonte = object()
    evento = _evento(boss, fonte=fonte, janela="golpe")

    boss.receber_evento(evento)
    boss.receber_evento(_evento(boss, fonte=fonte, janela="golpe"))
    assert boss._guarda_golpes == 1

    for _ in range(boss.GUARDA_TIMEOUT_TICKS):
        boss.atualizar([], player)

    assert boss._guarda_golpes == 0


def test_boss_pressiona_em_vez_de_ficar_parado_no_cooldown_da_espada():
    boss = EsqueletoBoss(0, 0)
    player = Player(0, 0)
    boss.rect.center = (100, 300)
    player.rect.center = (200, 300)
    boss.cooldown_ataq = 999
    boss.cooldown_projetil = 999
    boss.cooldown_escudo = 999

    boss._ia([], player)

    assert boss.estado == boss.Perseguir
    assert boss.vel.x > 0


def test_boss_projetil_nao_depende_do_cooldown_da_espada():
    boss = EsqueletoBoss(0, 0)
    player = Player(0, 0)
    boss.rect.center = (100, 300)
    player.rect.center = (240, 300)
    boss.cooldown_ataq = 999
    boss.cooldown_escudo = 999
    boss.cooldown_projetil = 0

    boss._ia([], player)

    assert boss._ataque_atual == "projetil"
    assert boss.cooldown_projetil == boss.Cooldown_projetil_max
    assert boss.cooldown_ataq == 999


def test_escudo_do_boss_nao_congela_outros_cooldowns():
    boss = EsqueletoBoss(0, 0)
    boss._escudo_ativo = True
    boss._duracao_escudo = 10
    boss.cooldown_escudo = 10
    boss.cooldown_ataq = 10
    boss.cooldown_projetil = 10

    boss._estado_especial([], Player(0, 0))

    assert boss.cooldown_escudo == 9
    assert boss.cooldown_ataq == 9
    assert boss.cooldown_projetil == 9


def test_boss_recompoe_postura_e_decide_imediatamente_apos_quebra():
    boss = EsqueletoBoss(100, 100)
    player = Player(5000, 300)
    for i in range(3):
        boss.receber_evento(_evento(boss, fonte=object(), janela=f"golpe_{i}"))

    assert boss._recuperacao_pendente == boss.Recomposicao_apos_quebra

    for _ in range(boss._timer_hit + 2):
        boss.atualizar([], player)
        if not boss._em_hit:
            break

    assert boss._em_recuperacao
    assert boss.estado == boss.Patrulha

    for _ in range(boss.Recomposicao_apos_quebra):
        boss.atualizar([], player)

    assert not boss._em_recuperacao
    assert boss._tempo_decisao == 0


def test_perfil_do_inimigo_manda_no_knockback_do_evento():
    mushroom = Mushroom(100, 300, 0, 500)
    evento = _evento(mushroom, duracao_hit=12)
    evento.knockback = KnockbackSpec(forca_x=4, forca_y=-2, frames=12)
    x_inicial = mushroom.rect.x

    mushroom.receber_evento(evento)
    for _ in range(Mushroom.KB_FRAMES):
        mushroom._atualizar_knockback([])

    assert mushroom.rect.x - x_inicial == Mushroom.KB_FORCA_X * Mushroom.KB_FRAMES


def test_hitstun_terrestre_usa_animacao_de_hit():
    assert Globin(0, 0, 0, 100).hitstun_padrao == 20
    assert Mushroom(0, 0, 0, 100).hitstun_padrao == 20
    assert Skeleton(0, 0, 0, 100).hitstun_padrao == 24
    assert Skeleton.RECUPERACAO_HIT_FRAMES == 6


def test_hitstop_do_player_foi_aumentado():
    player = Player(0, 0)
    for tiers in player.definicoes_ataque.values():
        for tier, variantes in tiers.items():
            for definicao in variantes.values():
                assert definicao.dano.hitstop == (4 if tier == "combo" else 3)


def test_movimento_subpixel_preserva_velocidades_decimais():
    for velocidade, esperado in ((0.8, 8), (1.2, 12), (2.4, 24)):
        entidade = Entity(0, 0, 10, 10, 1)
        entidade.USAR_MOVIMENTO_SUBPIXEL = True
        entidade.vel.x = velocidade

        for _ in range(10):
            entidade.mover_com_colisão([], [])

        assert entidade.rect.x == esperado


def test_movimento_subpixel_limitado_aos_inimigos_terrestres():
    assert Globin.USAR_MOVIMENTO_SUBPIXEL
    assert Mushroom.USAR_MOVIMENTO_SUBPIXEL
    assert Skeleton.USAR_MOVIMENTO_SUBPIXEL
    assert not FlyingEye.USAR_MOVIMENTO_SUBPIXEL
    assert not EsqueletoBoss.USAR_MOVIMENTO_SUBPIXEL
    assert not Player.USAR_MOVIMENTO_SUBPIXEL


def test_patrulha_nao_mantem_velocidade_de_perseguicao():
    for classe in (Globin, Mushroom):
        inimigo = classe(100, 300, 0, 500)
        inimigo.vel.x = classe.Vel_perseguir

        inimigo._patrulhar()

        assert inimigo.vel.x == classe.Vel_patrulha

    skeleton = Skeleton(100, 300, 0, 500)
    skeleton.vel.x = Skeleton.Vel_perseguir
    skeleton._ia([], Player(1000, 300))

    assert skeleton.vel.x == Skeleton.Vel_patrulha


def test_globin_e_mushroom_usam_animacao_de_patrulha_em_movimento():
    player = Player(5000, 300)

    for classe in (Globin, Mushroom):
        inimigo = classe(100, 300, 0, 500)
        inimigo.vel.x = classe.Vel_patrulha

        inimigo.atualizar([], player)

        assert inimigo.estado == inimigo.Patrulha
        assert inimigo.anim_atual is inimigo.anim_patrulha
