# Relatório dos novos sons — Profane Echo

> Data: 2026-10-31  
> Pasta analisada: `assets/sons/_entrada/` (antiga `novos_sons/`, 343,2 MiB, 63 arquivos de áudio)  
> Objetivo: inventariar os candidatos, indicar destino na nova árvore de áudio e separar o que já pode ser promovido do que ainda precisa de edição.

## 1. Resumo executivo

Os novos arquivos cobrem bem as prioridades da segunda rodada de escuta: passos/pouso em pedra, murro, impactos de esqueleto/globin e UI mais épica. Porém, a maior parte são **gravações longas ou compilações**, não efeitos prontos. Apenas **13 arquivos** têm duração curta o suficiente para virar SFX sem corte.

Situação por pasta:

| Pasta | Arquivos | Tamanho | Situação |
|---|---:|---:|---|
| `_revisar/` | 8 | 28,9 MiB | Candidatos ambíguos, loops e ambiência; ouvir antes de descartar |
| `impacto_esqueleto/` | 8 | 4,5 MiB | **Boa cobertura**; 6 arquivos curtos prontos para normalizar |
| `impacto_globin/` | 2 | 3,8 MiB | Pouca cobertura; ambos precisam de corte |
| `impactos_organicos/` | 18 | 247,7 MiB | Muitos candidatos, quase todos longos; principal fila de edição |
| `morte_inimigo/` | 1 | 0,1 MiB | Único arquivo, 5,72 s; precisa encurtar |
| `murro/` | 2 | 1,2 MiB | Candidatos longos; precisam de corte |
| `passos_pedra/` | 8 | 18,7 MiB | Sequências/loops; só 2 arquivos curtos |
| `pouso_pedra/` | 3 | 12,6 MiB | Apenas 1 arquivo curto; os outros são compilações |
| `ui_epica_ritualistica/` | 13 | 23,7 MiB | Identidade épica promissora; quase tudo precisa de corte |

**Conclusão:** não promover a pasta inteira para a árvore definitiva. Promover somente os arquivos curtos aprovados e manter o resto em `_entrada/` até edição.

## 2. Inventário detalhado

Legenda de prontidão:

- **Pronto**: duração curta (≤ 1,5 s), adequado para SFX após normalização.
- **Editar**: tem material útil, mas precisa de corte, fades ou separação de camadas.
- **Bruto**: compilação/loop/ambiência longa; não usar sem edição.
- **Revisar**: destino ou utilidade em dúvida.

### 2.1 `impacto_esqueleto/` — 8 arquivos, 4,5 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `147993__bewareofkites20__bone-cracking.wav` | 0,70 s | WAV 44,1 kHz | mono | Pronto | `sfx/materiais/osso/soco/` ou `.../espada_longa/` |
| `161381__vinrax__bone_crack1.wav` | 0,67 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/materiais/osso/_default/` |
| `192146__brassknucklesfilms__bone-crunch-fast.wav` | 0,90 s | WAV 44,1 kHz | mono | Pronto | `sfx/materiais/osso/soco/` |
| `369601__evanboyerman__bone-crunchcrack-2-mixed.wav` | 0,64 s | WAV 48 kHz | estéreo | Pronto | `sfx/materiais/osso/_default/` |
| `621977__rydra_wong__multiple-bones-cracking.wav` | 2,27 s | WAV 44,1 kHz | estéreo | Editar | `sfx/inimigos/skeleton/morte/_default/` |
| `792923__kvv_audio__gorebone_bone-crunch-dry-01_kvv-audio_free.wav` | 6,17 s | WAV 96 kHz | estéreo | Editar | `sfx/materiais/osso/espada_longa/` |
| `869107__robo9418__bone-crack.wav` | 0,31 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/materiais/osso/_default/` |
| `skeleton-hit-pesado.wav` | 0,52 s | WAV 96 kHz | estéreo | Pronto | `sfx/inimigos/skeleton/hit/_default/` |

Observações:

