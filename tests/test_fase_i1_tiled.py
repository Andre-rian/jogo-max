import os

from world.tile_map import TileMap
from world.validacao_tiled import validar_conexoes, validar_mapas_diretorio


RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAPAS = os.path.join(RAIZ, "assets", "maps")


def test_carregamento_salas_existentes_tmx():
    dimensoes_esperadas = {
        "calabouco_1.tmx": (56, 23),
        "calabouco_2.tmx": (80, 23),
    }
    for nome, (largura, altura) in dimensoes_esperadas.items():
        caminho = os.path.join(MAPAS, nome)
        colisao = TileMap.carregar_camada_tmx(caminho, "colisao")
        assert colisao is not None
        assert len(colisao) == altura
        assert len(colisao[0]) == largura

        objetos = TileMap.carregar_objetos_tmx(caminho, "objetos")
        assert isinstance(objetos, list)

        # Camadas opcionais ausentes devem ser toleradas sem exception
        camada_opt = TileMap.carregar_camada_tmx(caminho, "decoracao", obrigatoria=False)
        assert camada_opt is None or isinstance(camada_opt, list)


def test_template_tiled_tem_convencoes_basicas():
    caminho = os.path.join(MAPAS, "_template.tmx")
    texto = open(caminho, encoding="utf-8").read()
    for trecho in ["objectgroup", "name=\"objetos\"", "spawn", "inimigo", "tipo/type", "colisao"]:
        assert trecho.lower() in texto.lower()


def test_normalizacao_objetos_spawn_spwan_e_tipo_type():
    caminho = os.path.join(MAPAS, "calabouco_1.tmx")
    objetos = TileMap.carregar_objetos_tmx(caminho, "objetos")
    spawns = [o for o in objetos if o["tipo"] == "spawn"]
    assert spawns  # spwan legado normalizado

    inimigos = [o for o in objetos if o["tipo"] == "inimigo"]
    ids = {o["id"] for o in inimigos}
    assert 8 in ids  # inimigo corrigido/não deve ser perdido
    obj8 = next(o for o in inimigos if o["id"] == 8)
    assert obj8["propriedades"].get("tipo") == "skeleton"
    assert obj8["propriedades"].get("type") == "skeleton"


def test_ecofoco_experimental_sala_2_preservado():
    caminho = os.path.join(MAPAS, "calabouco_2.tmx")
    objetos = TileMap.carregar_objetos_tmx(caminho, "objetos")
    fogueiras = [o for o in objetos if o["tipo"] == "fogueira"]
    alvo = next(o for o in fogueiras if o.get("nome") == "Ecofoco experimental")
    assert alvo["col"] == 8
    assert alvo["linha"] == 20
    assert alvo["id"] == 4


def test_validacao_tiled_nao_reporta_erros_para_mapas_atuais():
    problemas = validar_mapas_diretorio(MAPAS)
    erros = [p for p in problemas if p.nivel == "erro"]
    assert erros == [], "\n".join(str(p) for p in problemas)


def test_validacao_conexoes_atuais_ok():
    assert validar_conexoes() == []
