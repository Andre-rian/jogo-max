from types import SimpleNamespace
import pygame
import pytest
from ui.hud.status import BarrasStatus
from ui.hud import trilho_status as trilho


def player(**kwargs):
    dados = dict(hp=200, hp_max=200, stamina=130, stamina_max=130,
                 stamina_delay=0, _frame_atual=0, buff_stamina_duracao=0)
    dados.update(kwargs)
    return SimpleNamespace(**dados)


def draw(p, **kwargs):
    tela = pygame.Surface((1280, 720))
    tela.fill((50, 60, 70))
    BarrasStatus(pygame.font.Font(None, 14), **kwargs).desenhar(tela, p)
    return tela


@pytest.fixture(autouse=True)
def caches():
    trilho.limpar_cache()
    yield
    trilho.limpar_cache()


@pytest.mark.parametrize('altura', [6, 8, 10])
@pytest.mark.parametrize('ratio', [0, .1, .5, 1, 2, -.1])
def test_preenchimento_limitado_borda_persistente_sem_mutar_player(altura, ratio):
    p = player(hp=200*ratio, stamina=130*ratio)
    antes = vars(p).copy()
    s = draw(p, altura_stamina=altura, usar_asset=False)
    assert vars(p) == antes
    assert s.get_at((33, 74))[:3] == trilho.BORDA
    assert s.get_at((282, 76))[:3] == trilho.BORDA
    assert s.get_at((35, 76+altura))[:3] == trilho.CONTORNO
    n = int(246*max(0,min(1,ratio)))
    assert sum(s.get_at((x,76))[:3] == (68,153,125) for x in range(35,281)) == n
    hp_cor = (184,51,65) if max(0,min(1,ratio)) > .3 else (200,30,40)
    assert sum(s.get_at((x,50))[:3] == hp_cor for x in range(35,281)) == n
    assert s.get_at((282,50))[:3] == trilho.BORDA
    assert s.get_at((296, 76))[:3] == (50,60,70)


def test_maximo_zero_e_clip_do_chamador():
    s = draw(player(hp_max=0,stamina_max=0), usar_asset=False)
    assert s.get_at((35,76))[:3] == trilho.FUNDO
    hud = BarrasStatus(pygame.font.Font(None,14), usar_asset=False)
    s.set_clip((10,10,100,100))
    hud.desenhar(s,player())
    assert s.get_clip() == pygame.Rect(10,10,100,100)


@pytest.mark.parametrize('corrompido',[False, True])
def test_fallback_real_ausente_ou_corrompido(tmp_path, monkeypatch, corrompido):
    caminho = tmp_path/'ProgressTrack.png'
    if corrompido:
        caminho.write_text('imagem inválida')
    monkeypatch.setattr(trilho,'CAMINHO_TRILHO',caminho)
    atual = draw(player())
    esperado = draw(player(),usar_asset=False)
    assert pygame.image.tobytes(atual,'RGB') == pygame.image.tobytes(esperado,'RGB')


def test_cache_nao_carrega_ou_escala_durante_frames(monkeypatch):
    chamadas=[]
    def carregar(*args, **kwargs):
        chamadas.append(1)
        return pygame.Surface((1,1))
    monkeypatch.setattr(trilho,'carregar_imagem',carregar)
    hud = BarrasStatus(pygame.font.Font(None,14))
    assert len(chamadas)==1
    def proibido(*a, **k):
        pytest.fail('I/O ou escala durante renderização')
    monkeypatch.setattr(trilho,'carregar_imagem',proibido)
    monkeypatch.setattr(pygame.transform,'scale',proibido)
    monkeypatch.setattr(pygame.transform,'smoothscale',proibido)
    s=pygame.Surface((1280,720))
    for frame in range(60):
        hud.desenhar(s,player(stamina=frame,_frame_atual=frame))


def test_sinalizacao_buff_e_espera_preserva_condicoes():
    base=draw(player(stamina=0),usar_asset=False)
    espera=draw(player(stamina=0,stamina_delay=10),usar_asset=False)
    apagado=draw(player(stamina=0,stamina_delay=10,_frame_atual=10),usar_asset=False)
    buff=draw(player(stamina=0,buff_stamina_duracao=1),usar_asset=False)
    raw=lambda s: pygame.image.tobytes(s,'RGB')
    assert raw(base)==raw(apagado)
    assert raw(base)!=raw(espera)
    assert base.get_at((40,88)) != buff.get_at((40,88))
    assert raw(draw(player(stamina_delay=10),usar_asset=False)) == raw(draw(player(),usar_asset=False))


def test_asset_local_margens_e_composicao_pixel_perfect():
    if not trilho.CAMINHO_TRILHO.exists():
        pytest.skip('Pack restrito opcional não instalado')
    src=pygame.image.load(str(trilho.CAMINHO_TRILHO))
    assert src.get_size()==(48,12)
    for y in range(12):
        assert all(src.get_at((x,y))==src.get_at((24,y)) for x in range(3,45))
    origem=trilho._origem()
    for altura in (6,8,10):
        s=trilho.obter_trilho(252,altura)
        for y in range(altura+6):
            sy=y if y<3 else (9+y-(altura+3) if y>=altura+3 else 3)
            for x,sx in [(0,0),(1,1),(2,2),(3,24),(248,24),(249,45),(250,46),(251,47)]:
                assert s.get_at((x,y))==origem.get_at((sx,sy))
