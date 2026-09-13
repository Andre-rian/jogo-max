import pygame
import os
import logging
import xml.etree.ElementTree as ET
from settings import Tile_size
from world.tiles import Registro_ID, Tile_vazio, PLATAFORMA_GIDS
from core.recursos import carregar_imagem, criar_placeholder

logger = logging.getLogger(__name__)

_cache_folhas = {}

def _carregar_folha(path):
    # carrega a imagem inteira do tileset e reproveita ela(cache global)

    if path not in _cache_folhas:
        folha = carregar_imagem(path)
        if folha.get_width() < Tile_size or folha.get_height() < Tile_size:
            logger.warning(
                f"[MAPA] tileset '{path}' menor que um tile {Tile_size}px — usando placeholder magenta"
            )
            folha = criar_placeholder((Tile_size, Tile_size))
        _cache_folhas[path] = folha
    return _cache_folhas[path]


class TileRef:
    # descreve Um tile pintado numa celula Tiled: de qual tileset veio e a posição dele dentro do tile
    __slots__ = ("tileset_nome", "imagem_path", "col", "linha", "tile_id_legado", "spacing", "margin", "gid",
                 "flip_h", "flip_v", "flip_d")

    def __init__(self, tileset_nome, imagem_path, col, linha, tile_id_legado=None, spacing=0, margin=0, gid=None):

        self.tileset_nome = tileset_nome
        self.imagem_path = imagem_path
        self.col = col
        self.linha = linha
        self.tile_id_legado = tile_id_legado
        self.spacing = spacing
        self.margin = margin
        self.gid = gid
        #Tiled guarda 3 bits de flip no topo do gid (0xE0000000); o id do tile fica nos 29 bits (0x1FFFFFFF)
        self.flip_h = bool(gid and gid & 0x80000000)  # horizontal
        self.flip_v = bool(gid and gid & 0x40000000)  # vertical
        self.flip_d = bool(gid and gid & 0x20000000)  # diagonal


    def get_surface(self):
        folha = _carregar_folha(self.imagem_path)
        x = self.margin + self.col * (Tile_size + self.spacing)
        y = self.margin + self.linha * (Tile_size + self.spacing)
        if x + Tile_size > folha.get_width() or y + Tile_size > folha.get_height():
            logger.warning(
                f"[MAPA] tile ({self.col},{self.linha}) fora do tileset '{self.imagem_path}' "
                f"({folha.get_width()}x{folha.get_height()})"
            )
            return _carregar_folha(self.imagem_path)
        surf = folha.subsurface((x, y, Tile_size, Tile_size))
        #aplica os flips que o Tiled guardou no gid
        if self.flip_d:
            surf = pygame.transform.rotate(surf, 90)
        if self.flip_h or self.flip_v:
            surf = pygame.transform.flip(surf, self.flip_h, self.flip_v)
        return surf


