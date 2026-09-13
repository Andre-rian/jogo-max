# Relatório de Mudanças — Profane Echo

Reorganização estrutural, padronização de logs e limpeza de debug.

## Mudanças principais e motivos

### 1. Logging centralizado (`logging_config.py` — novo)
- **Antes:** a configuração do `logging` vivia dentro do `main.py` (`force=True` + handlers soltos) e vários `print()` de debug estavam espalhados pelo projeto.
- **Depois:** módulo único `logging_config.py` com `configurar_logging()`, chamado no início do `main.py`.
- **Motivo:** manter a configuração de logs em um único lugar, reutilizável e testável.

### 2. `print()` de debug → `logger`
Todos os `print()` de debug foram substituídos por `logger` (níveis `debug`/`info`), espelhando o mesmo conteúdo:
- `entities/player.py` — equipar item, adicionar material, definir checkpoint, respawn
- `ui/hud.py` — notificação de item coletado
- `entities/objetos/drop.py` — criação de drop
- `core/menu_fogueira.py` — abertura do menu
- `core/game_scene.py` — fogueira criada e menu aberto
- `main.py` — remoção dos sanity checks de console

**Motivo:** unificar a saída de depuração no `jogo.log`/console com níveis, timestamp e nome do módulo — em vez de misturar `print` direto no stream.

### 3. `settings.py` → só constantes; tiles movidos para `world/tiles.py` (novo)
- **Antes:** `settings.py` misturava configuração do jogo com as classes `Tile`, `Espinho`, `Torcha` e o registro `Registro_ID`.
- **Depois:** `settings.py` ficou apenas com constantes de configuração (janela, física, combate, `DEBUG`). As classes de tile e o `Registro_ID`/ids de tile foram para `world/tiles.py`.
- **Builder/consumidores atualizados:** `world/tile_map.py` agora importa `Registro_ID`/`Tile_vazio` de `world.tiles`.

**Motivo:** separar responsabilidades — configuração (settings) vs. definição dos blocos do mundo (tiles).

### 4. Flag `DEBUG` em `settings.py` (default `False`)
- **Antes:** o desenho de depuração do mapa (retângulos vermelhos dos inimigos, máscaras em azul, parede do boss laranja, retângulo verde do player) e o painel de texto do HUD (estado/posição/velocidade) eram desenhados **sempre**.
- **Depois:** tudo fica atrás de `DEBUG`. Com `DEBUG = True` o visual de debug volta.

**Motivo:** visual limpo para quem joga, sem perder a ferramenta de depuração.

### 5. Telas de morte e pausa → `ui/overlays.py` (novo)
- **Antes:** `_desenhar_tela_morte` e `_desenhar_pausa` viviam dentro de `core/game_scene.py` (maior arquivo do projeto, ~980 linhas).
- **Depois:** funções puras `desenhar_tela_morte(tela, progresso)` e `desenhar_tela_pausa(tela, frame, opções, selecionada)` em `ui/overlays.py`. A lógica (estado, tempo, navegação) permanece na cena.

**Motivo:** reduzir `game_scene.py` e centralizar desenho de telas sobrepostas no pacote `ui/`.

### 6. Ícones dos itens → `ui/icones.py` (novo)
- **Antes:** todo o desenho vetorial dos ícones (espada, machado, poção, raiz, genérico) dentro do método `_desenhar_icone` de `core/inventario.py`.
- **Depois:** função `desenhar_icone_item(...)` em `ui/icones.py`, chamada pelo inventário.

**Motivo:** separar desenho de ícones da lógica do inventário.

### 7. `entities/objetos/poçao.py` → `pocao.py`
- **Motivo:** nome de arquivo sem acento — robustez entre sistemas/encodings diferentes. Import atualizado em `entities/player.py`.

### 8. Loop duplicado de fogueiras removido
- **Antes:** em `game_scene.py` o mesmo `for fogueira in self.fogueiras: ... ativa = True` rodava duplicado (externo e interno aninhados, com shadowing de variável).
- **Depois:** apenas o laço externo. Comportamento idêntico.

