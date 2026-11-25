"""Protege a geometria aprovada e a autoria manual da curadoria I.2.2."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

from scripts.gerar_bloco_celas import gerar, DESTINO


def test_curadoria_preserva_estrutura_aprovada_e_assets_originais():
    baseline = json.loads(Path("docs/mapas/previews/i22/baseline.json").read_text(encoding="utf-8"))
    root = ET.parse(DESTINO).getroot()
    # O polimento acrescenta apenas um baú e o gatilho da porta existente.
    esperado_atrib = dict(baseline["map_attrib"])
    esperado_atrib["nextobjectid"] = root.get("nextobjectid")
    assert root.attrib == esperado_atrib
    objetos = root.find("objectgroup[@name='objetos']")
    novos = [o for o in objetos if o.get("type") in ("bau", "transicao")]
    assert {o.get("name") for o in novos} == {"Insígnia na passagem profana", "passagem_direita"}
    for obj in novos:
        objetos.remove(obj)
    retorno = objetos.find("object[@name='direita']")
    assert retorno.get("x") == "3808"
    retorno.set("x", "3904")
    ET.indent(root)
    for chave, esperado in baseline["elementos"].items():
        elemento = next(e for e in root if e.tag + ":" + e.get("name", "") == chave)
        assert hashlib.sha256(ET.tostring(elemento)).hexdigest() == esperado, chave
    # Hashes dos sistemas são evidência da entrega, sem congelar código futuro.
    for caminho, esperado in baseline["arquivos"].items():
        if caminho.startswith("assets/tileset/"):
            assert hashlib.sha256(Path(caminho).read_bytes()).hexdigest() == esperado, caminho


def test_comando_legado_nao_sobrescreve_tmx():
    antes, mtime = DESTINO.read_bytes(), DESTINO.stat().st_mtime_ns
    gerar()
    assert DESTINO.read_bytes() == antes
    assert DESTINO.stat().st_mtime_ns == mtime
