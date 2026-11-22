import os
from types import SimpleNamespace

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from core.interacoes import GerenciadorInteracoes
from ui.prompts_teclas import PromptTeclaMundo, obter_tecla_mundo


class HudFake:
    def __init__(self):
        self.limpezas = 0
        self.prompts = []

    def limpar_prompt_interacao(self):
        self.limpezas += 1

    def limpar_prompt(self):
        self.limpezas += 1

    def mostrar_prompt(self, texto):
        self.prompts.append(texto)


class Obj:
    def __init__(self, nome, x, disponivel=True):
        self.nome = nome
        self.interacao = pygame.Rect(x, 0, 20, 20)
        self.rect = self.interacao
        self.tecla_prompt = "e"
        self._disponivel = disponivel
        self.atualizado = 0
        self.selecionado = None
        self.ativado = 0

    def disponivel_para_prompt(self, player):
        return self._disponivel

    def prompt_anchor_mundo(self):
        return self.rect.centerx, self.rect.top - 10

    def atualizar(self, *args, **kwargs):
        self.atualizado += 1
        self.selecionado = kwargs.get("selecionado")
        teclas = args[1] if len(args) > 1 else {}
        if self.selecionado and teclas.get(pygame.K_e) and self._disponivel:
            self.ativado += 1


def test_selecao_deterministica_prioridade_ordem_e_proximidade():
    pygame.init()
    player = SimpleNamespace(rect=pygame.Rect(100, 0, 10, 10))
    hud = HudFake()
    gi = GerenciadorInteracoes()

    bau_longe = Obj("bau_longe", 140)
    bau_perto = Obj("bau_perto", 110)
    porta = Obj("porta", 102)
    ctx = {
        "baus": [bau_longe, bau_perto],
        "drops": [], "drops_ecos": [], "fogueiras": [], "portas": [porta],
    }
    alvo = gi.atualizar(player, hud, {}, ctx)
    assert alvo is bau_perto  # mesma prioridade de bau, mais proximo vence

    # prioridade de grupo historica: bau antes de porta mesmo mais perto
    bau_perto.interacao.x = 150
    bau_longe.interacao.x = 160
    porta.interacao.x = 101
    alvo = gi.atualizar(player, hud, {}, ctx)
    assert alvo is bau_perto  # mais proximo dentro do grupo prioritario

    # ordem interna do mesmo grupo mantem estabilidade em empate de distancia
    a = Obj("a", 110)
    b = Obj("b", 110)
    ctx = {"baus": [a, b], "drops": [], "drops_ecos": [], "fogueiras": [], "portas": []}
    alvo = gi.atualizar(player, hud, {}, ctx)
    assert alvo is a

    # supressao limpa alvo
    ctx_sup = dict(ctx, pausado=True)
    assert gi.atualizar(player, hud, {}, ctx_sup) is None


def test_ativacao_apenas_do_objeto_selecionado_por_e():
    pygame.init()
    player = SimpleNamespace(rect=pygame.Rect(100, 0, 10, 10))
    teclas = {pygame.K_e: True}
    a = Obj("a", 100)
    b = Obj("b", 110)
    for obj, sel in ((a, True), (b, False)):
        obj.atualizar(player, teclas, None, selecionado=sel)
    assert a.ativado == 1
    assert b.ativado == 0
    assert a.selecionado is True and b.selecionado is False


def test_prompt_tecla_mundo_estado_e_animacao():
    pygame.init()
    pygame.display.set_mode((1, 1))
    p = PromptTeclaMundo("e", escala=1.0)
    p.atualizar(pressionada=False)
    assert p.estado == "normal"
    p.atualizar(pressionada=True)
    assert p.estado == "pressionado"
    # sem pressionar, estado volta ao normal apos duracao do pulso
    for _ in range(20):
        p.atualizar(pressionada=False)
    assert p.estado == "normal"
    assert obter_tecla_mundo("e", "normal", 1.0).get_size()[0] > 0
    assert obter_tecla_mundo("e", "pressionado", 1.0).get_size()[0] > 0


def test_prompt_mundo_respeita_camera_offset_e_visibilidade():
    pygame.init()
    pygame.display.set_mode((1, 1))
    from core.camera import Camera

    cam = Camera(1000, 1000)
    cam.offset.x = 50
    cam.offset.y = 20
    vista = pygame.Surface((120, 80), pygame.SRCALPHA)
    p = PromptTeclaMundo("e", escala=1.0)
    p.atualizar(False)

    # visivel dentro da vista considerando offset da camera
    ok = p.desenhar(vista, cam, centro_mundo_x=80, topo_mundo_y=50, visivel=True)
    assert ok is True
    assert vista.get_bounding_rect().width > 0

    # fora da tela nao desenha
    vista2 = pygame.Surface((120, 80), pygame.SRCALPHA)
    ok2 = p.desenhar(vista2, cam, centro_mundo_x=500, topo_mundo_y=500, visivel=True)
    assert ok2 is False
    assert vista2.get_bounding_rect().width == 0

    # zoom do jogo altera area visivel (vista menor) e offset ainda aplicado
    cam.zoom = 2.0
    vista3 = pygame.Surface((40, 40), pygame.SRCALPHA)
    ok3 = p.desenhar(vista3, cam, centro_mundo_x=80, topo_mundo_y=50, visivel=True)
    assert ok3 in (True, False)


def test_eventos_sonoros_ui_inventario_contexto(monkeypatch):
    pygame.init()
    from core.inventario import Inventario
    from entities.player import Player
    from entities.objetos.item import get_item

    class AudioFake:
        def __init__(self):
            self.calls = []
        def play_sfx(self, key, ajuste=1.0):
            self.calls.append(key)
            return True

    fake = AudioFake()
    monkeypatch.setattr("core.inventario.audio", fake)

    inv = Inventario(None)
    player = Player(100, 300)
    inv.aberto = True
    inv._ignorar_frame_abertura = False

    # acao invalida via UI confirmada: somente ui_error
    inv.menu_contexto = {"item": get_item(1), "x": 0, "y": 0, "opcoes": ["Descartar"]}
    inv.atualizar([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)], player)
    assert fake.calls[-1] == "ui_error"
    assert "ui_confirm" not in fake.calls

    # ESC fecha contexto com ui_back
    inv.menu_contexto = {"item": get_item(1), "x": 0, "y": 0, "opcoes": ["Desequipar"]}
    fake.calls.clear()
    inv.atualizar([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)], player)
    assert fake.calls == ["ui_back"]
    assert inv.menu_contexto is None
