# Relatório Fase I.0 — Auditoria de Mapas e Assets

Data: 2026-11-22  
Escopo: auditoria técnica/documental. **Nenhum mapa, colisão, spawn, save, áudio ou UI foi alterado.**

## 1. Resumo executivo

- Mapas TMX encontrados: **3** (`_template.tmx`, `calabouco_1.tmx`, `calabouco_2.tmx`).
- Tilesets TSX encontrados: **8**.
- Salas lógicas definidas em código: **5** (`calabouço_1` a `calabouço_5`, `world/rooms.py` + `world/niveis.py`).
- Salas com TMX real: **2** (`calabouco_1`, `calabouco_2`). Salas 3-5 usam **fallback para grade Python**.
- Referências de tileset/imagem quebradas nos TMX auditados: **0**.
- Inconsistências relevantes: nomenclatura `spwan` vs `spawn`; `calabouco_1.tmx` sem camada `plataformas`; `calabouco_2.tmx` sem `decoracao/escadas/plataformas`; objeto inimigo id=8 em `calabouco_1.tmx` usa `type=skeleton` mas propriedade `tipo` ausente (lógica espera `propriedades.tipo`); salas 3-5 sem TMX; `spwans` em `niveis.py` não bate com spawns TMX reais.

## 2. Inventário de mapas TMX

| Mapa | Dimensões (tiles) | Dimensões (px) | Tile | Camadas | Objetos | Tilesets | Status |
|---|---:|---:|---:|---|---:|---:|---|
| `assets/maps/_template.tmx` | 56x23 | 1792x736 | 32x32 | fundo(0), escadas(0), plataformas(0), colisao(0), decoracao(0) | 0 | 8 | Template vazio |
| `assets/maps/calabouco_1.tmx` | 56x23 | 1792x736 | 32x32 | fundo(1288), escadas(9), colisao(606), decoracao(68) | 4 | 7 | TMX usado |
| `assets/maps/calabouco_2.tmx` | 80x23 | 2560x736 | 32x32 | fundo(1840), colisao(589) | 4 | 5 | TMX usado |

## 3. Detalhe por mapa
### `assets/maps/_template.tmx`

- Dimensões: 56x23 tiles (1792x736 px), tile 32x32.
- Camadas:
  - `fundo`: 0/1288 tiles não vazios.
  - `escadas`: 0/1288 tiles não vazios.
  - `plataformas`: 0/1288 tiles não vazios.
  - `colisao`: 0/1288 tiles não vazios.
  - `decoracao`: 0/1288 tiles não vazios.
- Object group `objetos`: 0 objetos.
- Tilesets:
  - firstgid=1 source=`../tileset/tilesets/parede_variantes.tsx` tsx=OK image=OK name=`parede_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=97 source=`../tileset/tilesets/chao_variantes.tsx` tsx=OK image=OK name=`chao_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=193 source=`../tileset/tilesets/decoracao_tileset.tsx` tsx=OK image=OK name=`decoracao_tileset` 4 tiles 32x32 spacing=0 margin=0
  - firstgid=197 source=`../tileset/tilesets/The Sidescroller's Dungeon Tiles 32x32.tsx` tsx=OK image=OK name=`The Sidescroller's Dungeon Tiles 32x32` 399 tiles 32x32 spacing=0 margin=0
  - firstgid=596 source=`../tileset/tilesets/Platformer Asset All K.tsx` tsx=OK image=OK name=`Platformer Asset All K` 1862 tiles 32x32 spacing=10 margin=0
  - firstgid=2458 source=`../tileset/tilesets/Dungeon Tile Set 32px.tsx` tsx=OK image=OK name=`Dungeon Tile Set 32px` 270 tiles 32x32 spacing=0 margin=0
  - firstgid=2728 source=`../tileset/tilesets/Torch Sprite Sheet 32x64.tsx` tsx=OK image=OK name=`Torch Sprite Sheet 32x64` 16 tiles 32x32 spacing=0 margin=0
  - firstgid=2744 source=`../tileset/tilesets/tileset.tsx` tsx=OK image=OK name=`tileset` 20 tiles 32x32 spacing=0 margin=0

### `assets/maps/calabouco_1.tmx`

- Dimensões: 56x23 tiles (1792x736 px), tile 32x32.
- Camadas:
  - `fundo`: 1288/1288 tiles não vazios.
  - `escadas`: 9/1288 tiles não vazios.
  - `colisao`: 606/1288 tiles não vazios.
  - `decoracao`: 68/1288 tiles não vazios.
