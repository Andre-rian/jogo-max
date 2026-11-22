# Relatório Fase H.1 — Direção Musical

## Escopo
- Ajuste de direção musical/progressão sonora sobre a base da Fase H.
- **Não refatorado**: sistema de áudio/sliders/persistência da Fase H (`core/preferencias.py`, `configuracoes_usuario.json`, sliders/volumes por categoria).
- Sem commit/push; sem mudanças em IA/combate/progressão/inventário/mapas/Ecofocos além da integração sonora necessária.

## Inventário de áudio (músicas e ambiências reais)

### Músicas (`assets/sons/musica`)
| Caminho completo (repo) | Contexto | Uso H.1 | Seleção/motivo | Início | Interrupção/fade-out | Fade-in | Repetição |
|---|---|---|---|---|---|---:|---|
| `assets/sons/musica/menu/menu_01.mp3` | Menu principal | Usada | Única faixa em `musica/menu`; selecionada por `AudioManager._resolver_caminho_musica("menu")` | `main.py` ao iniciar app e ao voltar ao menu (`audio.play_music("menu", ..., fade_ms=2500/2000)`) | Ao entrar no jogo, contexto musical de sala comum pede stop com fade (`_atualizar_audio_sala` -> `stop_music(fade_ms=800)`) | 2.5s inicial, 2.0s retorno | Loop infinito (`pygame.mixer.music.play(loops=-1)`) |
| `assets/sons/musica/exploracao/exploracao_01.mp3` | Exploração | **Preservada, desativada por padrão** | Arquivo mantido para reuso futuro; `MUSICA_POR_SALA` não mapeia salas comuns para música | Não inicia automaticamente nas salas comuns | N/A em fluxo padrão | N/A | N/A |
| `assets/sons/musica/boss/boss_01.mp3` | Batalha chefe | Usada | Única faixa em `musica/boss`; selecionada por contexto `boss` | Somente quando batalha do chefe realmente inicia (`GameScene._atualizar_estado_batalha_chefe`) | Ao derrotar chefe, sala muda ou batalha encerra: fade-out e retorno à ambiência/regra da sala | 800ms | Loop infinito |
| `assets/sons/musica/descanso/descanso_01.ogg` | Descanso/Ecofoco | Usada | Única faixa em `musica/descanso`; contexto `descanso` | Sala de descanso (`MUSICA_POR_SALA`/`AMBIENCIA_POR_SALA`) ou menu de fogueira aberto | Ao fechar menu fogueira/sair do contexto de descanso: transição por regra de sala; fade-out quando aplicável | 1200ms | Loop infinito; **não reinicia** se contexto já é `descanso` |

### Ambiências (`assets/sons/ambiencia`)
| Caminho completo (repo) | Contexto/sala | Uso H.1 | Seleção/motivo | Início | Interrupção | Repetição | Observação |
|---|---|---|---:|---|---|---|---|
| `assets/sons/ambiencia/calabouco/841640__newlocknew__ambdsgn_madness-prisonambiencelaughterscreamsfootstepscell-doorsceiling-leaka-faulty-lamp(funciona como um bom som de atmosphera de fundo, vamos promover-lo a ).mp3` | Calabouço padrão/salas comuns | Usada | Primeiro/único arquivo válido na pasta `ambiencia/calabouco` indexada; fallback padrão de sala | Ao carregar sala sem ambiência específica (`AMBIENCIA_POR_SALA.get(...,"calabouco")`) | Troca de sala/stop explícito | Loop no canal de ambiência | Nome longo preservado; arquivo já existente |
| `assets/sons/ambiencia/sala_descanso/sala_descanso_caverna_01.wav` | Sala descanso (`calabouço_4`) | Usada | Arquivo na pasta `ambiencia/sala_descanso` | Carregamento/troca para sala descanso | Troca de sala | Loop | Coexiste com música `descanso` discreta |
| `assets/sons/ambiencia/arena_boss/arena_boss_sombria_01.wav` | Arena boss (`calabouço_5`) | Disponível/selecionável | Pasta `ambiencia/arena_boss` indexada; escolha por `_som_valido`/`_escolher_arquivo` | Carregamento/troca para arena boss | Troca de sala | Loop | Música de boss só entra na batalha real |
| `assets/sons/ambiencia/arena_boss/arena_boss_sombria_02.wav` | Arena boss (`calabouço_5`) | Disponível/selecionável | Variante na mesma pasta | Conforme seleção | Troca de sala | Loop | Mantido; sem remoção |

