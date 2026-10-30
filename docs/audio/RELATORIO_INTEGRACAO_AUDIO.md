# Relatório de integração de áudio — Profane Echo

## 1. Resumo

A primeira etapa de áudio implementa somente efeitos sonoros (SFX) com os arquivos existentes em `assets/sons/`. Música e ambiência permanecem fora do escopo.

Todos os sons passam por um gerenciador central (`core/audio.py`). As entidades e menus disparam eventos semânticos, sem conhecer caminhos de arquivo. A suíte automatizada terminou com **117 testes passando**.

## 2. Arquitetura implementada

- Singleton `audio = AudioManager()` em `core/audio.py`.
- `37` especificações de SFX carregadas uma única vez.
- `24` canais de mixer, sendo:
  - canal `0`: reservado para UI;
  - canal `1`: reservado para dano e morte do jogador;
  - canais `2`–`23`: efeitos gerais.
- Volume final calculado por evento:

```text
master × sfx × categoria × volume_base × ajuste
```

- Alterações de volume global ou de categoria também atualizam sons já em reprodução.
- Cooldown por grupo e limite de instâncias evitam rajadas e sobreposição excessiva.
- Variações centralizadas:
  - `hit`: escolhe aleatoriamente entre `hit_1`, `hit_2` e `hit_3`;
  - `player_step`: alterna `player_step_1`, `player_step_2` e `player_step_3`.
- Falha de mixer, arquivo ausente ou dispositivo indisponível geram no-op com aviso em log.
- `PROFANE_AUDIO=0` desabilita o áudio sem derrubar o jogo.
- `pygame.mixer.pre_init(44100, -16, 2, 512)` é executado antes de `pygame.init()`.

## 3. Eventos integrados

### Jogador — `entities/player.py`

| Evento | Som |
|---|---|
| Ataque | `player_attack` → `slash` |
| Dash | `player_dash` |
| Passos | `player_step` |
| Pouso | `player_land` |
| Abrir poção | `potion_open` |
| Beber poção | `potion_drink` |
| Dano | `player_hurt` |
| Morte | `player_death` |

Passos usam distância real acumulada de `48 px`, alternam variações e são suprimidos no ar, na escada, no dash, no ataque, durante dano, queda, poção, coleta, escalada e morte. O pouso exige queda mínima e é suprimido após respawn e durante queda de plataforma.

### Combate — `core/game_scene.py`, `entities/inimigo_base.py`, `entities/projeteis/bomba.py`

| Evento | Som |
|---|---|
| Acerto em inimigo | `hit` |
| Bloqueio com escudo | `block` |
| Morte de inimigo | `enemy_death` |
| Início de ataque inimigo | `enemy_attack` |
| Explosão da bomba | `bomb_explosion` |

A explosão só toca uma vez por bomba. O processamento usa os eventos já deduplicados pelo `CombatSystem`.

### Interações — baú, drops, fogueira, porta, inventário

| Evento | Som |
|---|---|
| Abrir baú | `chest_open` |
| Item saindo do baú | `item_pickup` |
| Coletar item | `item_pickup` |
| Coletar Eco | `eco_pickup` |
| Acender fogueira | `campfire_light` |
| Descansar | `campfire_rest` |
| Abrir porta | `door_open` |
| Fechar porta | `door_close` |
| Equipar arma | `equip_weapon` |
| Subir de nível | `level_up` |

O acendimento da fogueira só toca na primeira ativação. A troca de arma só toca quando o slot realmente muda.

### Interface

| Contexto | Eventos |
|---|---|
| Menu inicial | `ui_move`, `ui_confirm`, `ui_back`, `ui_error` |
| Pausa | `ui_pause_open`, `ui_pause_close`, `ui_move` |
| Inventário | `ui_inventory_open`, `ui_inventory_close`, `ui_move`, `ui_confirm`, `ui_back`, `ui_error` |
| Menu da fogueira | `ui_move`, `ui_confirm`, `ui_back`, `ui_error` |
| Salvar | `ui_save`, `ui_error` |

