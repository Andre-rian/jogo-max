# Sons faltando — lista de trabalho

> Baseado em `core/audio.py`, na árvore `assets/sons/` e nos relatórios de áudio.
> Atualizado em 2026-11-07.

## Resumo

- Os **37 sons obrigatórios** de `ESPECIFICACOES` em `core/audio.py` **existem todos**; os 37 caminhos foram verificados em `assets/sons/`.
- O que falta são os sons **específicos**. Enquanto a pasta está vazia, a cascata de fallback usa um som genérico já existente.
- Muitos itens já têm candidato em `assets/sons/_entrada/`; o CSV `tools/promocao_exec_final.csv` registra as promoções executadas e o inventário restante está em `tools/inventario_sons_restantes.csv`.

### Promovidos em 2026-11-07

Já preenchidos (não são mais pastas vazias): hits do Skeleton (`_default`, `machado_guerra`, `soco`), hits do Mushroom e Flying Eye (`soco`), mortes do Skeleton, impacto em osso (`_default`, `espada_longa`), impacto em carne (`_default`, `soco`, 4× `espada_longa`), impacto em metal (`_default`, `espada_longa`, `machado_guerra`), morte do Mushroom, swings do soco, bloqueio de escudo do Boss Carrasco, hit de soco do Boss, ataque do Globin, `ui/confirmar`, `ui/erro`, `ui/navegar`, `ui/pausa`, `mundo/portas`, passos (madeira + 33 em pedra), passos de inimigos (`globin/passos` e `inimigos/_default/passos`, 4 cada) e pouso em pedra (8). O registro está em `assets/sons/_config/LICENCAS.csv` e os CSVs executados em `tools/promocao_exec_*.csv`.

Ainda fora da promoção: `_entrada/_fatias/` (38 fatias em 7 pastas), `_entrada/_uteis/` (16 fontes para depois; as 2 de passos de inimigos já foram usadas nos cortes, mas os originais permanecem) e as 4 fontes longas de passos em `5_mundo_movimento/passos_pedra/`. O `_para_fatiar/` foi removido após a 2ª triagem; `_entrada/_revisar/` está vazia no momento. O inventário atualizado está em `tools/inventario_sons_restantes.csv` e `docs/audio/INVENTARIO_SONS_RESTANTES.md`.

Legenda de prioridade:

- **P1** — muda bastante a sensação de combate; hoje toca fallback de material ou genérico.
- **P2** — boss/projéteis/inimigos específicos.
- **P3** — mundo, movimento e ambiência.

---

## P1 — Combate e jogador

| Destino (pasta vazia) | O que é | Hoje toca (fallback real) |
|---|---|---|
| `sfx/player/armas/machado_guerra/` | swing do machado | `sfx/combate/generico/hit_01..05` |
| `sfx/player/armas/_default/` | swing genérico de arma | `sfx/combate/generico/hit_01..05` |
| `sfx/materiais/osso/machado_guerra/` | impacto em osso com machado | `sfx/materiais/osso/_default/hit_01.wav` no Boss; o Skeleton usa `skeleton/hit/machado_guerra/hit_01.wav` |
| `sfx/materiais/carne/machado_guerra/` | impacto em carne com machado | `sfx/materiais/carne/_default/hit_01.wav` |
| `sfx/materiais/fungo/{_default,espada_longa,machado_guerra}/` | impacto em fungo | `sfx/combate/generico/hit_01..05` |
| `sfx/materiais/etereo/{_default,espada_longa,machado_guerra}/` | impacto etéreo (Flying Eye) | `sfx/combate/generico/hit_01..05` |
| `sfx/materiais/metal/soco/` | impacto em metal com soco | `sfx/materiais/metal/_default/hit_01..04` |
| `sfx/inimigos/skeleton/hit/espada_longa/` | hit do Skeleton com espada | `sfx/inimigos/skeleton/hit/_default/hit_01.wav` |
| `sfx/inimigos/globin/hit/{_default,machado_guerra}/` | hit do Globin com machado/arma padrão | `sfx/materiais/carne/_default/hit_01.wav` |
| `sfx/inimigos/globin/hit/soco/` | hit do Globin com soco | `sfx/materiais/carne/soco/hit_01..09` |
| `sfx/inimigos/globin/hit/espada_longa/` | hit do Globin com espada | `sfx/materiais/carne/espada_longa/hit_01..04` |
| `sfx/inimigos/mushroom/hit/{_default,espada_longa,machado_guerra}/` | hit específico do Mushroom | `sfx/combate/generico/hit_01..05` |
| `sfx/inimigos/flying_eye/hit/{_default,espada_longa,machado_guerra}/` | hit específico do Flying Eye | `sfx/combate/generico/hit_01..05` |
| `sfx/inimigos/boss_carrasco/hit/espada_longa/` | hit do Boss com espada | `sfx/materiais/osso/espada_longa/hit_01.wav` |
| `sfx/inimigos/boss_carrasco/hit/{machado_guerra,quebra_guarda}/` | hit do Boss com machado/quebra-guarda | `sfx/materiais/osso/_default/hit_01.wav` |
| `sfx/inimigos/_default/hit/_default/` | hit genérico de inimigo | `sfx/materiais/<material>/<arma>` → `_default` → `sfx/combate/generico/hit_01..05` |