### 9. Orbes de Eco Profano menores (visual)
- Núcleo, fragmentos em órbita, sombra e partículas reduzidos (~60% menores) para evitar sobreposição visual estranha no mundo/janela do inventário. Coleta e alcance intactos.

### 10. Hitboxes de debug removidas do gameplay (flag `DEBUG`)
- Rects de depuração que ainda apareciam sempre para o jogador foram colocados atrás de `DEBUG`:
  - `entities/objetos/bau.py` (contorno dourado)
  - `entities/objetos/porta.py` (contorno marrom)
  - `entities/objetos/fogueira.py` (contorno laranja)
  - `entities/projeteis/bomba.py` (hitbox laranja da explosão)
  - `entities/projeteis/projetil_boss.py` (hitbox dourada)

**Motivo:** nenhum contorno de hitbox deve aparecer na tela do jogador em builds normais.

### 11. Carregador de imagens seguro (`core/recursos.py` — novo)
- `carregar_imagem(caminho)` centraliza `pygame.image.load` com `try/except`/log (`warning`) e fallback magenta em vez de exception.
- Aplicado em: `core/animated_sprite.py`, `entities/objetos/bau.py`, `entities/objetos/porta.py`, `world/tile_map.py`, `world/tiles.py`.
- `get_surface`/`_carregar_frames`/`_carregar_variantes` ganharam guards de dimensão mínima (tileset/frame menor que o esperado não derruba o mapa).

### 12. `save_manager.py` à prova de falha
- `CAMINHO_DB` agora é absoluto (`os.path.dirname(__file__)`), então funciona de qualquer pasta.
- Todas as operações (`connect`, `criar_tabela`, `salvar`, `carregar`, `deletar`, `fechar`) com `try/except` + log; banco indisponível degrada com `disponivel=False` em vez de crashar.
- `carregar()` decodifica cada campo JSON com `_decode_json` (dado corrompido vira fallback, não exception).
- `fechar()` é idempotente e agora **é chamado** no `main.py` (QUIT + `atexit`).

### 13. `main.py` com handler global de exceção
- Todo o corpo do loop (`rodar`) dentro de `try/except`: exceção → `log.exception` + **save de emergência** do slot atual + saída limpa.
- QUIT e leitura de eventos com `_sair()` que fecha o save manager antes do `sys.exit`.
- `atexit.register(save_manager.fechar)` garante fechamento em qualquer caminho de saída.

### 14. `entities/objetos/item.py` mais robusto
- `itens.json` carregado com `try/except` (falta/corrompido → `_banco = {}` + warning) em vez de crashar no import.
- Atalhos `EspadaLonga`/`MachadadoDeGuerra` via `Registro_Itens.get(...)` (sem `KeyError`).

### 15. Bug das partículas do Eco Profano corrigido
- `drop_eco.py` tinha `if self._timer * 8 == 0` (nunca verdadeiro; partículas nunca spawnavam) → `self._timer % 8 == 0`.

### 16. `jogo.log` com `FileHandler` (arquivo único)
- `jogo.log` é **um único arquivo** com `FileHandler(mode="a")`: as execuções acumulam no mesmo `jogo.log`, sem rotação. **Razão:** com `RotatingFileHandler` (versão anterior) o histórico virava `jogo.log.1/.2/.3` múltiplos, e vários logs "soltos" se espalhavam; com arquivo único fica simples de acompanhar. (Nesta sessão: `RotatingFileHandler` → `FileHandler`.)

### 17. Prompt contextual de interação (`mostrar_prompt`/`limpar_prompt`)
- **Antes:** os objetos (baú, porta, fogueira, drops, eco) mediam uma distância pelo `centerx` do player (`dist < 10/50/60/80`) e chamavam `hud.mostra_mensagem(...)`, que seta um timer de 180 frames — a dica aparecia de longe e **ficava na tela** mesmo depois de o player sair.
- **Depois:** o HUD ganhou um "prompt" com estado próprio (`Mensagens.mostrar_prompt`/`limpar_prompt`), separado da mensagem temporizada:
  - os objetos só chamam `mostrar_prompt` quando `player.rect.colliderect(objeto.rect)` (colisão real com a hitbox);
  - ao sair da colisão, cada objeto chama `limpar_prompt()` — a dica **some**;
  - ao coletar/interagir (abrir baú, pegar item, alternar porta, descansar), o prompt é limpo na hora.
