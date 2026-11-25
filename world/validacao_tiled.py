"""Validação automática de mapas TMX/TSX - Fase I.1.

Não altera gameplay; apenas inspeciona arquivos e reporta problemas.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from world.niveis import Conexoes


TIPOS_OBJETO_CONHECIDOS = {"spawn", "spwan", "inimigo", "fogueira", "tocha", "bau", "porta", "transicao"}
TIPOS_INIMIGO_CONHECIDOS = {"skeleton", "globin", "mushroom", "flying_eye", "esqueleto_boss"}
CAMADAS_OFICIAIS = ["fundo", "escadas", "plataformas", "colisao", "decoracao"]
SPAWNS_VALIDOS = {"default", "esquerda", "direita"}


@dataclass
class ProblemaValidacao:
    nivel: str  # erro | aviso
    mapa: str
    mensagem: str

    def __str__(self):
        return f"[{self.nivel.upper()}] {self.mapa}: {self.mensagem}"


def _ler_tilesets(raiz, pasta_base):
    tilesets = []
    problemas = []
    for ts in raiz.findall("tileset"):
        firstgid = int(ts.get("firstgid", 0))
        source = ts.get("source")
        if source:
            caminho_tsx = os.path.normpath(os.path.join(pasta_base, source))
            if not os.path.exists(caminho_tsx):
                problemas.append(("erro", f"TSX ausente: {source}"))
                continue
            try:
                raiz_tsx = ET.parse(caminho_tsx).getroot()
            except Exception as exc:
                problemas.append(("erro", f"TSX inválido '{source}': {exc}"))
                continue
            nome = raiz_tsx.get("name", os.path.basename(source))
            tilecount = int(raiz_tsx.get("tilecount", 0) or 0)
            columns = int(raiz_tsx.get("columns", 1) or 1)
            img = raiz_tsx.find("image")
            pasta_img = os.path.dirname(caminho_tsx)
        else:
            nome = ts.get("name", "<embedded>")
            tilecount = int(ts.get("tilecount", 0) or 0)
            columns = int(ts.get("columns", 1) or 1)
            img = ts.find("image")
            pasta_img = pasta_base

        if img is None:
            problemas.append(("aviso", f"Tileset '{nome}' sem imagem"))
        else:
            source_img = img.get("source", "")
            caminho_img = os.path.normpath(os.path.join(pasta_img, source_img))
            if not os.path.exists(caminho_img):
                problemas.append(("erro", f"PNG/imagem ausente para tileset '{nome}': {source_img}"))

        tilesets.append({
            "firstgid": firstgid,
            "nome": nome,
            "tilecount": tilecount,
            "columns": max(1, columns),
            "source": source,
        })

    tilesets.sort(key=lambda t: t["firstgid"])
    for i, ts in enumerate(tilesets):
        if ts["tilecount"] <= 0:
            problemas.append(("aviso", f"Tileset '{ts['nome']}' com tilecount inválido/ausente"))
            continue
        fim = ts["firstgid"] + ts["tilecount"] - 1
        for prox in tilesets[i + 1:]:
            if prox["firstgid"] <= fim:
                problemas.append(("aviso", f"Sobreposição potencial de GIDs: '{ts['nome']}' e '{prox['nome']}'"))
                break
    return tilesets, problemas


def _resolver_gid_valido(gid, tilesets):
    gid_masc = gid & 0x1FFFFFFF
    if gid_masc == 0:
        return True
    alvo = None
    for ts in tilesets:
        if gid_masc >= ts["firstgid"]:
            alvo = ts
        else:
            break
    if alvo is None:
        return False
    if alvo["tilecount"] <= 0:
        return True
    id_local = gid_masc - alvo["firstgid"]
    return 0 <= id_local < alvo["tilecount"]


def validar_mapa_tmx(caminho_tmx):
    nome_mapa = os.path.basename(caminho_tmx)
    problemas = []
    if not os.path.exists(caminho_tmx):
        return [ProblemaValidacao("erro", nome_mapa, "Arquivo TMX ausente")]

    try:
        raiz = ET.parse(caminho_tmx).getroot()
    except Exception as exc:
        return [ProblemaValidacao("erro", nome_mapa, f"TMX inválido: {exc}")]

    pasta_base = os.path.dirname(caminho_tmx)
    tilesets, problemas_ts = _ler_tilesets(raiz, pasta_base)
    problemas.extend(ProblemaValidacao(n, nome_mapa, msg) for n, msg in problemas_ts)

    nomes_camadas = [(c.get("name") or "").strip() for c in raiz.findall("layer")]
    nomes_lower = {n.lower() for n in nomes_camadas}
    if "colisao" not in nomes_lower:
        problemas.append(ProblemaValidacao("erro", nome_mapa, "Camada obrigatória 'colisao' ausente"))
    for camada in CAMADAS_OFICIAIS:
        if camada not in nomes_lower and camada != "colisao":
            problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Camada opcional oficial '{camada}' ausente"))

    largura = int(raiz.get("width", 0) or 0)
    altura = int(raiz.get("height", 0) or 0)
    for camada in raiz.findall("layer"):
        nome_camada = camada.get("name", "<sem-nome>")
        data = camada.find("data")
        if data is None or not (data.text or "").strip():
            problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Camada '{nome_camada}' sem dados CSV"))
            continue
        encoding = (data.get("encoding") or "csv").lower()
        if encoding != "csv":
            problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Camada '{nome_camada}' com encoding '{encoding}' (esperado csv)"))
            continue
        gids = [int(v) for v in data.text.replace("\n", "").split(",") if v.strip() != ""]
        esperado = largura * altura
        if esperado and len(gids) != esperado:
            problemas.append(ProblemaValidacao("erro", nome_mapa, f"Camada '{nome_camada}' tem {len(gids)} GIDs, esperado {esperado}"))
        for gid in gids:
            if gid != 0 and not _resolver_gid_valido(gid, tilesets):
                problemas.append(ProblemaValidacao("erro", nome_mapa, f"GID inválido {gid} na camada '{nome_camada}'"))
                break

    ids = [obj.get("id") for obj in raiz.findall("objectgroup/object") if obj.get("id")]
    if len(ids) != len(set(ids)):
        problemas.append(ProblemaValidacao("erro", nome_mapa, "IDs de objetos duplicados entre camadas"))
    grupos = [og for og in raiz.findall("objectgroup") if (og.get("name") or "").strip().lower() == "objetos"]
    if not grupos:
        problemas.append(ProblemaValidacao("aviso", nome_mapa, "Object layer 'objetos' ausente"))
        return problemas

    for obj in grupos[0].findall("object"):
        tipo = (obj.get("type") or obj.get("class") or "").strip().lower()
        tipo_norm = "spawn" if tipo == "spwan" else tipo
        oid = obj.get("id", "?")
        if not tipo_norm:
            problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Objeto id={oid} sem tipo"))
            continue
        if tipo_norm not in TIPOS_OBJETO_CONHECIDOS:
            problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Objeto id={oid} com tipo desconhecido '{tipo}'"))
        props = {}
        props_el = obj.find("properties")
        if props_el is not None:
            for p in props_el.findall("property"):
                nome = p.get("name")
                valor = p.get("value")
                if valor is None:
                    valor = p.text
                if nome:
                    props[nome] = valor

        if tipo_norm == "spawn":
            nome_spawn = (obj.get("name") or props.get("nome") or "default").strip().lower()
            if nome_spawn not in SPAWNS_VALIDOS:
                problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Spawn id={oid} com nome '{nome_spawn}' fora do padrão {sorted(SPAWNS_VALIDOS)}"))
        elif tipo_norm == "inimigo":
            tipo_inimigo = props.get("tipo", props.get("type"))
            if not tipo_inimigo:
                problemas.append(ProblemaValidacao("erro", nome_mapa, f"Inimigo id={oid} sem propriedade obrigatória 'tipo/type'"))
            elif str(tipo_inimigo).strip().lower() not in TIPOS_INIMIGO_CONHECIDOS:
                problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Inimigo id={oid} com tipo desconhecido '{tipo_inimigo}'"))
        elif tipo_norm == "bau":
            if "id_item" not in props:
                problemas.append(ProblemaValidacao("erro", nome_mapa, f"Baú id={oid} sem propriedade obrigatória 'id_item'"))
        elif tipo_norm == "transicao":
            if props.get("lado") not in {"esquerda", "direita"}:
                problemas.append(ProblemaValidacao("erro", nome_mapa, f"Transição id={oid} sem lado válido"))
            if float(obj.get("width", 0)) <= 0 or float(obj.get("height", 0)) <= 0:
                problemas.append(ProblemaValidacao("erro", nome_mapa, f"Transição id={oid} sem área válida"))
        elif tipo_norm == "porta":
            if "destino" not in props and "sala_destino" not in props:
                problemas.append(ProblemaValidacao("aviso", nome_mapa, f"Porta id={oid} sem propriedade de destino (destino/sala_destino)"))

    return problemas


def validar_conexoes(conexoes=None):
    conexoes = Conexoes if conexoes is None else conexoes
    problemas = []
    salas = set(conexoes.keys())
    for sala, destinos in conexoes.items():
        for lado, destino in destinos.items():
            if lado not in {"esquerda", "direita"}:
                problemas.append(ProblemaValidacao("aviso", "conexoes", f"Sala '{sala}' tem lado desconhecido '{lado}'"))
            if destino is None:
                continue
            if destino not in salas:
                problemas.append(ProblemaValidacao("erro", "conexoes", f"'{sala}' -> {lado} aponta para sala inexistente '{destino}'"))
                continue
            lado_oposto = "esquerda" if lado == "direita" else "direita"
            volta = conexoes.get(destino, {}).get(lado_oposto)
            if volta != sala:
                problemas.append(ProblemaValidacao("erro", "conexoes", f"Conexão inconsistente: '{sala}' {lado}->{destino}, mas '{destino}' {lado_oposto}->{volta}"))
    return problemas


def validar_mapas_diretorio(diretorio="assets/maps"):
    problemas = []
    if not os.path.isdir(diretorio):
        return [ProblemaValidacao("erro", diretorio, "Diretório de mapas não encontrado")]
    for nome in sorted(os.listdir(diretorio)):
        if nome.lower().endswith(".tmx"):
            problemas.extend(validar_mapa_tmx(os.path.join(diretorio, nome)))
    problemas.extend(validar_conexoes())
    return problemas


def formatar_problemas(problemas):
    if not problemas:
        return "Nenhum problema encontrado."
    return "\n".join(str(p) for p in problemas)