- É a família mais consistente do lote. Dá para montar 3–4 variações de impacto em osso só com os arquivos curtos.
- `792923...` e `621977...` têm cauda longa e devem ser cortados para ~0,6–1,0 s.
- Converter 48/96 kHz para 44,1 kHz e reduzir para mono.

### 2.2 `impacto_globin/` — 2 arquivos, 3,8 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `333516__oscaraudiogeek__hand-slap-on-sweater.wav` | 23,30 s | WAV 48 kHz | mono | Bruto | `sfx/materiais/carne/_default/` após recortar um golpe |
| `hit-critico_ou_pesado.wav` | 2,09 s | WAV 44,1 kHz | estéreo | Editar | `sfx/inimigos/globin/hit/_default/` |

Observações:

- Cobertura insuficiente para as 3 variações recomendadas. Buscar mais 1–2 impactos de corpo mole/tecido.
- O `hand-slap-on-sweater` tem timbre bom para Globin, mas é uma sequência longa.

### 2.3 `impactos_organicos/` — 18 arquivos, 247,7 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `342397__christopherderp__swords-clash-w-swing-1.wav` | 2,54 s | WAV 44,1 kHz | estéreo | Editar | `sfx/player/armas/espada_longa/` (swing + clash) |
| `345308__samsterbirdies__sword-sounds-compilation.wav` | 21,27 s | WAV 44,1 kHz | estéreo | Bruto | Separar em `swing_01..0N` |
| `395330__ihitokage__fist-clenching-2(...).ogg` | 5,01 s | OGG | — | Editar | `sfx/player/armas/soco/` ou `sfx/materiais/fungo/` |
| `492254__soundflakes__tyrael-sword-slice-flesh-02.wav` | 1,60 s | WAV 44,1 kHz | estéreo | Editar | `sfx/materiais/carne/espada_longa/` |
| `492548__soundflakes__imperius-hit-the-giants-eye_flesh.wav` | 1,56 s | WAV 44,1 kHz | estéreo | Editar | `sfx/materiais/carne/espada_longa/` |
| `574612__eminyildirim__sword-hit.wav` | 44,50 s | WAV 44,1 kHz | estéreo | Bruto | Compilação; separar golpes |
| `593282__...__dropping-a-damp-cloth-on-different-surfaces.wav` | 24,20 s | WAV 48 kHz | estéreo | Bruto | `sfx/materiais/carne/_default/` após recorte |
| `593878__makadunyiswe__punching-gloves.wav` | 8,50 s | WAV 48 kHz | estéreo | Editar | `sfx/player/armas/soco/` |
| `636102__fonografico__shieldhit2.wav` | 2,19 s | WAV 44,1 kHz | estéreo | Editar | `sfx/inimigos/boss_carrasco/hit/escudo_bloqueio/` |
| `679994__imnotdubmass__metal-drop.wav` | 27,72 s | WAV 44,1 kHz | estéreo | Bruto | `sfx/materiais/metal/_default/` após recorte |
| `718259__georgediamond__sword-stab-body-hit.wav` | 1,00 s | WAV 48 kHz | estéreo | Pronto | `sfx/materiais/carne/espada_longa/` |
| `733887__velcronator__sword-impact.wav` | 1,39 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/materiais/carne/_default/` ou `metal/_default/` |
| `794249__artninja__metal_pipe_hit...wav` | 74,51 s | WAV 44,1 kHz | estéreo | Bruto | Compilação de metal; separar golpes |
| `819311__artninja__...heavy_sword_hit.wav` | 112,61 s | WAV 44,1 kHz | estéreo | Bruto | Compilação; separar golpes |
| `850681__artninja__...medieval_distortion_clank_hit.wav` | 50,92 s | WAV 44,1 kHz | estéreo | Bruto | Compilação; separar golpes |
| `852663__artninja__hunting_knife...wav` | 354,59 s | WAV 44,1 kHz | estéreo | Bruto | Maior arquivo do lote; separar/usar só se necessário |
| `852716__artninja__tmnt_2012_custom_heavy_bostaff_hit.wav` | 26,64 s | WAV 44,1 kHz | estéreo | Bruto | Compilação de impacto pesado; separar golpes |
| `864997__artninja__custom_punch_body_or_body_kick...wav` | 46,51 s | WAV 48 kHz | estéreo | Bruto | Compilação de murro/chute; separar golpes |

Observações:

- Esta pasta concentra **72% do tamanho total**. Não versionar o lote inteiro sem necessidade; compilações longas podem ficar fora do Git.
- Os arquivos `artninja` são compilações com muitos golpes; o ideal é recortar 3–4 takes curtos por família.
- `718259` e `733887` são os únicos prontos sem corte.

### 2.4 `murro/` — 2 arquivos, 1,2 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `158783__alexkandrell__punching.wav` | 4,98 s | WAV 48 kHz | mono | Editar | `sfx/player/armas/soco/swing_01.wav` |
| `232358__richerlandtv__heavy-impacts.mp3` | 11,84 s | MP3 | — | Bruto | `sfx/player/armas/soco/` após recorte |

Observações:

- Resolve diretamente o problema do murro usando o mesmo som da espada.
- Precisa de pelo menos 2–3 variações curtas (`swing_01..03`), mais um impacto seco opcional.

### 2.5 `passos_pedra/` — 8 arquivos, 18,7 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `216004__brainwaves8__walking-down-the-hallway.wav` | 20,98 s | WAV 48 kHz | estéreo | Bruto | `sfx/player/movimento/passos/pedra/` após separar passos |
| `465299__softdistortionfx__concrete-footsteps.flac` | 59,90 s | FLAC | — | Bruto | Separar em `step_01..04` |
| `770072__vrymaa__footsteps-knight-fight-courtyard.wav` | 33,51 s | WAV 48 kHz | mono | Bruto | Separar passos de armadura |
| `footsteps-stone-sequence.wav` | 13,08 s | WAV 44,1 kHz | mono | Bruto | Separar em `step_01..04` |
| `fx_005_footstep_stone_l.wav` | 0,30 s | WAV 48 kHz | estéreo | Pronto | `sfx/player/movimento/passos/pedra/step_01.wav` |
| `galbenshire__footsteps_stone.wav` | 19,00 s | WAV 44,1 kHz | estéreo | Bruto | Separar em `step_01..04` |
| `hiking-boot-footsteps-on-stone.wav` | 3,55 s | WAV 48 kHz | mono | Editar | Separar 1–2 passos |
| `stone_footstep_5.wav` | 1,29 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/player/movimento/passos/pedra/step_02.wav` |

