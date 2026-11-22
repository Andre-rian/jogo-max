"""F.3: renderização, coexistência, temporizadores e ausência de efeitos funcionais."""
import copy
from itertools import combinations
from types import SimpleNamespace

import pygame
import pytest

from entities.objetos.item import get_item
from entities.objetos.pocao import Pocao
from ui import sprites_itens
from ui.estilo import Fonte_texto, Fonte_titulo
from ui.hud import trilho_status
from ui.hud.boss import BarraBoss, COR_ATRASADA, COR_VIDA
from ui.hud.hud import Hud
from ui.hud.mensagens import Mensagens
from ui.hud.notificacao import NotificacaoItem


class FonteRegistrada:
    def __init__(self, fonte):
        self.fonte = fonte
        self.textos = []

    def render(self, texto, *args):
        self.textos.append(texto)
        return self.fonte.render(texto, *args)

    def __getattr__(self, nome):
        return getattr(self.fonte, nome)


def chefe(hp=300, hp_max=300, nome='Carrasco Esquelético'):
    return SimpleNamespace(hp=hp, hp_max=hp_max, nome=nome)


def jogador():
    return SimpleNamespace(hp=40, hp_max=200, stamina=0, stamina_max=130,
                           stamina_delay=30, _frame_atual=5, buff_stamina_duracao=180,
                           pocao=Pocao(), ecos=10**59 + 123, inventario={'itens': {2: 999}})


def tela():
    return pygame.Surface((1280, 720), pygame.SRCALPHA)


def contar_cor(superficie, rect, cor):
    return sum(superficie.get_at((x, rect.centery))[:3] == cor
               for x in range(rect.left, rect.right))


@pytest.fixture(autouse=True)
def caches():
    sprites_itens.limpar_cache()
    trilho_status.limpar_cache()
    yield
    sprites_itens.limpar_cache()
    trilho_status.limpar_cache()


@pytest.mark.parametrize('hp,maximo,ratio', [(300, 300, 1), (150, 300, .5),
    (30, 300, .1), (0, 300, 0), (-10, 300, 0), (400, 300, 1), (300, 0, 0), (10, -1, 0)])
def test_chefe_preenchimento_limitado_trilho_e_dados(hp, maximo, ratio):
    barra, superficie = BarraBoss(Fonte_titulo(18)), tela()
    boss = chefe(hp, maximo)
    antes = vars(boss).copy()
    for _ in range(3):
        superficie.fill((0, 0, 0, 0))
        barra.desenhar(superficie, boss)
        barra.atualizar()
    assert contar_cor(superficie, barra.interior, COR_VIDA) == int(barra.interior.width * ratio)
    assert superficie.get_at((barra.interior.x - 2, barra.interior.y))[:3] == trilho_status.BORDA
    assert superficie.get_bounding_rect() == barra.rect
    assert vars(boss) == antes
    assert barra._boss_ultimo_dano == 0


def test_dano_atrasado_acumula_expira_e_zero_nao_reinicia():
    barra, superficie, boss = BarraBoss(Fonte_titulo(18)), tela(), chefe()
    barra.desenhar(superficie, boss)
    boss.hp = 150
    barra.desenhar(superficie, boss)
    assert barra._boss_ultimo_dano == 150
    assert contar_cor(superficie, barra.interior, COR_ATRASADA) == 221
    barra.atualizar()
    assert barra._boss_hp_display == 298
    boss.hp = 130
    barra.desenhar(superficie, boss)
    assert barra._boss_ultimo_dano == 170
    assert barra._boss_timer_dano == 120
    for _ in range(120):
        barra.atualizar()
    assert barra._boss_hp_display == 130
    assert barra._boss_ultimo_dano == barra._boss_timer_dano == 0
    boss.hp = 0
    barra.desenhar(superficie, boss)
    for _ in range(150):
        barra.atualizar()
        barra.desenhar(superficie, boss)
    assert barra._boss_hp_display == 0
    assert contar_cor(superficie, barra.interior, COR_VIDA) == 0
    assert contar_cor(superficie, barra.interior, COR_ATRASADA) == 0


@pytest.mark.parametrize('reapresentar', [False, True])
def test_troca_e_reapresentacao_nao_herdam_dano(reapresentar):
    barra, superficie, boss = BarraBoss(Fonte_titulo(18)), tela(), chefe()
    barra.desenhar(superficie, boss)
    boss.hp = 80
    barra.desenhar(superficie, boss)
    if reapresentar:
        superficie.fill((0, 0, 0, 0))
        barra.desenhar(superficie, None)
        assert not superficie.get_bounding_rect()
        assert not barra.rect
    else:
        boss = chefe(20, 50)  # Mesmo nome, identidade e máximo diferentes.
    barra.desenhar(superficie, boss)
    assert barra._boss_hp_display == boss.hp
    assert barra._boss_ultimo_dano == barra._boss_timer_dano == 0


