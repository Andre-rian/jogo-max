# Relatório - Fase E.1: correção dos halos do menu

Data: 15/11/2026  
Branch: `sprites`  
Status: **halos corrigidos e validados; molduras, slots e saves não alterados**.  
Decisão aplicada: halo com alpha real, preservando o gradiente roxo e a
atmosfera escura; o efeito de círculos sólidos foi removido.

## 1. Escopo

- Corrigir somente a composição dos halos do `MenuInicial`.
- Preservar centros, raios e intensidades planejadas.
- Manter o halo central em `y=470`.
- Não substituir molduras, botões ou prompts.
- Não alterar lógica de saves, banco, inventário, HUD, combate ou áudio.
- Não criar commit.

## 2. Implementação

### `ui/estilo.py`

- Adicionado `_aplicar_brilho_alpha`, que aplica o alpha de superfície e faz
  blit RGBA normal, sem `BLEND_ADD`.
- `adicionar_brilho` ganhou `alpha_real=False`:
  - `False` mantém o comportamento anterior para telas fora do menu;
  - `True` usa a composição com alpha real.
- `desenhar_fundo` agora aplica o halo central com alpha real e centro explícito
  em `(640, 470)`, raio `230`, alpha `20..36`.
- `desenhar_eco_profano` ganhou o mesmo parâmetro opcional para que os pequenos
  halos do menu também tenham borda suave; o padrão continua preservando o uso
  atual no inventário/HUD.

### `core/menu.py`

- Título e símbolos do menu passam a usar `alpha_real=True`.
- O halo central foi preservado em `y=470`; o halo do título continua em
  `(640, 84)`, raio `320`, intensidade `0.22`.
- Ajuste discreto de contraste, sem trocar a paleta:
  - título: `clarear(Roxo_espectral, 0.08)`;
  - subtítulo: `clarear(Cinza_texto_escuro, 0.12)`.

O caminho antigo com `BLEND_ADD` continua disponível para outras telas, evitando
mudanças não solicitadas no inventário, HUD, pausa ou menu de fogueira.

## 3. Capturas antes/depois

Todas foram geradas a partir de `MenuInicial`, com `frame=48`. As capturas com
save ocupado usam um gerenciador falso em memória; `saves.db` não foi escrito.

| Estado | Antes | Depois |
|---|---|---|
| Slots vazios | `menu_e1_antes_vazio.png` | `menu_e1_depois_vazio.png` |
| Dois saves sintéticos | `menu_e1_antes_ocupado.png` | `menu_e1_depois_ocupado.png` |
| Confirmação de exclusão | `menu_e1_antes_confirmar_delete.png` | `menu_e1_depois_confirmar_delete.png` |

Comparativo: `menu_e1_comparativo.png` (1400×1360), com os três pares.

As capturas estão em `docs/arte/previews/` e não contêm assets restritos.

## 4. Medições de contraste

Contraste calculado entre a cor do texto e o fundo nos pixels dos glifos, sem
desenhar o texto sobre a amostra.

| Elemento | Antes (mediana) | Depois (mediana) | Depois (p10) | Depois (mín.) |
|---|---:|---:|---:|---:|
| Título | 1,37:1 | **3,08:1** | 3,04:1 | 2,66:1 |
| Subtítulo | 1,55:1 | **3,85:1** | 3,82:1 | 3,80:1 |

A borda interna clara do slot selecionado (`Azul_claro`) passou de **1,14:1**
para **3,65:1** contra o fundo imediatamente externo. A borda externa escura
ficou mais discreta (`3,67:1` → `1,13:1`), mas a definição da seleção agora vem
da linha interna clara e dos cantos, que permanecem visíveis.

## 5. Gradiente e ausência de círculos sólidos

Perfis de luminância medidos nas capturas:

| Amostra | Antes | Depois |
|---|---|---|
| Linha `y=200` (halo do título): maior salto entre pixels | `0,0535` | `0,0029` |
| Linha `y=360` (cruzamento dos halos): maior salto | `0,1429` | `0,0037` |
| Níveis de luminância em `y=200` | 7 | 16 |
| Níveis de luminância em `y=360` | 69 | 74 |

O antes tinha região praticamente plana e salto brusco na borda; o depois tem
queda gradual. O halo central foi mantido em `y=470` e o raio de `230` foi
preservado.

## 6. Tela de confirmação

- Captura gerada com o overlay de exclusão e o painel central.
- O overlay escurece o fundo e não interfere no gradiente dos halos.
- O painel continua sobreposto corretamente, sem clipping de texto.
- O alerta vermelho mantém o contraste anterior de aproximadamente `2,57:1`
  sobre `Cinza_carvao`; não foi alterado nesta fase para não ampliar o escopo.
  Se desejado, pode ser clareado em uma etapa de acessibilidade visual.

## 7. Testes

Novo arquivo `tests/test_estilo_halos.py`:

- `test_halo_com_alpha_tem_queda_gradual`: verifica valores decrescentes do
  centro para a borda e pelo menos três níveis de intensidade.
- `test_halo_central_continua_em_y_470`: isola o fundo, mede o gradiente vertical
  e confirma o centro em `y=470`.

Validação executada:

- `python -m pytest -q`: **172 testes passaram**.
- `git diff --check`: sem erros de whitespace.
- Capturas geradas com dados sintéticos; nenhuma escrita em `saves.db`.
- Nenhum commit criado.

## 8. Arquivos modificados

- `core/menu.py`
- `ui/estilo.py`
- `tests/test_estilo_halos.py` (novo)
- `docs/arte/RELATORIO_FASE_E1_HALOS_MENU.md` (novo)
- `docs/arte/previews/README.md`
- `docs/arte/INVENTARIO_SPRITES.md`
- `docs/arte/previews/menu_e1_*.png` (antes/depois/comparativo)

Não foram modificados: `save_manager.py`, `main.py`, `core/inventario.py`,
`ui/overlays.py`, HUD, combate, áudio, molduras ou assets de UI.

## 9. Pendências

1. Escolher a família de molduras dos slots (AbyssOwl, lygame ou híbrido) em
   etapa posterior.
2. Definir prompts definitivos de ENTER/DELETE e a troca do rodapé textual.
3. Avaliar, se necessário, o contraste do alerta vermelho da confirmação de
   exclusão.
4. Avaliar o menor contraste do título nos pixels de antialiasing (`2,66:1`);
   a mediana e o p10 já estão acima de `3:1`.
