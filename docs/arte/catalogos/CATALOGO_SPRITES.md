# Catálogo de Sprites — Curadoria Visual

Data: 14/11/2026 (atualizado em 15/11/2026 com as Fases D.0, D.1 e E.0)
Branch: `sprites`
Escopo: curadoria visual dos packs recebidos. Nenhuma alteração de código do jogo, nenhuma integração e nenhum commit nesta etapa. As comparações de menu/saves da E.0 estão em `docs/arte/RELATORIO_FASE_E0_MENU_SALVAMENTO.md`.

> Regra aplicada: nenhuma seleção automática. Os catálogos apenas apresentam os assets com IDs estáveis para que a escolha seja feita manualmente.

## Como ler os catálogos

- Cada célula mostra, de cima para baixo: **ID**, **nome do arquivo** e **dimensão original**.
- O fundo xadrez indica transparência.
- As imagens foram ampliadas com interpolação *nearest-neighbor* (pixels nítidos); a dimensão real está sempre na legenda.
- Use o ID (por exemplo `M012`, `AB021`, `LY003`) para indicar a escolha.
- Para os sheets do Beast, o ID é atribuído em ordem de leitura **apenas às células ocupadas**; as coordenadas da célula aparecem na legenda (`gx,gy`), pois células vazias são puladas.

## Arquivos gerados

| Arquivo | Conteúdo | Dimensões | Versionável? |
|---|---|---|---|
| `beast_materiais.png` | 105 materiais de crafting (M001–M105) | 1720×1634 | Sim (CC0) |
| `beast_armas.png` | 56 armas/ferramentas (A001–A056) + 6 extras (X001–X006) | 1720×1204 | Sim (CC BY 4.0, com crédito) |
| `recursos_especiais_minerais.png` | Candidatos Umbrita/Abissita/Nyxita em 24/48/26/4× e estudo de paleta | 1600×1480 | Sim (Beast CC0) |
| `recursos_especiais_fase_d0.png` | Catálogo completo, incluindo candidatos locais do Eco Profano | 1600×1894 | **Não** (contém lygame) |
| `propostas_recursos/refinamentos_d1.png` | Refinamentos D.1 dos quatro recursos, escalas e contraste | 1600×1120 | Sim (Beast CC0 + Eco original) |
| `propostas_recursos/slots_inventario_d1.png` | Simulação dos ícones em slots 60×60 | 1600×430 | Sim (Beast CC0 + Eco original) |
| `ui_comparativo.png` | Amostra curada de UI por função (71 itens) | 1720×3114 | Não (contém packs restritos) |
| `ui_comparativo_abyssowl.png` | AbyssOwl completo (AB001–AB079) | 1720×2716 | Não |
| `ui_comparativo_kibyra.png` | Kibyra completo (KB001–KB208) | 1720×2966 | Não |
| `ui_comparativo_lygame.png` | lygame UI completo (LY001–LY015) | 1720×1294 | Não |
| `kingdom_icons.png` | **Não gerado** — pack não localizado | — | — |

Os quatro catálogos de UI e qualquer futura imagem `kingdom_icons*.png` estão cobertos por `docs/arte/catalogos/ui_comparativo*.png` e `docs/arte/catalogos/kingdom_icons*.png` no `.gitignore`, pois derivam de packs restritos ou de licença não confirmada e o repositório é público. O catálogo combinado `recursos_especiais_fase_d0.png` também é ignorado por incluir lygame; o recorte apenas de minerais (`recursos_especiais_minerais.png`) é CC0 e versionável. As capturas de inventário da Fase D.1 (`docs/arte/previews/*ly005*.png`) contêm o painel LY005 e também ficam fora do Git. Decisão D.1 (15/11/2026): M042, M025, M023 e Eco aprovados; M052 descartada. A Umbrita M042 foi integrada ao ID 5; Abissita, Nyxita e Eco ainda não foram integradas.

## Beast — confirmação técnica

| Sheet | Dimensão | Tile | Grade | Células ocupadas | Margem externa | Espaçamento |
|---|---|---|---|---|---|---|
| `beast_crafting_materials/resources_outlined.png` | 264×264 | 24×24 | 11×11 | 105 | 0 | 0 |
| `beast_weapons_tools/weapon_and_tools_outlined.png` | 192×168 | 24×24 | 8×7 | 56 (todas) | 0 | 0 |
| `beast_weapons_tools/extra_resources_outlined.png` | 48×72 | 24×24 | 2×3 | 6 (todas) | 0 | 0 |

