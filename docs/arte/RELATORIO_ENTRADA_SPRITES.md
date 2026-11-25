# Relatório de entrada de sprites

Data: 14/11/2026  
Escopo: organização dos pacotes baixados em `assets/sprites/_entrada/`.  
Nada foi promovido para a árvore final do jogo e nenhum código foi alterado.

## Resumo

- **5.080 arquivos**, **6,95 MB**, sendo **5.059 PNG**.
- 12 pacotes organizados: 6 de itens, 4 de UI (3 com conteúdo + 1 reservado),
  2 de prompts e 1 de fonte.
- Os pacotes que estavam soltos em `_entrada/itens/` foram movidos para as
  pastas corretas em `itens/`, `ui/`, `prompts/` e `fontes/`.
- Estrutura interna dos pacotes preservada; nenhum arquivo original renomeado.
- 6 pacotes com licença restrita ou não confirmada foram incluídos no
  `.gitignore` para não serem versionados por acidente.

## Estrutura aplicada

```text
assets/sprites/_entrada/
├── _inbox/                              # vazia (aguardando novos downloads)
├── _revisar/                            # vazia
├── itens/
│   ├── beast_crafting_materials/        # 10 arquivos
│   ├── beast_weapons_tools/             # 11 arquivos
│   ├── lygame_dark_fantasy/             # 221 arquivos
│   ├── quintino_assorted_icons/         # 32 arquivos
│   ├── quintino_skill_icons/            # 108 arquivos
│   └── raven_fantasy_icons/             # 4.385 arquivos
├── ui/
│   ├── abyssowl_gothic_pixel_ui/        # 80 arquivos
│   ├── hypnobius_dark_ages_ui/          # 3 arquivos
│   ├── kibyra_medieval_fantasy_ui/      # 214 arquivos
│   └── ruins_xianxia_pixel_ui/          # vazia (não baixado)
├── prompts/
│   ├── greatdocbrown_gamepad_ui/        # 5 arquivos
│   └── greedy_toad_keyboard_ui/         # 4 arquivos
├── fontes/
│   └── antiquity_print/                 # 2 arquivos
├── LEIA-ME.md
└── CREDITOS_E_LICENCAS.md
```

## Inventário por pacote

| Pack | Pasta | Arquivos | PNG | Formatos / tamanhos | Licença | Estado |
|---|---|---:|---:|---|---|---|
| Beast Pixels — Crafting Materials | `itens/beast_crafting_materials` | 10 | 8 | Spritesheets 264×264 (7 variantes), preview 258×205; `.ase`/`.aseprite` | CC0 | Recebido |
| Beast Pixels — Weapons and Tools | `itens/beast_weapons_tools` | 11 | 7 | `weapon_and_tools.png` 192×168, versão outlined, recursos 48×72, title 432×432; `.ase` | CC BY 4.0 | Recebido |
| Quintino — Assorted Icons | `itens/quintino_assorted_icons` | 32 | 32 | 32 ícones 32×32 (`icon1..icon32`) | CC0 (provável) | Recebido |
| Quintino — Skill Icons | `itens/quintino_skill_icons` | 108 | 108 | 54 ícones 24×24 + 54 em 48×48 | A esclarecer | Recebido; adiado |
| Clockwork Raven — Raven Fantasy Icons | `itens/raven_fantasy_icons` | 4.385 | 4.384 | 2.192 ícones 16×16 + 2.192 em 32×32; nomes `fa1..fa2192` | Não incluída | Recebido; ignorado no Git |
| Dark Fantasy Free Pack (autor a confirmar) | `itens/lygame_dark_fantasy` | 221 | 220 | 36 equipamentos 32×32, 36 itens/recursos 32×32, 36 sistema/interação 32×32, 86 alquimia (32/64/96), 16 UI + contact sheets | Não incluída | Recebido; autor pendente |
| AbyssOwl — Gothic Pixel UI | `ui/abyssowl_gothic_pixel_ui` | 80 | 80 | Sheet 1300×800 + 40 frames/bars + 6 toggles + 33 grids (16/24/32 px) | Não incluída | Recebido; ignorado no Git |
| Hypnobius — Dark Ages UI | `ui/hypnobius_dark_ages_ui` | 3 | 1 | Tilesheet 384×352 com 25 assets; LICENSE e README | Própria: sem redistribuir | Recebido; ignorado no Git |
| Kibyra — Free Medieval Fantasy UI | `ui/kibyra_medieval_fantasy_ui` | 214 | 213 | 192 ícones 32×32 (3 lotes de 64), 16 ícones de menu 64×32, 5 sheets (até 1448×1086) | Própria: sem redistribuir | Recebido; ignorado no Git |
| greatdocbrown — Gamepad UI | `prompts/greatdocbrown_gamepad_ui` | 5 | 4 | 4 sheets 560×640 (teclado, PlayStation, Switch, Xbox) + `.aseprite` | CC0 | Recebido |
| greedy_toad — Keyboard UI Buttons | `prompts/greedy_toad_keyboard_ui` | 4 | 1 | Sheet 2688×4228 + GIF + 2 `.aseprite` | Não especificada | Recebido; ignorado no Git |
| SciGho — Antiquity Print | `fontes/antiquity_print` | 2 | 1 | `antiquity-print.ttf` + spritesheet 240×129 | CC BY 4.0 | Recebido |
| ruins0707 — Xianxia Pixel UI | `ui/ruins_xianxia_pixel_ui` | 0 | 0 | — | A confirmar | Não baixado |

