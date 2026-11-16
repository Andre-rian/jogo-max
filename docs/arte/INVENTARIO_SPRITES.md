# Inventário de sprites

Mapa entre elementos do jogo e arquivos aprovados.

**Status (16/11/2026): Fase F.3 integrada; F.1/F.2 preservadas.** Cinco ícones
integrados (IDs 1–5), fallback global ativo, prompts de teclado integrados e
LY005 1× adotado como moldura preferencial do inventário. A moldura anterior
permanece como fallback. Na E.2, `Frame1Empty`/`Frame1` entraram em teste nos
slots do menu, com `USAR_MOLDURA_LYGAME` para rollback. Abissita e Nyxita
têm propostas aprovadas, mas ainda não integradas. O Eco original D.1 está no
contador da HUD; a poção F reutiliza M095 sem consultar o estoque do ID 2.

## Itens

| ID real do item | Nome exibido | Categoria | Sprite final | Pack de origem | Estado |
|---|---|---|---|---|---|
| 1 | Espada Longa | arma | `assets/sprites/itens/equipamentos/espada_longa.png` | Beast Weapons and Tools (A017) | integrado |
| 2 | Poção de vida | consumivel | `assets/sprites/itens/consumiveis/pocao_vida.png` | Beast Crafting Materials (M095) | integrado |
| 3 | Machado de Guerra | arma | `assets/sprites/itens/equipamentos/machado_guerra.png` | Beast Weapons and Tools (A045) | integrado |
| 4 | Raiz Amarga | consumivel | `assets/sprites/itens/consumiveis/raiz_amarga.png` | Beast Crafting Materials (M067) | integrado |
| 5 | Umbrita | material | `assets/sprites/itens/materiais/umbrita.png` | Beast Crafting Materials (M042; paleta D.1) | integrado |

Fallback global: `assets/sprites/itens/_default/item_desconhecido.png` (24×24,
gerado para o projeto). Se o arquivo faltar, `ui/icones.py` recorre ao desenho
procedural antigo.

### Integração (Fase B)

- Mapa explícito por ID real em `ui/sprites_itens.py` (1–5).
- `player.pocao` não possui `id`; o resolvedor usa `icone == "pocao"` → ID 2.
- Cache de `Surface` por ID; carregamento e escala (`pygame.transform.scale`,
  nearest-neighbor, 24×24 → 48×48) acontecem uma vez por sessão.
- Pré-carga em `Inventario.__init__`; nenhuma carga por frame.
- Escala inteira 2× centralizada em slots de 60×60; alpha preservado.

### Candidatos sugeridos (não promovidos)

| ID | Candidato em `_entrada` | Observação |
|---|---|---|
| 1 | `itens/lygame_dark_fantasy/FunctionIcons/Equipment/Broadsword.png` (32×32) | Alternativa: recortar `itens/beast_weapons_tools/weapon_and_tools.png` |
| 2 | `itens/lygame_dark_fantasy/FunctionIcons/Items&Resources/HealthPotion.png` (32×32) | Nome exato “HealthPotion” |
| 3 | `itens/lygame_dark_fantasy/FunctionIcons/Equipment/BarbedAxe.png` (32×32) | Alternativa: `BroadHalberd.png` ou recorte da Beast |
| 4 | `itens/lygame_dark_fantasy/FunctionIcons/Items&Resources/AntidoteHerbs.png` (32×32) | Representa erva/raiz |
| — | `itens/lygame_dark_fantasy/FunctionIcons/Items&Resources/SealedOrb.png` ou `SoulFragment.png` | Sugestão histórica para Eco Profano; substituída pela proposta original da D.1 |

## UI