- Object group `objetos`: 4 objetos.
  - id=1 type=`spwan` name=`None` x=115.0 y=271.0 props={}
  - id=2 type=`spwan` name=`None` x=1664.0 y=544.0 props={'nome': 'direita'}
  - id=8 type=`inimigo` name=`None` x=347.0 y=228.0 props={'type': 'skeleton'}
  - id=9 type=`inimigo` name=`None` x=550.0 y=224.0 props={'patrulha_dir': '1', 'patrulha_esq': '1', 'tipo': 'skeleton'}
- Tilesets:
  - firstgid=1 source=`../tileset/tilesets/parede_variantes.tsx` tsx=OK image=OK name=`parede_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=97 source=`../tileset/tilesets/chao_variantes.tsx` tsx=OK image=OK name=`chao_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=193 source=`../tileset/tilesets/decoracao_tileset.tsx` tsx=OK image=OK name=`decoracao_tileset` 4 tiles 32x32 spacing=0 margin=0
  - firstgid=197 source=`../tileset/tilesets/The Sidescroller's Dungeon Tiles 32x32.tsx` tsx=OK image=OK name=`The Sidescroller's Dungeon Tiles 32x32` 399 tiles 32x32 spacing=0 margin=0
  - firstgid=596 source=`../tileset/tilesets/Platformer Asset All K.tsx` tsx=OK image=OK name=`Platformer Asset All K` 1862 tiles 32x32 spacing=10 margin=0
  - firstgid=2458 source=`../tileset/tilesets/Dungeon Tile Set 32px.tsx` tsx=OK image=OK name=`Dungeon Tile Set 32px` 270 tiles 32x32 spacing=0 margin=0
  - firstgid=2728 source=`../tileset/tilesets/Torch Sprite Sheet 32x64.tsx` tsx=OK image=OK name=`Torch Sprite Sheet 32x64` 16 tiles 32x32 spacing=0 margin=0

### `assets/maps/calabouco_2.tmx`

- Dimensões: 80x23 tiles (2560x736 px), tile 32x32.
- Camadas:
  - `fundo`: 1840/1840 tiles não vazios.
  - `colisao`: 589/1840 tiles não vazios.
- Object group `objetos`: 4 objetos.
  - id=1 type=`spwan` name=`None` x=32.0 y=652.0 props={}
  - id=2 type=`bau` name=`None` x=2449.0 y=511.0 props={'id_item': '1'}
  - id=3 type=`inimigo` name=`None` x=1859.0 y=628.0 props={'patrulha_dir': '30', 'patrulha_esq': '30', 'tipo': 'skeleton'}
  - id=4 type=`fogueira` name=`Ecofoco experimental` x=256.0 y=640.0 props={}