Observações:

- Só há **2 passos individuais prontos**. O restante são sequências que precisam ser fatiadas.
- Prioridade: obter 3–4 variações curtas e consistentes de passo em pedra.

### 2.6 `pouso_pedra/` — 3 arquivos, 12,6 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `422753__kierankeegan__landing_stone_1.wav` | 0,22 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/player/movimento/pouso/pedra/land_01.wav` |
| `grande_impacto.wav` | 10,46 s | WAV 44,1 kHz | estéreo | Bruto | Recortar impacto curto |
| `impactos_geral.wav` | 26,76 s | WAV 44,1 kHz | estéreo | Bruto | Recortar 1–2 impactos |

Observações:

- Apenas um pouso curto. As outras duas opções são compilações de impacto.

### 2.7 `morte_inimigo/` — 1 arquivo, 0,1 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `skeleton-morrendo-sound.mp3` | 5,72 s | MP3 | — | Editar | `sfx/inimigos/skeleton/morte/morte_01.mp3` |

Observações:

- A cauda é longa para o tempo da tela de morte. Cortar para ~0,8–1,5 s ou aplicar fade curto.
- Converter para WAV 44,1 kHz mono/OGG conforme o padrão final.

### 2.8 `ui_epica_ritualistica/` — 13 arquivos, 23,7 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `207183__klankbeeld__heavy-steel-noise-03.wav` | 6,56 s | WAV 48 kHz | estéreo | Editar | `sfx/ui/confirmar/` (corte curto) |
| `235459__jcdecha__gong_hits_slow.wav` | 22,19 s | WAV 48 kHz | estéreo | Bruto | `sfx/ui/confirmar/` ou `ambiencia/` |
| `467585__ryusa__deep-dark-not-fancy-air-impact-reverb-ui.wav` | 4,00 s | WAV 48 kHz | estéreo | Editar | `sfx/ui/confirmar/` ou `sfx/ui/pausa/` |
| `819290__johnmode__mystical-female-choir-swell-01(...).wav` | 7,56 s | WAV 48 kHz | estéreo | Editar | `sfx/ui/confirmar/` ou `musica/` |
| `819291__johnmode__mystical-female-choir-swell-02.wav` | 7,56 s | WAV 48 kHz | estéreo | Editar | `sfx/ui/confirmar/` ou `musica/` |
| `819349__johnmode__mystical-female-choir-swell-03.wav` | 5,62 s | WAV 48 kHz | estéreo | Editar | `sfx/ui/confirmar/` ou `musica/` |
| `831971__bassimat__metal-stand-gong-hit...wav` | 2,13 s | WAV 44,1 kHz | mono | Editar | `sfx/ui/confirmar/` |
| `848526__mikiko850__atmospheric-mysterious-tonal-sweeps.wav` | 19,50 s | WAV 44,1 kHz | estéreo | Bruto | `ambiencia/calabouco/` |
| `858212__tommasomotteran__failed-quest-stinger-01...wav` | 6,00 s | WAV 44,1 kHz | estéreo | Editar | `sfx/ui/erro/` |
| `858948__tommasomotteran__horror-ui-select-stinger-01.wav` | 2,50 s | WAV 44,1 kHz | estéreo | Editar | `sfx/ui/navegar/` |
| `861361__feraly__bwung.wav` | 1,11 s | WAV 44,1 kHz | estéreo | Pronto | `sfx/ui/confirmar/` ou `sfx/ui/voltar/` |
| `873222__mikiko850__abyssal-horror-stingers.wav` | 17,73 s | WAV 44,1 kHz | estéreo | Bruto | `sfx/ui/erro/` após recorte |
| `873650__packsmithy__dark-confirm-synth-horror-game-interface-sounds(...).wav` | 1,01 s | WAV 44,1 kHz | mono | Pronto | `sfx/ui/confirmar/` ou `sfx/ui/inventario/` |