class TileMap:

    #calcula a fisica dos blocos, danos e desenha na tela

    def __init__(self, grid, grid_decoracao=None, grid_fundo=None, grid_escadas=None, grid_plataformas=None):

        self.grid = self._converter_grid_fallback(grid)
        self.linhas = len(self.grid)
        self.colunas = len(self.grid[0]) if self.linhas > 0 else 0

        self.grid_decoracao = grid_decoracao
        self.grid_fundo = grid_fundo
        self.grid_escadas = grid_escadas
        self.grid_plataformas = grid_plataformas

        self.rects_solidos = self._calcular_rects_solidos()
        self.rects_plataforma = self._calcular_rects_plataforma()
        self.rects_dano = self._calcular_rects_danos()
        self.rects_bau = self._calcular_rects_baus()
        self.rects_escada = self._calcular_rects_escada()        

    @staticmethod
    def _converter_grid_fallback(grid):
        #grids python (ints 0..9, usados quando nao existe tmx) viram TileRef
        #placeholder para a fisica e desenho do jogo
        novo = []
        for linha in grid:
            nova = []
            for ref in linha:
                if isinstance(ref, int):
                    if ref == 0:
                        nova.append(None)
                    else:
                        nova.append(TileRef("placeholder", "", 0, 0, tile_id_legado=ref))
                else:
                    nova.append(ref)
            novo.append(nova)
        return novo        

    #carregamento do tmx

    @staticmethod
    def _ler_tileset(raiz, pasta_base):
        tilesets = []

        for ts in raiz.findall("tileset"):
            firstgid = int(ts.get("firstgid"))
            origem = ts.get("source")


            if origem:
                #tileset externo (.tsx) - o firstgid fica no .tmx, o resto vive no arquivo .tsx
                caminho_tsx = os.path.normpath(os.path.join(pasta_base, origem))
                try:
                    raiz_tsx = ET.parse(caminho_tsx).getroot()
                except (FileNotFoundError, ET.ParseError) as e:
                    logger.warning(f"[MAPA] não consegiu abrir tileset externo '{caminho_tsx}': {e}")
                    continue

                nome = raiz_tsx.get("name")
                img = raiz_tsx.find("image")
                tilewidth = int(raiz_tsx.get("tilewidth", Tile_size))
                tileheight = int(raiz_tsx.get("tileheight", Tile_size))
                tilecount_attr = raiz_tsx.get("tilecount")
                columns_attr = raiz_tsx.get("columns")
                spacing = int(raiz_tsx.get("spacing", 0))
                margin = int(raiz_tsx.get("margin", 0))
                pasta_da_imagem = os.path.dirname(caminho_tsx)

            else:
                # tileset embutido no tmx
                nome = ts.get("name")
                img = ts.find("image")
                tilewidth = int(ts.get("tilewidth", Tile_size))
                tileheight = int(ts.get("tileheight", Tile_size))
                tilecount_attr = ts.get("tilecount")
                columns_attr = ts.get("columns")
                spacing = int(ts.get("spacing", 0))
                margin = int(ts.get("margin", 0))
                pasta_da_imagem = pasta_base

            if img is None:
                logger.warning(f"[MAPA] tileset '{nome}' sem <imagem> (nem embutida no .tsx) - ignorado")
                continue

    
            largura_img = int(img.get("width"))
            altura_img = int(img.get("height"))

            if columns_attr:
                colunas = int(columns_attr)
            else:
                pas_x = tilewidth + spacing
                colunas = max(1, (largura_img - 2 * margin + spacing) // pas_x) if pas_x > 0 else 1

            caminho_img = img.get("source")
            caminho_img = os.path.normpath(os.path.join(pasta_da_imagem, caminho_img))

            
            if tilecount_attr:
                tilecount = int(tilecount_attr)
            else:
                pas_y = tileheight + spacing
                linhas = max(1, (altura_img - 2 * margin + spacing) // pas_y) if pas_y > 0 else 1
                tilecount = colunas * linhas

            tilesets.append({
                "firstgid" : firstgid,
                "nome" : nome,
                "imagem_path" :  caminho_img,
                "colunas" : colunas,
                "tilecount" : tilecount,
                "spacing" : spacing,
                "margin" : margin,
                
            })

        tilesets.sort(key=lambda t: t["firstgid"])
        return tilesets

    @staticmethod
    def _resolver_gid(gid, tileset):
        #gids do Tiled tem bits de flag (flip h/v/diagonal) no topo: id real = gid & 0x1FFFFFFF
        gid_masc = gid & 0x1FFFFFFF
        if gid_masc == 0:
            return None

        alvo = None
        for ts in tileset:
            if gid_masc >= ts["firstgid"]:
                alvo = ts
            else:
                break

        if alvo is None:
            return None

        id_local = gid_masc - alvo["firstgid"]
        col = id_local % alvo["colunas"]
        linha = id_local // alvo["colunas"]

        if alvo["nome"] == "placerholde":
            return TileRef(alvo["nome"], alvo["imagem_path"], col, linha, tile_id_legado=id_local + 1,
                           spacing=alvo.get("spacing", 0), margin=alvo.get("margin", 0), gid=gid)

        return TileRef(alvo["nome"], alvo["imagem_path"], col, linha,
                       spacing=alvo.get("spacing", 0), margin=alvo.get("margin", 0), gid=gid)

    @staticmethod
    def carregar_objetos_tmx(caminho, nome_camada="objetos"):
        arvore = ET.parse(caminho)
        raiz = arvore.getroot()


        grupo = None
        nomes_encontrados = []

        for og in raiz.findall("objectgroup"):
            nomes_encontrados.append(og.get("name"))
            if (og.get("name") or "").strip().lower() == nome_camada.strip().lower():
                grupo = og
                break

        if grupo is None:
            logger.warning(f"[MAPA] object layer '{nome_camada}' não encontrado em '{caminho}'"
                           f"Object layers disponíveis: {nomes_encontrados}")
            return None

        objetos = []
        for obj in grupo.findall("object"):
            tipo = (obj.get("type") or obj.get("class") or "").strip().lower()
            x, y = float(obj.get("x")), float(obj.get("y"))


            propriedades = {}
            props_el = obj.find("properties")
            if props_el is not None:
                for p in props_el.findall("property"):
                    propriedades[p.get("name")] = p.get("value")

            objetos.append({
                "tipo" : tipo,
                "id": int(obj.get("id")),
                "col" : int(x // Tile_size),
                "linha" : int(y // Tile_size) ,
                "propriedades" : propriedades ,
                
            })
        return objetos




    @staticmethod
    def carregar_camada_tmx(caminho, nome_camada):
        arvore = ET.parse(caminho)
        raiz = arvore.getroot()
        largura = int(raiz.get("width"))
        altura = int(raiz.get("height"))
        pasta_base = os.path.dirname(caminho)

        tilesets = TileMap._ler_tileset(raiz, pasta_base)

        camada = None
        nomes_encontrados = []
        for c in raiz.findall("layer"):
            nomes_encontrados.append(c.get("name"))
            if (c.get("name") or "").strip().lower() == nome_camada.strip().lower():
                camada = c
                break

        if camada is None:
            logger.warning(
                f"[MAPA] camada '{nome_camada}' não encontrado em '{caminho}'. "
                f"Camadas disponiveis: {nomes_encontrados}"

            )
            return None

        dados = camada.find("data")
        texto = dados.text.strip()
        gids = [int(v) for v in texto.replace("\n", "").split(",") if v.strip() != ""]

        grid = []
        for linha_i in range(altura):
            inicio = linha_i * largura
            linha_gids = gids[inicio:inicio + largura]
            linha = [TileMap._resolver_gid(g, tilesets) for g in linha_gids]
            grid.append(linha)

        return grid


    # fisica - (colisao/dano)

    def _tile_info(self, ref):
        if ref is None:
            return False, 0


        if ref.tileset_nome == "placerholder":
            tile = Registro_ID.get(ref.tile_id_legado)
            if tile is None:
                return False, 0
            return tile.solid, tile.damage

        return True, 0

    def _calcular_rects_solidos(self):
        rects = []
        for linha_i, linha in enumerate(self.grid):
            for col_i, ref in enumerate(linha):
                solid, _ = self._tile_info(ref)
                if solid and not self._eh_plataforma(ref):
                    rects.append(pygame.Rect(
                        col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size

                    ))
        return rects

    def _eh_plataforma(self, ref):
        #tiles one-way: fora da colisao solida, viram piso so por cima (gid sem os bits de flip)
        return ref is not None and ref.gid is not None and (ref.gid & 0x1FFFFFFF) in PLATAFORMA_GIDS

    def _calcular_rects_plataforma(self):
        rects = []
        #colisao com gid de plataforma (compatibilidade com a forma antiga)
        for linha_i, linha in enumerate(self.grid):
            for col_i, ref in enumerate(linha):
                if self._eh_plataforma(ref):
                    rects.append(pygame.Rect(
                        col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size
                    ))
        #camada dedicada 'plataformas': qualquer tile pintado vira plataforma
        if self.grid_plataformas:
            for linha_i, linha in enumerate(self.grid_plataformas):
                for col_i, ref in enumerate(linha):
                    if ref is not None:
                        r = pygame.Rect(col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size)
                        if r not in rects:
                            rects.append(r)
        return rects

    def _calcular_rects_escada(self):
        rects = []
        if not self.grid_escadas:
            return rects
        for linha_i, linha in enumerate(self.grid_escadas):
            for col_i, ref in enumerate(linha):
                if ref is not None:
                    rects.append(pygame.Rect(
                        col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size
                    ))
        return rects

    def _calcular_rects_danos(self):
        rects = []
        for linha_i, linha in enumerate(self.grid):
            for col_i, ref in enumerate(linha):
                _, damage = self._tile_info(ref)
                if damage > 0:
                    rects.append((
                        pygame.Rect(col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size),
                        damage
                                    
                    ))
                    
        return rects


    def _calcular_rects_baus(self):
        rects = []
        for linha_i, linha in enumerate(self.grid):
            for col_i, ref in enumerate(linha):
                if ref is not None and ref.tileset_nome == "placeholder" and ref.tile_id_legado == 6:
                    rects.append((
                        pygame.Rect(col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size),
                        col_i, linha_i
                    ))

        return rects


    # Desenhar

    def desenhar(self, tela, camera):
        cam_x = int(camera.offset.x)
        cam_y = int(camera.offset.y)

        col_inicio = max(0, cam_x // Tile_size)
        col_fim = min(self.colunas, col_inicio + tela.get_width() // Tile_size + 2)
        linha_inicio = max(0, cam_y // Tile_size)
        linha_fim = min(self.linhas, linha_inicio + tela.get_height() // Tile_size + 2)


        self._desenhar_camada_simples(tela, camera, self.grid_fundo, 
                                      linha_inicio, linha_fim, col_inicio, col_fim)

        self._desenhar_camada_simples(tela, camera, self.grid_escadas,
                                      linha_inicio, linha_fim, col_inicio, col_fim)

        self._desenhar_camada_simples(tela, camera, self.grid_plataformas,
                                      linha_inicio, linha_fim, col_inicio, col_fim)

        for linha_i in range(linha_inicio, linha_fim):
            for col_i in range(col_inicio, col_fim):
                ref = self.grid[linha_i][col_i]            
                if ref is None:
                    continue

                rect_mundo = pygame.Rect(col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size)
                rect_tela = camera.aplicar(rect_mundo)


                if ref.tileset_nome == "placeholder":
                    tile = Registro_ID.get(ref.tile_id_legado)
                    if tile is None:
                        continue
                    tile.draw(tela, rect_tela, col=col_i, linha=linha_i)
                else:
                    tela.blit(ref.get_surface(), rect_tela)


        self._desenhar_camada_simples(tela, camera, self.grid_decoracao, 
                                      linha_inicio, linha_fim, col_inicio, col_fim)

    def _desenhar_camada_simples(self, tela, camera, grid, li, lf, ci, cf):
        if not grid:
            return
        for linha_i in range(li, lf):
            for col_i in range(ci, cf):
                ref = grid[linha_i][col_i]
                if ref is None:
                    continue
                if not ref.imagem_path:
                    #marcador sem sprite (ex: camada de escadas ainda sem imagem)
                    continue
                rect_mundo = pygame.Rect(col_i * Tile_size, linha_i * Tile_size, Tile_size, Tile_size)
                rect_tela = camera.aplicar(rect_mundo)
                tela.blit(ref.get_surface(), rect_tela)

    # consulta uteis

    def get_tile(self, col, linha):
        if 0 <= linha < self.linhas and 0 <= col < self.colunas:
            ref = self.grid[linha][col]
            if ref is not None and ref.tileset_nome == "placeholder":
                return ref.tile_id_legado
            return 1 if ref is not None else 0
        return 1

    def remover_tile(self, col, linha):
        if 0 <= linha < self.linhas and 0 <= col < self.colunas:
            self.grid[linha][col] = None
            self.rects_solidos = self._calcular_rects_solidos()
            self.rects_plataforma = self._calcular_rects_plataforma()
            self.rects_dano = self._calcular_rects_danos()
            self.rects_bau = self._calcular_rects_baus()

