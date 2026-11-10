# Avaliação dos 15 SFX legados

> Pasta de triagem: **não é carregada pelo jogo**. Os arquivos foram consolidados
> aqui apenas para facilitar a escuta e a anotação.
>
> Dos 15 MP3, 14 continuam preservados, sem comprovação individual de origem.
> O rejeitado 09 foi removido na limpeza de 2026-11-10; hash e recuperação em
> [LIMPEZA_ENTRADA.csv](../../../../../docs/audio/auditoria_geral/LIMPEZA_ENTRADA.csv).
> Para 03 e 07 foram obtidas cópias de fontes **CC0 verificadas**, editadas e
> integradas ao jogo. Não foi atribuída uma licença por suposição aos MP3 antigos.
>
> **Revisão em 2026-11-09:** 2 destinos integrados com fontes verificadas,
> 11 aprovados com prévias prontas aguardando comprovação de origem,
> 1 rejeitado (09) e 1 reservado para o futuro (15).
> Pesquisa, fontes e limitações: [LICENCAS_PESQUISADAS.md](LICENCAS_PESQUISADAS.md).
> Edições dos 13 aprovados: [PREVIAS.csv](PREVIAS.csv) e [previas_editadas/](previas_editadas/).
> As durações abaixo são dos originais; o CSV registra as durações após aparar silêncio.

## Como preencher

1. Ouça cada arquivo.
2. Escreva em **Observação** o que achou (timbre, duração, cortes necessários).
3. Marque uma opção em **Decisão**.
4. Se souber o destino correto, anote em **Destino final**.

## Resumo

| # | Arquivo | Destino sugerido | Duração | Observação | Decisão |
|---:|---|---|---:|---|---|
| 01 | `espada_escudo_hit_01.mp3` | `sfx/combate/generico/` (`_04`) | 1,56 s | Está ok; funciona como defesa contra arma cortante, não apenas espada. | Promover no genérico |
| 02 | `machado_escudo_hit_01.mp3` | `sfx/combate/generico/` (`_05`) | 8,03 s | Necessário corte; também serve como defesa de escudo a um impacto. | Cortar e promover no genérico |
| 03 | `boss_carrasco_rugido_01.mp3` | `sfx/inimigos/boss_carrasco/rugido/` | 4,48 s | Está ok; leve corte para ficar mais curto, com final suave. | Cortar com fade suave |
| 04 | `flying_eye_asas_01.mp3` | `sfx/inimigos/flying_eye/asas/` | 2,40 s | Não precisa de corte; pode ser subdividido, mas está ok. | Promover; loop opcional |
| 05 | `flying_eye_ataque_bite_01.mp3` | `sfx/inimigos/flying_eye/ataque/` | 2,09 s | Leve corte no final; ok para o destino. | Cortar final |
| 06 | `flying_eye_morte_01.mp3` | `sfx/inimigos/flying_eye/morte/` | 1,03 s | Está ok; atentar à duração da animação de morte do flying eye. | Promover; conferir animação |
| 07 | `globin_morte_01.mp3` | `sfx/inimigos/globin/morte/` | 1,71 s | Está ok; atentar à duração da animação de morte. | Cortar para ~1,3 s |
| 08 | `mushroom_default_hit_01.mp3` | `sfx/inimigos/mushroom/hit/_default/` | 1,08 s | Ok; cortar o final, pois o som deve ser o hit do player. | Cortar final; entrar como `_02` |
| 09 | `skeleton_ataque_machado_guerra_01.mp3` | `sfx/inimigos/skeleton/ataque/` | 3,02 s | Não agrada: o som sugere alvo acertado; funcionaria sem o impacto. | Descartar por ora |
| 10 | `carne_default_hit_02.mp3` | `sfx/materiais/carne/_default/` | 1,38 s | Ok; alto demais, deve ficar baixo em gameplay; funciona como alternativo. | Promover com volume baixo (`_02`) |
| 11 | `metal_soco_hit_01.mp3` | `sfx/materiais/metal/soco/` | 4,41 s | Corte para ~1,50 s. | Cortar para ~1,50 s |
| 12 | `armas_espada_longa_swing_03.mp3` | `sfx/player/armas/espada_longa/` | 2,19 s | Leve corte no final; fica ok. | Cortar leve final (`_03`) |
| 13 | `armas_machado_guerra_swing_01.mp3` | `sfx/player/armas/machado_guerra/` | 0,57 s | Ok. | Promover |
| 14 | `projeteis_bomba_impacto_02.mp3` | `sfx/projeteis/bomba/impacto/` | 3,05 s | Cortar um pouco do final; fica ok. | Cortar final (`_02`) |
| 15 | `projeteis_magico_disparo_01.mp3` | `_uteis/magico/` (futuro) | 3,02 s | Disparo mágico guardado por enquanto; pode ser útil no futuro. | Movido para úteis futuros |