Observações:

- A família tem a identidade “épica/ritualística” pedida no feedback.
- A maioria tem cauda longa; UI precisa ser curta e responsiva. Recortar para ≤ 0,6 s, exceto confirmações especiais.
- Os coros e gongs podem virar camadas de menu/ambiência, não botões.

### 2.9 `_revisar/` — 8 arquivos, 28,9 MiB

| Arquivo | Duração | Formato | Canais | Prontidão | Destino sugerido |
|---|---:|---|---:|---|---|
| `109360__soundcollectah__stone-falls-and-breaks-low-pitch.aiff` | 4,59 s | AIFF | — | Revisar | `sfx/mundo/mecanismos/` ou `pouso/pedra/` |
| `443958__anational__box-dropping-with-stones.wav` | 18,25 s | WAV 44,1 kHz | mono | Revisar | `sfx/mundo/mecanismos/` após recorte |
| `565712__ralphwhitehead__footsteps-walking-on-wooden-floor-slow-pace.wav` | 58,00 s | WAV 48 kHz | estéreo | Revisar | `sfx/player/movimento/passos/madeira/` |
| `841640__newlocknew__ambdsgn_madness-prison-ambience...mp3` | 200,31 s | MP3 | — | Revisar | `ambiencia/calabouco/` |
| `844329__nahuelmartinez__stone-slab-door-grinding-heavy-rock-scrape-mono.wav` | 16,85 s | WAV 48 kHz | mono | Revisar | `sfx/mundo/portas/` |
| `footsteps-stone-sneaker.wav` | 17,29 s | WAV 48 kHz | mono | Revisar | `sfx/player/movimento/passos/pedra/` |
| `fps-footsteps-loop.wav` | 4,63 s | WAV 44,1 kHz | mono | Revisar | `sfx/player/movimento/passos/pedra/` (loop, não ideal) |
| `hit-no-skeleton(talvez).mp3` | 10,10 s | MP3 | — | Revisar | `sfx/inimigos/skeleton/hit/_default/` após recorte |

