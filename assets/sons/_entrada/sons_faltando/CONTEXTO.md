# Contexto — sons pendentes (para continuar a implementação)

> **Revisão atual: 2026-11-09.** Consulte
> [OBSERVACOES.md](avaliacao_15_mp3/OBSERVACOES.md) e
> [LICENCAS_PESQUISADAS.md](avaliacao_15_mp3/LICENCAS_PESQUISADAS.md).
> Dois destinos foram integrados com novas cópias de fontes CC0 verificadas;
> onze aprovados têm prévias prontas e aguardam comprovação de origem.
> Rugido, asas e seleção de ataque por tipo estão implementados. O script agora
> rejeita `LIVRE`/licença vazia; o exemplo antigo abaixo não deve ser executado.
> O restante deste documento é o histórico de planejamento de 2026-11-08;
> contagens, gatilhos ausentes e decisões antigas foram substituídos pela revisão.

> Atualizado em 2026-11-08. Esta pasta **não é carregada pelo jogo**: é triagem.
> O que já foi promovido está em `assets/sons/sfx/` e registrado em
> `assets/sons/_config/LICENCAS.csv`.

## O que já foi feito

- Todos os SFX promovidos em `assets/sons/sfx/` foram renomeados para o padrão de
  **contexto completo** (ex.: `materiais/carne/soco/carne_soco_hit_01.wav`,
  `player/movimento/passos/pedra/movimento_passos_pedra_step_01.wav`).
  Foram 143 arquivos renomeados (0 colisões, 19 já estavam no padrão).
- `core/audio.py` (`ESPECIFICACOES`) e o filtro da cascata foram atualizados.
- `LICENCAS.csv` teve 112 linhas re-apontadas para os novos caminhos.
- Os 15 MP3 desta pasta foram reorganizados em subpastas por destino e renomeados
  com o mesmo padrão. A avaliação foi concluída; 14 continuam **pendentes de
  licença/corte/promoção** e 1 foi movido para `_uteis/magico/`.
- Testes de áudio passaram (`tests/test_audio.py`, `tests/test_audio_cascata.py`).

## Regra de nomes

`<contexto completo em snake_case>_<ação>_<NN>.wav`

- Sem espaços, acentos, maiúsculas ou parênteses.
- O contexto acumula as pastas a partir da categoria (material/inimigo + arma/parte).
- `_default` nunca vira nome: no destino ele costuma virar `default`
  (ex.: `mushroom_default_hit_01`).
- Ao promover, o `preparar_sons.py` **converte para WAV 44,1 kHz mono 16-bit,
  normaliza o pico para -3 dBFS** e aplica fade. Portanto o arquivo final é `.wav`,
  mesmo que a fonte seja `.mp3`.

## Os 15 pendentes

> **2026-11-09:** os 15 MP3 foram consolidados em `avaliacao_15_mp3/` para
> facilitar a escuta. Os caminhos da tabela abaixo são os originais, antes da
> consolidação; use `avaliacao_15_mp3/OBSERVACOES.md` para registrar a avaliação.
> Na revisão, 09 foi descartado por ora e o disparo mágico (15) foi movido para
> `_uteis/magico/`; os outros 14 aguardam licença antes da promoção.

Duração/pico/golpes medidos com `python tools/preparar_sons.py inspecionar` nesta pasta.
`golpes` é a detecção automática de transientes (ajuda a achar compilações).

