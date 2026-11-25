"""Compatibilidade I.2.2: o TMX editado no Tiled é a fonte de verdade.

O antigo gerador foi aposentado para não restaurar decorações descartadas.
Este comando agora apenas valida o TMX existente. Não escreve nenhum arquivo.
A versão histórica está em docs/mapas/previews/i22/gerador_antes.py.txt.
"""
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
DESTINO = RAIZ / "assets/maps/bloco_celas_esquecidas.tmx"


def gerar():
    """Nome legado mantido; validação somente leitura, sem regeneração."""
    from world.validacao_tiled import validar_mapa_tmx

    print("I.2.2: o TMX é a fonte de verdade. Regeneração aposentada; validando sem gravar.")
    problemas = validar_mapa_tmx(str(DESTINO))
    for problema in problemas:
        print(problema)
    if any(p.nivel == "erro" for p in problemas):
        raise SystemExit(1)
    print("TMX preservado e válido.")


if __name__ == "__main__":
    gerar()
