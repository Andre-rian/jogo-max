"""Gera somente os três TMX novos da beta; não modifica mapas anteriores."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]


def gerar(nome, titulo, largura, fase):
    altura, piso = 24, 20
    root = ET.Element("map", version="1.10", tiledversion="1.12.2",
                      orientation="orthogonal", renderorder="right-down",
                      width=str(largura), height=str(altura), tilewidth="32", tileheight="32",
                      infinite="0", backgroundcolor="#0b0d18")
    props = ET.SubElement(root, "properties")
    ET.SubElement(props, "property", name="titulo", value=titulo)
    ET.SubElement(props, "property", name="fase", value=str(fase))
    base = ET.parse(RAIZ / "assets/maps/bloco_celas_esquecidas.tmx").getroot()
    for ts in base.findall("tileset"):
        root.append(deepcopy(ts))
    grids = {n: [[0] * largura for _ in range(altura)] for n in
             ("fundo", "decoracao_fundo", "escadas", "plataformas", "colisao", "decoracao")}
    for y in range(altura):
        for x in range(largura):
            grids["fundo"][y][x] = 430 if (x * 17 + y * 7) % 5 == 0 else 429
            if y >= piso or y <= 2:
                grids["colisao"][y][x] = 1859 if y == piso else 1821 + (x + y) % 2
            if x in (0, largura - 1) and (y < piso - 3 or fase == 4 and x == largura - 1):
                grids["colisao"][y][x] = 1821

    def desenho(x, y, gids, camada="decoracao_fundo"):
        for dy, row in enumerate(gids):
            for dx, gid in enumerate(row):
                grids[camada][y + dy][x + dx] = gid

    def galeria(x, y, fim):
        for col in range(x - 2, fim):
            grids["plataformas"][y][col] = 2595
        # A física limita o TOPO do rect ao topo da escada: dois tiles acima
        # do patamar permitem apoiar os pés e sair lateralmente da escalada.
        for row in range(y - 2, piso):
            grids["escadas"][row][x] = 2628 if row == y - 2 else 2598

    objetos = ET.Element("objectgroup", id="7", name="objetos")

    def objeto(classe_objeto, x, y, nome="", **propriedades):
        obj = ET.SubElement(objetos, "object", id=str(len(objetos) + 1), name=nome,
                            type=classe_objeto, x=str(x * 32), y=str(y * 32), width="0", height="0")
        if propriedades:
            p = ET.SubElement(obj, "properties")
            for chave, valor in propriedades.items():
                ET.SubElement(p, "property", name=chave, value=str(valor))

    def inimigo(tipo, col, linha, esq=0, direita=0):
        objeto("inimigo", col, linha, tipo, tipo=tipo,
               patrulha_esq=esq * 32, patrulha_dir=direita * 32)

    for name, x in (("default", 3), ("esquerda", 3), ("direita", largura - 4)):
        objeto("spawn", x, piso - 2, name)
    # Ruínas e correntes do atlas já usado pelas celas. Nenhum sprite novo.
    for x in range(7, largura - 8, 15):
        desenho(x, 8, [[7107], [7115]])
        desenho(x + 3, 4, [[2640], [2655]])
        desenho(x + 5, piso - 1, [[2648, 2649]], "decoracao")
    for x in range(6, largura - 3, 14 if fase == 3 else 10):
        objeto("tocha", x, 15, variante="fraca" if fase == 3 else "forte")

    if fase == 2:
        objeto("bau", 10, 19, "Primeira espada", id_item=1)
        inimigo("skeleton", 29, 18, 28, 33)
        inimigo("globin", 51, 18, 49, 55)
        galeria(38, 15, 46)
        objeto("bau", 43, 14, "Reserva do arsenal", id_item=2)
        # Caixas e suportes de madeira, com armas/armaduras do atlas medieval.
        for x in (15, 18, 24, 58, 62):
            desenho(x, 19, [[2603]], "decoracao")
        for x in (12, 22, 57):
            desenho(x, 17, [[2594, 2595, 2596], [2609, 2610, 2611]])
            desenho(x + 1, 18, [[1139], [1177]])
    elif fase == 3:
        galeria(23, 14, 30)
        galeria(62, 13, 73)
        for x in range(34, 47):
            topo = 18 if 38 <= x < 43 else 19
            for y in range(topo, piso):
                grids["colisao"][y][x] = 1859 if y == topo else 1821
        inimigo("globin", 19, 18, 17, 21)
        inimigo("skeleton", 53, 18, 51, 56)
        inimigo("mushroom", 77, 18, 75, 80)
        inimigo("flying_eye", 91, 16, 88, 94)
        objeto("bau", 27, 13, "Suprimentos da galeria", id_item=2)
        objeto("fogueira", 105, 19, "Ecofoco antes da arena")
        desenho(103, 12, [[7103, 7104], [7111, 7112], [7119, 7120]])
    else:
        inimigo("esqueleto_boss", 30, 17)
        for x in (13, 35):
            desenho(x, 7, [[7103, 7104], [7111, 7112], [7119, 7120]])

    for i, (nome_camada, grid) in enumerate(grids.items(), 1):
        layer = ET.SubElement(root, "layer", id=str(i), name=nome_camada,
                              width=str(largura), height=str(altura))
        if nome_camada == "fundo":
            layer.set("tintcolor", "#ff8896ce" if fase == 3 else "#ffb0b8ff")
        ET.SubElement(layer, "data", encoding="csv").text = "\n" + ",\n".join(
            ",".join(map(str, row)) for row in grid) + "\n"
    root.append(objetos)
    root.set("nextlayerid", "8")
    root.set("nextobjectid", str(len(objetos) + 1))
    ET.indent(root)
    path = RAIZ / f"assets/maps/{nome}.tmx"
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print(path.name)


if __name__ == "__main__":
    gerar("antigo_arsenal_guardas", "Antigo Arsenal dos Guardas", 72, 2)
    gerar("corredores_profundos", "Corredores Profundos", 112, 3)
    gerar("arena_chefe", "Arena do Chefe", 48, 4)