- Aplicado em: `entities/objetos/bau.py`, `porta.py`, `fogueira.py`, `drop.py`, `drop_eco.py`. Mensagens de evento ("Jogo salvo", "O caminho esta livre") continuam no `mostra_mensagem` temporizado.
- **Ajuste pós-teste:** descobriu-se que a porta é **sólida na física** (`game_scene` adiciona `p.rect` das portas fechadas aos `rects_solidos`), então o player é bloqueado na frente dela e **nunca sobrepõe a hitbox real** — com `colliderect` estrito a porta ficava impossível de abrir. Cada objeto ganhou um `interacao` (rect inflado): a porta com ~1 tile de folga de cada lado (abre encostado, dos dois lados), baú/fogueira/drops/eco com folga de meio tile. Demais objetos continuam em tiles caminháveis, então a sobreposição acontece normalmente.

## Plataformas, escadas, colisão e tilesets (nova leva)

### 18. Plataformas one-way estilo Terraria + drop
- Tiles de plataforma (gids globais `PLATAFORMA_GIDS` no `world/tiles.py`) não participam da colisão sólida — funcionam como piso: o player anda/salta por **baixo** delas, **segura só caindo de cima** e **desce com S+Espaço** (ou Seta-baixo+Espaço).
- Física em `world/tile_map.py` + `world/tiles.py`: `_eh_plataforma` reconhece a plataforma pelo gid (máscara `& 0x1FFFFFFF` para flips) e existe camada dedicada `plataformas` no TMX (qualquer tile pintado vira plataforma).
- **Subida limpa:** ao pular por baixo de uma plataforma ladeada por parede, o sólido da **mesma row** da plataforma não bloqueia a subida (o pulo passa pelo vão e pousa em cima) — mas teto real de outra row continua bloqueando.
- **Drop** (`entities/player.py`): S+Espaço dispara o atravessamento (`_timer_atravessar=8`) ignorando só a row da plataforma até o player descer abaixo dela; ordem invertida (Espaço→S) tem janela de tolerância de 6 frames.

### 19. Drop só com o retângulo inteiro sobre a plataforma
- **Pedido do usuário:** o player só pode descer se o espaço abaixo "cabe" ele — nada de descer "metade na plataforma, metade em cima de um bloco".
- Implementado via `_poder_descer(rects_solidos)` em `player.py`: antes de disparar o drop, se algum sólido da **row do pé** encostar na faixa horizontal do player, o drop é **bloqueado** (fica parado, não pula nem desce). Metade sobre o **vazio** (sem bloco) continua descendo normalmente.

### 20. Correção do "lançamento"/teleporte ao colidir
- `entities/entity.py` — `mover_com_colisão`:
  - **Antes:** o loop resolvia **todas** as tiles colidindo no mesmo frame (cascata de snaps de 32px por tile → teleporte através das paredes) e escolhia o lado pela **direção da velocidade** — preso no lado contrário ao movimento (respawn/teletransporte dentro de parede), o player era lançado `rect.left = tile.right` e atravessava tudo.
  - **Depois:** resolução por **penetração mínima** (face mais próxima) no eixo X e no ramo de queda, + `break` depois do 1º sólido resolvido por eixo por frame. Regressões verificadas (harness G): spawn no canto da parede, drop+D e drop+A contra parede — nenhum teleporte.

### 21. Escadas
- Em `player.py`: agarrar a escada segurando W/S ao encostar (com `_bloqueio_escalada` logo após pulo); durante a escalada o player fica **preso na coluna** da escada (`rect.centerx` pinado), movimento vertical por W/S (sem gravidade), clamp no corredor da escada (`_escada_top`/`_escada_bottom`); ao soltar, `_empurrar_fora_dos_solidos` tira o player dos blocos pelo menor deslocamento (sem "jogada"). Bloqueio de pegar escada ao empurrar contra uma parede. Validado nos cenários de descida passando por parede, soltar no meio da escada e teto de bloco acima.

