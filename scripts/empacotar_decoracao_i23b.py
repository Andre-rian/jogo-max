"""Empacota sete sprites da revisao artistica sem redesenhar a arte ou gravar TMX."""
from pathlib import Path
import hashlib
import json
import os
import shutil

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "docs/mapas/previews/i23b"
DESTINO = RAIZ / "assets/tileset/profane_echo_celas_v2"
SPECS = {
    "cama_pedra": ((96, 32), (0, 0), True),
    "fissura_profana": ((64, 96), (96, 0), True),
    "umidade": ((64, 64), (160, 0), False),
    "rachadura": ((32, 64), (224, 0), False),
    "marcas_dias": ((64, 32), (0, 96), False),
    "esqueleto_sentado": ((64, 64), (64, 96), True),
    "porta_saida": ((96, 128), (128, 96), True),
}


def empacotar():
    pygame.init()
    pygame.display.set_mode((1, 1))
    DESTINO.mkdir(parents=True, exist_ok=True)
    fontes = EVIDENCIA / "fontes"
    fontes.mkdir(exist_ok=True)
    geracao = json.loads((EVIDENCIA / "geracao.json").read_text(encoding="utf-8"))
    atlas = pygame.Surface((256, 224), pygame.SRCALPHA)
    manifest = {"firstgid": 7100, "tile_size": 32, "columns": 8, "sprites": {}}
    for nome, (tamanho, posicao, base) in SPECS.items():
        fonte = fontes / f"{nome}.png"
        if not fonte.exists():
            shutil.copyfile(geracao["assets"][nome]["source"], fonte)
        original = pygame.image.load(str(fonte)).convert_alpha()
        bbox = original.get_bounding_rect(min_alpha=1)
        escala = min((tamanho[0] - 2) / bbox.w, (tamanho[1] - (0 if base else 2)) / bbox.h)
        tamanho_reduzido = (max(1, round(bbox.w * escala)), max(1, round(bbox.h * escala)))
        reduzido = pygame.transform.scale(original.subsurface(bbox), tamanho_reduzido)
        sprite = pygame.Surface(tamanho, pygame.SRCALPHA)
        offset = ((tamanho[0] - reduzido.get_width()) // 2,
                  tamanho[1] - reduzido.get_height() if base else (tamanho[1] - reduzido.get_height()) // 2)
        sprite.blit(reduzido, offset)
        pygame.image.save(sprite, str(DESTINO / f"{nome}.png"))
        atlas.blit(sprite, posicao)
        ids = [[(posicao[1] // 32 + y) * 8 + posicao[0] // 32 + x
                for x in range(tamanho[0] // 32)] for y in range(tamanho[1] // 32)]
        manifest["sprites"][nome] = {"size": tamanho, "atlas_xy": posicao, "local_ids": ids,
            "gids": [[7100 + i for i in linha] for linha in ids], "offset": offset,
            "source": fonte.relative_to(RAIZ).as_posix(), "source_sha256": hashlib.sha256(fonte.read_bytes()).hexdigest(),
            "alpha_bbox": list(bbox), "scaled_size": tamanho_reduzido}
    pygame.image.save(atlas, str(DESTINO / "decoracao_celas_v2.png"))
    (DESTINO / "manifesto.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    contato = pygame.Surface(atlas.get_size())
    contato.fill((16, 25, 40))
    contato.blit(atlas, (0, 0))
    pygame.image.save(pygame.transform.scale(contato, (768, 672)), str(EVIDENCIA / "atlas_ampliado.png"))
    pygame.quit()


if __name__ == "__main__":
    empacotar()