def test_hud_encaminha_ausencia_e_cura_nao_cria_dano():
    hud, superficie, boss, player = Hud(), tela(), chefe(), jogador()
    hud.desenhar(superficie, player, boss)
    boss.hp = 80
    hud.desenhar(superficie, player, boss)
    hud.desenhar(superficie, player)
    boss.hp = 160
    hud.desenhar(superficie, player, boss)
    assert hud.boss_bar._boss_hp_display == 160
    assert hud.boss_bar._boss_ultimo_dano == 0
    boss.hp = 200
    hud.desenhar(superficie, player, boss)
    assert hud.boss_bar._boss_hp_display == 200
    assert hud.boss_bar._boss_ultimo_dano == 0


@pytest.mark.parametrize('id_item', [1, 2, 3, 4, 5])
def test_notificacao_preserva_sprite_nome_quantidade(id_item):
    fonte = FonteRegistrada(Fonte_titulo(18))
    notif, superficie, item = NotificacaoItem(fonte), tela(), get_item(id_item)
    antes = copy.deepcopy(vars(item))
    notif.mostrar(item, 1234567890123456789)
    notif.desenhar(superficie)
    assert item.nome in fonte.textos
    assert '1234567890123456789' in fonte.textos
    assert vars(item) == antes
    sprite = sprites_itens.obter_sprite_de_item(item)
    x, y = 12, (notif._painel.get_height() - sprite.get_height()) // 2
    for sx in range(sprite.get_width()):
        for sy in range(sprite.get_height()):
            cor = sprite.get_at((sx, sy))
            if cor.a == 255:
                assert notif._painel.get_at((x + sx, y + sy)) == cor


def test_duracao_e_fade_da_notificacao_inteira_sobre_fundo_claro():
    notif, superficie = NotificacaoItem(Fonte_titulo(18)), tela()
    notif.mostrar(get_item(2), 3)
    for _ in range(150):
        notif.atualizar()
        notif.desenhar(superficie)
    assert notif._notif_timer == 60
    assert notif._painel.get_alpha() == 255
    for _ in range(30):
        notif.desenhar(superficie)
    assert notif._notif_timer == 30
    assert notif._painel.get_alpha() == 127
    superficie.fill((240, 240, 240))
    notif.desenhar(superficie)
    assert all(c > 110 for c in superficie.get_at(notif.rect.center)[:3])
    for _ in range(29):
        notif.desenhar(superficie)
    assert notif._notif_timer == 0
    superficie.fill((240, 240, 240))
    notif.desenhar(superficie)
    assert superficie.get_at((640, 510))[:3] == (240, 240, 240)
    notif.mostrar(get_item(4))
    assert notif._notif_timer == 210


@pytest.mark.parametrize('com_chefe', [False, True])
@pytest.mark.parametrize('extenso', [False, True])
@pytest.mark.parametrize('fonte_maior', [False, True])
def test_retangulos_reais_sem_colisoes_e_f1_f2_preservadas(com_chefe, extenso, fonte_maior):
    hud, superficie, player = Hud(), tela(), jogador()
    if fonte_maior:
        fonte = pygame.font.Font(None, 26)
        hud.boss_bar = BarraBoss(fonte)
        hud.notificacao_item = NotificacaoItem(fonte)
        hud.mensagens = Mensagens(pygame.font.Font(None, 32), fonte)
    boss = chefe(nome='Guardião Esquelético dos Corredores do Castelo Esquecido' if extenso else 'Carrasco Esquelético')
    item = get_item(2) if not extenso else SimpleNamespace(
        id=2, icone='pocao', nome='Poção de Vida dos Guardiões Esquecidos do Castelo das Sombras Eternas')
    hud.mostrar_item_coletado(item, 10**59 + 123 if extenso else 2)
    hud.mostrar_prompt('Pressione E para abrir a porta do calabouço e atravessar o corredor' if extenso else '[E] Abrir baú')
    hud.mostra_mensagem('Você recuperou seus Ecos Profanos e pode continuar explorando o castelo.' if extenso else 'Jogo salvo')
    antes = copy.deepcopy(vars(player))
    boss_antes = vars(boss).copy()
    hud.desenhar(superficie, player, boss if com_chefe else None)
    rects = [hud.notificacao_item.rect, hud.mensagens.rect_prompt, hud.mensagens.rect_mensagem]
    for componente in (hud.status, hud.pocao_slot, hud.ecos):
        separado = tela()
        componente.desenhar(separado, player)
        rects.append(separado.get_bounding_rect())
    if com_chefe:
        separado = tela()
        hud.boss_bar.desenhar(separado, boss)
        assert separado.get_bounding_rect() == hud.boss_bar.rect
        rects.append(hud.boss_bar.rect)
    assert all(superficie.get_rect().contains(r) for r in rects)
    for a, b in combinations(rects, 2):
        assert not a.colliderect(b), (a, b)
    assert hud.status._st_interior.height == 8
    assert vars(player.pocao) == vars(antes.pop('pocao'))
    assert {k: v for k, v in vars(player).items() if k != 'pocao'} == antes
    assert vars(boss) == boss_antes