### 22. Tocha animada como entidade (`entities/objetos/tocha.py` — novo)
- A folha `Torch Sprite Sheet 32x64.png` (128x128) contém na verdade **duas tochas de 32x64 empilhadas**: linhas 0–1 = chama fraca, linhas 2–3 = chama forte; cada tocha tem 4 frames (colunas).
- `carregar_frames_tocha(variante)` fatia os 4 frames 32x64 (padrão `forte`); `Tocha` anima a 6 fps (velocidade=6) e desenha com a câmera.
- Detecção em `core/game_scene.py`: células do `grid_decoracao` do tileset **pelo nome** (`NOME_TILESET_TOCHA`) com `flame row` viram entidades; a "haste" da célula logo abaixo é removida. Suporte também a objectos `type="tocha"` no TMX (propriedade `variante`, default `forte`).

### 23. Tilesets externos (.tsx) + projeto Tiled + mapa molde
- Os tilesets **embutidos** nos `.tmx` foram **externalizados** para `assets/tileset/tilesets/*.tsx` (um arquivo por conjunto: `parede_variantes`, `chao_variantes`, `decoracao_tileset`, `tileset`, `Sidescroller`, `Platformer Asset All K`, `Dungeon Tile Set 32px`, `Torch Sprite Sheet 32x64`). O motor já suportava `.tsx` externos (`_ler_tileset`), e os `firstgid` foram preservados — validado: hashes das camadas dos dois mapas **byte-idênticos** antes/depois.
- **Benefício:** editar um tile no `.tsx` atualiza automáticamente todos os mapas que o referenciam (sem duplicação/divergência de tilesets embutidos por `.tmx`).
- `jogo-max.tiled-project` (raiz) indexa a pasta `assets` → no Tiled os tilesets aparecem num painel fixo.
- `assets/maps/_template.tmx` — **mapa molde** vazio com os 8 tilesets externos e as camadas padrão (`fundo`, `escadas`, `plataformas`, `colisao`, `decoracao`, `objetos`). Para mapa novo: File → Save As. `Dungeon Tile Set 32px` fica no firstgid 2458, então os gids de plataforma (`PLATAFORMA_GIDS`) seguem válidos em qualquer mapa novo.

---

## Divisão em subpastas — implementado

Estrutura atual do projeto:

```
jogo-max/
├── main.py  settings.py  save_manager.py  logging_config.py
├── core/        animated_sprite, recursos, camera, navegacao,
│                game_scene, inventario, menu, menu_fogueira
├── entities/    entity, inimigo_base, player, monsters/, objetos/, projeteis/
├── ui/          estilo, icones, overlays, particulas, hud/
├── world/       rooms, niveis, tile_map, tiles
└── assets/
```

**Implementado:**
- ✅ **`ui/hud.py` (474 linhas) → pacote `ui/hud/`** — componentes separados por responsabilidade:
  ```
  ui/hud/
  ├── __init__.py     (re-exporta Hud)
  ├── hud.py          (monta/coordena)
  ├── status.py       (barras HP/stamina + ícone + buff)
  ├── ecos.py         (indicador de ecos)
  ├── pocao.py        (slot de poção)
  ├── mensagens.py    (mensagem central)
  ├── notificacao.py  (item coletado + ícone vetorial)
  ├── boss.py         (barra do boss)
  └── debug_painel.py (painel DEBUG)
  ```
  Import público preservado: `from ui.hud import Hud` (também re-exporta as subclasses).
- ✅ **`world/rooms.py` dividido** — `world/niveis.py` (novo) guarda `Conexoes`, `spwans`, `Inimigos_por_sala`, `Drops_inimigos`, `Drops_fixos`; `world/rooms.py` ficou só com as grades + `Salas`. Imports em `game_scene.py` atualizados (`from world.niveis import ...`).
- ✅ **Renomeações:** `core/camera_player.py` → `core/camera.py`; `core/menu_navegavel.py` → `core/navegacao.py`. Imports em `game_scene.py`, `inventario.py` e `menu.py` atualizados.