## Mapeamento por sala/evento (H.1)

| Sala/evento | Ambiência | Música | Regra H.1 |
|---|---|---|---|
| Menu inicial | Nenhuma ambiência de calabouço | `menu` | Fade-in 2.5s; respeita sliders; sem corte seco |
| Menu -> Novo Jogo / Continuar | `calabouco` (ou da sala carregada) | Nenhuma por padrão em salas comuns | Música do menu faz fade-out; exploração comum fica só com ambiência |
| Calabouço 1 (`calabouço_1`) | `calabouco` | nenhuma | Sem trilha automática |
| Calabouço 2 (`calabouço_2`) | `calabouco` | nenhuma | Sem trilha automática |
| Calabouço 3 (`calabouço_3`) | `calabouco` | nenhuma | Sem trilha automática |
| Calabouço 4 / sala descanso (`calabouço_4`) | `sala_descanso` | `descanso` (discreta) | Música de descanso preservada, volume alvo menor que boss |
| Calabouço 5 / arena boss (`calabouço_5`) | `arena_boss` | `boss` só após batalha iniciar | Antes do aggro/encontro real: apenas ambiência |
| Inimigos comuns | Ambiência da sala | nenhuma automática | Não adiciona música intensa automática |
| Batalha chefe inicia | Ambiência da sala | `boss` | Gatilho: `_atualizar_estado_batalha_chefe` (player vivo + perto/aggro real), não no carregamento |
| Chefe derrotado | Ambiência da sala | fade-out para regra da sala | Retorna à ambiência; sem música residual entre salas |
| Ecofoco abre menu | Ambiência atual | `descanso` | Se já em descanso, não reinicia; se solicitado mesmo contexto, mantém reprodução |
| Ecofoco fecha menu | Ambiência da sala | regra da sala | Sem corte/reinício brusco |
| Retorno Menu Principal | N/A | `menu` | `stop_all_sfx`; música menu com fade-in 2.0s |

## Diagnóstico de reprodução (antes H.1)

- `AudioManager.play_music` tocava por contexto/pasta e aceitava apenas `contexto`; não havia estado de fade-out/fade-in progressivo controlado por `atualizar()`.
- Troca de música usava `stop_music()` imediato e `play(..., fade_ms=500)` padrão; faltava controle explícito de fade-out antes de novo contexto.
- `GameScene._atualizar_audio_sala` iniciava música `exploracao` por padrão em salas comuns e iniciava `boss` quando `boss_atual.vivo`, inclusive na carga da sala.
- Menu iniciava música sem fade-in gradual de 2-3s.
- Diagnóstico de música não incluía sala atual, contexto solicitado, caminho exato, volume final, ambiência ativa e motivo da transição de forma consolidada.

## Mudanças implementadas

### `core/audio.py`
- Estado musical H.1: `parada/tocando/fade_in/fade_out`, volume alvo por contexto, fade por atualização de frame (`atualizar()`), pendência de faixa após fade-out.
- `play_music(contexto, origem=None, fade_ms=..., fade_out_ms=..., motivo=...)` com compatibilidade de assinatura por chamada defensiva onde aplicável.
- `stop_music(fade_ms=..., motivo=...)` suporta fade-out.
- `set_contexto_sala` e `obter_estado_musical()` para diagnóstico.
- Volume alvo por contexto: `menu=1.0`, `exploracao=1.0`, `boss=1.0`, `descanso=0.72` (descanso mais discreto).
- Ambiência registra nome/caminho ativo; música não interfere no canal de ambiência.