Observações:

- `_revisar/` tem material útil para ambiência, portas e passos em madeira.
- O nome `hit-no-skeleton(talvez)` tem parênteses e ambiguidade; renomear ao promover.

## 3. Lacunas em relação à árvore proposta

Ainda não há candidatos suficientes para:

- `sfx/player/armas/machado_guerra/` — nenhum swing pesado separado;
- `sfx/inimigos/mushroom/` e `sfx/inimigos/flying_eye/` — nenhum ataque/morte específico;
- `sfx/inimigos/boss_carrasco/` — só o escudo tem candidato; faltam rugido, entrada, ataque e morte;
- `sfx/projeteis/` — nenhum disparo/voo/impacto de bomba, esporo, olho ou boss;
- `sfx/player/movimento/pulo/` — nenhum pulo;
- `sfx/player/movimento/passos/{madeira,terra,metal}` — só madeira em `_revisar/`;
- `sfx/player/movimento/pouso/{madeira,terra,metal}` — nenhum;
- `sfx/mundo/tochas/`, `sfx/mundo/mecanismos/`, `sfx/interacao/eco_profano/` — sem candidatos claros;
- `ambiencia/sala_descanso/`, `ambiencia/arena_boss/` — sem candidatos;
- `musica/` — os MP3/OGG atuais continuam sendo os únicos.

## 4. Riscos técnicos

1. **Formato fora do padrão:** a maioria está em 48 kHz ou 96 kHz, e muitos em estéreo. O padrão do projeto é WAV 44,1 kHz mono para SFX.
2. **Durações longas:** 9 arquivos passam de 20 s e 4 passam de 60 s. Nenhum deve entrar na pasta final sem corte.
3. **Compilações:** vários arquivos contêm dezenas de golpes. O jogo sorteia arquivos inteiros por pasta; uma compilação tocaria 20–350 s.
4. **Nomes originais:** preservam autoria, mas têm parênteses, acentos e espaços. Ao promover, renomear para ASCII minúsculo (`hit_01.wav`, `swing_01.wav`, etc.).
5. **Licenças:** `CREDITOS_E_LICENCAS.md` ainda está sem preenchimento. Não promover nenhum arquivo antes de registrar autor, URL e licença.
6. **Peso no Git:** `impactos_organicos/` sozinho tem 247,7 MiB. Se o repositório não deve carregar isso, manter compilações fora do versionamento ou usar Git LFS.

## 5. Licenças

O arquivo `assets/sons/_entrada/CREDITOS_E_LICENCAS.md` existe, mas a tabela está vazia. Ações obrigatórias antes da promoção:

- preencher uma linha por arquivo promovido;
- confirmar se a licença permite uso e redistribuição no projeto;
- manter o link original e o autor mesmo em CC0;
- evitar CC BY-NC se houver possibilidade de uso comercial.

## 6. Recomendação de promoção

### Promover primeiro (após normalizar para 44,1 kHz mono)

- `impacto_esqueleto/`: `147993`, `161381`, `192146`, `369601`, `869107`, `skeleton-hit-pesado` → 3–4 variações de `hit` em osso.
- `impactos_organicos/718259` e `733887` → impacto orgânico/metal curto.
- `pouso_pedra/422753` → `land_01`.
- `passos_pedra/fx_005` e `stone_footstep_5` → `step_01` e `step_02`.
- `ui_epica_ritualistica/861361` e `873650` → confirmação/UI curta.

### Editar antes de promover

