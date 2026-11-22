# Relatório Fase H.2 — Correções de Gameplay e SFX

## Escopo
Correções pontuais dos 5 problemas reportados em teste manual, preservando Fase H.1 (música/fades/contextos), Fase H/G.1, saves, mapas/Ecofocos e sem `git add/commit/push`.

## Problemas e correções

### 1) Inventário não abre corretamente (prioridade máxima)
- **Causa raiz**: string corrompida na opção de pausa em `core/game_scene.py` (`"Inventǭrio"`/bytes corrompidos) não batia com a opção exibida `"Inventário"`, impedindo o branch que chama `self.inventario.abrir()`.
- **Correção**: normalizada a comparação para `"Inventário"` em `core/game_scene.py`.
- **Preservado**: ESC/pausa, fechamento por ESC dentro do inventário, supressão G.1, sem novo atalho.

### 2) Passos do jogador com alternância inconsistente
- **Causa raiz**: `_tocar_cascata/_escolher_arquivo` usava escolha aleatória por pasta; passos podiam repetir/trocar timbre de forma inconsistente.
- **Correção**: `core/audio.py` agora usa sequência determinística por pasta quando `grupo == "step"` (`_indices_cascata`), mantendo fallback por material. Adicionado `ultimo_sfx_debug` para diagnóstico pontual de SFX.
- **Preservado**: cascata de material, cooldown/volume existentes, sem mudança em música H.1.

### 3) Swing da espada reproduzindo impacto metálico
- **Causa raiz**: `play_swing()` incluía `sfx/combate/generico` com `prefixo_generico="hit"`, caindo em `generico_hit_*` quando faltava swing específico.
- **Correção**: `play_swing()` restrito a `sfx/player/armas/{arma}` e `sfx/player/armas/_default`; sem fallback para hits metálicos genéricos.
- **Preservado**: `play_hit`/`play_block` e resolução de combate por `DamageEvent`.

### 4) Hit do Flying Eye com SFX inadequado
- **Causa raiz**: cascata priorizava hits específicos do Flying Eye; arquivos específicos eram curtos/duplicados e destoavam do material etéreo.
- **Correção**: substituição pontual dos arquivos de hit do Flying Eye (espada/machado/soco/_default) pelos equivalentes etéreos já existentes em `assets/sons/sfx/materiais/etereo/*`, mantendo nomes/caminhos esperados pela cascata.
- **Preservado**: `SOM_ID/MATERIAL` do Flying Eye, sem reordenar cascata global.

### 5) Escudo do chefe protegendo corpo inteiro, inclusive costas
- **Causa raiz**: `InimigoBase.receber_hit` retornava bloqueio sempre que `_escudo_ativo` era `True`, sem checagem direcional.
- **Correção**: bloqueio apenas quando golpe é frontal (`olhando_dir` vs `direcao_knockback` do CombatSystem). Feedback visual do escudo em `SkeletonBoss._desenhar_extra` restrito à faixa frontal.
- **Preservado**: quebra de guarda, cooldowns, hiper armor, reação de stagger e comportamento de combate existente.

## Testes adicionados
- `tests/test_fase_h2.py`
  - `test_swing_nao_usa_hit_generico_como_fallback`
  - `test_passos_sequencia_deterministica`
  - `test_boss_escudo_bloqueia_frente_mas_nao_costas`
  - `test_inventario_opcao_pausa_abre`

## Valida??o executada
- `python -m py_compile core\audio.py core\game_scene.py entities\inimigo_base.py entities\monsters\skeleton_boss.py tests\test_fase_h2.py` ? OK
- `python -m pytest tests\test_fase_h2.py tests\test_audio_cascata.py tests\test_audio_auditoria.py tests\test_combat_audio.py tests\test_enemy_regressions.py -q --tb=short` ? **80 passed** (pr?-H.2.1); foco H.2 p?s-revis?o: `tests/test_fase_h2.py tests/test_audio_cascata.py` = **19 passed**.
- `python -m pytest -q --tb=short` ? **294 passed, 0 failed** (exit 0).
- `git diff --check` ? sem erros; warnings LF?CRLF em arquivos tocados/preexistentes.

## H.2.1 ? revis?o ap?s teste manual (causas reais)

