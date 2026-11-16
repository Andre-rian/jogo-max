# Relatório - Fase E.0: menu principal e seleção de saves

Data: 15/11/2026  
Branch: `sprites`  
Status: **análise visual concluída; nenhuma integração funcional ou escolha final**.  
Escopo: capturar o menu atual, comparar molduras para os três slots, avaliar
estados de botão, prompts de teclado e a interferência dos halos roxos no título
e nos saves.

## 1. Restrições respeitadas

- `core/menu.py`, `save_manager.py`, `main.py`, `ui/estilo.py` e
  `ui/prompts_teclas.py` **não foram alterados**.
- Nenhum item, save, personagem, inventário, HUD ou combate foi modificado.
- Nenhum asset foi promovido para `assets/sprites/ui/`.
- Nenhuma dependência nova foi adicionada.
- `saves.db` não foi escrito; as capturas com save ocupado usam um gerenciador
  falso em memória.
- Nenhum commit foi criado.

## 2. Menu atual

O “menu principal” e a “seleção de saves” são a mesma tela: `MenuInicial`, em
`core/menu.py`. Não existe uma cena separada de seleção de save.

- Título `PROFANE ECHO` em `(640, 58)`, fonte de 78 px.
- Subtítulo em `y=146` e linha ornamental em `y=176`.
- Três slots de `500×110`, em `x=390`, com `y=240`, `380` e `520`.
- Cada slot já mostra “Novo Jogo” ou “Continuar”, sala e data.
- A seleção usa borda `Azul_claro` e o símbolo `desenhar_eco_profano`.
- O rodapé atual usa texto com `↑↓` do sistema, sem sprites de tecla.
- `saves.db` está vazio no momento: a consulta read-only não retornou linhas.

Capturas da classe real:

| Arquivo | Conteúdo | Dimensão |
|---|---|---|
| [`previews/menu_e0_atual_vazio.png`](previews/menu_e0_atual_vazio.png) | Menu com os três slots vazios | 1280×720 |
| [`previews/menu_e0_atual_ocupado.png`](previews/menu_e0_atual_ocupado.png) | Dois saves sintéticos e slot 2 selecionado | 1280×720 |
| [`previews/menu_e0_atual_confirmar_delete.png`](previews/menu_e0_atual_confirmar_delete.png) | Overlay de confirmação de exclusão | 1280×720 |

## 3. Achado principal: os halos roxos não são suaves

O menu chama `adicionar_brilho` para o título e `desenhar_fundo` para o halo
central. As duas funções usam `pygame.BLEND_ADD`; nos testes, o alpha por pixel
e o alpha de superfície não modularam a adição. O resultado é uma cor roxa cheia
onde deveria haver um gradiente.

- Halo do título: raio 320, centro `(640, 84)`. Cobre praticamente todo o título
  e o subtítulo com roxo sólido.
- Halo central: raio 230, centro `(640, 470)`. Cobre o slot 2, parte do slot 3 e
  os vãos entre slots.
- Os dois halos se sobrepõem perto de `y=360`, produzindo roxo muito claro
  (amostra: `(174, 120, 255)`).

Impacto medido nos pixels dos glifos, com a mesma paleta:

| Elemento | Contraste mediano atual | Contraste com halo corrigido |
|---|---:|---:|
| Título (`Roxo_espectral`) | **1,37:1** | **2,56:1** |
| Subtítulo (`Cinza_texto_escuro`) | **1,55:1** | **2,92:1** |
| Borda selecionada (`Azul_claro`) sobre halo claro | **1,07:1** | 5,77:1 sobre fundo base |

Leitura: o problema não é a paleta em si, mas o blending. O título roxo sobre
roxo sólido perde separação; a borda azul do slot selecionado quase desaparece
quando cruza o halo central.

Recomendação para etapa funcional separada: corrigir `adicionar_brilho` e o halo
de `desenhar_fundo` para respeitar alpha (premultipliar a cor antes de
`BLEND_ADD`, ou usar blending alpha normal). Depois disso, reavaliar as molduras.

Correção aplicada na Fase E.1: ver
[`RELATORIO_FASE_E1_HALOS_MENU.md`](RELATORIO_FASE_E1_HALOS_MENU.md).