- Os 105 recortes de `resources_outlined.png` são únicos (verificado por SHA-256).
- Alguns sprites encostam nas bordas da célula, portanto o recorte correto é a célula inteira de 24×24, sem margem por sprite.
- As variantes `resources_basic.png`, `resources_*_bg.png` e `resources_neutral_bg_outlined.png` compartilham a mesma grade 11×11; use apenas uma variante como base.
- Faixa de IDs: `M001`–`M105` (materiais), `A001`–`A056` (armas/ferramentas), `X001`–`X006` (extras).

## Kingdom Assets Icons — pendente

Não localizado no repositório nem em `Downloads`, `Desktop` ou `Documents`. Nenhum pack foi usado como substituto. Envie o pacote para gerar `kingdom_icons.png` e complementar este documento.

## UI — AbyssOwl Gothic Pixel UI (79 assets)

Fonte: `assets/sprites/_entrada/ui/abyssowl_gothic_pixel_ui/split_assets/`. O sheet original `gothic_pixel_ui_free-v1-0-2.png` não entra no catálogo.

| Seção | IDs | Qtd. | Observações |
|---|---|---|---|
| Bordas 16px | AB001–AB008 | 8 | 4 bordas + 2 cantos externos + 2 internos |
| Bordas 24px | AB009–AB016 | 8 | 4 bordas + 2 cantos externos + 2 internos |
| Molduras ornamentais | AB017–AB022 | 6 | 4 `large_ornate_frame` + `ornate_arch` + `ornate_oval` |
| Limites de luz | AB023–AB025 | 3 | `light_boundary` grande/médio/pequeno |
| Barras, preenchimento e sliders | AB026–AB036 | 11 | 4 barras + 3 `bar_fill` + 4 `slider_handle` |
| Seletores | AB037–AB040 | 4 | `small_selector_01..04` |
| Grades | AB041–AB046 | 6 | 16/24/32px, alpha e solid |
| Ícones 16px | AB047–AB055 | 9 | beetle, crow, hat, inkwell, pocketwatch, potion, satchel, teapot, typewriter |
| Ícones 24px | AB056–AB064 | 9 | mesma temática, 24×24 |
| Ícones 32px | AB065–AB073 | 9 | mesma temática, 32×32 |
| Toggles e switches | AB074–AB079 | 6 | `check_*_strip3`, `radio_*_strip3`, `toggle_01/02` |

- `check_*_strip3` e `radio_*_strip3` são tiras horizontais com 3 estados; convém fatiar em 3 quadros ao integrar.
- `bar_fill_*` têm 4×6 px: são texturas de preenchimento para repetição, não barras completas.
- **Lacuna:** não há botões de ação explícitos nem arquivos nomeados como aba.
- Licença não confirmada nos arquivos; manter local.

## UI — Kibyra Medieval Fantasy UI (208 assets)

Fonte: `assets/sprites/_entrada/ui/kibyra_medieval_fantasy_ui/`.

| Seção | IDs | Qtd. | Dimensão |
|---|---|---|---|
| UI Icons (`icon1`–`icon64`) | KB001–KB064 | 64 | 32×32 |
| UI Icons 2 (`icon1`–`icon64`) | KB065–KB128 | 64 | 32×32 |
| UI Icons 3 (`icon1`–`icon64`) | KB129–KB192 | 64 | 32×32 |
| Main Menu Icons (`mainmenuicon1`–`16`) | KB193–KB208 | 16 | 64×32 |

- Os arquivos `icons1.png`, `icons2.png`, `icons3.png` e `mainmenuicons.png` na raiz do pack são folhas de contato/prévia; use os arquivos individuais das pastas.
- `DoNotForget.png` é um aviso do autor, não um asset.
- **Lacuna:** não há molduras, painéis ou slots explícitos; o pack é essencialmente de ícones.
- Licença restrita: proíbe redistribuir originais ou versões modificadas. Catálogo e arquivos permanecem locais.

## UI — lygame Dark Fantasy UI (15 componentes)

Fonte: `assets/sprites/_entrada/itens/lygame_dark_fantasy/UI/`. `all.png` é prévia e não entra.

