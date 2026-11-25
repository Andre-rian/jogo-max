# Relatório - Fase E.2.1: legibilidade dos prompts de tecla

Data: 15/11/2026  
Branch: `sprites`  
Status: **ajuste implementado e capturado; aprovação visual pendente**.  
Escolha aplicada: escala A (+25%) no rodapé e no slot ocupado; escala B (+50%)
no modal de confirmação. Nenhum commit criado.

## 1. Escopo

- Ampliar setas, ENTER e DELETE no rodapé, no slot ocupado e no modal.
- Testar as escalas A (+25%) e B (+50%).
- Preservar a pixel art com nearest-neighbor.
- Ajustar espaçamento ícone/texto, alinhamento vertical e padding interno.
- Manter o rodapé discreto e o modal mais legível.
- Não alterar molduras da E.2, halos da E.1, inventário, HUD, combate, áudio,
  saves ou lógica funcional.

## 2. Implementação

### `ui/prompts_teclas.py`

- `obter_tecla(nome, escala=1.0)` agora aceita escala e usa
  `pygame.transform.scale` (nearest-neighbor), com cache por tecla e escala.
- `criar_prompt` ganhou `escala`, `padding`, `cor_fundo` e `raio_fundo`.
- O conteúdo é centralizado verticalmente pelo maior elemento do prompt, com
  padding explícito em X/Y.
- `desenhar_prompts` repassa escala, padding, fundo e espaçamentos, mantendo os
  valores padrão anteriores para o inventário.
- `limpar_cache` também limpa as superfícies escaladas.

### `core/menu.py`

- Constantes de escala e legibilidade:
  - rodapé/slot: `1.25` (A), fonte `18`;
  - modal: `1.50` (B), fonte `20`.
- Rodapé e slot usam fundo discreto `(10, 10, 14, 80)`; o modal usa
  `(18, 16, 22, 140)`.
- Gaps ícone/texto passaram de `6` para `9` (A) e `11` (B); gap entre ícones
  passou de `2` para `4`/`5`.
- Padding: `(5, 3)` no rodapé/slot e `(8, 5)` no modal.
- Posições ajustadas para manter os prompts dentro das áreas originais:
  - rodapé em `y=670`;
  - prompt DELETE no slot em `top+70`;
  - prompts do modal em `painel.top+74`.

O inventário continua chamando `desenhar_prompts` sem os novos parâmetros, ou
seja, mantém escala `1.0`, padding `0` e sem fundo adicional.

## 3. Escalas testadas

Dimensões do conjunto de prompts:

| Contexto | Atual | A (+25%) | B (+50%) | Escolha |
|---|---:|---:|---:|---|
| Rodapé (setas + ENTER) | 240×20 | 296×27 | 334×30 | **A** |
| Slot ocupado (DELETE) | 130×20 | 156×27 | 179×30 | **A** |
| Modal (ENTER + ESC) | 230×20 | 277×27 | 323×34 | **B** |

No rodapé final, o conjunto ocupa `296×27` em `y=670` e termina em `697`,
deixando 23 px de margem inferior. O prompt do slot termina em `x=872` e
`y=477`, dentro do slot de 500×110. O modal ocupa `323×34` a partir de
`y=364`, terminando em `398`, dentro do painel que vai até `430`.

## 4. Capturas

Comparações versionáveis (sem lygame):

- `menu_e21_comparativo_rodape_fallback.png`
- `menu_e21_comparativo_slot_fallback.png`
- `menu_e21_comparativo_modal_fallback.png`
- `menu_e21_ajustado_fallback_vazio.png`
- `menu_e21_ajustado_fallback_ocupado.png`
- `menu_e21_ajustado_fallback_confirmar_delete.png`

Comparações locais, não versionáveis (contêm lygame):

- `menu_e21_comparativo_rodape_lygame.png` - atual × A × B
- `menu_e21_comparativo_slot_lygame.png` - atual × A × B
- `menu_e21_comparativo_modal_lygame.png` - atual × A × B
- `menu_e21_candidato_a_lygame_ocupado.png`
- `menu_e21_candidato_b_lygame_ocupado.png`
- `menu_e21_candidato_a_lygame_confirmar_delete.png`
- `menu_e21_candidato_b_lygame_confirmar_delete.png`
- `menu_e21_ajustado_lygame_vazio.png`
- `menu_e21_ajustado_lygame_ocupado.png`
- `menu_e21_ajustado_lygame_confirmar_delete.png`

As capturas com save ocupado usam um gerenciador falso em memória; `saves.db`
não foi escrito. As imagens com lygame permanecem fora do Git.

## 5. Testes

Novo arquivo `tests/test_prompts_teclas.py`:

- dimensões arredondadas de ENTER em `1.25` e `1.5`;
- escala nearest-neighbor sem introduzir cores novas;
- padding/fundo aumentando a área do prompt;
- `desenhar_prompts` com escala e padding.

Validação executada:

- `python -m pytest -q`: **180 testes passaram**.
- `git diff --check`: sem erros de whitespace.
- Nenhuma escrita em `saves.db` e nenhum commit criado.

## 6. Arquivos modificados

- `core/menu.py`
- `ui/prompts_teclas.py`
- `tests/test_prompts_teclas.py` (novo)
- `docs/arte/RELATORIO_FASE_E2_1_PROMPTS_TECLA.md` (novo)
- `docs/arte/RELATORIO_FASE_E2_MENU_MOLDURAS.md`
- `docs/arte/previews/README.md`
- `docs/arte/INVENTARIO_SPRITES.md`
- `docs/arte/ASSETS_UI_ORIGENS.md`

Não foram alterados: molduras da E.2, halos da E.1, `save_manager.py`,
`main.py`, inventário, HUD, combate ou áudio.

## 7. Pendências

1. Avaliação visual para confirmar A no rodapé/slot e B no modal.
2. Se o rodapé parecer grande demais, reduzir apenas o padding ou voltar a
   escala para `1.0`; o parâmetro já é configurável.
3. Se o modal ainda estiver apertado, testar fonte `21` ou padding `(9, 6)`.