---

## 01 — espada_escudo_hit_01.mp3

- **Origem:** `1_combate/bloqueio/espada_escudo_hit_01.mp3`
- **Destino sugerido:** `sfx/combate/generico/` como `_04`
- **Duração:** 1,56 s
- **Pendência:** nenhuma técnica; entra no bloqueio genérico, disponível para todos os inimigos.
- **Observação:** Está ok; funciona como defesa contra arma cortante, não apenas espada.

- **Decisão:** [x] promover  [ ] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/combate/generico/generico_block_04.wav`.

---

## 02 — machado_escudo_hit_01.mp3

- **Origem:** `1_combate/bloqueio/machado_escudo_hit_01.mp3`
- **Destino sugerido:** `sfx/combate/generico/` como `_05`
- **Duração:** 8,03 s
- **Pendência:** cortar a cauda longa. A inspeção detectou 1 golpe, então o excesso é cauda, não múltiplos impactos. Corte candidato: ~0,65 s.
- **Observação:** Necessário corte; também serve como defesa de escudo a um impacto.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/combate/generico/generico_block_05.wav`, após corte para ~0,65 s.

---

## 03 — boss_carrasco_rugido_01.mp3

- **Origem:** `2_inimigos/boss_carrasco/rugido/boss_carrasco_rugido_01.mp3`
- **Destino sugerido:** `sfx/inimigos/boss_carrasco/rugido/`
- **Duração:** 4,48 s
- **Implementação:** fonte CC0 de Robson220pl integrada com 3,20 s e fade final de 300 ms. O Boss ruge uma vez ao detectar o jogador. O MP3 antigo permanece preservado; detalhes na pesquisa de licenças.
- **Observação:** Está ok; leve corte para ficar mais curto, com final suave.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/boss_carrasco/rugido/boss_carrasco_rugido_01.wav`, após corte com fade suave.

---

## 04 — flying_eye_asas_01.mp3

- **Origem:** `2_inimigos/flying_eye/asas/flying_eye_asas_01.mp3`
- **Destino sugerido:** `sfx/inimigos/flying_eye/asas/`
- **Duração:** 2,40 s
- **Pendência:** confirmar a fonte/licença do MP3. Prévia editada pronta; gatilho implementado com intervalo de 144 ticks, volume baixo e sem novos disparos durante morte, hit, knockback ou fora do alcance. Não há loop permanente.
- **Observação:** Não precisa de corte; pode ser subdividido, mas está ok.

- **Decisão:** [x] promover  [ ] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/flying_eye/asas/flying_eye_asas_01.wav`; criar gatilho e avaliar loop.

---

## 05 — flying_eye_ataque_bite_01.mp3

- **Origem:** `2_inimigos/flying_eye/ataque/flying_eye_ataque_bite_01.mp3`
- **Destino sugerido:** `sfx/inimigos/flying_eye/ataque/`
- **Duração:** 2,09 s
- **Pendência:** confirmar a fonte/licença. Prévia cortada para 1,30 s. Confirmado: `play_enemy_attack` consulta `ataque/<tipo>/` e depois esta pasta.
- **Observação:** Leve corte no final; ok para o destino.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/flying_eye/ataque/flying_eye_ataque_bite_01.wav`, após corte final.

---

## 06 — flying_eye_morte_01.mp3

- **Origem:** `2_inimigos/flying_eye/morte/flying_eye_morte_01.mp3`
- **Destino sugerido:** `sfx/inimigos/flying_eye/morte/`
- **Duração:** 1,03 s
- **Pendência:** conferir alinhamento com a morte: a animação tem 4 frames × 6 ticks ≈ 0,4 s, mas o estado dura `Duracao_morte = 60` ticks (~1 s), então o som de 1,03 s encaixa no tempo de remoção.
- **Observação:** Está ok; atentar à duração da animação de morte do flying eye.

- **Decisão:** [x] promover  [ ] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/flying_eye/morte/flying_eye_morte_01.wav`.

