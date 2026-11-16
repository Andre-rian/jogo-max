# Relatório — Fase C: acabamento do inventário

Data: 2026-11-14 (finalizado em 2026-11-15)
Status: **concluída** — LY005 1× adotado, com fallback automático para a moldura
anterior.
Escopo: legibilidade e acabamento visual do inventário, preservando lógica,
navegação, áudio, salvamento e identidade do menu principal. Nenhum commit foi
criado.

## 1. Círculos roxos atrás do inventário

Causa identificada: o brilho radial de `desenhar_botao` era aplicado à aba
selecionada em um raio grande, criando um halo roxo que escapava do painel. O
slot selecionado também desenhava um segundo halo radial.

Correção:

- `ui/estilo.py`: `desenhar_botao` ganhou `brilho=True`; o comportamento padrão
  (menu principal, pausa etc.) permanece inalterado.
- `core/inventario.py`: abas chamam `desenhar_botao(..., brilho=False)` e o halo
  do slot selecionado foi removido. A seleção continua indicada por fundo e
  borda azul.
- Validação por pixel nas três capturas: **0 pixels roxos** fora da área do
  painel/abas (antes eram 14.151 na captura de equipamentos).

## 2. Rótulo e contraste

- Quarta aba corrigida de `materias` para **Materiais**.
- Criada cor secundária (`misturar(Cinza_texto, Branco_texto, 0.28)`) para
  descrições, rótulos de atributos, status, estado vazio e instruções.
- Valores de atributos continuam em `Branco_texto`; nenhuma cor de destaque foi
  alterada.

## 3. Prompts de teclado no rodapé

- Novo módulo `ui/prompts_teclas.py`.
- Recorta em runtime as teclas de
  `assets/sprites/_entrada/prompts/greatdocbrown_gamepad_ui/gdb-keyboard-2.png`
  (greatdocbrown Gamepad UI, CC0): setas, Tab e Esc.
- Cache de `Surface`; nenhum recorte por frame.
- Fallback desenhado com rótulos `ESC`, `TAB`, `<`, `>`, `^`, `v` caso o
  spritesheet não esteja presente.
- Textos associados: “navegar”, “trocar aba” e “fechar”, com as teclas reais já
  usadas por `Inventario.atualizar`.

## 4. Ícones nos slots equipados

- `core/inventario.py`: slots Mão Direita, Mão Esquerda e Armadura exibem um
  ícone 26×26 do item equipado, alinhado à direita.
- Nomes passaram para a fonte pequena para não colidir com o ícone; “Dano”
  continua visível.
- `ui/icones.py`: sprites maiores que o slot agora são reduzidos com
  `pygame.transform.scale`; slots de 60×60 continuam usando o sprite 48×48 sem
  alteração. Contagem de cargas/quantidade preservada.
- Lógica de equipar/desequipar não foi alterada.

## 5. LY005 e LY006 (avaliação)

As primeiras comparações eram inválidas: o gerador temporário apagava a área
interna com `pygame.draw.rect(..., (0, 0, 0, 0), ...)` em uma surface opaca, o
que pintava o painel de preto. A investigação confirmou que o 9-slice estava
correto; o defeito era exclusivamente do script de prévia. As imagens foram
refeitas e analisadas.

Validação programática registrada na época: moldura cream com 5.392 px em 1× e
10.679 px em 2×; centro grafite uniforme; nenhuma área apagada. A contagem de
pixels de texto ficou idêntica à referência (202 brancos e 1.113 secundários),
indicando que a moldura não cobriu o conteúdo. Contraste sobre o grafite:
11,1:1 (branco) e 6,8:1 (secundário), acima de WCAG AA. Os quatro ícones têm
24×24 com alpha preservado; o fallback da Umbrita tem 388 px opacos.

As prévias dessa etapa eram temporárias e foram removidas em 15/11/2026 após a
aprovação visual, para não serem confundidas com capturas futuras. Imagens com
asset lygame continuam proibidas no Git; a licença permite uso em jogos, mas não
redistribuição.

## 6. Capturas

As capturas e comparações geradas durante a Fase C foram removidas em 15/11/2026
após a aprovação visual. O diretório `docs/arte/previews/` é temporário e contém
apenas orientação de uso; novas capturas devem ser geradas a partir da classe
`Inventario` real e apagadas/substituídas ao concluir cada etapa.

Imagens que contenham lygame ou outros packs restritos não devem ser
versionadas.

## 7. Testes

- Fase C.1: `python -m pytest -q tests/test_inventario_sprites.py tests/test_ui_audio.py tests/test_interaction_audio.py` → **28 passed**.
- `python -m pytest -q` → **169 passed** (`exit=0`).
- Reexecução na finalização (15/11): **28 passed**, **169 passed** e fallback sem
  `Panel1.png` validado (0 px de cream, sem exceção).
- `python -m py_compile` nos arquivos alterados → sem erros.
- Contraste textual sobre o grafite: **11,1:1** (branco) e **6,8:1**
  (secundário), acima de WCAG AA.
- Nenhuma lógica de combate, inventário, salvamento ou áudio foi alterada.

## 8. Fase C.2 — integração e adoção do LY005

O LY005 1× foi integrado ao inventário real e **aprovado visualmente**. O LY006
continua fora desta etapa; LY005 2× foi descartado.

- Novo módulo `ui/painel_lygame.py`: 9-slice de `Panel1.png` com margem 12,
  bordas tiled (sem esticar a pixel art), cache e fallback automático para a
  moldura anterior se o asset faltar.
- Paleta resfriada: cream `(200, 187, 162)` → `(196, 199, 210)`; cinzas
  intermediários também receberam leve viés azul-acinzentado. Preenchimento
  grafite preservado em `(30, 31, 37)`.
- `core/inventario.py`: constante `USAR_PAINEL_LYGAME = True` e flag por
  instância. Para voltar à moldura anterior, basta definir a constante como
  `False` ou usar `inventario.usar_painel_lygame = False`.
- Quando o LY005 está ativo, o conteúdo interno é deslocado 6 px para dentro
  (topo/esquerda) e os prompts sobem 6 px. Abas, slots equipados, grid,
  descrições, status e ícones não foram alterados; as hitboxes do mouse usam o
  mesmo deslocamento.
- Validação geométrica: 5.392 px de cream na moldura; **0 px de cream na área
  interna**; abas idênticas à versão anterior (0 px de diferença); prompts com
  333×16 px em y=588..604, antes da linha interna em y=608; nenhum texto ou
  ícone removido.
- Capturas reais foram geradas para Equipamentos, Itens e Materiais e removidas
  após a aprovação, junto das comparações com a moldura anterior.
- Validação interativa: troca de abas, hover/clique nos slots, abertura do menu,
  equipar, descrições/status e prompts passaram em script dedicado.
- LY005 1× é a aparência padrão quando `Panel1.png` está disponível; se o asset
  não existir, a moldura anterior é usada automaticamente. Nenhum commit foi
  criado.

## 9. Conclusão e pendências

**Fase C concluída em 15/11/2026.**

1. LY005 1× adotado como moldura preferencial do inventário, com grafite e
   contorno frio preservados.
2. Moldura anterior mantida como fallback automático; rollback manual disponível
   por `USAR_PAINEL_LYGAME = False`.
3. LY005 2× descartado; LY006 1× reservado para futuros menus menores.
4. Umbrita (ID 5) continua usando o fallback até receber sprite aprovado.
5. Capturas antigas removidas para evitar confusão com novas prévias.
6. Sem commits, conforme solicitado.