### 1) Invent?rio n?o abria pelo menu de pausa
- **Causa real**: op??o/fluxo de pausa dependia de string fr?gil com encoding corrompido (`Invent?rio`), sem ID est?vel de a??o.
- **Arquivos/fun??es**: `core/game_scene.py` (`__init__` opcoes/ACOES_PAUSA, `_ativar_opcao_pausa`, `_abrir_inventario_por_pausa`, `_atualizar_pausa`).
- **Evid?ncia anterior**: instrumenta??o mostrou sele??o `Invent?rio`; H.2 cobria igualdade textual, n?o o fluxo completo robusto.
- **Altera??o**: a??es est?veis `ACOES_PAUSA`, normaliza??o `Invent?rio`, `_abrir_inventario_por_pausa()` com valida??o de estado, pausa fecha antes de abrir invent?rio. Fluxo main?scene?invent?rio preservado.
- **Testes**: `tests/test_fase_h2.py::test_inventario_opcao_pausa_abre`, `test_inventario_fluxo_completo_pausa_render_fechamento`.
- **Evid?ncia p?s-fix**: integra??o main-like passou (ESC pausa?seleciona Invent?rio?Enter/mouse?`paused False inv True` por frames seguintes?ESC fecha invent?rio).

### 2) Passos continuam alternando sons estranhos
- **Causa real**: `sfx/player/movimento/passos/pedra` tem 33 WAVs heterog?neos (0.19s?0.45s, hashes distintos). Sele??o determin?stica percorria todos, expondo timbres incoerentes no mesmo piso/material (`pedra`).
- **Arquivos/fun??es**: `core/audio.py` (`_arquivos_para_grupo`, `_escolher_arquivo`, `_PASSOS_CURADOS`, `play_step`).
- **Evid?ncia anterior**: diagn?stico 20 passos consecutivos (cooldown bypass) tocou 20 arquivos ?nicos `step_01..20`.
- **Altera??o**: subconjunto curado pedra `step_01..06`, determin?stico dentro do subconjunto; assets originais n?o modificados.
- **Teste**: `tests/test_fase_h2.py::test_passos_pedra_20_consecutivos_curados`.
- **Evid?ncia p?s-fix**: 20 passos consecutivos = ciclo apenas `step_01..06`; sem troca de pasta/material.

### 3) Espada continua produzindo som met?lico sem atingir nada
- **Causa real**: swing da espada longa cont?m impacto met?lico no pr?prio asset. `armas_espada_longa_swing_01.mp3`: 1.103s, peak 1.0, onset ~0.10s; `swing_02.wav`: 1.804s. `play_swing('espada_longa')` tocava swing_01.
- **Arquivos/fun??es**: `core/audio.py` (`play_swing`).
- **Evid?ncia anterior**: instrumenta??o `_tocar_som` em swing no ar capturou apenas `.../espada_longa/armas_espada_longa_swing_01.mp3`; an?lise confirmou peak/onset met?lico.
- **Altera??o**: `play_swing` mapeia `espada_longa` para `sfx/player/armas/_default` (whoosh curto, sem `hit`); sem fallback para combate gen?rico. `play_hit/play_block` preservados.
- **Testes**: `tests/test_fase_h2.py::test_swing_nao_usa_hit_generico_como_fallback`, `test_swing_espada_longa_nao_emite_hit_metalico`; `tests/test_audio_cascata.py::test_play_swing_encontra_arma_especifica`.
- **Evid?ncia p?s-fix**: swing espada longa toca `armas_default_swing_01.wav` (0.156s), sem `hit` no nome/caminho.

## Arquivos alterados/criados
- `core/game_scene.py` ? IDs est?veis de pausa, abertura robusta do invent?rio.
- `core/audio.py` ? passos curados/determin?sticos, swing espada longa sem hit met?lico.
- `entities/inimigo_base.py` ? bloqueio direcional do escudo (H.2).
- `entities/monsters/skeleton_boss.py` ? feedback frontal do escudo (H.2).
- `assets/sons/sfx/inimigos/flying_eye/hit/**` ? 4 WAVs substitu?dos pontualmente por equivalentes et?reos (H.2).
- `tests/test_fase_h2.py` ? regress?es H.2/H.2.1.
- `tests/test_audio_auditoria.py`, `tests/test_audio_cascata.py` ? compatibilidade/expectativa H.2.1.
- `docs/RELATORIO_FASE_H2_CORRECOES_GAMEPLAY_SFX.md` ? este relat?rio.

## Riscos / observa??es
- Subconjunto de passos em pedra ? curado por c?digo; demais materiais mant?m comportamento anterior (pode exigir curadoria auditiva se reportado).
- `espada_longa` usa whoosh `_default` por falta de swing dedicado sem impacto met?lico; registrar asset dedicado futuro se desejado.
- N?o houve `git add/commit/push`.
