"""Pranchas técnicas de recortes existentes (documentação, nunca assets novos)."""
from pathlib import Path
import csv
import json
import os
import sys
import textwrap
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from world.tile_map import TileMap

OUT = RAIZ / "docs/mapas/previews/i22"
GRADE = [[3268, 3269, 3270], [3317, 3318, 3319],
         [3366, 3367, 3368], [3415, 3416, 3417]]
ARCO = [[434, 435], [455, 456], [476, 477], [497, 498]]
# Parecer depende da função e montagem, não apenas do alpha do recorte.
CANDIDATOS = [
    ("APROVADO", "Barril", [[2648]], "Recipiente completo; apoiar no piso ou plataforma."),
    ("APROVADO", "Vaso", [[2649]], "Perfil legível; nenhum brilho de coleta ou interação."),
    ("APROVADO", "Argola e corrente curta", [[2639]], "Uma fixação na parede; não empilhar argolas."),
    ("APROVADO", "Corrente com continuação", [[2640], [2655]], "Um só ponto de fixação; término completo."),
    ("APROVADO", "Grilhões na parede", [[2642, 2643, 2644]], "Curva inteira e dois suportes visíveis."),
    ("APROVADO", "Detritos pequenos", [[2657, 2659]], "Fragmentos baixos; reservar aglomerados para ruínas."),
    ("APROVADO", "Ossada ambiental", [[2658]], "Crânio e ossos; exclusivo da cela fechada."),
    ("APROVADO", "Teia inteira no canto", [[2678, 2679, 2680, 2681]], "Somente sob teto e junto à parede; uma ocorrência."),
    ("APROVADO", "Grade com moldura contínua", GRADE, "Recorte nativo sem lacunas; janela da cela / ferro recolhido."),
    ("APROVADO", "Arco de saída assentado", ARCO, "Só na saída; base atrás do piso, sem espaço vazio sob ela."),
    ("APROVADO", "Tijolos do fundo existente", [[429, 430]], "Base fria preservada; não usar como prop sobreposto."),
    ("APROVADO", "Piso físico existente", [[1859, 1860]], "Preservado em colisao; não representa uma cama."),
    ("REJEITADO", "Falsa rachadura profana", [[1920, 1921], [1958, 1959], [1996, 1997]], "Ornamento biomecânico fragmentado; não é rachadura."),
    ("REJEITADO", "Ruína anterior", [[0, 904, 0], [1998, 943, 944]], "Recortes desconexos, caveira e ferragens; pedras sem apoio."),
    ("REJEITADO", "Cama improvisada", [[1678, 0, 0], [1859, 1860, 1859]], "Pilhas de blocos aparentam colisão; falta sprite de cama."),
    ("REJEITADO", "Grade truncada repetida", [[766, 767], [804, 805], [842, 843]], "Passo 42 corta a moldura; repetição amplia o defeito."),
    ("REJEITADO", "Teia vertical isolada", [[2679], [2680]], "Dois miolos de teia não formam bandeira nem teia presa."),
    ("REJEITADO", "Hastes da saída anterior", [[1600, 0, 1602], [1600, 0, 1602]], "Repetição de partes de janela; não são folhas de ferro."),
    ("REJEITADO", "Lâmina semicircular", [[2690, 2691, 2692]], "Não usar o nome arch_dome para inferir arquitetura."),
    ("REJEITADO", "Baú decorativo", [[2605]], "Sugere recompensa/interação inexistente nesta área."),
    ("ADAPTAVEL", "Janela circular gradeada", [[2513, 2514], [2528, 2529]], "Desenho completo; fundo opaco pede alvenaria da mesma família."),
    ("ADAPTAVEL", "Musgo de superfície", [[215, 216]], "Verde muito vivo; exige ajuste futuro de paleta e encaixe."),
    ("ADAPTAVEL", "Madeira e prateleira", [[2600, 2601]], "Só como apoio preso à parede; nunca substituir cama por suposição."),
    ("REJEITADO", "Escada quebrada como íntegra", [[2613]], "Faltam degraus; não mudar a escada funcional aprovada."),
]


def main():
    os.chdir(RAIZ)
    pygame.init()
    pygame.display.set_mode((1, 1))
    root = ET.parse("assets/maps/_template.tmx").getroot()
    ET.SubElement(root, "tileset", firstgid="3000",
                  source="../tileset/tilesets/Platformer K - grade continua.tsx")
    sets = TileMap._ler_tileset(root, "assets/maps")
    font = pygame.font.SysFont("consolas", 14)
    title = pygame.font.SysFont("consolas", 16, bold=True)
    rows = []
    for page in range(2):
        sheet = pygame.Surface((1440, 1080))
        sheet.fill((17, 21, 29))
        for k, (status, nome, gids, motivo) in enumerate(CANDIDATOS[page * 12:page * 12 + 12]):
            x, y = k % 4 * 360, k // 4 * 360
            cor = {"APROVADO": (141, 207, 166), "REJEITADO": (227, 146, 134),
                   "ADAPTAVEL": (228, 199, 130)}[status]
            sheet.blit(title.render(f"{page * 12 + k + 1:02} | {status}", True, cor), (x + 10, y + 8))
            sheet.blit(title.render(nome, True, (225, 225, 225)), (x + 10, y + 31))
            preview = pygame.Surface((32 * len(gids[0]), 32 * len(gids)), pygame.SRCALPHA)
            fontes, locais, ids = set(), [], []
            for j, linha in enumerate(gids):
                for i, gid in enumerate(linha):
                    if not gid:
                        continue
                    ref = TileMap._resolver_gid(gid, sets)
                    preview.blit(ref.get_surface(), (i * 32, j * 32))
                    ts = next(t for t in sets if t["nome"] == ref.tileset_nome)
                    fontes.add(ref.tileset_nome)
                    locais.append(gid - ts["firstgid"])
                    ids.append(gid)
            escala = min(2, 320 / preview.get_width(), 144 / preview.get_height())
            size = (int(preview.get_width() * escala), int(preview.get_height() * escala))
            # Quadriculado explicita transparência, sem alterar o sprite.
            for yy in range(0, 144, 12):
                for xx in range(0, 336, 12):
                    pygame.draw.rect(sheet, (35, 40, 50) if (xx + yy) // 12 % 2 else (26, 30, 39),
                                     (x + 10 + xx, y + 57 + yy, 12, 12))
            sheet.blit(pygame.transform.scale(preview, size), (x + 10, y + 57))
            texto = [" / ".join(sorted(fontes)), "local: " + ", ".join(map(str, locais)),
                     "GID: " + ", ".join(map(str, ids)), motivo]
            cursor = y + 208
            for line in texto:
                for wrapped in textwrap.wrap(line, width=40):
                    sheet.blit(font.render(wrapped, True, (205, 211, 219)), (x + 10, cursor))
                    cursor += 16
            rows.append({"numero": page * 12 + k + 1, "parecer": status, "elemento": nome,
                         "tileset": " / ".join(sorted(fontes)), "ids_locais": locais,
                         "gids": ids, "matriz": gids, "motivo": motivo})
        pygame.image.save(sheet, str(OUT / f"catalogo_{page + 1:02}.png"))
    (OUT / "catalogo.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT / "catalogo.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    pygame.quit()


if __name__ == "__main__":
    main()
