"""F.2: dados reais, legibilidade, fallback e integração da HUD."""
import copy
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from entities.objetos.pocao import Pocao
from ui import sprites_itens
from ui.estilo import Fonte_texto, Fonte_titulo
from ui.hud import ecos, trilho_status
from ui.hud.hud import Hud
from ui.hud.pocao import SlotPocao


class FonteRegistrada:
    def __init__(self, fonte):
        self.fonte = fonte
        self.textos = []

    def render(self, texto, *args):
        self.textos.append(texto)
        return self.fonte.render(texto, *args)

    def __getattr__(self, nome):
        return getattr(self.fonte, nome)


def jogador(**valores):
    dados = dict(hp=200, hp_max=200, stamina=130, stamina_max=130,
                 stamina_delay=0, _frame_atual=0, buff_stamina_duracao=0,
                 pocao=Pocao(), ecos=0, inventario={'itens': {2: 999}})
    dados.update(valores)
    return SimpleNamespace(**dados)


def estado(p):
    campos = ('hp', 'hp_max', 'stamina', 'stamina_max', 'stamina_delay',
              '_frame_atual', 'buff_stamina_duracao', 'ecos', 'inventario')
    return copy.deepcopy({**{c: getattr(p, c) for c in campos}, 'pocao': vars(p.pocao)})


@pytest.fixture(autouse=True)
def caches():
    sprites_itens.limpar_cache()
    ecos._obter_icone.cache_clear()
    trilho_status.limpar_cache()
    yield
    sprites_itens.limpar_cache()
    ecos._obter_icone.cache_clear()
    trilho_status.limpar_cache()


@pytest.mark.parametrize('cargas', [3, 1, 0])
def test_pocao_mostra_cargas_reais_e_tecla_sem_ler_estoque(cargas):
    fonte = FonteRegistrada(Fonte_texto(14))
    slot = SlotPocao(fonte)
    p = jogador()
    p.pocao.cargas = cargas
    p.pocao._colldown = 42
    antes = estado(p)
    tela = pygame.Surface((1280, 720), pygame.SRCALPHA)
    slot.desenhar(tela, p)
    assert fonte.textos == ['POÇÃO', 'F', 'POÇÃO', 'F', f'{cargas} / 3']
    assert estado(p) == antes
    assert tela.get_bounding_rect() == pygame.Rect(20, 636, 148, 64)
    assert pygame.image.tobytes(slot._icone, 'RGBA') != pygame.image.tobytes(slot._icone_vazio, 'RGBA')


def test_uso_real_cura_cooldown_e_flash_duram_os_mesmos_ticks():
    hud = Hud()
    tela = pygame.Surface((1280, 720))
    p = jogador(hp=40)
    hud.desenhar(tela, p)
    assert p.pocao.usar(p)
    assert (p.hp, p.pocao.cargas, p.pocao._colldown) == (120, 2, 90)
    hud.desenhar(tela, p)
    assert hud.pocao_slot._flash_da_pocao == 12
    antes = estado(p)
    com_flash = tela.subsurface((20, 636, 148, 64)).copy()
    for _ in range(11):
        hud.atualizar()
        hud.desenhar(tela, p)
    assert hud.pocao_slot._flash_da_pocao == 1
    hud.atualizar()
    hud.desenhar(tela, p)
    assert hud.pocao_slot._flash_da_pocao == 0
    assert estado(p) == antes
    assert not p.pocao.usar(p)
    assert estado(p) == antes
    assert pygame.image.tobytes(com_flash, 'RGB') != pygame.image.tobytes(
        tela.subsurface((20, 636, 148, 64)), 'RGB')
    for _ in range(90):
        p.pocao.atualizar()
    assert p.pocao.usar(p)
    assert (p.hp, p.pocao.cargas, p.pocao._colldown) == (200, 1, 90)
    hud.flash_pocao()
    assert hud.pocao_slot._flash_da_pocao == 12


def test_recarga_ou_troca_de_player_nao_inicia_flash():
    slot = SlotPocao(Fonte_texto(14))
    tela = pygame.Surface((1280, 720))
    p = jogador()
    p.pocao.cargas = 1
    slot.desenhar(tela, p)
    p.pocao.recarregar()
    slot.desenhar(tela, p)
    p.pocao = Pocao()
    p.pocao.cargas = 0
    p.pocao._colldown = 90
    slot.desenhar(tela, p)
    assert slot._flash_da_pocao == 0
    slot.desenhar(tela, SimpleNamespace())


@pytest.mark.parametrize('tamanho', [(320, 240), (640, 480), (1280, 720), (1920, 1080)])
@pytest.mark.parametrize('quantidade', [0, 137, 1234567890123456789, 10**59 + 123])
def test_ecos_todos_os_digitos_dentro_da_tela_e_dados_intactos(tamanho, quantidade):
    fonte = FonteRegistrada(Fonte_titulo(18, negrito=True))
    contador = ecos.IndicadorEcos(fonte)
    tela = pygame.Surface(tamanho, pygame.SRCALPHA)
    p = jogador(ecos=quantidade)
    antes = estado(p)
    contador.desenhar(tela, p)
    assert ''.join(fonte.textos) == str(quantidade)
    assert estado(p) == antes
    caixa = tela.get_bounding_rect()
    assert tela.get_rect().inflate(-40, -40).contains(caixa)
    assert caixa.right == tamanho[0] - 20
    assert caixa.bottom == tamanho[1] - 20
    for texto in contador._linhas:
        assert texto.get_width() <= contador._painel.get_width() - 80


