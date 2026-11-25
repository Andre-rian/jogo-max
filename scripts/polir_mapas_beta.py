"""Correções locais e idempotentes nos TMX existentes; não reconstrói as fases."""
from pathlib import Path
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
PORTA = [[7128, 7129, 7130], [7136, 7137, 7138],
         [7144, 7145, 7146], [7152, 7153, 7154]]


def polir(nome, piso):
    path = RAIZ / f"assets/maps/{nome}.tmx"
    root = ET.parse(path).getroot()
    w = int(root.get("width"))
    grids = {}
    for layer in root.findall("layer"):
        values = [int(v) for v in layer.find("data").text.replace("\n", "").split(",") if v.strip()]
        grids[layer.get("name")] = [values[i:i+w] for i in range(0, len(values), w)]
    objetos = root.find("objectgroup[@name='objetos']")

    def objeto(tipo, name, x, y, width=0, height=0, **props):
        obj = next((o for o in objetos if o.get("name") == name), None)
        if obj is None:
            oid = max(int(o.get("id")) for o in root.findall("objectgroup/object")) + 1
            obj = ET.SubElement(objetos, "object", id=str(oid))
        elif any(o is not obj and o.get("id") == obj.get("id")
                 for o in root.findall("objectgroup/object")):
            obj.set("id", str(max(int(o.get("id")) for o in root.findall("objectgroup/object")) + 1))
        obj.attrib.update(type=tipo, name=name, x=str(x), y=str(y), width=str(width), height=str(height))
        old = obj.find("properties")
        if old is not None:
            obj.remove(old)
        ps = ET.SubElement(obj, "properties")
        for key, value in props.items():
            ET.SubElement(ps, "property", name=key, value=str(value))

    def passagem(col, lado):
        for dy, row in enumerate(PORTA):
            for dx, gid in enumerate(row):
                grids["decoracao_fundo"][piso - 4 + dy][col + dx] = gid
        # O objeto ocupa o vão, não a moldura: usado também para desenhar o fundo escuro.
        objeto("transicao", f"passagem_{lado}", col * 32 + 16, (piso - 4) * 32 + 24,
               48, 104, lado=lado)

    if nome == "bloco_celas_esquecidas":
        passagem(121, "direita")
        # Voltar desembarca fora do gatilho, diante da porta.
        spawn = next(o for o in objetos if o.get("name") == "direita" and o.get("type") == "spawn")
        spawn.set("x", str(119 * 32))
        objeto("bau", "Insígnia na passagem profana", 79 * 32, 11 * 32, id_item=9)
    else:
        passagem(1, "esquerda")
        if nome != "arena_chefe":
            passagem(w - 5, "direita")
        for o in objetos:
            if o.get("type") == "spawn":
                col = w - 8 if o.get("name") == "direita" else 5
                o.set("x", str(col * 32))
        # As antigas bordas abertas deixam de parecer passagens adicionais.
        # Somente os tiles dos antigos acessos são alterados na colisão.
        for y in range(piso - 3, piso):
            for x in (0, w - 1):
                grids["colisao"][y][x] = 1821

    if nome == "antigo_arsenal_guardas":
        # Remover as prateleiras incompletas que pareciam plataformas utilizáveis.
        # Caixas apoiadas permanecem; fragmentos de armadura também saem.
        for x in (12, 22, 57):
            for y in (17, 18):
                for dx in range(3):
                    if grids["decoracao_fundo"][y][x+dx] in (2594, 2595, 2596, 2609, 2610, 2611):
                        grids["decoracao_fundo"][y][x+dx] = 0
        for row in grids["decoracao_fundo"]:
            for x, gid in enumerate(row):
                if gid in (1139, 1177):
                    row[x] = 0
        for o in objetos:
            if o.get("name") == "Reserva do arsenal":
                o.find("properties/property[@name='id_item']").set("value", "6")
    if nome == "corredores_profundos":
        for o in objetos:
            if o.get("name") == "Suprimentos da galeria":
                o.find("properties/property[@name='id_item']").set("value", "10")
            if o.get("type") == "tocha" and float(o.get("x")) == 62 * 32:
                o.set("x", str(58 * 32))  # livre da escada da galeria
        # Dois objetos estavam desenhados dentro da pedra dos degraus.
        for y, row in enumerate(grids["decoracao"]):
            for x, gid in enumerate(row):
                if gid and grids["colisao"][y][x]:
                    row[x] = 0
        for x in (102, 103):
            grids["decoracao"][19][x] = 0  # leitura limpa do terceiro frasco
    if nome == "arena_chefe":
        # A arena ganha legibilidade sem objetos decorativos atravessando o combate.
        for row in grids["decoracao"]:
            for x, gid in enumerate(row):
                if gid in (2648, 2649):
                    row[x] = 0

    for layer in root.findall("layer"):
        layer.find("data").text = "\n" + ",\n".join(
            ",".join(map(str, row)) for row in grids[layer.get("name")]) + "\n"
    root.set("nextobjectid", str(max(int(o.get("id")) for o in root.findall("objectgroup/object")) + 1))
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    for nome, piso in (("bloco_celas_esquecidas", 26), ("antigo_arsenal_guardas", 20),
                       ("corredores_profundos", 20), ("arena_chefe", 20)):
        polir(nome, piso)
