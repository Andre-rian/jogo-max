# PROFANE ECHO — Fase G: menus, interações e Ecofoco experimental

Data: 16/11/2026. Branch: `sprites`. Base: `e8d7ef1` (F.3), confirmada
também no remoto antes da publicação. Nenhum AGENTS.md encontrado.
Relatórios C–F.3 e estado real do repositório consultados.

## Resultado

- Pausa: painel grafite 440×450, cena visível pelo overlay de alpha 130,
  halos com alpha real da E.1 e botões sem brilho aditivo. Cinco opções
  preservadas. Retângulos 320×42 com passo 52 compartilhados pelo desenho,
  hover e clique. Clique externo não executa a opção selecionada.
- ESC permanece controlado por `main.py`: a cena não processa novamente o
  evento que acabou de abrir a pausa. Teste cobre essa sequência.
- Interações: tecla E real do spritesheet existente, painel F.3, escala 1,5,
  cache, fallback gráfico e quebra de textos extensos. Mantida a faixa de
  prompts abaixo das notificações. Dicas ocultas durante pausa, inventário,
  menu do Ecofoco e morte; removidas ao sair do alcance ou iniciar a ação.
- Disputa por E: escolha determinística na ordem histórica (baús, drops,
  Ecos perdidos, fogueiras, portas; ordem da lista dentro de cada grupo).
  Somente o escolhido recebe E e pode mostrar/limpar o prompt. Os outros
  continuam atualizando animações. Um objeto distante não apaga a indicação.
  Cooldown bloqueia a indicação; baú em animação retém prioridade sem dica.
- Ecofoco: menu principal grafite, botões 320×40, prompts gráficos, símbolo
  original D.1 e contraste maior. Evolução ganha espaço abaixo dos títulos,
  painel de atributos ampliado e hitboxes correspondentes dos controles.
  Valores `atual / projetado`, custo, atributos e cálculos preservados.

Não foram alterados os métodos de custo/compra/preview de evolução, regras
de cura, recompensas, áudio, combate, inventário ou saída/salvamento da pausa.
O helper `core/interacoes.py` apenas escolhe o destinatário e filtra as
chamadas de prompt; não substitui os métodos de interação dos objetos.

## Ecofoco na sala 2

Arquivo: `assets/maps/calabouco_2.tmx`, 80×23 tiles de 32 px.
Novo objeto id 4, `type="fogueira"`, em **(256,640)**, tile **(8,20)**,
com apoio no chão y=672 (linha 21). Próximo à entrada, corredor livre;
teste confere o volume do jogador desde x=64 até x=288 e o apoio do objeto.
Camadas `fundo` e `colisao` e objetos anteriores permanecem idênticos.
O TMX não tem camadas separadas de plataformas/escadas nessa sala.

Carregamento: posições TMX têm preferência; ausência de fogueiras TMX usa
a grade legada. Um conjunto de coordenadas elimina duplicação; a fogueira
da sala 4 permanece em (9,10), carregada pelo fallback existente.

Ativações novas usam `(sala, col, linha)` dentro do mesmo JSON de saves;
nenhuma coluna/migração de banco. Pares antigos `(col,linha)` continuam
válidos na sala 4, única sala com fogueira no legado, e não ativam a nova
fogueira da sala 2. Testada gravação/leitura de registros novos e leitura
de registros antigos em SQLite temporário.

O checkpoint agora guarda o canto superior esquerdo do jogador ao ativar.
Guardar o centro da fogueira como se fosse a posição do jogador podia
enterrá-lo no chão ao renascer. Testados checkpoint, reload do save,
renascimento sem colisão com sólidos, descanso, cura e recarga de poções.

## Validação

- Base: **264 testes passaram**.
- Final: **280 testes passaram**, incluindo **16 casos G**.
- `python -m pytest -o addopts='' -q --tb=short -p no:cacheprovider`.
- Testes G: pausa/teclado/hover/cliques, estados visuais, composição alpha,
  baú/porta/drop/Ecos/fogueira, alvo único em cena real, ocultação em menus,
  geometria TMX, descanso/checkpoint/SQLite/legado, evolução e fallback sem
  LY015, sem símbolo opcional e sem spritesheet de teclado.