def test_mensagens_temporizadores_prioridade_limpeza_e_conteudo():
    fonte = FonteRegistrada(Fonte_titulo(18))
    mensagens, superficie = Mensagens(fonte, fonte), tela()
    mensagens.mostrar('Jogo salvo', 180)
    # Prompts de interacao migraram para sprites no mundo (G.1): HUD nao renderiza prompt.
    mensagens.mostrar_prompt('[E] Abrir porta')
    for _ in range(3):
        mensagens.desenhar(superficie)
    assert mensagens._timer_mensagem == 180
    assert 'Jogo salvo' in fonte.textos
    assert '[E] Abrir porta' not in fonte.textos
    assert mensagens.rect_mensagem
    assert not mensagens.rect_prompt
    mensagens.mostrar('Mensagem prioritária', 10)
    for _ in range(9):
        mensagens.atualizar()
    mensagens.desenhar(superficie)
    assert mensagens._cache['mensagem'][1].get_alpha() == 5
    mensagens.atualizar()
    mensagens.desenhar(superficie)
    assert not mensagens.rect_mensagem
    mensagens.limpar_prompt()
    assert mensagens._prompt is None
    mensagens.mostrar('Outra mensagem')
    mensagens.limpar()
    assert mensagens._timer_mensagem == 0

@pytest.mark.parametrize('falha', ['ausente', 'corrompido'])
def test_fallback_e_cache_sem_leitura_escala_ou_render_por_frame(tmp_path, monkeypatch, falha):
    caminho = tmp_path / 'opcional.png'
    if falha == 'corrompido':
        caminho.write_bytes(b'invalido')
    monkeypatch.setattr(trilho_status, 'CAMINHO_TRILHO', caminho)
    monkeypatch.setitem(sprites_itens._MAPA_SPRITES, 2, str(caminho))
    fonte = FonteRegistrada(Fonte_titulo(18))
    notif, barra = NotificacaoItem(fonte), BarraBoss(fonte)
    msg = Mensagens(fonte, fonte)
    superficie, boss = tela(), chefe()
    notif.mostrar(get_item(2), 4)
    msg.mostrar('Mensagem')
    msg.mostrar_prompt('[E] Abrir')
    notif.desenhar(superficie)
    barra.desenhar(superficie, boss)
    msg.desenhar(superficie)

    def proibido(*args, **kwargs):
        pytest.fail('Leitura, escala ou renderização de texto repetida')

    monkeypatch.setattr(pygame.image, 'load', proibido)
    monkeypatch.setattr(pygame.transform, 'scale', proibido)
    monkeypatch.setattr(pygame.transform, 'smoothscale', proibido)
    monkeypatch.setattr(fonte, 'render', proibido)
    for _ in range(60):
        notif.desenhar(superficie)
        barra.atualizar()
        barra.desenhar(superficie, boss)
        msg.atualizar()
        msg.desenhar(superficie)
    assert not any(superficie.get_at((x, 510))[:3] == (255, 0, 255) for x in range(1280))


@pytest.mark.parametrize('componente', ['boss', 'notificacao', 'mensagens'])
def test_clip_do_chamador_preservado(componente):
    superficie = tela()
    clip = pygame.Rect(500, 490, 140, 200)
    superficie.set_clip(clip)
    fonte = Fonte_titulo(18)
    if componente == 'boss':
        BarraBoss(fonte).desenhar(superficie, chefe())
    elif componente == 'notificacao':
        notif = NotificacaoItem(fonte)
        notif.mostrar(get_item(2))
        notif.desenhar(superficie)
    else:
        msg = Mensagens(fonte, fonte)
        # prompts de interacao migraram para sprites no mundo (G.1)
        msg.mostrar('Mensagem')
        clip = pygame.Rect(0, 220, 1280, 120)
        superficie.set_clip(clip)
        msg.desenhar(superficie)
    assert superficie.get_clip() == clip
    assert clip.contains(superficie.get_bounding_rect())