- Tilesets:
  - firstgid=1 source=`../tileset/tilesets/parede_variantes.tsx` tsx=OK image=OK name=`parede_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=97 source=`../tileset/tilesets/chao_variantes.tsx` tsx=OK image=OK name=`chao_variantes` 96 tiles 32x32 spacing=0 margin=0
  - firstgid=193 source=`../tileset/tilesets/tileset.tsx` tsx=OK image=OK name=`tileset` 20 tiles 32x32 spacing=0 margin=0
  - firstgid=213 source=`../tileset/tilesets/The Sidescroller's Dungeon Tiles 32x32.tsx` tsx=OK image=OK name=`The Sidescroller's Dungeon Tiles 32x32` 399 tiles 32x32 spacing=0 margin=0
  - firstgid=612 source=`../tileset/tilesets/Dungeon Tile Set 32px.tsx` tsx=OK image=OK name=`Dungeon Tile Set 32px` 270 tiles 32x32 spacing=0 margin=0

## 4. Salas lógicas (código) vs TMX

| Sala | Grade Python | TMX | Conexões | Spawn `niveis.py` | Inimigos `niveis.py` | Drops fixos | Material | Observação |
|---|---|---|---|---|---|---|---|---|
| calabouço_1 | Sim | `assets/maps/calabouco_1.tmx` | esq=None dir=calabouço_2 | (10,15) | [] | - | pedra | TMX carregado; possui objetos spawn/inimigo; tem escadas/decoracao; sem `plataformas`. |
| calabouço_2 | Sim | `assets/maps/calabouco_2.tmx` | esq=1 dir=3 | (1,10) | flying_eye | - | pedra | TMX carregado; possui bau/fogueira/inimigo; sem `decoracao/escadas/plataformas`. |
| calabouço_3 | Sim | Não (fallback) | esq=2 dir=4 | (2,10) | skeleton,globin,mushroom | - | pedra | Sem TMX; usa grade Python. |
| calabouço_4 | Sim | Não (fallback) | esq=3 dir=5 | (2,10) | [] | (5,5,10.7?) id_item=5 | pedra | Sala descanso; fogueira por tile 9 no grid; drop fixo definido. |
| calabouço_5 | Sim | Não (fallback) | esq=4 dir=None | (2,10) | esqueleto_boss | - | pedra | Arena boss; parede boss por tile 8; sem TMX. |

## 5. Como o carregamento funciona

- `core/game_scene.py:_carregar_sala` normaliza nome (`calabouço_1` -> `calabouco_1.tmx`), tenta carregar TMX. Se camada `colisao` ausente ou TMX inexistente, cai para `world/rooms.py` (grade Python).
- Camadas TMX lidas por nome case-insensitive: `colisao`, `decoracao`, `fundo`, `escadas`, `plataformas`. Object layer: `objetos`.
- Objetos TMX processados: `spwan` (spawn), `tocha`, `bau`, `porta`, `fogueira`, `inimigo`. Tipos desconhecidos são ignorados com warning (ex.: id=8 `inimigo` sem `tipo` útil).
- Inimigos: se TMX tem objetos, usa TMX; senão usa `Inimigos_por_sala`/fallback Python. Boss derrotado é persistido em `bosses_derrotados` por sala.
- Baús/portas/fogueiras: estado persistido por `(col,linha)` em sets; fogueiras ativas em `fogueiras_ativas`.
- Spawns: prioriza TMX (`nome`/default) por lado de entrada; fallback usa `spwans`/grid. `_spawn_seguro` ajusta bloco 2x2 para não nascer enterrado/flutuando.
- Conexões laterais: `world/niveis.py:Conexoes`; transição por borda esquerda/direita em `game_scene.py` (sem portas TMX de transição dedicadas).
- Colisão: `TileMap` cria rects sólidos de `colisao`; plataformas one-way por GIDs em `world/tiles.py:PLATAFORMA_GIDS` e por camada `plataformas`; escadas por camada `escadas`.

## 6. Problemas e inconsistências

### Alta prioridade
- **Calabouço 1 TMX: objeto inimigo id=8** tem `type=inimigo` e `props={"type":"skeleton"}` mas código procura `propriedades.get("tipo")`; resultado: warning e inimigo ignorado. Confirmar convenção (`tipo`/`type`) e normalizar loader.
- **Salas 3-5 sem TMX**: dependem de fallback Python; limita evolução visual/objetos Tiled e dificulta mapa conceitual.
- **Nomenclatura `spwan`** no TMX/código (`_resolver_spwan`, `spwans_tmx`, tipo objeto). Funciona, mas aumenta risco de erro ao criar novos mapas.

### Média prioridade
- `calabouco_1.tmx` não tem camada `plataformas` (warning no carregamento). `calabouco_2.tmx` não tem `decoracao/escadas/plataformas`.
- `spwans` em `world/niveis.py` não reflete spawns TMX reais (calabouco_1 TMX default é col 3,linha 8; niveis.py diz (10,15)).
- `calabouco_2.tmx` usa tileset `tileset.tsx` (20 tiles) além dos principais; avaliar padronização de paleta.
- `Drops_fixos` calabouço_4 usa y 10.7 (float) no código — validar intenção/posicionamento.
- Assets grandes/duplicados: `Platformer Asset All K.png` ~3.3MB referenciado por template e calabouco_1; vários PNGs de dungeon/decoração não referenciados por TSX/TMX atuais.

### Futura/observação
- `PLATAFORMA_GIDS` hardcoded para GIDs específicos; frágil se tileset for reordenado/reexportado.
- Tileset placeholder/legado em `world/tiles.py` coexiste com TMX; manter compatibilidade até migração completa.
- Falta camada/objeto padrão para portas de transição, chaves, elevadores, áreas secretas, triggers de câmera/eventos.

## 7. Evidências geradas

- Previews reais renderizados: `docs/mapas/previews/calabouco_1.png`, `calabouco_2.png`, `calabouco_3.png`, `calabouco_4.png`, `calabouco_5.png`.
- Avisos observados na renderização: `calabouco_1` sem camada `plataformas`; `calabouco_2` sem `decoracao/escadas/plataformas`; `pygame.Surface.convert` warnings em dummy video (não afeta lógica).

## 8. Não alterado
- Nenhum TMX, tileset, colisão, spawn, save, áudio, UI ou gameplay foi modificado nesta auditoria.
