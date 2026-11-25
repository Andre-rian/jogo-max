"""Regressões de portais, frascos adquiridos e balanceamento da beta.

Fixtures posicionam atores para isolar contratos. O percurso integral separado
em test_beta_final usa somente entradas de teclado desde o spawn inicial.
"""
from collections import defaultdict
from copy import deepcopy
from unittest.mock import patch
import xml.etree.ElementTree as ET

import pygame
import pytest

from core.game_scene import Gamescene
from entities.objetos.item import get_item
from save_manager import Savemaneger
from world.niveis import Conexoes, Drops_fixos, SALAS_BETA


FRASCOS = [(SALAS_BETA[1], 36, 19), (SALAS_BETA[2], 65, 12), (SALAS_BETA[2], 102, 19)]
PASSAGENS = [(sala, lado, destino) for sala in SALAS_BETA
             for lado, destino in Conexoes[sala].items() if destino]


@pytest.fixture
def cena():
    return Gamescene(pygame.Surface((1280, 720)))


def passo(cena, *keys):
    with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {k: True for k in keys})):
        cena.atualizar([])


def coletar_frasco(cena, chave):
    cena._carregar_sala(chave[0])
    cena.inimigos.clear()
    drop = next(d for d in cena.drops if d.chave_fixa == chave)
    cena.player.rect.midbottom = drop.rect.midbottom
    cena.player.vel.xy = (0, 0)
    cena.player.cooldown_interacao = 0
    passo(cena, pygame.K_e)
    assert not drop.ativo
    assert chave in cena.drops_fixos_coletados
    return drop


@pytest.mark.parametrize("origem,lado,destino", PASSAGENS)
def test_cruzar_arco_e_retornar_com_input_sem_rebote(cena, origem, lado, destino):
    cena._carregar_sala(origem)
    cena.inimigos.clear()
    portal = next(r for r, l in cena.passagens if l == lado)
    assert portal.collidelist(cena.mapa.rects_solidos) == -1
    direita = lado == "direita"
    cena.player.rect.midbottom = (portal.left - 45 if direita else portal.right + 45, portal.bottom)
    cena.player.vel.xy = (0, 0)
    for _ in range(100):
        passo(cena, pygame.K_d if direita else pygame.K_a)
        if cena.sala_atual != origem:
            break
    assert cena.sala_atual == destino
    assert cena.player.rect.collidelist(cena.mapa.rects_solidos) == -1
    assert not any(r.collidepoint(cena.player.rect.center) for r, _ in cena.passagens)
    for _ in range(30):
        passo(cena)
    assert cena.sala_atual == destino
    cena.inimigos.clear()
    for _ in range(100):
        passo(cena, pygame.K_a if direita else pygame.K_d)
        if cena.sala_atual != destino:
            break
    assert cena.sala_atual == origem
    assert cena.player.rect.collidelist(cena.mapa.rects_solidos) == -1


@pytest.mark.parametrize("sala,lado,_destino", PASSAGENS)
def test_paredes_altura_errada_e_portal_sem_movimento_nao_transicionam(cena, sala, lado, _destino):
    cena._carregar_sala(sala)
    portal = next(r for r, l in cena.passagens if l == lado)
    cena.player.rect.center = portal.center
    cena.player.vel.x = 0
    cena._checar_transiçao()
    assert cena.sala_atual == sala
    cena.player.rect.centery = portal.top - 64
    cena.player.vel.x = 3 if lado == "direita" else -3
    cena._checar_transiçao()
    assert cena.sala_atual == sala
    cena.player.rect.x = cena.largura_mapa if lado == "direita" else -40
    cena._checar_transiçao()
    assert cena.sala_atual == sala


@pytest.mark.parametrize("sala", SALAS_BETA)
def test_tmx_portais_correspondem_as_conexoes_e_ids_sao_unicos(cena, sala):
    root = ET.parse(f"assets/maps/{sala}.tmx").getroot()
    ids = [int(o.get("id")) for o in root.findall("objectgroup/object")]
    assert len(ids) == len(set(ids)) and int(root.get("nextobjectid")) > max(ids)
    cena._carregar_sala(sala)
    assert sorted(l for _, l in cena.passagens) == sorted(l for l, d in Conexoes[sala].items() if d)


def test_tres_pickups_unicos_sem_pocao_em_baus_e_ecofoco_respeita_capacidade(cena):
    fixos = [(s, c, l) for s in SALAS_BETA for item, c, l in Drops_fixos.get(s, []) if item == 2]
    assert fixos == FRASCOS
    for sala in SALAS_BETA:
        cena._carregar_sala(sala)
        assert not any(b.id_item == 2 for b in cena.baus)
    cena._descansar_fogueira()
    assert cena.player.pocao.cargas == cena.player.pocao.cargas_max == 0
    for numero, chave in enumerate(FRASCOS, 1):
        drop = coletar_frasco(cena, chave)
        assert cena.player.pocao.cargas_max == numero
        assert cena.player.pocao.cargas == 1  # a carga anterior foi gasta abaixo
        assert "2" not in cena.player.inventario["itens"]
        for _ in range(50):
            passo(cena, pygame.K_e)
        assert cena.player.pocao.cargas_max == numero and not drop.ativo
        cena.player.pocao.cargas = 0
        cena._descansar_fogueira()
        assert cena.player.pocao.cargas == numero
        assert not any(d.ativo and d.chave_fixa == chave for d in cena.drops)
        cena.player.pocao.cargas = 0
    assert not cena.player.pocao.obter_frasco()
    for sala in SALAS_BETA:
        cena._carregar_sala(sala)
        assert not any(d.ativo and d.frasco for d in cena.drops)