| ID | Arquivo | Dimensão | Função |
|---|---|---|---|
| LY001 | `Button1.png` | 48×20 | Botão |
| LY002 | `Button1_small.png` | 27×12 | Botão pequeno |
| LY003 | `Close.png` | 48×48 | Fechar |
| LY004 | `Close_small.png` | 20×20 | Fechar pequeno |
| LY005 | `Panel1.png` | 64×64 | Painel |
| LY006 | `Panel1_small.png` | 32×32 | Painel pequeno |
| LY007 | `Frame1.png` | 48×48 | Moldura/slot |
| LY008 | `Frame1Empty.png` | 48×48 | Moldura vazia |
| LY009 | `Checkbox.png` | 48×48 | Checkbox |
| LY010 | `Checkbox_small.png` | 20×20 | Checkbox pequeno |
| LY011 | `Checkbox3.png` | 64×18 | Checkbox horizontal |
| LY012 | `CheckboxChecked.png` | 48×48 | Checkbox marcado |
| LY013 | `CheckboxChecked_small.png` | 20×20 | Checkbox marcado pequeno |
| LY014 | `ProgressBar.png` | 42×6 | Preenchimento de barra |
| LY015 | `ProgressTrack.png` | 48×12 | Trilho de barra |

- `FunctionIcons/` e `SceneObjects/` ficaram fora do escopo desta etapa.
- Licença não confirmada nos arquivos; manter local.

## Comparativo curado (`ui_comparativo.png`)

Amostra por função, referenciando os IDs dos catálogos completos:

| Função | IDs |
|---|---|
| Molduras e painéis | AB017–AB022, LY005–LY008 |
| Bordas 24px | AB009–AB016 |
| Slots e seletores | AB043–AB046 (grades 24/32), AB037–AB040 (seletores) |
| Botões e ícones (amostra) | KB001–KB008, LY001–LY004 |
| Barras HUD | AB026–AB036, LY014–LY015 |
| Toggles e checkboxes | AB074–AB079, LY009–LY013 |
| Ícones temáticos (AbyssOwl) | AB047–AB055 |

## Lacunas e observações

- **Abas:** nenhum pack possui arquivo explicitamente nomeado como aba. Se necessário, derivar de botões/painéis.
- **AbyssOwl** não tem botões explícitos; bom para molduras, slots, barras, toggles e ícones.
- **Kibyra** não tem molduras/painéis/slots; bom para ícones de inventário, HUD e menu.
- **lygame** é a única fonte com painéis, molduras, progresso e checkboxes explícitos.
- **9-slice:** candidatos naturais são as bordas/cantos do AbyssOwl (16px e 24px). As bordas do lygame também devem ser testadas; os `mainmenuicon` do Kibyra (64×32) parecem botões rotulados, não 9-slice.
- **Densidades diferentes:** os packs vão de 4 px (`bar_fill`) a 140 px (`light_boundary_large`). Defina uma política de escala por contexto (HUD, inventário, menus) antes de integrar.
- Os ícones temáticos do AbyssOwl (besouro, corvo, cartola, tinteiro, relógio, poção, bolsa, bule, máquina de escrever) não cobrem todas as funções de jogo; são uma coleção temática, não um conjunto completo.

## Licenças e versionamento

- Beast Crafting Materials: CC0.
- Beast Weapons and Tools: CC BY 4.0 (atribuição obrigatória).
- AbyssOwl e lygame: licença não confirmada nos arquivos.
- Kibyra: licença restrita; redistribuição de originais ou modificados proibida.
- Como o repositório é público, somente `beast_materiais.png` e `beast_armas.png` são versionáveis. Os catálogos de UI estão ignorados pelo Git conforme regra adicionada em `.gitignore`.

## Próximo passo

1. Abra os catálogos em `docs/arte/catalogos/` (localmente).
2. Indique os IDs escolhidos por função de UI (moldura de painel, slot, botão, barra de vida/mana, checkbox/toggle, aba) e por item do jogo (Espada Longa, Poção de vida, Machado de Guerra, Raiz Amarga, Umbrita, Abissita, Nyxita e Eco Profano). Para os recursos especiais, use o relatório da Fase D.0.
3. Com os IDs definidos, a integração ao código será feita em uma etapa separada, com recortes e escala padronizados.