| Elemento | Estado | Sprite final | Origem | Estado |
|---|---|---|---|---|
| Slot de inventário | normal | `ui/inventario/slots/slot_normal.png` |  | pendente |
| Slot de inventário | selecionado | `ui/inventario/slots/slot_selecionado.png` |  | pendente |
| Slot de inventário | equipado | `ui/inventario/slots/slot_equipado.png` |  | pendente |
| Slot de inventário | desabilitado | `ui/inventario/slots/slot_desabilitado.png` |  | pendente |
| Slot de save | normal | `assets/sprites/_entrada/itens/lygame_dark_fantasy/UI/Frame1Empty.png` (local, opcional) | lygame Dark Fantasy UI | E.2 experimental; fallback para `desenhar_painel` |
| Slot de save | selecionado | `Frame1Empty.png` / `Frame1.png` (local, opcional) | lygame Dark Fantasy UI | E.2 experimental; 9-slice com paleta fria |
| Botão | normal | `ui/botoes/botao_normal.png` |  | E.0: opções avaliadas; menu atual não usa botão separado |
| Botão | selecionado | `ui/botoes/botao_selecionado.png` |  | E.0: opções avaliadas; menu atual não usa botão separado |
| Prompt de teclado (setas/Tab/Esc/Enter) | integrado | `assets/sprites/_entrada/prompts/greatdocbrown_gamepad_ui/gdb-keyboard-2.png` | greatdocbrown Gamepad UI (CC0) | recorte em runtime + fallback; E.2.1 usa escala A (+25%) no rodapé e B (+50%) no modal |
| Prompt de teclado (Delete) | fallback | `assets/sprites/_entrada/prompts/greatdocbrown_gamepad_ui/gdb-keyboard-2.png` | greatdocbrown Gamepad UI (CC0) | sem recorte no spritesheet; fallback `DEL` 33×16, escala A no slot |
| Painel do inventário | padrão | `assets/sprites/_entrada/itens/lygame_dark_fantasy/UI/Panel1.png` (local, opcional) | lygame Dark Fantasy UI | integrado; fallback automático para a moldura anterior |

Comparações da Fase E.0 (molduras de slot, botões, ícones Kibyra e prompts):
ver [`RELATORIO_FASE_E0_MENU_SALVAMENTO.md`](RELATORIO_FASE_E0_MENU_SALVAMENTO.md).
As prévias com packs restritos ficam em `docs/arte/previews/*restrito*.png` e
não são versionadas. A correção dos halos do menu está registrada em
[`RELATORIO_FASE_E1_HALOS_MENU.md`](RELATORIO_FASE_E1_HALOS_MENU.md). As
molduras experimentais dos slots, os prompts reais e o alerta vermelho estão em
[`RELATORIO_FASE_E2_MENU_MOLDURAS.md`](RELATORIO_FASE_E2_MENU_MOLDURAS.md);
`USAR_MOLDURA_LYGAME` permite voltar à moldura anterior. O ajuste de escala,
padding e legibilidade dos prompts está em
[`RELATORIO_FASE_E2_1_PROMPTS_TECLA.md`](RELATORIO_FASE_E2_1_PROMPTS_TECLA.md).

### Acabamento do inventário (Fase C)

- Halos roxos removidos apenas no inventário (abas e slot selecionado); o brilho
  padrão de `desenhar_botao` foi preservado para o menu principal.
- Rótulo da quarta aba corrigido para “Materiais”.
- Ícones 26×26 dos itens equipados nos slots Mão Direita, Mão Esquerda e Armadura.
- Rodapé com teclas reais (setas, Tab e Esc) recortadas de `gdb-keyboard-2.png`;
  se o spritesheet faltar, um fallback desenhado mantém os rótulos legíveis.
- Textos secundários (descrição, atributos e instruções) receberam contraste
  discreto; valores continuam em branco.
- LY005/LY006 avaliados em prévias locais; as primeiras comparações tinham um
  bug de script que apagava o miolo e foram refeitas. O LY005 1× foi aprovado e
  adotado; o LY006 segue reservado.
- Os 4 ícones iniciais (IDs 1–4, 24×24, alpha preservado) e o fallback da
  Umbrita foram validados em capturas temporárias, removidas após a aprovação.
  Na D.1, a Umbrita ID 5 ganhou sprite próprio; o fallback permanece para itens
  sem sprite.