| Original (commit 9b73e1c) | Nome novo | Destino sugerido | Dur | Situação |
|---|---|---|---|---|
| `Espada_hit_escudo.mp3` | `espada_escudo_hit_01.mp3` | `sfx/inimigos/boss_carrasco/hit/escudo_bloqueio/` | 1,56 s | **Confirmar destino** (ver nota) |
| `Machado_hit_escudo.mp3` | `machado_escudo_hit_01.mp3` | `sfx/inimigos/boss_carrasco/hit/escudo_bloqueio/` | **8,03 s** | **Cortar** |
| `Boss_rugido.mp3` | `boss_carrasco_rugido_01.mp3` | `sfx/inimigos/boss_carrasco/rugido/` | **4,48 s** | **Cortar** cauda; precisa de gatilho |
| `Flying_eye_assas.mp3` | `flying_eye_asas_01.mp3` | `sfx/inimigos/flying_eye/asas/` | **2,40 s** | **Cortar/loop**; sem gatilho |
| `flying_eye_bite.mp3` | `flying_eye_ataque_bite_01.mp3` | `sfx/inimigos/flying_eye/ataque/` | 2,09 s | OK |
| `flying_eye_death.mp3` | `flying_eye_morte_01.mp3` | `sfx/inimigos/flying_eye/morte/` | 1,03 s | OK |
| `Goblin_death.mp3` | `globin_morte_01.mp3` | `sfx/inimigos/globin/morte/` | 1,71 s | OK (pico baixo: normaliza) |
| `Golpe_em_gogumelo.mp3` | `mushroom_default_hit_01.mp3` | `sfx/inimigos/mushroom/hit/_default/` | 1,08 s | OK |
| `squeleton_axe.mp3` | `skeleton_ataque_machado_guerra_01.mp3` | `sfx/inimigos/skeleton/ataque/` | **3,02 s** | **Cortar** |
| `Impacto_carne.mp3` | `carne_default_hit_02.mp3` | `sfx/materiais/carne/_default/` | 1,38 s | OK |
| `Punch_em_metal.mp3` | `metal_soco_hit_01.mp3` | `sfx/materiais/metal/soco/` | **4,41 s** | **Cortar** |
| `Sword_slasher.mp3` | `armas_espada_longa_swing_03.mp3` | `sfx/player/armas/espada_longa/` | 2,19 s | **Cortar** (~0,5 s) |
| `Hit_machado_ar.mp3` | `armas_machado_guerra_swing_01.mp3` | `sfx/player/armas/machado_guerra/` | 0,57 s | OK |
| `bomba.mp3` | `projeteis_bomba_impacto_02.mp3` | `sfx/projeteis/bomba/impacto/` | **3,05 s** | **Cortar** (2 golpes → 1) |
| `ataque_magico.mp3` | `projeteis_magico_disparo_01.mp3` | **a definir** (ver nota) | **3,02 s** | **Cortar** (2 golpes) |

Notas de destino que precisam de decisão:

- **`espada_escudo_hit_01` / `machado_escudo_hit_01`**: parecem ser impactos de
  arma na **armadura/escudo do Boss Carrasco**, que já tem
  `boss_carrasco_escudo_bloqueio_hit_01.wav`. Sugestão: promover como `_02`/`_03`
  dessa pasta. Se a intenção for bloqueio genérico, o destino é
  `sfx/combate/generico/`. `play_block(inimigo)` consulta
  `sfx/inimigos/<inimigo>/hit/escudo_bloqueio` e depois o genérico.
- **`projeteis_magico_disparo_01`**: não existe pasta final `projeteis/magico/`.
  Opções: criar `sfx/projeteis/magico/disparo/` ou encaixar em
  `sfx/projeteis/boss/disparo/` (ou `esporo`/`olho`). Lembrar que
  `play_projectile` **não é chamado em lugar nenhum** hoje.

## O que o código já indexa sozinho

Estes destinos são lidos por varredura de pasta; **não precisa mexer em
`ESPECIFICACOES`**, só soltar o arquivo no lugar:

- `play_swing(arma)` → `sfx/player/armas/<arma>/` e `.../_default/`
- `play_block(inimigo)` → `sfx/inimigos/<inimigo>/hit/escudo_bloqueio/` e genérico
- hits/ataques/mortes de inimigos e materiais → pastas `sfx/inimigos/...` e
  `sfx/materiais/...`
- `play_projectile` existe, mas **não tem chamada** (só `bomb_explosion` toca).

Gatilhos que ainda **não existem** e precisam ser implementados:

