# Origens e licenças dos assets de UI e sprites

Registro consolidado de autor, URL, versão, licença, crédito e limites de
redistribuição. Preencher antes de promover qualquer arquivo para
`assets/sprites/`.

## Packs candidatos

| Pack | Autor | URL | Uso previsto | Licença declarada | Crédito | Estado |
|---|---|---|---|---|---|---|
| Crafting Materials | Beast Pixels | https://beast-pixels.itch.io/crafting-materials | Materiais, minerais e gemas | CC0 | Não obrigatório | Recebido; 3 ícones integrados |
| Weapons and Tools | Beast Pixels | https://beast-pixels.itch.io/weapons-and-tools | Equipamentos e ferramentas | CC BY 4.0 | Obrigatório | Recebido; 2 ícones integrados |
| Free Assorted Icons | Quintino Pixels | https://quintino-pixels.itch.io/assorted-icons | Consumíveis, chaves e extras | CC0 | Não obrigatório | Recebido; confirmar pack |
| Free Pixel Art Skill Icons | Quintino Pixels | https://quintino-pixels.itch.io/free-pixel-art-skill-icons-pack | Habilidades/status | A esclarecer (CC BY 4.0 no metadado) | Dar crédito por prudência | Recebido; adiado |
| Raven Fantasy Icons | Clockwork Raven | https://clockworkraven.itch.io/raven-fantasy-icons | Itens raros/especiais | Não incluída no pacote | A confirmar | Recebido; ignorado no Git |
| Antiquity Print | SciGho | https://ninjikin.itch.io/font-antiquity-script | Títulos e textos especiais | CC BY 4.0 | Obrigatório | Recebido; testar acentos |
| Pixel Keyboard UI Buttons | greedy_toad | https://greedy-toad.itch.io/pixel-keyboard-ui-buttons | Prompts de teclas | Não especificada na página | A confirmar | Recebido; ignorado no Git |
| Gamepad UI | greatdocbrown | https://greatdocbrown.itch.io/gamepad-ui | Prompts de teclado/controle | CC0 | Não obrigatório | Recebido; teclado em uso no inventário e no menu |
| Gothic Pixel UI | AbyssOwl | https://abyssowl.itch.io/gothic-pixel-ui | Molduras, slots, barras e painéis | Não incluída no pacote | A confirmar | Recebido; ignorado no Git |
| Free Medieval Fantasy UI Pack | Kibyra | https://kibyra.itch.io/free-medieval-fantasy-ui-pack | Botões, divisores e HUD | Própria: uso pessoal/comercial; redistribuição/revenda proibida | Apreciado | Recebido; ignorado no Git |
| Dark Ages UI | Hypnobius | https://hypnobius.itch.io/ | Molduras, painéis e barras | Própria: sem redistribuir | Opcional | Recebido; ignorado no Git |
| Dark Fantasy Free Pixel Art Assets | lygame | https://lygame.itch.io/dark-fantasy-free-pixel-art-assets | Ícones e objetos extras | Própria: uso em jogos permitido; proibido revender, redistribuir ou reivindicar autoria | Apreciado, não obrigatório | Recebido; licença confirmada na página; não versionar |
| Xianxia Pixel UI | ruins0707 | https://ruins0707.itch.io/xianxia-pixel-ui | Elementos rituais/ornamentais | A confirmar no download | A confirmar | Não baixado |

## Arquivos efetivamente integrados

| Arquivo final | Pack / arquivo original | Autor | Licença | Atribuição usada |
|---|---|---|---|---|
| `assets/sprites/itens/equipamentos/espada_longa.png` | Weapons and Tools / `weapon_and_tools_outlined.png`, célula (0,2) = A017 | Beast Pixels | CC BY 4.0 | Crédito a Beast Pixels nos créditos do jogo |
| `assets/sprites/itens/equipamentos/machado_guerra.png` | Weapons and Tools / `weapon_and_tools_outlined.png`, célula (4,5) = A045 | Beast Pixels | CC BY 4.0 | Crédito a Beast Pixels nos créditos do jogo |
| `assets/sprites/itens/consumiveis/pocao_vida.png` | Crafting Materials / `resources_outlined.png`, célula (0,10) = M095 | Beast Pixels | CC0 | Crédito não obrigatório (registrado) |
| `assets/sprites/itens/consumiveis/raiz_amarga.png` | Crafting Materials / `resources_outlined.png`, célula (8,6) = M067 | Beast Pixels | CC0 | Crédito não obrigatório (registrado) |
| `assets/sprites/itens/materiais/umbrita.png` | Crafting Materials / `resources_outlined.png`, célula (3,4) = M042; paleta refinada na D.1 | Beast Pixels | CC0 | Crédito não obrigatório (registrado) |
| `assets/sprites/itens/_default/item_desconhecido.png` | Original do projeto (gerado como fallback) | Profane Echo | — | — |
| `assets/sprites/itens/ecos/eco_profano.png` | Cópia binária de `docs/arte/propostas_recursos/eco_profano_d1.png`, aprovado na D.1 | Profane Echo | Original do projeto; licença MIT do repositório | Sem pixels de terceiros; integrado ao contador na F.2 |

