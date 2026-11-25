"""Contratos dos cinco itens novos da beta final (IDs 6 a 10)."""

import json
import os

import pygame
import pytest

from core.game_scene import Gamescene
from core.inventario import Inventario
from entities.objetos.item import (
    Consumivel,
    Material,
    Registro_Itens,
    Reliquia,
    get_item,
)
from entities.objetos.pocao import Cura_percentual
from entities.player import Player
from save_manager import Savemaneger
from ui import sprites_itens
from ui.icones import desenhar_icone_item

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAMINHO_ITENS = os.path.join(RAIZ, "itens.json")
PASTA_SPRITES = os.path.join(RAIZ, "assets", "sprites", "itens")

ESPERADOS = {
    6: {
        "nome": "Atadura Gasta",
        "tipo": "consumivel",
        "icone": "atadura",
        "descricao": "Um pedaço de linho esquecido nas celas. Ainda pode aliviar ferimentos leves.",
        "sprite": os.path.join("consumiveis", "atadura_gasta.png"),
    },
    7: {
        "nome": "Cinzas de um Eco",
        "tipo": "consumivel",
        "icone": "cinzas",
        "descricao": "Restos de uma lembrança que já não encontra seu dono.",
        "sprite": os.path.join("consumiveis", "cinzas_eco.png"),
    },
    8: {
        "nome": "Lasca de Umbrita",
        "tipo": "material",
        "icone": "lasca_umbrita",
        "descricao": "Um fragmento de minério escuro, capaz de fortalecer o aço quando trabalhado corretamente.",
        "sprite": os.path.join("materiais", "lasca_umbrita.png"),
    },
    9: {
        "nome": "Insígnia do Carcereiro",
        "tipo": "reliquia",
        "icone": "insignia",
        "descricao": "O símbolo de um guarda que serviu ao castelo antes de suas masmorras serem esquecidas.",
        "sprite": os.path.join("reliquias", "insignia_carcereiro.png"),
    },
    10: {
        "nome": "Anel da Vigília",
        "tipo": "reliquia",
        "icone": "anel",
        "descricao": "Dizem que os guardas o utilizavam para suportar as longas noites nas profundezas.",
        "sprite": os.path.join("reliquias", "anel_vigilia.png"),
    },
}


@pytest.fixture(autouse=True)
def cache_limpo():
    sprites_itens.limpar_cache()
    yield
    sprites_itens.limpar_cache()


def _carregar_sem_ids_duplicados():
    def sem_duplicatas(pares):
        resultado = {}
        for chave, valor in pares:
            if chave in resultado:
                raise AssertionError(f"ID duplicado em itens.json: {chave}")
            resultado[chave] = valor
        return resultado

    with open(CAMINHO_ITENS, encoding="utf-8") as arquivo:
        return json.load(arquivo, object_pairs_hook=sem_duplicatas)


def test_ids_unicos_e_sequenciais_sem_reaproveitar_ids_existentes():
    banco = _carregar_sem_ids_duplicados()
    ids = sorted(int(chave) for chave in banco)
    assert ids == list(range(1, 11))
    assert sorted(Registro_Itens) == ids
    assert set(ESPERADOS) == {6, 7, 8, 9, 10}


@pytest.mark.parametrize("item_id", sorted(ESPERADOS))
def test_registro_nome_descricao_e_categoria(item_id):
    esperado = ESPERADOS[item_id]
    item = get_item(item_id)
    assert item is not None
    assert item.id == item_id
    assert item.nome == esperado["nome"]
    assert item.descricao == esperado["descricao"]
    assert item.tipo == esperado["tipo"]
    assert item.icone == esperado["icone"]
    assert Registro_Itens[item_id].nome == esperado["nome"]