- Suíte inclui regressões F.1–F.3, combate e áudio. Nenhuma falha restante.
- `git diff --check` passou. SHA-256 de `saves.db` e `jogo.log` preservados
  durante as capturas; hashes registrados nas evidências.

Ambiente: Python 3.14.7, pygame-ce 2.5.7; dependências não alteradas.
Uma falha de codificação UTF-8 na primeira edição e ajustes do gerador/testes
foram corrigidos antes da validação final, sem publicar versões quebradas.

## Capturas

Gerador: `python docs/arte/gerar_previews_g.py`. SDL dummy, 1280×720,
renderer real, posições e valores preparados em memória, sem `main` ou
gerenciador de saves. LY015 explicitamente desativado nas capturas.

- [Pausa anterior](previews/fase_g_pausa_antes_local.png)
- [Pausa nova](previews/fase_g_pausa_depois_local.png)
- [Menu de descanso](previews/fase_g_descanso_local.png)
- [Evolução](previews/fase_g_evolucao_local.png)
- [Baú da sala 2](previews/fase_g_bau_local.png)
- [Porta: cenário de teste](previews/fase_g_porta_local.png)
- [Sala 2 e Ecofoco com prompt](previews/fase_g_sala2_ecofoco_local.png)
- [Evidências e integridade](previews/fase_g_evidencias.json)

Os TMX atuais não instanciam portas. A captura de porta usa `Porta` real
adicionada somente à instância em memória, sem alterar mapas ou distribuição
de objetos. Isso é um cenário de validação, não uma nova porta entregue.
As sete imagens completas ficam locais/ignoradas por conterem arte de mundo.

## Origem dos assets

Nenhum asset externo novo ou restrito promovido. Tecla E: greatdocbrown
Gamepad UI, CC0, recorte `(96,48,16,16)` de `gdb-keyboard-2.png`, mesmo pack
usado no inventário/menu. Ampliação nearest-neighbor 1,5 para legibilidade.
Eco original D.1 reaproveitado via cache F.2. Painéis, botões e fallbacks
procedurais existentes. Licenças anteriores continuam aplicáveis.

## Arquivos

- Runtime: `ui/overlays.py`, `ui/prompts_teclas.py`, `ui/hud/mensagens.py`,
  `core/game_scene.py`, `core/menu_fogueira.py`, `core/interacoes.py`.
- Objetos: `entities/objetos/bau.py`, `porta.py`, `drop.py`, `drop_eco.py`,
  `fogueira.py` (textos/visibilidade; chave e checkpoint na fogueira).
- Mapa: `assets/maps/calabouco_2.tmx` (um objeto e nextobjectid).
- Verificação: `tests/test_fase_g.py`, `docs/arte/gerar_previews_g.py`,
  `docs/arte/referencias/overlays_antes_g.py`,
  `docs/arte/previews/fase_g_evidencias.json`.
- Documentação: este relatório, `docs/arte/previews/README.md`,
  `docs/arte/ASSETS_UI_ORIGENS.md`, `.gitignore`.

## Git e limites

Commit/push expressamente autorizados. Publicar somente os arquivos acima,
após revisão do índice; confirmar hash local contra `refs/heads/sprites`.
O resultado e hash definitivo ficam no relatório final e no recibo ignorado
`previews/fase_g_publicacao_local.json`, após resposta real do remoto.

Preservadas fora do commit: sete exclusões antigas de prévias/JSONs F.0 e
a alteração preexistente de `jogo.log`. Nenhum save/log/cache/pack restrito
incluído. Sem force push, reset, rebase ou merge na main.

Pendências: avaliação manual em fullscreen/DPI e sessão prolongada;
avisos preexistentes de PNG iCCP e camadas opcionais ausentes continuam.
A posição do Ecofoco é experimental; o redesenho geral do mapa ficou fora
do escopo. Saves novos são compatíveis com este código e o JSON existente;
versões antigas do jogo não reconhecerão chaves de fogueira com sala.


## Atualização G.1
- Implementação complementar de prompts no mundo e ajustes de áudio UI realizada em etapa posterior; ver `docs/arte/RELATORIO_FASE_G1_INTERACOES_AUDIO.md`, `docs/arte/previews/fase_g_evidencias.json` (seção `g1`) e capturas `fase_g1_*_local.png`.