### LY005 adotado (Fase C.2)

- Moldura externa LY005 1× em `ui/painel_lygame.py`, com 9-slice de
  `Panel1.png`, margem 12, bordas tiled, preenchimento grafite `(30, 31, 37)` e
  contorno resfriado para azul-acinzentado.
- `Panel1.png` é opcional e local: quando ausente, o inventário usa
  automaticamente a moldura anterior. O asset não é versionado.
- Interruptor de rollback: `USAR_PAINEL_LYGAME` em `core/inventario.py` (ou
  `inventario.usar_painel_lygame = False`).
- Conteúdo interno deslocado 6 px quando o painel está ativo; abas, slots,
  ícones, descrições e prompts preservados. Navegação do mouse acompanha o
  deslocamento.
- LY006 1× permanece reservado; LY006 2× e LY005 2× não são usados.
- Capturas desta fase foram removidas após a aprovação para evitar referências
  desatualizadas.

## Recursos e Ecos

| Elemento | Sprite final / destino | Proposta aprovada (D.1) | Origem | Observações |
|---|---|---|---|---|
| Eco Profano | `assets/sprites/itens/ecos/eco_profano.png` | [`eco_profano_d1.png`](propostas_recursos/eco_profano_d1.png) | Original do projeto | Integrado no contador `player.ecos` na F.2; cópia binária 24×24, sem item/ID novo |
| Umbrita (+1 a +4) | `itens/materiais/umbrita.png` | [`recurso_m042_d1.png`](propostas_recursos/recurso_m042_d1.png) | Beast CC0 | M042 integrada ao ID 5 em 15/11/2026; M052 descartada |
| Abissita (+5 a +8) | `itens/materiais/abissita.png` | [`recurso_m025_d1.png`](propostas_recursos/recurso_m025_d1.png) | Beast CC0 | Aprovada; ainda não integrada |
| Nyxita (+9) | `itens/materiais/nyxita.png` | [`recurso_m023_d1.png`](propostas_recursos/recurso_m023_d1.png) | Beast CC0 | Aprovada; ainda não integrada |

Curadoria da Fase D.0 em
[`RELATORIO_FASE_D0_RECURSOS_ESPECIAIS.md`](RELATORIO_FASE_D0_RECURSOS_ESPECIAIS.md)
e refinamento da Fase D.1 em
[`RELATORIO_FASE_D1_RECURSOS_ESPECIAIS.md`](RELATORIO_FASE_D1_RECURSOS_ESPECIAIS.md).
Decisão de 15/11/2026: M042, M025, M023 e Eco aprovados; M052 descartada.
A Umbrita M042 foi copiada para `assets/sprites/itens/materiais/umbrita.png` e
mapeada ao ID 5, sem criar item ou ID novo. Abissita e Nyxita continuam
como propostas aprovadas, reservadas a uma etapa funcional separada.
O Eco já existia como moeda em `player.ecos`: sua integração visual na F.2
não exigiu criar itens/IDs nem alterar progressão ou salvamento.

## HUD — F.1, F.2 e F.3

- F.1: proposta C, painel grafite, vida vermelha, stamina verde com 8 px úteis;
  LY015 opcional e fallback procedural preservados.
- F.2: slot F com M095 em 2×, cargas `atual / máximo`, vazio escurecido e flash
  de 12 ticks; contador de Ecos com símbolo D.1 em 1× e painel adaptável.
- Nenhum pack restrito é necessário para os dois componentes da F.2.
- [Relatório, validações e comparativo](RELATORIO_FASE_F2_HUD.md).
- F.3: barra de chefe híbrida, dano atrasado distinto, notificações com os
  sprites IDs 1–5 e faixas separadas de prompts/mensagens; sem novos assets.
- [Relatório F.3, testes e capturas](RELATORIO_FASE_F3_HUD.md).

## Packs em triagem

Ver `assets/sprites/_entrada/LEIA-ME.md` para o fluxo e
`docs/arte/ASSETS_UI_ORIGENS.md` para licenças.