- rugido do Boss (`boss_carrasco/rugido/`)
- asas do Flying Eye (`flying_eye/asas/`)
- tiro mágico (`play_projectile`)

## Como promover

Monte um CSV (`origem;destino`) e rode o dry-run antes:

```csv
origem;destino;licenca;inicio_s;fim_s;dur_max_s
assets/sons/_entrada/sons_faltando/3_materiais/carne/carne_default_hit_02.mp3;sfx/materiais/carne/_default/carne_default_hit_02.wav;LIVRE;;;1.0
```

```bash
python tools/preparar_sons.py inspecionar assets/sons/_entrada/sons_faltando
python tools/preparar_sons.py fatiar <arquivo> --max 8 --dur-max 1.0
python tools/preparar_sons.py promover tools/promocao_pendentes.csv --dry-run
python tools/preparar_sons.py promover tools/promocao_pendentes.csv
```

`destino` aceita `{n}` para numerar automaticamente. O script marca as linhas
promovidas com `#` para não duplicar numa segunda execução.

## Músicas — licenças e uso

Pasta `musicas/`. **Nada aqui está commitado** (é untracked). Leia o alerta antes
de `git add`.

| Pack | Faixas | Licença | Situação |
|---|---|---|---|
| `1-music-loop-bundle-troubadeck` | 19 | **CC0** (Abstraction/Tallbeard) | Seguro |
| `2-music-loop-bundle-2026-q3` | 6 | **CC0** (Abstraction) | Seguro |
| `3-music-loop-bundle-2026-q1` | 7 | **CC0** (Abstraction) | Seguro |
| `Fantasy RPG Music Vol. 2` | 18 | **AlkaKrab** (royalty-free, uso comercial permitido) | **Ver alerta** |
| `TopfHelm_Medieval_RPG_Music_Pack` | 3 | **Grátis só NÃO-comercial**, atribuição obrigatória | **Ver alerta** |

Uso sugerido (anotação do autor em `Fantasy RPG Music Vol. 2/mp3/anotação.md`):

- `Action 2` → música geral de combate; outros `Action` → momentos mais grandiosos.
- `Ambient 1` → menu inicial; `Ambient 2` → menu da fogueira.
- `Night Ambient 2/3` → exploração tranquila do calabouço (fora de batalha).
- Demais `Ambient`/`Light Ambient` → sem função definida, úteis no futuro.

### ⚠️ Alerta de licença (ler antes de commitar)

O repositório é **MIT/open-source**, ou seja, publicar os arquivos é redistribuí-los.

- **AlkaKrab** permite uso comercial, mas proíbe redistribuir a faixa "as-is" e diz
  explicitamente: *"If you want to use these tracks in open-source games, contact
  me directly for a permission."* → **não commitar `Fantasy RPG Music Vol. 2/`
  sem autorização por escrito** (`alkakrab04@gmail.com`).
- **TopfHelm** é grátis apenas para projetos **não-comerciais** e exige atribuição:
  `Music by TopfHelm — https://topfhelm.com`. Projeto de faculdade se encaixa, mas
  redistribuir num repo público é zona cinzenta. Se for commitado, incluir a
  atribuição nos créditos e manter o texto da licença junto.
- Os packs **Abstraction são CC0** e não têm esse problema.

Enquanto a licença não estiver resolvida, mantenha `musicas/` **fora do commit**
(ex.: `git add` só dos 15 SFX; não usar `git add -A`/`git add .`).

## Checklist de amanhã

1. Decidir destino de `espada_escudo_hit_01`, `machado_escudo_hit_01` e
   `projeteis_magico_disparo_01`.
2. Cortar os arquivos marcados **Cortar** (ouvir as fatias).
3. Promover por CSV → gera `.wav` e registra licença.
4. Implementar gatilhos de rugido, asas e `play_projectile` (se for usar).
5. Rodar `python -m pytest -q` e `git lfs fsck`.
6. Só então decidir o que fazer com `musicas/` (licença!).