Prévia: [`previews/menu_e0_legibilidade.png`](previews/menu_e0_legibilidade.png)
(1600×1080), com quatro variantes: atual, alpha correto, sem halo atrás do
título e alpha + faixa escura.

## 4. Molduras para os três slots

Foram testados recortes reais dos packs, sempre em prévias locais:

- **AbyssOwl**: `large_ornate_frame1..4`, aplicados em 9-slice com margem de
  12 px; seleção com `small_selector_01` (AB037) + contorno `Azul_claro`.
  - `frame1` e `frame2` têm preenchimento escuro; `frame3` tem centro vazado;
    `frame4` é uma variante compacta.
  - Melhor encaixe visual inicial: `frame1` para slot normal e `frame3` para
    seleção, mantendo `frame4` como alternativa. A escolha final fica com o
    responsável.
- **lygame**: `Frame1.png` e `Frame1Empty.png`, simples e coerentes com o
  `Panel1.png` já usado no inventário. Menos ornamentado; licença restrita.
- **Kibyra**: não possui molduras, painéis ou slots; os 16 ícones de menu
  `64×32` (KB193–KB208) servem para ícone + rótulo, não para moldura.
- **Hypnobius**: tilesheet de UI com licença de uso sem redistribuição; não foi
  escolhido para esta rodada.
- **Ruins Xianxia**: pasta vazia/não baixada; não avaliado.

Prévias locais (não versionar):

| Arquivo | Conteúdo | Dimensão |
|---|---|---|
| [`previews/menu_e0_mock_abyssowl_restrito.png`](previews/menu_e0_mock_abyssowl_restrito.png) | Menu com frame1, frame3 selecionado e frame4 | 1280×720 |
| [`previews/menu_e0_mock_lygame_restrito.png`](previews/menu_e0_mock_lygame_restrito.png) | Menu com Frame1Empty/Frame1 | 1280×720 |
| [`previews/menu_e0_molduras_restrito.png`](previews/menu_e0_molduras_restrito.png) | 7 opções de moldura, normal e selecionada | 1600×1280 |
| [`previews/menu_e0_kibyra_icones_restrito.png`](previews/menu_e0_kibyra_icones_restrito.png) | KB193–KB208 ampliados | 1600×820 |

## 5. Botões: normal, selecionado e desabilitado

O menu atual não tem botões de ação separados; os slots funcionam como alvos de
seleção. Os estados abaixo são uma simulação de componente para a próxima etapa.

- **Atual procedural**: `desenhar_botao` distingue normal/selecionado, mas o
  selecionado também sofre com o halo rígido. Não há estado desabilitado nativo.
- **AbyssOwl**: não tem botão explícito; a moldura + texto funciona, mas exige
  desenho de estado. O seletor ajuda no foco.
- **lygame**: `Button1.png` é um retângulo de 48×20, adequado para 9-slice;
  simples, porém pouco expressivo e restrito.
- **Kibyra**: ícones de menu não são botões; usar apenas como ícone + rótulo.

Prévia: [`previews/menu_e0_botoes_restrito.png`](previews/menu_e0_botoes_restrito.png)
(1600×900), com quatro famílias em três estados.

Recomendação: não adicionar botões novos na E.0. Se forem necessários, preferir
AbyssOwl para moldura ou lygame `Button1` para um botão discreto, sempre com
estado selecionado sem halo rígido e estado desabilitado com contraste mínimo.

## 6. Prompts de teclado

- O inventário já usa `ui/prompts_teclas.py`, com recortes reais de
  `greatdocbrown gdb-keyboard-2.png` (CC0) e fallback desenhado.
- Reutilizáveis hoje: setas, TAB e ESC.
- **Lacuna:** não há recortes de ENTER e DELETE em `_RECORTES`. A prévia usa
  fallback no mesmo estilo (fundo grafite, contorno azul, rótulo claro).
- O rodapé atual usa `↑↓` como texto; em fontes sem esses glifos pode aparecer
  como quadrado. A troca por prompts gráficos elimina esse risco.

Prévia: [`previews/menu_e0_prompts.png`](previews/menu_e0_prompts.png)
(1600×620), comparando o texto atual, o reuso direto do inventário e a proposta
com ENTER/DEL.

