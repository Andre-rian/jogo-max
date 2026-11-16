# Relatório — Fase B: integração inicial das sprites

Data: 2026-11-14
Escopo: integração dos quatro ícones aprovados ao inventário real, com cache,
escala pixel-perfect e fallback. Painéis lygame **não** foram aplicados (etapa
separada). Nenhum commit foi criado.

## 1. Recortes promovidos

Originais apenas lidos; nenhum arquivo de `_entrada/` foi alterado.

| ID item | Item | Arquivo final | Origem | Célula | x,y | Licença |
|---|---|---|---|---|---|---|
| 1 | Espada Longa | `assets/sprites/itens/equipamentos/espada_longa.png` | `beast_weapons_tools/weapon_and_tools_outlined.png` (A017) | (0,2) | 0,48 | CC BY 4.0 |
| 2 | Poção de vida | `assets/sprites/itens/consumiveis/pocao_vida.png` | `beast_crafting_materials/resources_outlined.png` (M095) | (0,10) | 0,240 | CC0 |
| 3 | Machado de Guerra | `assets/sprites/itens/equipamentos/machado_guerra.png` | `beast_weapons_tools/weapon_and_tools_outlined.png` (A045) | (4,5) | 96,120 | CC BY 4.0 |
| 4 | Raiz Amarga | `assets/sprites/itens/consumiveis/raiz_amarga.png` | `beast_crafting_materials/resources_outlined.png` (M067) | (8,6) | 192,144 | CC0 |
| — | Fallback | `assets/sprites/itens/_default/item_desconhecido.png` | Original do projeto | — | — | — |

Todos os ícones finais têm 24×24 com alpha. A contagem de pixels opacos confere
com a validação da Fase A: 269, 267, 331, 326.

M067 usa a coordenada correta **(8,6)**; a anotação antiga (1,6) não foi usada.

## 2. Integração no inventário

| Arquivo | Alteração |
|---|---|
| `ui/sprites_itens.py` (novo) | Mapa explícito por ID real (1–4), cache de `Surface`, escala 24→48 px, fallback e pré-carga. |
| `ui/icones.py` | `desenhar_icone_item` tenta o sprite por ID; usa o fallback; mantém o desenho procedural como última reserva. Contagem de cargas/quantidade preservada. |
| `core/inventario.py` | Importa e chama `precarregar_sprites_itens()` em `__init__`. Nenhuma lógica de inventário alterada. |

Detalhes:

- Escala fixa 2× com `pygame.transform.scale` (nearest-neighbor), centralizada em
  slots de 60×60. Transparência preservada com `convert_alpha`.
- Cache por ID: carregamento e escala ocorrem uma única vez por sessão; falhas
  também ficam em cache para não repetir tentativas.
- `player.pocao` é um objeto especial sem `id`; o resolvedor mapeia
  `icone == "pocao"` para o ID real 2.
- Itens sem sprite mapeado (ex.: Umbrita/ID 5) usam
  `_default/item_desconhecido.png`; se esse arquivo faltar, o ícone procedural
  antigo é desenhado. Nenhum dado de inventário foi alterado.

## 3. Capturas do inventário real

Geradas a partir da classe `Inventario` real (`docs/arte/previews/`):

- `inventario_real_equipamentos.png` — espada equipada + machado.
- `inventario_real_itens.png` — poção e Raiz Amarga com quantidade.
- `inventario_real_materiais.png` — Umbrita usando o fallback.

As capturas contêm apenas sprites Beast/projeto e podem ser versionadas.

## 4. Testes

- Suíte completa: `python -m pytest -q` → **169 passed**.
- Novo arquivo `tests/test_inventario_sprites.py` (10 testes):
  - PNGs finais existem, são 24×24 e têm alpha.
  - Sprites resolvidos por ID real 1–4 em 48×48.
  - `Pocao` sem `id` resolve para o sprite do ID 2.
  - ID 5 não mapeado usa fallback.
  - Desenho com sprite e com fallback não quebra.
  - Inventário vazio desenha em todas as abas sem erro.
  - Quatro itens, quantidades e abas corretas.
  - Troca de aba (TAB) e seleção (setas) preservadas.
  - Equipar arma pelo inventário preservado.
  - Pré-carga popula o cache.
- Testes existentes de áudio, combate, inventário e UI continuam passando.

## 5. Créditos e licenças

- Beast Pixels — Weapons and Tools: CC BY 4.0, crédito obrigatório.
- Beast Pixels — Crafting Materials: CC0 (crédito registrado por cortesia).

Registrado em `docs/arte/ASSETS_UI_ORIGENS.md`,
`docs/arte/INVENTARIO_SPRITES.md` e
`assets/sprites/_entrada/CREDITOS_E_LICENCAS.md`.

## 6. Pendências

1. Umbrita (ID 5) continua sem sprite aprovado; usa o fallback.
2. Painéis lygame (LY005) permanecem fora desta etapa.
3. Ícones procedurais seguem no código apenas como reserva caso o fallback
   também falhe.
4. Demais packs e telas (HUD, menu, prompts) não foram tocados.
5. Sem commits, conforme solicitado.