## Destaques por categoria

### Itens

**Beast Pixels — Crafting Materials (CC0)**
- 8 PNGs: `resources_basic`, `resources_outlined`, versões com fundo azul,
  verde, neutro, neutro outlined e vermelho, todas 264×264; `preview` 258×205.
- Bom para **Umbrita, Abissita e Nyxita**, mas os ícones estão em spritesheet:
  é preciso confirmar o grid (provável base 24×24) e recortar.
- Não há ícones separados individualmente.

**Beast Pixels — Weapons and Tools (CC BY 4.0)**
- `weapon_and_tools.png` (192×168) e versão outlined: spritesheet de armas,
  ferramentas e escudos em base 24×24 (grade provável 8×7).
- `resources.png` e `extra_resources.png` (48×72) concentram ícones menores.
- Crédito obrigatório à Beast Pixels.

**Quintino — Assorted Icons (CC0)**
- 32 ícones 32×32 com nomes genéricos `icon1..icon32`; exigem seleção visual.
- Úteis para consumíveis, chaves e complementos do inventário.
- É provável que esta pasta seja o pack Assorted Icons; confirmar.

**Quintino — Skill Icons**
- 54 ícones em 24×24 e os mesmos 54 em 48×48, nomes `skill_icons1..54`.
- Reserva para habilidades/status; não é prioridade do inventário atual.

**Raven Fantasy Icons**
- 2.192 ícones em 16×16 e 2.192 em 32×32, todos com nomes sem significado
  (`fa1..fa2192`). Não há índice por categoria.
- Alguns podem servir para itens raros, chaves, recursos e símbolos, mas a
  triagem precisa ser visual e manual.
- Não há arquivo de licença; a nota do pacote diz “thank you for your purchase”.
  Manter fora do Git e confirmar os termos antes de usar.

**Dark Fantasy Free Pack (pasta `lygame_dark_fantasy`)**
- Pacote mais pronto para uso imediato no inventário:
  - `FunctionIcons/Equipment/` — 36 ícones 32×32 com nomes semânticos
    (`Broadsword`, `BarbedAxe`, `RoundShield`, `ChainPauldron` etc.).
  - `FunctionIcons/Items&Resources/` — 36 ícones 32×32
    (`HealthPotion`, `StaminaPotion`, `AntidoteHerbs`, `MagicCrystalOre`,
    `AncientTombKey`, `Torch`, `SoulFragment` etc.).
  - `FunctionIcons/System&Interaction/` — 36 ícones 32×32
    (`SaveGame`, `Open`, `UseItem`, `EquipmentInventory`, `Settings` etc.).
  - `SceneObjects/AlchemyForbidden/` — 86 objetos em 32/64/96 px.
  - `UI/` — 16 componentes (`Button1`, `Panel1`, `Frame1`, `ProgressBar`,
    `Checkbox`, `Close` etc.).
- Pode cobrir sozinho a primeira etapa de itens. Falta o arquivo de licença e
  a confirmação do autor/URL.

### UI

**AbyssOwl — Gothic Pixel UI**
- Candidato mais forte para painéis, molduras e slots.
- `split_assets/frames and bars/` (40): bordas 16 px e 24 px, cantos internos e
  externos, `large_ornate_frame1..4`, `ornate_arch`, `ornate_oval`,
  `small_selector_01..04`, `slider_handle_01..04` e barras
  (`bar_fill_01..03`, 54×16, 56×16, 60×24).
- `split_assets/grids and icons/` (33): grids sólidos/alpha em 16, 24 e 32 px,
  além de ícones temáticos (poção, bolsa, chapéu, pena, corvo etc.).
- `split_assets/toggles and switches/` (6): toggles, checkboxes e radios.
- Verificar 9-slice nas bordas antes de adotar em painéis redimensionáveis.

**Hypnobius — Dark Ages UI**
- Tilesheet 384×352 com 25 assets de UI; o README indica corte em 16×16 ou
  escala a partir de 32×32.
- Licença incluída: uso comercial permitido, redistribuição do pack proibida.
- Alternativa complementar de molduras, botões e barras.

**Kibyra — Free Medieval Fantasy UI**
- 3 lotes de 64 ícones 32×32 (`UI Icons`, `UI Icons 2`, `UI Icons 3`),
  16 ícones de menu principal 64×32 e 5 spritesheets.
- Readme: uso pessoal/comercial livre, crédito apreciado, redistribuição do
  pack proibida.
- Bom para botões, ícones de menu, divisores e HUD.

### Prompts

**greatdocbrown — Gamepad UI (CC0)**
- `gdb-keyboard-2.png`, `gdb-playstation-2.png`, `gdb-switch-2.png` e
  `gdb-xbox-2.png`, todos 560×640, mais o `.aseprite` fonte.