- `murro/158783` e `232358` → 2–3 `swing_01..03` de soco.
- `morte_inimigo/skeleton-morrendo-sound.mp3` → morte curta do Skeleton.
- `impacto_globin/hit-critico_ou_pesado.wav` → 1–2 variações de Globin.
- `impactos_organicos`: `342397`, `492254`, `492548`, `593878`, `636102` → cortar takes curtos.
- `ui_epica_ritualistica`: `207183`, `467585`, `858212`, `858948`, `831971` → UI curta.
- `_revisar/844329` → porta de pedra; `_revisar/565712` → passos em madeira.

### Manter como bruto / separar depois

- Compilações `artninja`, `samsterbirdies`, `eminyildirim`, `makadunyiswe`.
- Loops de passos (`216004`, `465299`, `770072`, `footsteps-stone-sequence`, `galbenshire`, `fps-footsteps-loop`).
- Ambiência de prisão (`841640`) e sweeps (`848526`).

## 7. Próximos passos

1. Preencher `CREDITOS_E_LICENCAS.md` dos arquivos que serão usados.
2. Editar/normalizar os candidatos “Pronto” e “Editar” para WAV 44,1 kHz mono, com headroom de -3 a -1 dBFS.
3. Promover para `assets/sons/sfx/...` com nomes `hit_01`, `swing_01`, `step_01`, `land_01`, `morte_01`.
4. Manter o restante em `assets/sons/_entrada/` com o nome original.
5. Validar em jogo com a cascata de fallback: Skeleton × espada, Globin × espada, soco × qualquer e passos/pouso em pedra.

## 8. Organização aplicada nesta etapa

- Os sons integrados foram migrados de `player/`, `combate/`, `interaçao/`, `ui/` e `musica/` para a árvore `sfx/`, `ambiencia/` e `musica/`, com nomes ASCII e variações numeradas.
- A pasta `interaçao/` (com cedilha) deixou de existir; o equivalente agora é `sfx/interacao/`.
- A maior parte dos arquivos novos continua em `assets/sons/_entrada/` porque ainda precisa de corte, normalização ou registro de licença. Esses arquivos **não são carregados pelo jogo**.
- `assets/sons/_config/audio.json` concentra volumes e limites por evento.
- `assets/sons/_config/LICENCAS.csv` é o registro central de licenças.
- `core/audio.py` agora indexa as pastas no boot e resolve impacto/morte por cascata:
  `inimigos/<inimigo>/<tipo>/<arma>` → `inimigos/<inimigo>/<tipo>/_default` → `materiais/<material>/<arma>` → `materiais/<material>/_default` → `combate/generico`.
- O ataque do jogador usa `sfx/player/armas/<arma>/`; passos e pouso usam `MATERIAL_PISO` por sala.
- Passos e pouso em pedra agora usam os arquivos promovidos em `passos/pedra/` e `pouso/pedra/`; `madeira/` continua como último recurso para materiais sem arquivo.
- A suíte de testes passou com **127 testes**, incluindo a nova cascata de fallback.

## 9. Etapa 1 aplicada — passos e pouso em pedra

Arquivos promovidos com `tools/preparar_sons.py`:

| Destino | Origem | Licença |
|---|---|---|
| `sfx/player/movimento/passos/pedra/step_01..03.wav` | `fx_005_footstep_stone_l.wav` (Freesound 390764, d00121058) | CC0 |
| `sfx/player/movimento/passos/pedra/step_04..06.wav` | `stone_footstep_5.wav` (Freesound 386693, laurenmg95) | CC BY 4.0 |
| `sfx/player/movimento/pouso/pedra/land_01..03.wav` | `422753__kierankeegan__landing_stone_1.wav` (Freesound 422753, KieranKeegan) | CC0 |

Todos foram convertidos para WAV PCM 16-bit, 44,1 kHz, mono, com pico em -3 dBFS. O registro está em `assets/sons/_config/LICENCAS.csv`; a atribuição CC BY está em `assets/sons/_entrada/CREDITOS_E_LICENCAS.md`.