---

## 07 — globin_morte_01.mp3

- **Origem:** `2_inimigos/globin/morte/globin_morte_01.mp3`
- **Destino sugerido:** `sfx/inimigos/globin/morte/`
- **Duração:** 1,71 s
- **Implementação:** fonte CC0 de spookymodem integrada. Limite de 1,30 s; após aparar o silêncio, o áudio útil ficou em 0,686 s, com pico de -3 dBFS. Encaixa no estado de morte de 60 ticks (~1 s). O MP3 antigo foi preservado.
- **Observação:** Está ok; atentar à duração da animação de morte.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/globin/morte/globin_morte_01.wav`, após corte para ~1,3 s.

---

## 08 — mushroom_default_hit_01.mp3

- **Origem:** `2_inimigos/mushroom/hit/mushroom_default_hit_01.mp3`
- **Destino sugerido:** `sfx/inimigos/mushroom/hit/_default/` como `_02`
- **Duração:** 1,08 s
- **Pendência:** cortar o final; o `mushroom_default_hit_01.wav` do lote 2 é mantido. Corte candidato: ~0,65 s.
- **Observação:** Ok; cortar o final, pois o som deve ser o hit do player.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/inimigos/mushroom/hit/_default/mushroom_default_hit_02.wav`, após corte final.

---

## 09 — skeleton_ataque_machado_guerra_01.mp3

- **Origem:** `2_inimigos/skeleton/ataque/skeleton_ataque_machado_guerra_01.mp3`
- **Destino sugerido:** `sfx/inimigos/skeleton/ataque/`
- **Duração:** 3,02 s
- **Pendência:** o impacto já está embutido. A inspeção detectou 1 golpe só, então não dá para separar o impacto com um corte simples. Reavaliar apenas se houver edição espectral.
- **Observação:** Não agrada: o som sugere alvo acertado; funcionaria sem o impacto.

- **Decisão:** [ ] promover  [ ] cortar  [x] descartar  [ ] outro destino
- **Destino final:** — (reavaliar apenas se o impacto for removido).

---

## 10 — carne_default_hit_02.mp3

- **Origem:** `3_materiais/carne/carne_default_hit_02.mp3`
- **Destino sugerido:** `sfx/materiais/carne/_default/`
- **Duração:** 1,38 s
- **Pendência:** baixar o volume em gameplay; já existe `carne_default_hit_01.wav`, então entra como `_02`.
- **Observação:** Ok; alto demais, deve ficar baixo em gameplay; funciona como alternativo.

- **Decisão:** [x] promover  [ ] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/materiais/carne/_default/carne_default_hit_02.wav`, com volume reduzido em gameplay.

---

## 11 — metal_soco_hit_01.mp3

- **Origem:** `3_materiais/metal/metal_soco_hit_01.mp3`
- **Destino sugerido:** `sfx/materiais/metal/soco/`
- **Duração:** 4,41 s
- **Pendência:** cortar para ~1,50 s; a pasta final está vazia.
- **Observação:** Corte para ~1,50 s.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/materiais/metal/soco/metal_soco_hit_01.wav`, após corte para ~1,50 s.

---

## 12 — armas_espada_longa_swing_03.mp3

