# Relatório — Fase A: validação de sprites do inventário

Data: 2026-11-14
Escopo: **somente Fase A** (auditoria, validação dos recortes, prévias locais,
licenças). A **Fase B não foi executada**: nenhum asset foi promovido, nenhum
código do jogo foi alterado e nenhum commit foi criado.

## 1. Auditoria do inventário e carregamento de assets

| Arquivo | Papel |
|---|---|
| `core/inventario.py` | `class Inventario` (linha 21); abas `Equipamentos/Itens/Chaves/materias` (l. 35); painel `840x520` (l. 53-54); desenho em `desenhar` (l. 475). |
| `core/recursos.py` | `carregar_imagem` (l. 13) com `convert_alpha`; fallback placeholder magenta 1x1 em caso de falha. |
| `ui/icones.py` | ícones procedurais por `item.icone`. |
| `entities/objetos/item.py` | `get_item` lê `itens.json`. |
| `ui/estilo.py` | `desenhar_painel` (l. 230), `desenhar_botao` (l. 259), `desenhar_overlay` (l. 208). |
| `assets/sprites/itens/` | subpastas finais já existem (`equipamentos`, `consumiveis`, `materiais`, `ecos`, `_default`), apenas com `.gitkeep`. |

Nenhum desses arquivos foi modificado nesta fase.

## 2. Recortes validados (24x24, alpha preservado)

IDs e coordenadas conferidos programaticamente com `GridItems` (mesma rotina do
catálogo). Nenhum recorte ficou vazio.

| ID catálogo | Item (ID real) | Sheet | Célula (gx,gy) | x,y (px) | Pixels opacos | Cores | SHA-256 (16) |
|---|---|---|---|---|---|---|---|
| A017 | Espada Longa (1) | `weapon_and_tools_outlined.png` | (0,2) | 0,48 | 269 / 576 | 17 | `e446972cb83ed694a10b0aa05c36e6e2` |
| M095 | Poção de vida (2) | `resources_outlined.png` | (0,10) | 0,240 | 267 / 576 | 17 | `69ca85b3fafc4c5e72cef2c6d8ceca1e` |
| A045 | Machado de Guerra (3) | `weapon_and_tools_outlined.png` | (4,5) | 96,120 | 331 / 576 | 15 | `7b9c81fe202e9e469a3f584815b8152b` |
| M067 | Raiz Amarga (4) | `resources_outlined.png` | (8,6) | 192,144 | 326 / 576 | 13 | `af0f11e44ce4c16e3f0bd997bf7eb756` |

Bounding boxes (alpha) e hash completos em `validacao_recortes.tsv` (gerado em
diretório temporário, fora do repositório).

### Divergência M067 x M060

- O catálogo atribui **M067** a `(8,6)` = `(192,144)`.
- A anotação de `INVENTARIO_SPRITES_ATUALIZADO.md` citava `(1,6)`, que no
  catálogo é **M060** = `(24,144)`.
- A prévia usa **M067 (8,6)**, seguindo o ID do catálogo. Os dois candidatos
  aparecem lado a lado na folha de recortes para conferência visual.

## 3. Prévia local

Geradas em `docs/arte/previews/` (não integradas ao jogo):

| Arquivo | Dimensão | Conteúdo |
|---|---|---|
| `preview_itens_recortes.png` | 1500x1100 | Sheet de origem com célula destacada + recortes 1x/2x/4x + bbox/cor/hash + faixa M067 x M060. |
| `preview_itens_inventario.png` | 1280x720 | Mock do inventário (840x520) com os 4 ícones em slots 60x60, seleção e descrição. |
| `preview_lygame_paineis.png` | 1800x1320 | Painéis lygame em 9-slice no tamanho real, `Panel1` (margem 12) e `Panel1_small` (margem 6), borda 1x e 2x. |
| `preview_lygame_9slice_guia.png` | 1600x1000 | Guia de margens/cantos, zoom de pixels e resultado da checagem. |

As prévias com painéis lygame são **locais** e estão no `.gitignore`
(`docs/arte/previews/preview_lygame*.png`). As prévias de itens (Beast) podem ser
versionadas.

## 4. 9-slice dos painéis lygame

Checagem programática de uniformidade:

- `LY005 Panel1` (64x64, margem 12): centro uniforme, topo/base/esquerda/direita
  constantes; centro `#0A0A0C` (A=255).
- `LY006 Panel1_small` (32x32, margem 6): mesmos resultados; centro `#0A0A0C`
  (A=255).

Conclusão: ambos funcionam como 9-slice exato, com bordas/cantos repetidos sem
esticamento e sem deformação visual. `Panel1_small` é a opção mais econômica
para o painel de 840x520; `Panel1` preserva mais detalhe ornamental.

## 5. Licenças

- **lygame — Dark Fantasy Free Pixel Art Assets** (`https://lygame.itch.io/dark-fantasy-free-pixel-art-assets`):
  uso permitido em jogos comerciais e não comerciais; **proibido** revender,
  redistribuir ou reivindicar autoria. Originais e derivados não vão para o Git.
- **Beast Pixels — Crafting Materials**: CC0.
- **Beast Pixels — Weapons and Tools**: CC BY 4.0 (crédito obrigatório a Beast
  Pixels).

Registrado em `docs/arte/ASSETS_UI_ORIGENS.md` e
`assets/sprites/_entrada/CREDITOS_E_LICENCAS.md`.

## 6. Arquivos alterados/gerados nesta fase

- `.gitignore`: adicionada a regra `docs/arte/previews/preview_lygame*.png`.
- `docs/arte/ASSETS_UI_ORIGENS.md`: licença lygame confirmada + observação.
- `assets/sprites/_entrada/CREDITOS_E_LICENCAS.md`: linha lygame (pack e situação).
- `docs/arte/previews/`: 4 prévias locais.
- `docs/arte/RELATORIO_FASE_A_SPRITES.md`: este relatório.
- `docs/arte/catalogos/`: 6 catálogos + `CATALOGO_SPRITES.md` (já existentes).

Nenhum arquivo de `core/`, `ui/`, `entities/`, `itens.json` ou asset original
foi alterado.

## 7. Testes executados

- Validação de IDs A017/A045/M095/M067/M060 via `GridItems`: coordenadas
  conferem com o catálogo.
- Recortes não vazios: 267–331 pixels opacos por célula de 576.
- Geração das 4 prévias: OK, dimensões verificadas.
- Checagem 9-slice LY005/LY006: todas as uniformidades `True`.
- `.gitignore`: `git check-ignore` confirma as prévias lygame e o pack lygame.

## 8. Pendências e decisões antes da Fase B

1. **Confirmar M067 x M060** para a Raiz Amarga (ver seção 2).
2. **Escolher o painel**: `Panel1_small` (econômico) ou `Panel1` (ornamental).
3. Aprovar as prévias de recorte e do mock de inventário.
4. Só então executar a Fase B (promover 4 ícones, mapear pelos IDs reais 1–4,
   fallback para Umbrita/ID 5, testes e atualização de `INVENTARIO_SPRITES.md`).
