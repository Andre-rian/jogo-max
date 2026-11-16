# Entrada de sprites

Área de triagem, avaliação e reserva de sprites de UI, itens e prompts.
**Nada aqui é carregado pelo jogo.**

Plano completo: [docs/arte/SPRITES_UI_PLANO.md](../../../docs/arte/SPRITES_UI_PLANO.md).
Licenças: [CREDITOS_E_LICENCAS.md](CREDITOS_E_LICENCAS.md) e
[docs/arte/ASSETS_UI_ORIGENS.md](../../../docs/arte/ASSETS_UI_ORIGENS.md).
Inventário atual dos packs recebidos:
[docs/arte/RELATORIO_ENTRADA_SPRITES.md](../../../docs/arte/RELATORIO_ENTRADA_SPRITES.md).

## Estrutura

| Pasta | Função |
|---|---|
| `_inbox/` | Downloads novos ainda sem classificação |
| `_revisar/` | Arquivos ambíguos ou não aprovados |
| `itens/` | Pacotes de ícones de itens, materiais e equipamentos |
| `ui/` | Pacotes de molduras, painéis, slots, abas e botões |
| `prompts/` | Pacotes de prompts de teclado e controle |
| `fontes/` | Fontes decorativas/auxiliares para teste |

Cada pack fica em sua própria subpasta, **como recebido**: PNGs, spritesheets,
arquivos-fonte, README e licença originais. Não renomear nem editar arquivos
dentro dos pacotes originais.

Diretórios vazios usam `.gitkeep` como marcador de organização.

## Packs recebidos em 14/11/2026

| Categoria | Packs |
|---|---|
| Itens | `beast_crafting_materials`, `beast_weapons_tools`, `quintino_assorted_icons`, `quintino_skill_icons`, `raven_fantasy_icons`, `lygame_dark_fantasy` |
| UI | `abyssowl_gothic_pixel_ui`, `hypnobius_dark_ages_ui`, `kibyra_medieval_fantasy_ui` |
| Prompts | `greatdocbrown_gamepad_ui`, `greedy_toad_keyboard_ui` |
| Fonte | `antiquity_print` |

Packs com licença restrita ou não confirmada estão no `.gitignore` e permanecem
apenas localmente. Detalhes e candidatos por item no
[relatório](../../../docs/arte/RELATORIO_ENTRADA_SPRITES.md).

## Fluxo para novos sprites

1. Baixar somente os packs de interesse e guardar o pacote original em
   `_inbox/` ou na subpasta do autor em `itens/`, `ui/`, `prompts/` ou `fontes/`.
2. Registrar autor, URL, versão, licença e condições de crédito antes de usar.
3. Inspecionar tamanho nativo, transparência, spritesheet, 9-slice e legibilidade
   na escala real do jogo.
4. Fazer a seleção visual e anotar `pack / arquivo original / uso desejado /
   aprovado? / observação`. O responsável escolhe; o agente não decide sozinho.
5. Copiar **somente os aprovados** para a árvore final em `assets/sprites/ui/`,
   `assets/sprites/itens/` etc., renomeando em `snake_case` sem acentos.
6. Testar no jogo (normal, selecionado, equipado, desabilitado, fallback,
   escala inteira e cache) antes de declarar a escolha definitiva.

## Regras de nome

- ASCII minúsculo, sem acento, espaço ou parênteses.
- Nomes semânticos e alinhados ao ID real do item no código.
- Estados como sufixo: `slot_normal.png`, `slot_selecionado.png`,
  `slot_equipado.png`, `slot_desabilitado.png`.
- Nomes propostos para os primeiros itens: `umbrita.png`, `abissita.png`,
  `nyxita.png`, `eco_profano.png`, `pocao_vida.png`,
  `item_desconhecido.png`.
- Pasta `_default/` é o fallback local; prefixo `_` não representa uma
  categoria jogável.

## Cuidados

- Não copiar packs completos para o repositório por conveniência.
- Pacotes com restrição de redistribuição ficam fora do Git (pasta local
  ignorada); versionar apenas o que a licença permitir.
- Não misturar autores, bordas, espessuras ou níveis de detalhe conflitantes.
- Preferir molduras 9-slice; não esticar pixel art ornamental.
