# Relatório - Fase E.2: molduras, prompts e alerta do menu

Data: 15/11/2026  
Branch: `sprites`  
Status: **implementação experimental concluída; escolha visual final pendente**.  
A moldura lygame nos slots, os prompts reais de ENTER/DELETE e o alerta vermelho
mais claro estão funcionando, mas permanecem sujeitos à avaliação visual do
usuário antes de serem tratados como definitivos.

> Atualização E.2.1: os prompts foram ampliados para A (+25%) no rodapé/slot e
> B (+50%) no modal. Ver
> [`RELATORIO_FASE_E2_1_PROMPTS_TECLA.md`](RELATORIO_FASE_E2_1_PROMPTS_TECLA.md).

## 1. Escopo

- Avaliar `Frame1.png` e `Frame1Empty.png` do pack lygame para os slots de save.
- Aplicar uma moldura escura com contorno frio/prateado, preenchimento grafite e
  bordas discretas, sem dourado/bege.
- Usar prompts reais de teclado no rodapé, no hint de apagar e na confirmação.
- Melhorar discretamente o contraste do alerta vermelho da confirmação.
- Manter os halos da E.1, a lógica de saves, o banco, o inventário, o HUD, o
  combate e o áudio sem alterações.
- Não criar commit.

## 2. Implementação

### `ui/moldura_menu_lygame.py` (novo)

- 9-slice experimental com margem `5` e bordas tiled.
- Estados: `vazio`, `ocupado`, `selecionado_vazio` e `selecionado_ocupado`.
- `Frame1Empty.png` é usado nos estados vazios/ocupados não selecionados e no
  selecionado vazio; `Frame1.png` é usado no selecionado ocupado.
- As cores originais quentes do pack são remapeadas para uma paleta fria:
  contorno prateado-azulado, contorno interno azul-acinzentado e preenchimento
  grafite.
- Cache por estado e fallback automático: se o asset faltar, o módulo retorna
  `False` e o menu desenha a moldura anterior.

### `core/menu.py`

- Novo interruptor `USAR_MOLDURA_LYGAME = True`.
- Cada slot chama `desenhar_moldura_slot` com os estados `selecionado` e
  `ocupado`; se a moldura não estiver disponível, usa `desenhar_painel`.
- O eco esquerdo do slot selecionado foi preservado.
- O hint textual `DEL p/ apagar o save` foi substituído por prompt de tecla com
  o fallback `DEL` em vermelho mais claro.
- O rodapé agora usa setas reais + ENTER; a confirmação usa ENTER/ESC reais.
- O título do alerta passou de `Vermelho_ritual` para
  `clarear(Vermelho_ritual, 0.30)`; o texto do prompt de apagar usa
  `clarear(Vermelho_ritual, 0.40)`.

### `ui/prompts_teclas.py`

- Recorte real de ENTER em `(244, 64, 24, 16)`; TAB ajustado para
  `(36, 48, 24, 16)`.
- DELETE continua sem recorte no spritesheet e usa fallback desenhado `DEL`
  com `33×16` no tamanho padrão da fonte.
- Os prompts passam a ser usados também no `MenuInicial`, além do inventário.

## 3. Comparação dos dois assets

| Asset | Característica | Uso escolhido |
|---|---|---|
| `Frame1Empty.png` (LY008) | Centro transparente e borda dupla; permite controlar o preenchimento | Vazio, ocupado não selecionado e selecionado vazio |
| `Frame1.png` (LY007) | Centro preenchido e borda mais pesada | Selecionado ocupado |

A combinação escolhida evita que os três slots pareçam blocos sólidos iguais:
os estados não selecionados recebem preenchimento grafite próprio, enquanto o
slot selecionado ocupado usa o `Frame1` para ganhar densidade. O contorno foi
suavizado após a primeira renderização para evitar brilho excessivo.

Alternativas descartadas nesta etapa:

- `Frame1` em todos os estados: pesado demais e reduz a distinção entre slots
  vazios e ocupados.
- `Frame1Empty` em todos os estados: funcional, mas o selecionado ocupado perde
  densidade em relação às outras combinações.

## 4. Capturas

Versionáveis (sem assets lygame, demonstram o fallback):

- `menu_e2_fallback_vazio.png` (1280×720)
- `menu_e2_fallback_ocupado.png` (1280×720)
- `menu_e2_fallback_confirmar_delete.png` (1280×720)

Locais, não versionáveis (contêm lygame):

- `menu_e2_lygame_vazio.png` (1280×720)
- `menu_e2_lygame_ocupado.png` (1280×720)
- `menu_e2_lygame_confirmar_delete.png` (1280×720)
- `menu_e2_comparativo_lygame.png` (1840×860) - E.1 antes × E.2 depois
- `menu_e2_estados_molduras_lygame.png` (1080×360) - os quatro estados

As capturas ocupadas usam um gerenciador falso em memória; `saves.db` não foi
escrito. As imagens com lygame ficam fora do Git pelos padrões `*lygame*.png` e
`*restrito*.png`.

## 5. Contraste

Contraste calculado entre a linha clara da moldura e o preenchimento interno do
slot.

| Estado | Linha clara | Preenchimento | Contraste |
|---|---|---:|---:|
| Vazio | `(134, 142, 164)` | `(27, 28, 34)` | 5,19:1 |
| Ocupado | `(150, 158, 180)` | `(33, 35, 44)` | 5,85:1 |
| Selecionado vazio | `(160, 184, 218)` | `(36, 40, 52)` | 7,26:1 |
| Selecionado ocupado | `(160, 184, 218)` | `(38, 42, 54)` | 7,06:1 |

O alerta vermelho da confirmação passou de `2,57:1` para **4,68:1** contra
`Cinza_carvao`. O texto do prompt de apagar usa a variante de `5,81:1`.

## 6. Testes

Novos testes:

- `tests/test_moldura_menu_lygame.py`: disponibilidade, quatro estados distintos
  e fallback quando o asset não é encontrado.
- `tests/test_ui_audio.py::test_menu_inicial_desenha_com_e_sem_moldura_lygame`:
  renderização do menu com a moldura ativa, com fallback e na confirmação de
  exclusão.

Validação executada:

- `python -m pytest -q`: **176 testes passaram**.
- `git diff --check`: sem erros de whitespace.
- Nenhuma escrita em `saves.db` e nenhum commit criado.

## 7. Arquivos modificados

- `core/menu.py`
- `ui/moldura_menu_lygame.py` (novo)
- `ui/prompts_teclas.py`
- `tests/test_moldura_menu_lygame.py` (novo)
- `tests/test_ui_audio.py`
- `docs/arte/RELATORIO_FASE_E2_MENU_MOLDURAS.md` (novo)
- `docs/arte/previews/README.md`
- `docs/arte/INVENTARIO_SPRITES.md`
- `docs/arte/ASSETS_UI_ORIGENS.md`

Não foram alterados: `save_manager.py`, `main.py`, sistema de halos da E.1,
inventário, HUD, combate ou áudio.

## 8. Pendências

1. Avaliação visual do usuário para confirmar a combinação `Frame1Empty` +
   `Frame1` ou testar uma variante mais escura/menos brilhante.
2. Decidir se a moldura experimental será promovida a definitiva ou mantida
   atrás do interruptor.
3. Substituir o fallback `DEL` se um recorte adequado de DELETE for encontrado
   no spritesheet.