@pytest.mark.parametrize("item_id", sorted(ESPERADOS))
def test_sprite_24x24_com_transparencia_carrega_pelo_id(item_id):
    caminho = os.path.join(PASTA_SPRITES, ESPERADOS[item_id]["sprite"])
    assert os.path.isfile(caminho), caminho

    imagem = pygame.image.load(caminho).convert_alpha()
    assert imagem.get_size() == (24, 24)
    assert pygame.mask.from_surface(imagem).count() > 0
    for canto in ((0, 0), (23, 0), (0, 23), (23, 23)):
        assert imagem.get_at(canto).a == 0

    sprite = sprites_itens.obter_sprite_item(item_id)
    assert sprite is not None
    assert sprite.get_size() == (48, 48)
    assert sprites_itens.obter_sprite_de_item(get_item(item_id)) is sprite


def test_precarregamento_inclui_os_cinco_novos_ids():
    sprites_itens.precarregar()
    for item_id in ESPERADOS:
        assert sprites_itens.obter_sprite_item(item_id) is not None


def test_icones_dos_novos_itens_sao_desenhaveis_no_inventario():
    fonte = pygame.font.Font(None, 12)
    for item_id in ESPERADOS:
        tela = pygame.Surface((60, 60), pygame.SRCALPHA)
        desenhar_icone_item(tela, get_item(item_id), 30, 30, 0, 0, 60, fonte)
        assert pygame.mask.from_surface(tela).count() > 0


def test_atadura_cura_menos_que_pocao_e_respeita_vida_maxima():
    p = Player(100, 300)
    p.adicionar_ao_inventario(get_item(6))
    p.adicionar_ao_inventario(get_item(6))
    assert isinstance(get_item(6), Consumivel)

    p.hp = 20
    cura_atadura = int(p.hp_max * 0.12)
    assert cura_atadura < int(p.hp_max * Cura_percentual)
    assert get_item(6).usar(p, p.inventario)
    assert p.hp == 20 + cura_atadura
    assert p.inventario["itens"]["6"] == 1

    p.hp = p.hp_max - 2
    assert get_item(6).usar(p, p.inventario)
    assert p.hp == p.hp_max
    assert "6" not in p.inventario["itens"]

    p.adicionar_ao_inventario(get_item(6))
    p.hp = p.hp_max
    assert not get_item(6).usar(p, p.inventario)
    assert p.inventario["itens"]["6"] == 1


def test_cinzas_concedem_poucos_ecos_e_consomem_uma_unidade_por_uso():
    p = Player(100, 300)
    p.ecos = 0
    for _ in range(2):
        p.adicionar_ao_inventario(get_item(7))

    assert get_item(7).efeito == "ecos"
    assert p.inventario["itens"]["7"] == 2
    assert get_item(7).usar(p, p.inventario)
    assert p.ecos == 5
    assert p.inventario["itens"]["7"] == 1
    assert get_item(7).usar(p, p.inventario)
    assert p.ecos == 10
    assert "7" not in p.inventario["itens"]
    assert not hasattr(p, "ecos_cinzas")


def test_consumiveis_novos_funcionam_pela_acao_real_do_inventario():
    inventario = Inventario(None)
    p = Player(100, 300)
    p.hp = 10
    p.ecos = 3
    for item_id in (6, 7):
        p.adicionar_ao_inventario(get_item(item_id))

    assert inventario._opcao_contexto_valida("Usar", get_item(6), p)
    inventario._executar_opcao("Usar", get_item(6), p)
    assert p.hp == 10 + int(p.hp_max * 0.12)

    inventario._executar_opcao("Usar", get_item(7), p)
    assert p.ecos == 8
    assert p.inventario["itens"] == {}


def test_lasca_de_umbrita_e_material_empilhavel_sem_botao_de_uso():
    item = get_item(8)
    assert isinstance(item, Material)
    assert not hasattr(item, "efeito")

    p = Player(100, 300)
    p.adicionar_ao_inventario(item)
    p.adicionar_ao_inventario(get_item(8))
    assert p.inventario["materiais"]["8"] == 2

    inventario = Inventario(None)
    inventario.aba_atual = 3
    lasca = next(i for i in inventario._itens_da_aba(p) if i.id == 8)
    assert lasca.quantidade == 2
    assert not inventario._opcao_contexto_valida("Usar", lasca, p)