- Melhor opção imediata para prompts de teclado/controle.

**greedy_toad — Keyboard UI Buttons**
- `keyboard buttons.png` 2688×4228, GIF de demonstração e dois `.aseprite`.
- Licença não especificada na página; confirmar antes de integrar.

### Fontes

**Antiquity Print (CC BY 4.0)**
- `antiquity-print.ttf` e `Antiquity_SpriteSheet.png` 240×129.
- Usar apenas em títulos/textos especiais e testar `á à â ã é ê í ó ô õ ú ç`.

## Mapeamento sugerido para os itens já existentes

IDs reais em `itens.json`: 1 Espada Longa, 2 Poção de vida, 3 Machado de Guerra,
4 Raiz Amarga, 5 Umbrita. Nenhum foi promovido ainda.

| ID | Nome | Candidato sugerido | Alternativa |
|---|---|---|---|
| 1 | Espada Longa | `lygame_dark_fantasy/FunctionIcons/Equipment/Broadsword.png` | Recorte de `beast_weapons_tools/weapon_and_tools.png` |
| 2 | Poção de vida | `lygame_dark_fantasy/FunctionIcons/Items&Resources/HealthPotion.png` | Ícone de poção do AbyssOwl ou Kibyra |
| 3 | Machado de Guerra | `lygame_dark_fantasy/FunctionIcons/Equipment/BarbedAxe.png` | `BroadHalberd.png` ou recorte da Beast |
| 4 | Raiz Amarga | `lygame_dark_fantasy/FunctionIcons/Items&Resources/AntidoteHerbs.png` | Ícone de erva/raiz do Kibyra |
| 5 | Umbrita | `lygame_dark_fantasy/FunctionIcons/Items&Resources/MagicCrystalOre.png` | Recorte de `beast_crafting_materials/resources_outlined.png` |
| — | Eco Profano | `lygame_dark_fantasy/FunctionIcons/Items&Resources/SealedOrb.png` ou `SoulFragment.png` | Ícone próprio a criar |

Sugestões de UI:

| Elemento | Candidato |
|---|---|
| Slots normais | `abyssowl.../grids and icons/{24px,32px}/24px_grid_solid.png` |
| Seleção de slot | `abyssowl.../frames and bars/small_selector_01..04.png` |
| Molduras/painéis | `abyssowl.../frames and bars/large_ornate_frame1..4.png` e bordas 24 px |
| Barras | `abyssowl.../frames and bars/bar_fill_01..03.png` + `60x24px_bar_01.png` |
| Toggles/checkboxes | `abyssowl.../toggles and switches/toggle_01.png`, `check_01_strip3.png` |
| Botões | `lygame_dark_fantasy/UI/Button1.png`, `Button1_small.png`; Kibyra `UI Icons` |
| Painel de descrição | `lygame_dark_fantasy/UI/Panel1_small.png` ou `Frame1.png` |
| Slots de save | Kibyra `UI Main Menü Icons` (64×32) + moldura AbyssOwl |
| Prompts de teclado | `greatdocbrown_gamepad_ui/gdb-keyboard-2.png` |
| HUD | `lygame_dark_fantasy/UI/ProgressBar.png` + `ProgressTrack.png` |

## Licenças e riscos

- **Ignorados no Git** por licença restrita ou não confirmada:
  `raven_fantasy_icons`, `lygame_dark_fantasy`, `abyssowl_gothic_pixel_ui`,
  `kibyra_medieval_fantasy_ui`, `hypnobius_dark_ages_ui` e
  `greedy_toad_keyboard_ui`.
- Raven, Dark Fantasy Free Pack e AbyssOwl não trazem arquivo de licença.
  Confirmar autor, URL e termos da edição antes de promover qualquer arquivo.
- Kibyra e Hypnobius permitem uso no jogo, mas proíbem redistribuir o pacote.
  Não versionar os arquivos originais; promover somente os recortes aprovados.
- Beast Weapons é CC BY 4.0: o crédito à Beast Pixels é obrigatório.
- Beast Crafting, Quintino Assorted e greatdocbrown são CC0.
- A licença dos Skill Icons da Quintino permanece ambígua; dar crédito por
  prudência se forem usados.

## Pendências

1. Confirmar autor/URL/licença do `DarkFantasy_Free_Pack`.
2. Confirmar que `quintino_assorted_icons` corresponde ao pack Assorted Icons.
3. Fazer triagem visual dos 2.192 ícones Raven (16×16 e 32×32).
4. Confirmar o grid das spritesheets da Beast Pixels antes de recortar.
5. Definir e aprovar quais arquivos vão para `assets/sprites/itens/` e
   `assets/sprites/ui/`.
6. Criar o fallback `itens/_default/item_desconhecido.png`.
7. Testar a fonte Antiquity Print com acentos e símbolos dos menus.
8. Verificar 9-slice nas molduras do AbyssOwl e do Hypnobius.

## Validação

- Contagem e dimensões verificadas por leitura direta dos arquivos.
- Nenhum código, teste ou asset final do jogo foi alterado.
- `jogo.log` continua com alteração local não commitada, sem relação com esta
  organização.