**Ainda sugerido (não implementado):**
- ⏳ `core/` → separar por cenas (`core/cenas/`) — alto custo, baixa prioridade
- ⏳ `entities/player.py` (760 linhas) → subpacote `entities/player/` — desejável, exige cuidado
- ⏳ `save_manager.py` → subpacote `save/` quando crescer (hoje 132 linhas)

**Regra geral aplicada:** divisão por responsabilidade, um módulo = uma preocupação, e `__init__.py` re-exportando os nomes públicos para o resto do código não quebrar.

---

## Fraquezas e falta de tratamento de erro no código

### Carregamento de recursos (era o maior risco de crash) — ✅ corrigido
- **`core/animated_sprite.py`** — `pygame.image.load(...)` sem `try/except`. → agora usa `carregar_imagem()` com fallback magenta + guard de dimensão.
- **`entities/objetos/porta.py`, `bau.py`** — idem. → agora usam `carregar_imagem()`.
- **`world/tile_map.py` e `world/tiles.py`** — idem. → agora usam `carregar_imagem()` e `get_surface` não estoura com subsurface fora dos limites.
- **`entities/objetos/item.py`** — `itens.json` no import sem `try/except`. → load protegido (`_banco = {}` + warning) e atalhos com `Registro_Itens.get()`.

**Solução aplicada:** `core/recursos.py` com `carregar_imagem(caminho)` que tenta `convert_alpha` e, em qualquer falha, loga `warning` e devolve surface placeholder magenta (nunca `None`/exception).

### Banco de saves (`save_manager.py`) — ✅ corrigido
- ~~Nenhum `try/except`/`with`~~ → todas as operações protegidas com log; `disponivel` indica banco OK.
- ~~`json.loads` sem validação~~ → `_decode_json` com fallback por campo.
- ~~`fechar()` nunca chamado~~ → chamado no QUIT e via `atexit` no `main.py`.
- ~~`CAMINHO_DB` relativo ao CWD~~ → absoluto (`os.path.dirname(__file__)`).

### Loop principal (`main.py`) — ✅ corrigido
- ~~Nenhum tratamento global de exceção~~ → `try/except` em todo o corpo do loop com `log.exception`, **save de emergência** no slot atual e saída limpa.
- Detalhe: `pygame.display.toggle_fullscreen()` segue sem flag explícita (comportamento de plataforma diferente não foi alterado).

### Divisão por zero / ranges — ⏳ pendente
- **`game_scene.py` tela de morte:** `progresso = 1 - (self.timer_morto / self.duraçao_morte)` — se `duraçao_morte` for 0, `ZeroDivisionError`. (Hoje é constante 180, mas é uma armadilha.)
- **`entity.py` / física:** divisões e operações de vetor sem clamp — pulo/quedas extremas podem produzir valores fora da tela.

### Outros — parcialmente corrigido
- ✅ `get_item()` atalhos (`EspadaLonga = Registro_Itens[1]`) → `Registro_Itens.get(1)` (sem `KeyError`).
- ✅ Bug das partículas do `drop_eco` (`_timer * 8` → `_timer % 8`).
- ✅ `jogo.log` único (`FileHandler(mode="a")`) em vez de sobrescrita/rotação.
- ⏳ Nenhum `sys.setrecursionlimit`/proteção de loop infinito; callbacks (menu↔cena↔save) crescem sem coordenação central.
- ⏳ Sem type hints (dificulta tooling, IDE e refatoração segura).
- ⏳ Sem testes automatizados — o smoke test atual é manual/temporário.

## Mudanças necessárias (resumo, por ordem de prioridade)