Recomendação: reutilizar setas/ESC do inventário e, se aprovado, adicionar
recortes reais de ENTER/DEL em etapa funcional separada.

## 7. Origens, licenças e limites

| Pack | Origem | Uso na E.0 | Licença / limite | Versionar? |
|---|---|---|---|---|
| AbyssOwl Gothic Pixel UI | https://abyssowl.itch.io/gothic-pixel-ui | Molduras, seletor | Sem arquivo de licença no pacote; confirmar antes de promover | Não |
| Kibyra Medieval Fantasy UI | https://kibyra.itch.io/free-medieval-fantasy-ui-pack | Ícones de menu | Readme: uso pessoal/comercial; crédito apreciado; redistribuição/revenda proibida | Não |
| lygame Dark Fantasy UI | https://lygame.itch.io/dark-fantasy-free-pixel-art-assets | Frame1/Frame1Empty/Button1 | Uso em jogos permitido; proibido revender/redistribuir | Não |
| Hypnobius Dark Ages UI | https://hypnobius.itch.io/ | Não usado | Própria: uso sem redistribuir | Não |
| Ruins Xianxia Pixel UI | https://ruins0707.itch.io/xianxia-pixel-ui | Não avaliado | A confirmar; pasta não baixada | Não |
| greatdocbrown Gamepad UI | https://greatdocbrown.itch.io/gamepad-ui | Prompts | CC0 | Sim (já versionado) |

As prévias com AbyssOwl, Kibyra e lygame estão cobertas por
`docs/arte/previews/*restrito*.png` no `.gitignore` e permanecem locais.

## 8. Arquivos gerados

Versionáveis:

| Arquivo | Conteúdo | Dimensão |
|---|---|---|
| `docs/arte/previews/menu_e0_atual_vazio.png` | Menu real, slots vazios | 1280×720 |
| `docs/arte/previews/menu_e0_atual_ocupado.png` | Menu real com dados sintéticos | 1280×720 |
| `docs/arte/previews/menu_e0_atual_confirmar_delete.png` | Overlay de exclusão | 1280×720 |
| `docs/arte/previews/menu_e0_legibilidade.png` | Comparação de halos/faixa escura | 1600×1080 |
| `docs/arte/previews/menu_e0_prompts.png` | Comparação de prompts | 1600×620 |

Locais, não versionáveis:

| Arquivo | Conteúdo | Dimensão |
|---|---|---|
| `docs/arte/previews/menu_e0_mock_abyssowl_restrito.png` | Mock com AbyssOwl | 1280×720 |
| `docs/arte/previews/menu_e0_mock_lygame_restrito.png` | Mock com lygame | 1280×720 |
| `docs/arte/previews/menu_e0_molduras_restrito.png` | Ficha de molduras | 1600×1280 |
| `docs/arte/previews/menu_e0_botoes_restrito.png` | Ficha de botões | 1600×900 |
| `docs/arte/previews/menu_e0_kibyra_icones_restrito.png` | Ícones de menu Kibyra | 1600×820 |

## 9. Validação

- Capturas geradas a partir de `MenuInicial` real; dados de save são falsos e
  não tocam em `saves.db`.
- Nenhum código funcional alterado.
- Nenhum asset novo em `assets/sprites/`.
- Dimensões conferidas: capturas 1280×720; fichas 1600× variável.
- `docs/arte/previews/README.md`, `INVENTARIO_SPRITES.md`, `ASSETS_UI_ORIGENS.md`
  e `.gitignore` atualizados.
- `git diff --check` passou sem erros.
- `python -m pytest -q`: **170 testes passaram**.
- Nenhum commit criado.

## 10. Decisão pendente

Nenhuma moldura, botão ou prompt foi adotado. A escolha final deve considerar:

1. corrigir primeiro o blending dos halos;
2. escolher a família principal de moldura (AbyssOwl, lygame ou híbrido);
3. decidir se os ícones Kibyra entram como complemento;
4. aprovar ou não os prompts com ENTER/DEL em etapa funcional separada.

Até a avaliação do responsável, o menu atual permanece intocado.