def test_reliquias_aparecem_no_inventario_e_nao_sao_equipaveis():
    p = Player(100, 300)
    for item_id in (9, 10):
        item = get_item(item_id)
        assert isinstance(item, Reliquia)
        p.adicionar_ao_inventario(item)
        p.adicionar_ao_inventario(get_item(item_id))
        assert p.inventario["chaves"].count(item_id) == 1

    inventario = Inventario(None)
    inventario.aba_atual = 2
    itens = inventario._itens_da_aba(p)
    assert [item.id for item in itens] == [9, 10]
    assert [item.nome for item in itens] == [
        "Insígnia do Carcereiro", "Anel da Vigília"
    ]
    for item in itens:
        assert item.descricao
        assert sprites_itens.obter_sprite_de_item(item) is not None
        assert not inventario._opcao_contexto_valida("Equipar", item, p)
        assert not inventario._opcao_contexto_valida("Usar", item, p)
        inventario._executar_opcao("Equipar", item, p)
        assert p.inventario["mao_direita"] is None
        assert p.resistencia == Player.RESISTENCIA_INICIAL


def test_persistencia_dos_novos_ids_e_compatibilidade_com_save_antigo(tmp_path, monkeypatch):
    monkeypatch.setattr("save_manager.CAMINHO_DB", str(tmp_path / "novos_itens.db"))
    banco = Savemaneger()
    try:
        cena = Gamescene(pygame.Surface((640, 360)))
        p = cena.player
        p.ecos = 31
        p.adicionar_ao_inventario(get_item(6))
        p.adicionar_ao_inventario(get_item(7))
        p.adicionar_ao_inventario(get_item(8))
        p.adicionar_ao_inventario(get_item(9))
        p.adicionar_ao_inventario(get_item(10))
        assert banco.salvar(1, cena)

        dados = banco.carregar(1)
        assert dados["inventario"]["itens"] == {"6": 1, "7": 1}
        assert dados["inventario"]["materiais"] == {"8": 1}
        assert dados["inventario"]["chaves"] == [9, 10]

        nova = Gamescene(pygame.Surface((640, 360)))
        nova.carregar_save(dados)
        assert nova.player.inventario == p.inventario
        assert nova.player.ecos == 31

        legado = dict(dados)
        legado["inventario"] = {
            "mao_direita": None,
            "mao_esquerda": None,
            "armadura": None,
            "equipamentos": [],
            "itens": {"2": 1},
            "chaves": [],
            "materiais": {"5": 2},
        }
        antiga = Gamescene(pygame.Surface((640, 360)))
        antiga.carregar_save(legado)
        antiga.player.adicionar_ao_inventario(get_item(6))
        antiga.player.adicionar_ao_inventario(get_item(10))
        assert antiga.player.inventario["itens"] == {"2": 1, "6": 1}
        assert antiga.player.inventario["materiais"] == {"5": 2}
        assert antiga.player.inventario["chaves"] == [10]
    finally:
        banco.fechar()


def test_itens_existentes_nao_regrediram():
    existentes = {
        1: ("Espada Longa", "arma"),
        2: ("Poção de vida", "consumivel"),
        3: ("Machado de Guerra", "arma"),
        4: ("Raiz Amarga", "consumivel"),
        5: ("Umbrita", "material"),
    }
    for item_id, (nome, tipo) in existentes.items():
        item = get_item(item_id)
        assert item.nome == nome
        assert item.tipo == tipo
        assert sprites_itens.obter_sprite_item(item_id) is not None

    p = Player(100, 300)
    p.hp = 20
    p.adicionar_ao_inventario(get_item(2))
    assert get_item(2).usar(p, p.inventario)
    assert p.hp == 20 + int(p.hp_max * Cura_percentual)

    p.adicionar_ao_inventario(get_item(4))
    assert get_item(4).usar(p, p.inventario)
    assert p.buff_stamina_duracao == 180
    assert p.buff_stamina_valor == 2.0