| # | Mudança | Impacto | Esforço | Status |
|---|---------|---------|---------|--------|
| 1 | Carregador de imagens com fallback + log (`core/recursos.py`) | evita crash por asset faltando | baixo | ✅ |
| 2 | Tratamento de erro no `save_manager` + caminho absoluto + `fechar()` no quit | evita perda/corrupção de save | baixo | ✅ |
| 3 | `try/except` global no loop do `main.py` com save de emergência | jogo não morre por exceção boba | baixo | ✅ |
| 4 | Corrigir bug das partículas do `drop_eco` (`_timer % 8`) | comportamento esperado | trivial | ✅ |
| 5 | `FileHandler` para `jogo.log` (arquivo único, sem rotação) | histórico simples | trivial | ✅ |
| 6 | Dividir `ui/hud.py` em componentes (item 2 das subpastas) | manutenção | médio | ✅ |
| 7 | Separar `world/rooms.py` (dados de nível → `world/niveis.py`) | manutenção | baixo | ✅ |
| 8 | Renomear `camera_player.py`→`camera.py`, `menu_navegavel.py`→`navegacao.py` | consistência | médio | ✅ |
| 9 | `entities/objetos/item.py` robusto (`itens.json` + atalhos) | evita crash no import | baixo | ✅ |
| 10 | Unificar duplicidade de códigos de cor legados ⇄ `ui/estilo.py` | consistência visual | baixo | ⏳ |
| 11 | Renomear typos consagrados (`Screen_widht`, `Savemaneger`...) | consistência | médio | ⏳ |
| 12 | ZeroDivision na tela de morte (`duraçao_morte`) + clamps na física | robustez | baixo | ⏳ |
| 13 | Adicionar type hints e um primeiro teste automatizado | qualidade geral | alto | ⏳ |
| 14 | Câmera com zoom: aproxima do player (1.35x) e desaproxima na luta do boss (1.0x, ease suave) | jogabilidade | médio | ✅ |
| 15 | Spawn do player na troca de sala usa o spawn do TMX (nome do lado da entrada ou `default`); antes o jogador nascia dentro da parede do `calabouco_2` (linha fixa dos dados fallback) | bug | médio | ✅ |
| 16 | Salas sem TMX (fallback 3–5) crashavam no carregamento: grid de `int` ia direto para o `TileMap` que esperava `TileRef` — agora converte para placeholder | bug | alto | ✅ |
| 17 | Plataformas one-way + drop (S+Espaço, só com o player inteiro sobre a plataforma) e escadas | jogabilidade | médio | ✅ |
| 18 | Corrigir "lançamento"/teleporte ao colidir com parede (`mover_com_colisão` por penetração mínima + break) | bug | médio | ✅ |
| 19 | Tocha animada decorativa como entidade (detecção por tileset no TMX) | conteúdo | médio | ✅ |
| 20 | Tilesets externos `.tsx` + `.tiled-project` + mapa molde `_template.tmx` | pipeline | médio | ✅ |

## Status de validação
- Todos os arquivos alterados compilam (`compileall` exit 0).
- Smoke test de import (menu, cena, inventário, pausa, morte, fogueira, HUD novo, `core/recursos`, `core/camera`, `core/navegacao`, `world/niveis`, `save_manager`) — OK.
- Smoke test de runtime com `DEBUG=False`: `Gamescene` roda 120 frames + pausa + inventário + notificação + morte — OK.
- Teste do prompt contextual nos 5 objetos (baú, porta, fogueira, drop, eco): aparece na colisão com a hitbox e some ao sair — OK.
- Câmera: zoom 1.35 no dia a dia, ease para 1.0 em luta de boss e volta ao normal após a derrota — OK (teste com o boss real do calabouço_5).
- Spawn nas trocas de sala: `calabouço_1 → calabouço_2` usa o spawn do TMX (32, 640) sem cair em parede; ida e volta validado; salas fallback (3–5) carregam sem crash — OK.
- Harness de plataformas/escadas (`test_plataformas_escadas.py`): grupos A–H TUDO OK —
  - A/B: pousar em plataformas e descer com S+Espaço; C: **drop bloqueado** com metade do player sobre bloco (e liberado com metade sobre o vazio); D/E: subir por baixo da plataforma ladeada de parede e teto real bloqueando; F: escada restrita à coluna (desce passando pela parede, soltar sem "jogada", teto de bloco); G: sem teleporte ao nascer/tocar parede (regressão do "lançamento"); H: drop só com o retângulo inteiro sobre a plataforma.
- Tilesets `.tsx`: hashes das camadas dos dois mapas idênticos antes/depois da externalização; `Gamescene` carrega os dois `.tmx` e roda 60 frames (update+draw) sem exceção, com 1 tocha detectada por tileset nome — OK.