### `core/game_scene.py`
- `MUSICA_POR_SALA` adicionado: salas comuns `None`, descanso `descanso`, arena boss sem música automática.
- `boss_batalha_ativa` adicionado; boss não inicia música/entrada na carga.
- `_atualizar_estado_batalha_chefe()` inicia batalha apenas com player vivo e encontro real (detecção/aggro).
- `_atualizar_audio_sala()` aplica ambiência sempre; música só quando contexto exige; caso contrário fade-out para priorizar ambiência.
- Chefe derrotado: `boss_batalha_ativa=False`, fade-out/retorno por `_atualizar_audio_sala(motivo_extra="chefe_derrotado")`.

### `main.py`
- Menu inicial: `play_music("menu", fade_ms=2500)`.
- Retorno menu: `play_music("menu", fade_ms=2000, fade_out_ms=800)`.
- Loop principal chama `audio.atualizar()`.

### Testes
- `tests/test_audio_auditoria.py` atualizado para novo comportamento de contexto musical/fade/boss.
- Adicionado teste de boss: música só após batalha iniciar.
- Adicionado teste de fade-out/fade-in por atualização de tempo.

## Antes / Depois (comportamento)

| Cenário | Antes | Depois (H.1) |
|---|---|---|
| Menu inicial | Música iniciava sem fade-in 2-3s explícito | Fade-in 2.5s |
| Salas comuns 1-3 | Música `exploracao` em loop | Apenas ambiência; `exploracao_01.mp3` preservada |
| Entrar arena boss | Música `boss` podia iniciar com boss vivo carregado | Ambiência da arena; música `boss` só no encontro real |
| Derrotar chefe | Contexto dependia de atualização genérica | Fade-out boss e retorno à ambiência/regra da sala |
| Sala descanso/Ecofoco | Música descanso tocava; risco de reinício por chamadas repetidas | Descanso preservado, discreto; mesmo contexto não reinicia |
| Diagnóstico | Eventos gerais | Estado musical consolidado: sala, estado, solicitado, arquivo, volume final, ambiência, motivo, fade |

## Simultaneidade música/ambiência
- **Simultâneas por design**: descanso (`descanso` + ambiência de sala descanso) e boss (`boss` + ambiência de arena) quando aplicável.
- **Exploração comum**: ambiência ativa, música ausente por padrão.
- Canais/streams separados: `pygame.mixer.music` para música; canais mixer para ambiência/SFX.

## Arquivos alterados (H.1)
- `core/audio.py`
- `core/game_scene.py`
- `main.py`
- `tests/test_audio_auditoria.py`
- `docs/audio/RELATORIO_FASE_H1_DIRECAO_MUSICAL.md`

## Validação executada
- `python -m py_compile core\audio.py core\game_scene.py main.py tests\test_audio_auditoria.py` — OK.
- `python -m pytest tests\test_audio.py tests\test_audio_auditoria.py tests\test_ui_audio.py tests\test_interaction_audio.py -q --tb=short` — **50 passed**.
- `python -m pytest -q --tb=short` — **289 passed**.

## Limitações / avaliação auditiva manual recomendada
- Não foi executada avaliação auditiva humana real no ambiente desta sessão; validar manualmente:
  - Menu -> Novo Jogo: fade-in menu perceptível e transição suave para ambiência do calabouço.
  - Menu -> Continuar: idem.
  - Calabouço 1 -> Calabouço 2: ambiência contínua/coerente, sem música de exploração automática.
  - Exploração com/sem inimigos comuns: sem música intensa automática.
  - Início batalha chefe: música entra apenas ao encontro real.
  - Derrota chefe: fade-out da música e retorno à ambiência da sala.
  - Ecofoco: abrir/fechar menu não reinicia nem sobrepõe música de descanso.
  - Retorno ao menu principal: transição suave.
  - Sliders música/ambiência em 0% separadamente: categorias respeitadas.
- `pygame.mixer.music` não expõe posição/duração exata de forma uniforme; diagnóstico usa estado interno, caminho, volume calculado e motivo.