- **Origem:** `4_player/espada_longa/armas_espada_longa_swing_03.mp3`
- **Destino sugerido:** `sfx/player/armas/espada_longa/`
- **Duração:** 2,19 s
- **Pendência:** leve corte no final (a pendência antiga de ~0,5 s foi substituída pela observação). Já existem `swing_01.mp3` e `swing_02.mp3`; este entra como `_03`.
- **Observação:** Leve corte no final; fica ok.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/player/armas/espada_longa/armas_espada_longa_swing_03.wav`, após leve corte final.

---

## 13 — armas_machado_guerra_swing_01.mp3

- **Origem:** `4_player/machado_guerra/armas_machado_guerra_swing_01.mp3`
- **Destino sugerido:** `sfx/player/armas/machado_guerra/`
- **Duração:** 0,57 s
- **Pendência:** nenhuma técnica; a pasta final está vazia.
- **Observação:** Ok.

- **Decisão:** [x] promover  [ ] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/player/armas/machado_guerra/armas_machado_guerra_swing_01.wav`.

---

## 14 — projeteis_bomba_impacto_02.mp3

- **Origem:** `5_projeteis/bomba/projeteis_bomba_impacto_02.mp3`
- **Destino sugerido:** `sfx/projeteis/bomba/impacto/`
- **Duração:** 3,05 s
- **Pendência:** cortar o final; a inspeção detectou 2 golpes. Já existe `bomba_impacto_01.wav`, então entra como `_02`.
- **Observação:** Cortar um pouco do final; fica ok.

- **Decisão:** [ ] promover  [x] cortar  [ ] descartar  [ ] outro destino
- **Destino final:** `sfx/projeteis/bomba/impacto/bomba_impacto_02.wav`, após corte final.

---

## 15 — projeteis_magico_disparo_01.mp3

- **Origem:** `5_projeteis/magico/projeteis_magico_disparo_01.mp3`
- **Local atual:** `assets/sons/_entrada/sons_faltando/_uteis/magico/projeteis_magico_disparo_01.mp3`
- **Destino sugerido:** **a definir** — `sfx/projeteis/boss/disparo/`, `esporo/disparo/` ou `olho/disparo/`
- **Duração:** 3,02 s
- **Pendência:** guardado para o futuro; a inspeção detectou 2 golpes. Não existe pasta final `projeteis/magico/`.
- **Observação:** Disparo mágico guardado por enquanto; pode ser útil no futuro.

- **Decisão:** [ ] promover  [ ] cortar  [ ] descartar  [x] outro destino
- **Destino final:** `_uteis/magico/` (futuro); sem destino final por enquanto.

---

## Anotações gerais

- Observações do usuário sincronizadas nas seções em 2026-11-09.
- Aprovações sem corte: 01, 04, 06, 10 e 13.
- Aprovações com corte: 02, 03, 05, 07, 08, 11, 12 e 14.
- Decisões fechadas: 01/02 no bloqueio genérico; 08 como `_02`; 07 cortado para ~1,3 s; 15 movido para `_uteis/magico/`.
- Não promover: 09 (impacto embutido).
- **Licenças:** 11 aprovados ainda aguardam comprovação individual de origem. O script foi corrigido: licença vazia, `LIVRE`, `VERIFICAR` ou `PENDENTE` agora impede a promoção. O lote confirmado está em `tools/promocao_lote4.csv`; os 11 bloqueados, em `tools/promocao_lote4_pendentes.csv`.
- **Volume:** a prévia de carne (10) tem pico de -12 dBFS, 9 dB abaixo das demais; `pico_db` preserva esse ajuste quando a fonte for confirmada.
- **Preservação:** hashes dos 15 originais em `pesquisa_licencas/originais_sha256.json`. 09 foi removido na limpeza de 2026-11-10, sem promoção; 15 permanece em `_uteis/magico/`.
- Cortes candidatos: 02 ~0,65 s; 03 ~3,20 s + fade 300 ms; 05 ~1,30 s; 07 ~1,3 s; 08 ~0,65 s; 11 1,50 s; 12 ~1,20 s; 14 ~1,35 s.
- A inspeção de 2026-11-09 detectou: 02 com 1 golpe (cauda longa), 03/14/15 com 2 golpes e 04 com 3 batidas de asa.
- As fatias experimentais deste lote foram substituídas por `previas_editadas/` e removidas na limpeza; os originais aprovados e as 13 prévias permanecem.