> Os pontos `{...}` são as subpastas `espada_longa`, `machado_guerra`, `soco` e `_default`; onde `soco` já está preenchido no inimigo, ele foi omitido. O fallback de material só é usado depois de `inimigos/<id>/hit/<arma>` e `inimigos/<id>/hit/_default`.

---

## P2 — Inimigos, boss e projéteis

| Destino (pasta vazia) | O que é | Hoje toca (fallback real) |
|---|---|---|
| `sfx/inimigos/skeleton/ataque/` | ataque do Skeleton | `sfx/inimigos/_default/ataque/ataque_01.wav` |
| `sfx/inimigos/mushroom/ataque/` | ataque do Mushroom | `_default/ataque` |
| `sfx/inimigos/flying_eye/ataque/` | ataque do Flying Eye | `_default/ataque` |
| `sfx/inimigos/{globin,flying_eye}/morte/` | mortes específicas | `sfx/inimigos/_default/morte/morte_01.wav` |
| `sfx/inimigos/boss_carrasco/morte/` | morte do boss | `sfx/inimigos/_default/morte/morte_01.wav` |
| `sfx/inimigos/boss_carrasco/entrada/` | entrada do boss | *(nada específico)* |
| `sfx/inimigos/boss_carrasco/rugido/` | rugido do boss | *(nada específico)* |
| `sfx/inimigos/boss_carrasco/ataque/` | ataque do Boss (normal/varrido/projétil) | `_default/ataque` |
| `sfx/inimigos/mushroom/esporo/` | esporo do Mushroom | *(pasta não lida pelo áudio; ataque usa `_default/ataque`)* |
| `sfx/inimigos/flying_eye/asas/` | asas do Flying Eye | *(não implementado)* |
| `sfx/projeteis/bomba/disparo/` e `.../voo/` | disparo e voo da bomba | `sfx/projeteis/bomba/impacto/impacto_01.wav` *(se `play_projectile` fosse chamado)* |
| `sfx/projeteis/esporo/{disparo,voo,impacto}/` | esporo | `sfx/projeteis/bomba/impacto/` *(se `play_projectile` fosse chamado)* |
| `sfx/projeteis/olho/{disparo,voo,impacto}/` | projétil do olho | `sfx/projeteis/bomba/impacto/` *(se `play_projectile` fosse chamado)* |
| `sfx/projeteis/boss/{disparo,voo,impacto}/` | projétil do boss | `sfx/projeteis/bomba/impacto/` *(se `play_projectile` fosse chamado)* |