## Uso na HUD F.2 (15/11/2026)

- M095: mesmo `pocao_vida.png` já aprovado e registrado acima (Beast Crafting
  Materials, CC0); o cache existente fornece 24×24 → 48×48 com nearest-neighbor.
  A variante escurecida do frasco vazio existe apenas em memória.
- Eco D.1: 24×24, 196 pixels opacos; arquivo final idêntico à proposta aprovada.
  Não usa `SoulFragment.png` nem outro pixel do lygame.
- Molduras, tecla F, frasco de fallback, halo e fragmentos: código procedural
  do projeto, reutilizando `desenhar_painel` e `desenhar_eco_profano`.
- `hud_f2_comparativo.png` contém apenas M095/CC0, Eco original e desenho
  procedural sobre fundos sintéticos. Capturas completas `hud_f2_*_local.png`
  ficam ignoradas. Nenhum novo material externo foi baixado.
- F.1 mantém LY015 opcional, exclusivamente local; as capturas F.2 usam seu
  fallback procedural. As restrições dos demais packs continuam inalteradas.

## Observações

- “Gratuito” não significa licença livre; conferir a licença da **edição
  baixada** e os limites de redistribuição.
- Não versionar conteúdo premium nem packs completos por conveniência.
- O crédito obrigatório de CC BY deve aparecer nos créditos do projeto.
- **lygame (Dark Fantasy Free Pixel Art Assets)**: a página do itch.io autoriza
  uso em jogos comerciais e não comerciais, mas proíbe revender, redistribuir
  ou reivindicar autoria. Originais, catálogos e prévias derivadas ficam fora do
  Git público (uso local).
- O inventário usa `UI/Panel1.png` (LY005 1×) quando ele existe localmente; se
  faltar, a moldura anterior é aplicada automaticamente. `Panel1_small.png`
  (LY006) fica reservado para futuras interfaces menores.
- O menu usa experimentalmente `UI/Frame1Empty.png` (LY008) e `UI/Frame1.png`
  (LY007) nos slots de save desde a E.2, com 9-slice de margem 5 e paleta fria.
  Se faltar, o menu volta para `desenhar_painel`; `USAR_MOLDURA_LYGAME` desliga a
  moldura. A escolha ainda depende de aprovação visual.
- **AbyssOwl (Gothic Pixel UI)**: o pacote recebido não traz arquivo de licença;
  confirmar os termos antes de promover qualquer recorte. Na E.0 foi usado
  apenas em prévias locais com moldura 9-slice e seletor.
- **Kibyra (Medieval Fantasy UI)**: o `Readme.txt` autoriza uso pessoal e
  comercial, aprecia crédito e proíbe redistribuição/revenda. Os 16 ícones de
  menu (`64×32`) foram catalogados na E.0, mas não integrados.
- **Hypnobius / Ruins Xianxia**: não usados na E.0; Hypnobius segue sem
  redistribuição e Ruins Xianxia não foi baixado.
- A E.0 comparou molduras, botões, prompts e ícones em
  `docs/arte/RELATORIO_FASE_E0_MENU_SALVAMENTO.md`; prévias com packs restritos
  ficam em `docs/arte/previews/*restrito*.png` e não são versionadas.
- A E.2 integrou os recortes de ENTER e os fallbacks de DELETE de
  `gdb-keyboard-2.png` e avaliou `Frame1.png`/`Frame1Empty.png` no menu; detalhes
  e capturas locais em
  `docs/arte/RELATORIO_FASE_E2_MENU_MOLDURAS.md`.
- A E.2.1 ampliou os prompts com nearest-neighbor (`+25%` no rodapé/slot e
  `+50%` no modal). O inventário mantém a escala original; ver
  `docs/arte/RELATORIO_FASE_E2_1_PROMPTS_TECLA.md`.
- Registro de triagem fica em
  `assets/sprites/_entrada/CREDITOS_E_LICENCAS.md`.