Não há navegação sonora por hover. O fechamento da pausa é centralizado em `_fechar_pausa()` para evitar duplicação entre `ESC`, “Continuar” e abertura do inventário.

## 4. Volumes iniciais

| Parâmetro | Valor |
|---|---:|
| Master | `0.8` |
| SFX | `1.0` |
| Combate | `0.8` |
| Jogador | `0.9` |
| Interações | `0.7` |
| UI | `0.7` |

Ajustes por arquivo:

- `slash`, `ataque` e `bomba_explosao`: `volume_base` entre `0.65` e `0.75`;
- demais SFX: `0.9`–`1.0`.

Esses valores são o ponto de partida do plano. A calibragem final por audição, com fones e caixas, permanece pendente.

## 5. Decisão sobre o ataque do jogador

`slash` foi mantido como ataque básico padrão:

- é mais curto (`1,103 s`) e se encaixa melhor em ataques repetidos;
- já era o padrão inicial do sistema;
- `ataque.mp3` tem `2,350 s`, duração potencialmente longa para o golpe básico atual.

O teste A/B temporário com `F8` foi removido. A API de troca permanece para configuração futura, mas não há mais atalho de depuração no jogo.

A comparação auditiva final entre `slash.mp3` e `ataque.mp3` ainda deve ser feita em jogo.

## 6. Validação executada

- `python -m pytest`: **117 testes passando**.
- Carga dos assets em mixer dummy: **37 especificações, 37 sons carregados, 0 falhas**.
- Testes automatizados cobrem:
  - criação do gerenciador e carregamento dos sons;
  - áudio desabilitado por ambiente;
  - arquivo ausente e evento desconhecido sem crash;
  - limites de volume e atualização de sons em reprodução;
  - canais reservados e sons críticos simultâneos;
  - cooldown, variações e troca de ataque;
  - ataque, dano, passos, pouso, poção e morte do jogador;
  - combate, bomba e interações;
  - menu inicial, pausa, inventário, fogueira, level up e save.

Validação manual pendente: escuta em jogo, especialmente mixagem relativa, repetição de passos, pouso, ataque e sons de UI.

## 7. Sons ausentes e pendências

Registrados como pendentes, fora desta etapa:

- sons específicos do boss: entrada/rugido, ataque, quebra de escudo, morte e projétil;
- sons específicos de projéteis;
- esporo do Mushroom;
- passos de inimigos;
- pulo do jogador;
- troca de sala;
- vitória contra boss;
- música e ambiência;
- normalização/conversão dos MP3 e arquivos com pico alto;
- calibragem final de volumes por audição.

## 8. Problemas e decisões conhecidas

- O canal de UI é único. Eventos de UI imediatamente consecutivos podem ser descartados se o anterior ainda estiver tocando. Isso evita sobreposição e sons duplicados, mas exige que cada ação prioritize o som mais específico.
- `slash.mp3` e `ataque.mp3` estão em MP3 24 kHz estéreo, diferentes do restante em WAV 44,1 kHz mono. Não houve conversão nesta etapa.
- `slash.mp3` e `ataque.mp3` têm picos próximos de `0 dBFS`; por isso usam volume base reduzido.
- A pasta `fontes/` é ignorada pelo Git. Este relatório foi salvo em `docs/audio/` para permanecer versionável.
- Nenhuma lógica de dano, hitbox, timing, IA ou balanceamento foi alterada.

## 9. Arquivos principais

- `core/audio.py`
- `main.py`
- `core/game_scene.py`
- `core/menu.py`
- `core/menu_fogueira.py`
- `core/inventario.py`
- `entities/player.py`
- `entities/inimigo_base.py`
- `entities/projeteis/bomba.py`
- `entities/objetos/bau.py`
- `entities/objetos/drop.py`
- `entities/objetos/drop_eco.py`
- `entities/objetos/fogueira.py`
- `entities/objetos/porta.py`
- `tests/test_audio.py`
- `tests/test_player_audio.py`
- `tests/test_combat_audio.py`
- `tests/test_interaction_audio.py`
- `tests/test_ui_audio.py`