@pytest.mark.parametrize("quantidade", [0, 1, 2, 3])
def test_capacidade_e_pickups_persistem_em_save_morte_e_retorno(cena, quantidade, tmp_path, monkeypatch):
    for chave in FRASCOS[:quantidade]:
        coletar_frasco(cena, chave)
    sala_checkpoint = SALAS_BETA[2]
    cena._carregar_sala(sala_checkpoint)
    cena.player.defenir_checkpoint(sala_checkpoint, x=3360, y=576)
    cena.player.hp = 60
    cena.player.pocao.cargas = 0
    monkeypatch.setattr("save_manager.CAMINHO_DB", str(tmp_path / "frascos.db"))
    banco = Savemaneger()
    try:
        assert banco.salvar(1, cena)
        nova = Gamescene(cena.tela)
        nova.carregar_save(banco.carregar(1))
    finally:
        banco.fechar()
    assert nova.player.pocao.cargas_max == quantidade and nova.player.pocao.cargas == 0
    assert nova.player.hp == 60
    nova.player.receber_dano(60)
    for _ in range(182):
        passo(nova)
    assert nova.player.vivo and nova.sala_atual == sala_checkpoint
    assert nova.player.pocao.cargas_max == quantidade and nova.player.pocao.cargas == 0
    nova._descansar_fogueira()  # restauração ocorre ao descansar, como no comportamento anterior
    assert nova.player.pocao.cargas == quantidade
    disponiveis = []
    for sala in SALAS_BETA:
        nova._carregar_sala(sala)
        disponiveis.extend(d.chave_fixa for d in nova.drops if d.ativo and d.frasco)
    assert disponiveis == FRASCOS[quantidade:]
    if quantidade < 3:
        coletar_frasco(nova, FRASCOS[quantidade])
        assert nova.player.pocao.cargas_max == quantidade + 1


def test_save_anterior_sem_capacidade_mantem_tres_e_consumiveis(cena):
    inventario = deepcopy(cena.player.inventario)
    inventario["itens"] = {"2": 2}
    cena.carregar_save({"checkpoint_sala": SALAS_BETA[1], "checkpoint_x": 160,
                       "checkpoint_y": 576, "fogueiras_ativas": set(), "bosses_derrotados": set(),
                       "inventario": inventario, "estado_jogador": {
                           "pocoes": 1, "drops": {SALAS_BETA[1]: [
                               {"id_item": 4, "x": 1280, "y": 608,
                                "chave_fixa": [SALAS_BETA[1], 40, 19]}]}}})
    assert cena.player.pocao.cargas_max == 3 and cena.player.pocao.cargas == 1
    assert cena.player.inventario["itens"]["2"] == 2
    assert not any(d.frasco for d in cena.drops)
    assert next(d for d in cena.drops if d.id_item == 4).rect.bottom == 640
    cena._descansar_fogueira()
    assert cena.player.pocao.cargas == 3


@pytest.mark.parametrize("sala", SALAS_BETA[1:3])
def test_pickups_apoiados_sprites_visiveis_e_interacao_alinhada(cena, sala):
    cena._carregar_sala(sala)
    for drop in cena.drops:
        assert drop._sprite_mundo is not None
        sprite = drop._sprite_mundo
        assert sprite.get_bounding_rect().bottom == sprite.get_height()
        assert sprite.get_height() <= 32 and sprite.get_width() <= 32
        assert any(r.top == drop.rect.bottom and r.left <= drop.rect.centerx < r.right
                   for r in cena.mapa.rects_solidos + cena.mapa.rects_plataforma)
        assert drop.interacao.contains(drop.rect)


@pytest.mark.parametrize("sala,tipo,minimo,maximo", [
    (1, "globin", 4, 4), (1, "skeleton", 6, 6),
    (2, "mushroom", 6, 6), (2, "flying_eye", 4, 4), (3, "esqueleto_boss", 20, 20),
])
def test_vida_corresponde_a_golpes_simples_sem_defesa(cena, sala, tipo, minimo, maximo):
    cena._carregar_sala(SALAS_BETA[1])
    next(b for b in cena.baus if b.id_item == 1)._dar_item(cena.player, cena.hud)
    dano = cena.player.calcular_dano("normal")
    assert dano == 25
    cena._carregar_sala(SALAS_BETA[sala])
    inimigo = cena.boss_atual if sala == 3 else next(i for i in cena.inimigos if i.SOM_ID == tipo)
    golpes = 0
    while inimigo.vivo:
        # Fixture sem escudo/i-frames: verifica dano/vida, sem simular a IA.
        inimigo.invencivel = False
        assert inimigo.receber_hit(dano, 1)
        golpes += 1
        assert golpes <= maximo
    assert minimo <= golpes <= maximo


def test_distribuicao_dos_cinco_itens_sem_repeticao(cena):
    obtencoes = []
    for sala in SALAS_BETA:
        cena._carregar_sala(sala)
        obtencoes += [(sala, b.id_item) for b in cena.baus if 6 <= b.id_item <= 10]
        obtencoes += [(sala, d.id_item) for d in cena.drops if 6 <= d.id_item <= 10]
    assert sorted(i for _, i in obtencoes) == [6, 7, 8, 9, 10]
    assert (SALAS_BETA[0], 9) in obtencoes and (SALAS_BETA[1], 6) in obtencoes
    for item_id in (9, 10):
        assert not cena.inventario._opcao_contexto_valida("Equipar", get_item(item_id), cena.player)