> Mushroom e Skeleton já têm morte própria (`mushroom/morte/morte_01.wav`; o Skeleton usa `skeleton/morte/_default/morte_01.wav`), por isso não aparecem na lista.
>
> As subpastas `boss_carrasco/ataque/{normal,varrido,projetil}/` existem vazias, mas `play_enemy_attack` só consulta `sfx/inimigos/<id>/ataque/` e `_default/ataque`; para separar variantes é preciso alterar o código.
>
> `play_projectile(tipo, fase)` tenta `projeteis/<tipo>/<fase>`, depois `projeteis/<tipo>/impacto` e por fim `projeteis/bomba/impacto` — mas **não há chamada a `play_projectile` no código**. Hoje só a bomba toca algo no impacto, via `bomb_explosion`.

---

## P3 — Mundo, movimento e ambiência

| Destino (pasta vazia) | O que é | Situação |
|---|---|---|
| `sfx/player/movimento/pulo/` | som de pulo | não implementado em `player.py` (só o arquivo falta e o gatilho também) |
| `sfx/player/movimento/passos/terra/` | passos em terra | cai em `passos/madeira/` |
| `sfx/player/movimento/passos/metal/` | passos em metal | cai em `passos/madeira/` |
| `sfx/player/movimento/passos/_default/` | passos genéricos | cai em `passos/madeira/` |
| `sfx/player/movimento/pouso/terra/` | pouso em terra | cai em `pouso/madeira/` |
| `sfx/player/movimento/pouso/metal/` | pouso em metal | cai em `pouso/madeira/` |
| `sfx/player/movimento/pouso/_default/` | pouso genérico | cai em `pouso/madeira/` |
| `sfx/mundo/tochas/` | tochas | não integrado |
| `sfx/mundo/mecanismos/` | alavancas/mecanismos | não integrado |
| `sfx/interacao/eco_profano/` | Eco Profano | hoje usa `sfx/interacao/itens/eco_01.wav` |
| `sfx/inimigos/{skeleton,mushroom}/passos/` | passos específicos de Skeleton/Mushroom | caem em `inimigos/_default/passos/` |
| `ambiencia/calabouco/` | ambiência do calabouço | 1 arquivo bruto presente (`841640__...mp3`), mas o sistema de ambiência não está integrado |
| `ambiencia/sala_descanso/` | ambiência da fogueira | sistema de ambiência não integrado |
| `ambiencia/arena_boss/` | ambiência do boss | sistema de ambiência não integrado |

> Hoje todas as salas usam `material_piso = 'pedra'` (`world/niveis.py`), então `terra`/`metal` são baixa prioridade até existirem salas com esses pisos.

> `passos/pedra` tem 33 variações (`step_01..33`) e `pouso/pedra` tem 8 (`land_01..08`). `step_18..33` são novos; `step_17` e `step_30..33` foram refeitos com 0,30 s para não emendar dois passos. Passos de inimigos: `inimigos/globin/passos/step_01..04` e `inimigos/_default/passos/step_01..04`.

---

## Fora de pastas (pendências de sistema)

- som de **troca de sala**
- som de **vitória contra boss**
- **áudio de projéteis** em jogo (`play_projectile` existe, mas não é chamado; só a bomba usa `bomb_explosion`)
- **sistema de música** não integrado (há 4 faixas: `musica/menu`, `exploracao`, `descanso`, `boss`, mas nenhuma é tocada pelo código)
- **ambiência** integrada às cenas (incluindo renomear/promover o arquivo bruto de `ambiencia/calabouco/`)

---

## Atalho: já dá para preencher com `_entrada/`

Novos arquivos devem ser jogados em `_entrada/_inbox/`. Após a 2ª triagem de 2026-11-07, o material restante está separado em:

- `_entrada/_fatias/` — 38 fatias em 7 pastas (metal, socos em metal e impactos de boss). Use o nome da fatia no CSV de promoção.
- `_entrada/_uteis/` — 16 fontes boas guardadas para depois (metal, impactos de chefe, osso, menu, efeitos/choir, inventário, pouso alternativo, soco pesado e passos; as 2 fontes de passos de inimigos já foram usadas nos cortes).
- `_entrada/5_mundo_movimento/passos_pedra/` — 4 fontes longas mantidas para cortes alternativos; os cortes `step_18..33` e os passos de inimigos já foram promovidos.
- `_entrada/_revisar/` — vazia no momento.

