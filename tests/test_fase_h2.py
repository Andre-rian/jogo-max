import pygame
import pytest
import shutil
from types import SimpleNamespace
from pathlib import Path

from core.audio import AudioManager


@pytest.fixture(autouse=True)
def limpar_mixer():
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()
        pygame.mixer.set_num_channels(24)
        pygame.mixer.set_reserved(2)
    yield
    if pygame.mixer.get_init() is not None:
        pygame.mixer.stop()


def test_swing_nao_usa_hit_generico_como_fallback(tmp_path):
    # cria apenas hit gen?rico; sem swing espec?fico/default
    pasta = tmp_path / "assets" / "sons" / "sfx" / "combate" / "generico"
    pasta.mkdir(parents=True)
    (pasta / "hit_01.wav").write_bytes(b"")
    m = AudioManager(raiz=tmp_path)
    assert m.inicializar()
    assert not m.play_swing("arma_inexistente")


def test_passos_sequencia_deterministica(tmp_path):
    pasta = tmp_path / "assets" / "sons" / "sfx" / "player" / "movimento" / "passos" / "pedra"
    pasta.mkdir(parents=True)
    src = Path("assets/sons/sfx/player/movimento/passos/pedra")
    fontes = sorted(src.glob("*.wav"))[:3]
    assert len(fontes) == 3
    for i, fonte in enumerate(fontes, 1):
        shutil.copy2(fonte, pasta / f"movimento_passos_pedra_step_0{i}.wav")
    m = AudioManager(raiz=tmp_path)
    assert m.inicializar()
    tocados = []
    def spy(som, caminho, *args, **kwargs):
        tocados.append(Path(caminho).name)
        return True
    m._tocar_som = spy
    for _ in range(6):
        assert m.play_step("pedra")
    assert tocados == [
        "movimento_passos_pedra_step_01.wav", "movimento_passos_pedra_step_02.wav", "movimento_passos_pedra_step_03.wav",
        "movimento_passos_pedra_step_01.wav", "movimento_passos_pedra_step_02.wav", "movimento_passos_pedra_step_03.wav",
    ]


def test_boss_escudo_bloqueia_frente_mas_nao_costas():
    from entities.monsters.skeleton_boss import EsqueletoBoss
    boss = EsqueletoBoss(100, 100, 500)
    boss._escudo_ativo = True
    boss.olhando_dir = True  # olhando direita
    # atacante à esquerda: direcao_knockback = +1 (costas)
    aplicado_costas = boss.receber_hit(10, 1)
    assert aplicado_costas is True
    boss2 = EsqueletoBoss(100, 100, 500)
    boss2._escudo_ativo = True
    boss2.olhando_dir = True
    # atacante à direita/frente: direcao_knockback = -1
    aplicado_frente = boss2.receber_hit(10, -1)
    assert aplicado_frente is False


def test_inventario_opcao_pausa_abre(monkeypatch):
    from core.game_scene import Gamescene
    aberto = {"v": False}
    cena = SimpleNamespace(
        opcoes_pause=["Continuar", "Invent?rio", "Salvar", "Menu principal", "Sair"],
        ACOES_PAUSA=["continuar", "inventario", "salvar", "menu_principal", "sair"],
        opcao_pausa_selecionada=1,
        _save_callback=None,
        _menu_callback=None,
        pausado=True,
        inventario=SimpleNamespace(aberto=False, abrir=lambda: (setattr(cena.inventario, "aberto", True), aberto.__setitem__("v", True))),
        _fechar_pausa=lambda tocar_som=True: setattr(cena, "pausado", False),
    )
    cena._abrir_inventario_por_pausa = Gamescene._abrir_inventario_por_pausa.__get__(cena, SimpleNamespace)
    cena._ativar_opcao_pausa = Gamescene._ativar_opcao_pausa.__get__(cena, SimpleNamespace)
    cena._ativar_opcao_pausa()
    assert aberto["v"] is True
    assert cena.inventario.aberto is True
    assert cena.pausado is False


def test_inventario_fluxo_completo_pausa_render_fechamento(monkeypatch):
    """Integra??o: gameplay -> pausa -> invent?rio -> render -> fechar."""
    import os, pygame
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    if not pygame.get_init():
        pygame.init()
    from settings import Screen_widht, Screen_height
    pygame.display.set_mode((Screen_widht, Screen_height))
    from core.game_scene import Gamescene
    scene = Gamescene(pygame.display.get_surface())
    # abre pausa
    scene.pausado = True
    scene.opcao_pausa_selecionada = scene.ACOES_PAUSA.index('inventario')
    scene._frame_pausa = 0
    ev = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
    scene.atualizar(ev)
    scene.desenhar()
    assert scene.pausado is False
    assert scene.inventario.aberto is True
    # frame seguinte: invent?rio continua aberto e renderiza
    scene.atualizar([])
    scene.desenhar()
    assert scene.inventario.aberto is True
    # ESC fecha invent?rio
    scene.atualizar([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    scene.desenhar()
    assert scene.inventario.aberto is False
    assert scene.pausado is False


def test_swing_espada_longa_nao_emite_hit_metalico(tmp_path, monkeypatch):
    """Integra??o: swing no ar n?o pode tocar hit met?lico."""
    import os, pygame
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    pygame.mixer.pre_init(44100,-16,2,512)
    if not pygame.get_init():
        pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1,1))
    from core.audio import AudioManager
    a = AudioManager(); assert a.inicializar()
    tocados = []
    orig = a._tocar_som
    def rec(som,caminho,grupo,categoria,volume_base,cooldown,max_inst,ajuste):
        tocados.append(str(caminho))
        return orig(som,caminho,grupo,categoria,volume_base,cooldown,max_inst,ajuste)
    a._tocar_som = rec
    assert a.play_swing('espada_longa')
    assert tocados, 'nenhum som tocado'
    for p in tocados:
        nome = Path(p).name.lower()
        assert 'hit' not in nome
        assert 'swing' in nome or 'default' in nome


def test_passos_pedra_20_consecutivos_curados(monkeypatch):
    """Integra??o: 20 passos no mesmo piso usam apenas subconjunto curado coerente."""
    import os, pygame
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    pygame.mixer.pre_init(44100,-16,2,512)
    if not pygame.get_init():
        pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1,1))
    from core.audio import AudioManager
    a = AudioManager(); assert a.inicializar()
    tocados = []
    orig = a._tocar_som
    def rec(som,caminho,grupo,categoria,volume_base,cooldown,max_inst,ajuste):
        tocados.append(Path(str(caminho)).name)
        return orig(som,caminho,grupo,categoria,volume_base,cooldown,max_inst,ajuste)
    a._tocar_som = rec
    for _ in range(20):
        ok = a.play_step('pedra')
        assert ok, f"passo {_} falhou: disponivel={a.disponivel} init={pygame.mixer.get_init()}"
        a._ultimos['step'] = 0
        pygame.mixer.stop()  # dummy driver mant?m canais ocupados; libera para validar sele??o
    permitidos = {f'movimento_passos_pedra_step_0{i}.wav' for i in range(1,7)}
    assert len(tocados) == 20
    assert set(tocados).issubset(permitidos)
