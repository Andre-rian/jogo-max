"""Normaliza apenas tamanho/enquadramento e empacota arte gerada em RGBA.

Nao redesenha pixels nem modifica o TMX. Fontes e prompts ficam nas evidencias.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "docs/mapas/previews/i23"
DESTINO = RAIZ / "assets/tileset/profane_echo_celas"
ESPECIFICACOES = {
    "bed": ("cama_pedra", (96, 32), (0, 0)),
    "fissura": ("fissura_profana", (64, 96), (96, 0)),
    "umidade": ("umidade", (64, 64), (160, 0)),
    "rachadura": ("rachadura", (32, 64), (224, 0)),
}


def empacotar():
    pygame.init()
    pygame.display.set_mode((1, 1))
    DESTINO.mkdir(parents=True, exist_ok=True)
    fontes = EVIDENCIA / "fontes"
    fontes.mkdir(exist_ok=True)
    geracao = json.loads((EVIDENCIA / "geracao.json").read_text(encoding="utf-8"))
    atlas = pygame.Surface((256, 96), pygame.SRCALPHA)
    manifest = {"firstgid": 7000, "tile_size": 32, "columns": 8, "sprites": {}}
    for chave, (nome, tamanho, posicao) in ESPECIFICACOES.items():
        fonte = fontes / f"{nome}.png"
        if not fonte.exists():
            shutil.copyfile(geracao["assets"][chave]["source"], fonte)
        original = pygame.image.load(str(fonte)).convert_alpha()
        bbox = original.get_bounding_rect(min_alpha=1)
        recorte = original.subsurface(bbox)
        # Preserva proporcao e alpha; nearest-neighbor, sem suavizacao ou redesenho.
        limite = (tamanho[0] - 2, tamanho[1] if chave == "bed" else tamanho[1] - 2)
        escala = min(limite[0] / bbox.w, limite[1] / bbox.h)
        reduzido = pygame.transform.scale(recorte, (max(1, round(bbox.w * escala)), max(1, round(bbox.h * escala))))
        sprite = pygame.Surface(tamanho, pygame.SRCALPHA)
        deslocamento = ((tamanho[0] - reduzido.get_width()) // 2,
                        tamanho[1] - reduzido.get_height() if chave == "bed" else (tamanho[1] - reduzido.get_height()) // 2)
        sprite.blit(reduzido, deslocamento)
        pygame.image.save(sprite, str(DESTINO / f"{nome}.png"))
        atlas.blit(sprite, posicao)
        ids = [[(posicao[1] // 32 + y) * 8 + posicao[0] // 32 + x
                for x in range(tamanho[0] // 32)] for y in range(tamanho[1] // 32)]
        manifest["sprites"][nome] = {"size": tamanho, "atlas_xy": posicao, "local_ids": ids,
            "gids": [[7000 + i for i in linha] for linha in ids],
            "source": fonte.relative_to(RAIZ).as_posix(), "source_sha256": hashlib.sha256(fonte.read_bytes()).hexdigest(),
            "source_size": original.get_size(), "alpha_bbox": list(bbox), "scaled_size": reduzido.get_size(),
            "offset": deslocamento}
    pygame.image.save(atlas, str(DESTINO / "decoracao_celas.png"))
    (DESTINO / "manifesto.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Contato ampliado para revisar pixels e transparencia sobre fundo de pedra.
    contato = pygame.Surface(atlas.get_size())
    contato.fill((38, 43, 61))
    contato.blit(atlas, (0, 0))
    pygame.image.save(pygame.transform.scale(contato, (1024, 384)), str(EVIDENCIA / "atlas_ampliado.png"))
    pygame.quit()
    print("4 sprites RGBA; atlas 256x96; 24 slots de 32x32; firstgid 7000.")


if __name__ == "__main__":
    empacotar()