As fatias já estão em `assets/sons/_entrada/_fatias/<arquivo>/`. Para promover, referencie o caminho da fatia em um CSV (`origem;destino`) e rode `python tools/preparar_sons.py promover tools/seu_csv.csv --dry-run`. Para fatiar uma fonte nova, use `python tools/preparar_sons.py fatiar <prefixo> --max 8 --dur-max 0.35`.

---

## Onde encontrar

| Fonte | Melhor para | Licença |
|---|---|---|
| [Freesound.org](https://freesound.org) | impactos, passos, armas, ambiência (mesma fonte atual) | CC0 / CC BY (filtrar) |
| [OpenGameArt.org](https://opengameart.org) | SFX de fantasia, UI | CC0 / CC BY |
| [Kenney.nl](https://kenney.nl/assets?q=audio) | UI, cliques, impactos | CC0 |
| [Sonniss GDC bundles](https://sonniss.com/gameaudiogdc) | bibliotecas grandes de impacto/ambiência | Royalty-free |
| [itch.io — Game Assets > Audio](https://itch.io/game-assets/free/tag-audio) | packs indie | varia |
| [Pixabay Audio](https://pixabay.com/sound-effects/) | música/ambiência/SFX | Pixabay License |
| [Mixkit](https://mixkit.co/free-sound-effects/) | SFX e música | Mixkit License |
| [Zapsplat](https://www.zapsplat.com) | SFX variados | grátis com atribuição |

## Termos de busca (use em inglês)

- **Soco**: `punch impact`, `fist hit flesh`, `body punch`
- **Machado**: `heavy axe swing`, `axe whoosh`
- **Espada**: `sword swing`, `blade whoosh`, `metallic slash`
- **Osso**: `bone crack`, `bone crunch`, `skeleton hit`
- **Carne**: `flesh hit`, `meat impact`, `wet impact`
- **Fungo**: `wet squish`, `slime impact`, `mushroom squish`
- **Etéreo**: `ghostly hit`, `ethereal impact`, `magic hit`
- **Metal**: `metal clank`, `armor hit`, `shield block`
- **Boss**: `monster roar`, `giant growl`, `heavy stomp`, `boss entrance`
- **Projéteis**: `spore shot`, `magic projectile`, `energy whoosh`, `arrow flyby`
- **Portas/mecanismos**: `stone door grind`, `heavy mechanism`, `lever pull`
- **UI**: `dark UI confirm`, `horror menu click`, `ritual gong`, `error stinger`
- **Ambiência**: `dungeon ambience loop`, `campfire loop`, `boss arena drone`

## Dicas de preparo

1. **Filtre antes de baixar**: duração < 2 s, 44,1 kHz, mono, sem reverb longo.
2. **Não solte compilação**: o jogo sorteia o arquivo inteiro por pasta. Fatie primeiro.
3. **Padrão de saída**: WAV PCM 16-bit, 44,1 kHz, mono, pico entre -3 e -1 dBFS. UI ≤ 0,6 s; SFX ≤ 1,5 s; música/ambiência em OGG.
4. **Nomes**: ASCII minúsculo e numerado (`hit_01.wav`, `swing_01.wav`, `step_01.wav`). É só soltar na pasta certa — o `AudioManager` indexa no boot, sem mexer no código.
5. **Valide em jogo** com o áudio ligado e confira o log `[AUDIO]`.

## Licença

Os arquivos atuais são de licença livre. **Não é obrigatório preencher autor/URL** para promover: `tools/preparar_sons.py` agora registra `LIVRE` por padrão e só tenta deduzir a fonte pelo nome quando possível.

Se quiser manter o histórico, o registro continua em `assets/sons/_config/LICENCAS.csv`, mas não bloqueia mais a promoção.