def test_sprite_eco_copia_exata_da_arte_aprovada_e_pocao_em_2x():
    raiz = Path(__file__).resolve().parents[1]
    assert ecos.CAMINHO_ECO.read_bytes() == (raiz / 'docs/arte/propostas_recursos/eco_profano_d1.png').read_bytes()
    eco = ecos._obter_icone()
    assert eco.get_size() == (24, 24)
    assert pygame.mask.from_surface(eco).count() == 196
    origem = pygame.image.load(sprites_itens._MAPA_SPRITES[2])
    esperado = pygame.transform.scale(origem, (48, 48))
    slot = SlotPocao(Fonte_texto(14))
    assert pygame.image.tobytes(slot._icone, 'RGBA') == pygame.image.tobytes(esperado, 'RGBA')


@pytest.mark.parametrize('falha', ['ausente', 'corrompido', 'dimensao'])
def test_fallbacks_sem_placeholder_ou_novas_leituras(tmp_path, monkeypatch, falha):
    caminho = tmp_path / 'sprite.png'
    if falha == 'corrompido':
        caminho.write_bytes(b'imagem invalida')
    elif falha == 'dimensao':
        pygame.image.save(pygame.Surface((1, 1)), caminho)
    monkeypatch.setitem(sprites_itens._MAPA_SPRITES, 2, str(caminho))
    monkeypatch.setattr(ecos, 'CAMINHO_ECO', caminho)
    monkeypatch.setattr(trilho_status, 'CAMINHO_TRILHO', caminho)
    hud = Hud()
    assert hud.ecos._icone is None
    assert pygame.image.tobytes(hud.pocao_slot._icone, 'RGBA') == pygame.image.tobytes(
        SlotPocao._frasco_procedural(), 'RGBA')

    def proibido(*args, **kwargs):
        pytest.fail('Leitura ou escala repetida durante a renderização')

    monkeypatch.setattr(pygame.image, 'load', proibido)
    monkeypatch.setattr(pygame.transform, 'scale', proibido)
    monkeypatch.setattr(pygame.transform, 'smoothscale', proibido)
    # Falhas ficam em cache também entre instâncias.
    outro = Hud()
    for objeto in (hud, outro):
        tela = pygame.Surface((1280, 720))
        p = jogador(hp=40, stamina=0, stamina_delay=10, buff_stamina_duracao=60)
        p.pocao.cargas = 0
        antes = estado(p)
        for _ in range(60):
            objeto.atualizar()
            objeto.desenhar(tela, p)
        assert estado(p) == antes
        assert not any(tela.get_at((x, 670))[:3] == (255, 0, 255) for x in range(1280))


def test_cache_clip_e_animacao_com_assets(monkeypatch):
    fonte = FonteRegistrada(Fonte_titulo(18, negrito=True))
    contador = ecos.IndicadorEcos(fonte)
    slot = SlotPocao(fonte)
    tela = pygame.Surface((1280, 720), pygame.SRCALPHA)
    p = jogador(ecos=987654321)
    contador.desenhar(tela, p)
    slot.desenhar(tela, p)
    assert contador._efeito.get_at((32, 14)).a > 0  # Halo preservado sobre RGBA.
    renderizados = fonte.textos.copy()

    def proibido(*args, **kwargs):
        pytest.fail('Leitura, escala ou texto repetido a cada frame')

    monkeypatch.setattr(pygame.image, 'load', proibido)
    monkeypatch.setattr(pygame.transform, 'scale', proibido)
    monkeypatch.setattr(pygame.transform, 'smoothscale', proibido)
    monkeypatch.setattr(fonte, 'render', proibido)
    primeiro = pygame.image.tobytes(tela, 'RGBA')
    for _ in range(60):
        tela.fill((0, 0, 0, 0))
        contador.desenhar(tela, p)
        slot.desenhar(tela, p)
    assert contador._frame_hud == 61
    assert fonte.textos == renderizados
    assert pygame.image.tobytes(tela, 'RGBA') != primeiro
    tela.fill((0, 0, 0, 0))
    tela.set_clip((1100, 650, 100, 40))
    contador.desenhar(tela, p)
    slot.desenhar(tela, p)
    assert tela.get_clip() == pygame.Rect(1100, 650, 100, 40)
    assert tela.get_clip().contains(tela.get_bounding_rect())


@pytest.mark.parametrize('chefe', [False, True])
def test_cena_real_exploracao_e_combate_sem_lygame(tmp_path, monkeypatch, chefe):
    from core.game_scene import Gamescene
    from entities.objetos.item import get_item
    from ui import painel_lygame

    monkeypatch.setattr(trilho_status, 'CAMINHO_TRILHO', tmp_path / 'ausente.png')
    monkeypatch.setattr(painel_lygame, 'disponivel', lambda: False)
    tela = pygame.Surface((1280, 720))
    cena = Gamescene(tela)
    if chefe:
        cena._carregar_sala('calabouço_5', posiçao_spwan=(4, 8))
        cena.player.equipar(get_item(1))
        boss = cena.boss_atual
        cena.player.rect.midbottom = (boss.rect.centerx - 100, boss.rect.bottom)
        cena.player._disparar_ataque(False)
    for _ in range(14):
        cena.atualizar([])
    if chefe:
        assert cena.boss_atual.hp < cena.boss_atual.hp_max
    antes = estado(cena.player)
    boss_antes = cena.boss_atual.hp if chefe else None
    for _ in range(3):
        cena.desenhar()
    assert estado(cena.player) == antes
    assert not chefe or cena.boss_atual.hp == boss_antes
