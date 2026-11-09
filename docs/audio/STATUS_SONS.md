# Status dos sons — pendências de download e aprovação

> Atualizado em 2026-11-09.
> Base: `core/audio.py`, `docs/audio/SONS_FALTANDO.md`, `docs/audio/INVENTARIO_SONS_RESTANTES.md`, `assets/sons/_entrada/sons_faltando/CONTEXTO.md` e a árvore atual de `assets/sons/`.

## Resumo

- Os **37 SFX obrigatórios** de `ESPECIFICACOES` em `core/audio.py` existem.
- **55 pastas de destino** continuam vazias na árvore final. Todas têm candidatos ou bases de edição mapeados no novo lote; a adequação depende de escuta e aprovação.
- **66 novos candidatos** estão em `_entrada/sons_faltando/busca_2026_11_09/` (8,2 MiB): 64 arquivos de pacotes/fontes e 2 prévias públicas HQ. **Nenhum foi promovido.**
- Os **15 SFX anteriores** continuam preservados em `_entrada/sons_faltando`, aguardando aprovação/promoção. Total atual em triagem: **81 efeitos + 53 músicas** nessa pasta e suas subpastas.
- Também aguardam triagem: **42 fatias** em `_fatias`, **16 fontes** em `_uteis`, **4 fontes longas** de passos e **53 músicas**.
- 4 destinos vazios são variantes opcionais não lidas pelo código e não entram na contagem principal: `boss_carrasco/ataque/{projetil,varrido}/`, `boss_carrasco/hit/_default/` e `flying_eye/passos/`.

### Busca iniciada após o OK — lote de 2026-11-09

O usuário autorizou pesquisa e download, mantendo tudo em `sons_faltando`. O [guia do lote](../../assets/sons/_entrada/sons_faltando/busca_2026_11_09/LEIA-ME.md) reúne os arquivos e a ordem de escuta; o [mapa dos 55 destinos](../../assets/sons/_entrada/sons_faltando/busca_2026_11_09/COBERTURA_55_DESTINOS.csv) aponta os IDs dos candidatos para cada pasta.

- **18 destinos** têm ao menos um candidato de uso mais direto para avaliar; **37** têm bases para corte, composição ou adaptação. Nenhum destino está aprovado ou integrado pelo novo lote.
- Os 66 arquivos foram decodificados integralmente, com duração, formato, pico e SHA-256 registrados. A adequação artística continua pendente de escuta; presença de candidato não significa som pronto.
- Fontes: 20 páginas consultadas; 53 arquivos sob CC0 e 13 sob CC BY 3.0, com créditos registrados no lote.
- As prévias HQ são `bone-crunch-fast` (192146) e pouso em cascalho (819656). Estão identificadas no CSV; não são os downloads originais autenticados do Freesound.
- O WAV local `192146...bone-crunch-fast.wav` era somente um ponteiro Git LFS (130 bytes); foi preservado e a prévia foi baixada separadamente. Os 37 arquivos de `ESPECIFICACOES` não são ponteiros LFS.
- Hashes dos 381 arquivos preexistentes monitorados (`sfx`, `musica`, `ambiencia`, `_config` e `sons_faltando`) permaneceram iguais após os downloads. Nenhuma mudança de código ou promoção foi executada.

O [plano de busca](PLANO_BUSCA_SONS.md) conserva a direção sonora e as dependências de código. As 55 pastas são destinos; um mesmo candidato pode ser referenciado por vários destinos sem duplicar o arquivo.

---

## 1. Já baixados, faltam ser aprovados

### 1.1 Os 15 pendentes anteriores de `_entrada/sons_faltando`

| Arquivo | Destino | Situação |
|---|---|---|
| `1_combate/bloqueio/espada_escudo_hit_01.mp3` | `boss_carrasco/hit/escudo_bloqueio/` como `_02` | OK, confirmar destino |
| `1_combate/bloqueio/machado_escudo_hit_01.mp3` | `boss_carrasco/hit/escudo_bloqueio/` como `_03` | Cortar (8,03 s) |
| `2_inimigos/boss_carrasco/rugido/boss_carrasco_rugido_01.mp3` | `boss_carrasco/rugido/` | Cortar (4,48 s) + criar gatilho |
| `2_inimigos/flying_eye/asas/flying_eye_asas_01.mp3` | `flying_eye/asas/` | Cortar/loop + criar gatilho |
| `2_inimigos/flying_eye/ataque/flying_eye_ataque_bite_01.mp3` | `flying_eye/ataque/` | OK |
| `2_inimigos/flying_eye/morte/flying_eye_morte_01.mp3` | `flying_eye/morte/` | OK |
| `2_inimigos/globin/morte/globin_morte_01.mp3` | `globin/morte/` | OK |
| `2_inimigos/mushroom/hit/mushroom_default_hit_01.mp3` | `mushroom/hit/_default/` | OK |
| `2_inimigos/skeleton/ataque/skeleton_ataque_machado_guerra_01.mp3` | `skeleton/ataque/` | Cortar (3,02 s) |
| `3_materiais/carne/carne_default_hit_02.mp3` | `carne/_default/` | OK |
| `3_materiais/metal/metal_soco_hit_01.mp3` | `metal/soco/` | Cortar (4,41 s) |
| `4_player/espada_longa/armas_espada_longa_swing_03.mp3` | `espada_longa/` | Cortar (~0,5 s) |
| `4_player/machado_guerra/armas_machado_guerra_swing_01.mp3` | `machado_guerra/` | OK |
| `5_projeteis/bomba/projeteis_bomba_impacto_02.mp3` | `bomba/impacto/` | Cortar (3,05 s, 2 golpes) |
| `5_projeteis/magico/projeteis_magico_disparo_01.mp3` | a definir: `boss/disparo`, `esporo` ou `olho` | Cortar (3,02 s) |

### 1.2 Novo lote em `sons_faltando/busca_2026_11_09/`

| Pasta | Áudios | Uso sugerido |
|---|---:|---|
| `2_inimigos/` | 19 | Hits/vocais, ataque do Mushroom, entrada/morte/quebra de guarda do Boss e passos |
| `3_materiais/` | 12 | Carne, osso, fungo e texturas etéreas |
| `4_player/` | 14 | Swing genérico, pulo, passos e pousos |
| `5_projeteis/` | 12 | Bomba, esporo, olho, Boss e base compartilhada de voo |
| `6_mundo/` | 6 | Tochas, mecanismos e Eco Profano |
| `7_ambiencia/` | 3 | Arena do Boss e sala de descanso |

Veja [ESCUTA.md](../../assets/sons/_entrada/sons_faltando/busca_2026_11_09/ESCUTA.md) para abrir os candidatos por prioridade e [CANDIDATOS.csv](../../assets/sons/_entrada/sons_faltando/busca_2026_11_09/CANDIDATOS.csv) para registrar aprovação e observações. São arquivos de triagem, sem normalização ou cortes nesta rodada.

### 1.3 Outros já baixados

| Grupo | Quantidade | Destino / situação |
|---|---|---|
| `_entrada/_fatias/` | 42 fatias em 8 pastas | Metal (`metal/_default`, `metal/espada_longa`) e impacto de boss (`boss_carrasco/ataque/normal`); falta escolher/cortar e promover |
| `_entrada/_uteis/efeitos/` | 5 | `sfx/efeitos/` (pasta final ainda não existe) |
| `_entrada/_uteis/impactos/grande_impacto` | 1 | `boss_carrasco/ataque/normal/` |
| `_entrada/_uteis/inventario/873650` | 1 | `sfx/ui/inventario/` |
| `_entrada/_uteis/menu/207183` | 1 | `musica/menu/` |
| `_entrada/_uteis/metal/342397` | 1 | `materiais/metal/_default/` |
| `_entrada/_uteis/osso/` | 2 | `materiais/osso/_default/` |
| `_entrada/_uteis/passos/465299` | 1 | `player/movimento/passos/pedra/` |
| `_entrada/_uteis/passos_inimigos/` | 2 | `inimigos/_default/passos/` e `inimigos/globin/passos/` |
| `_entrada/_uteis/pouso/109360` | 1 | `player/movimento/pouso/pedra/` (futuro) |
| `_entrada/_uteis/soco/232358` | 1 | `player/armas/soco/` |
| `5_mundo_movimento/passos_pedra/` | 4 fontes longas | `player/movimento/passos/pedra/`; gerar mais variações |
| `ambiencia/calabouco/841640...mp3` | 1 | Já na árvore final, mas bruto; falta aprovar, renomear/loop e integrar |
| `_entrada/sons_faltando/musicas/` | 53 faixas em 5 packs | Pendente de licença e integração; ver observação abaixo |

#### Músicas — licenças

| Pack | Faixas | Licença | Situação |
|---|---|---|---|
| `1-music-loop-bundle-troubadeck` | 19 | CC0 (Abstraction/Tallbeard) | Seguro |
| `2-music-loop-bundle-2026-q3` | 6 | CC0 (Abstraction) | Seguro |
| `3-music-loop-bundle-2026-q1` | 7 | CC0 (Abstraction) | Seguro |
| `Fantasy RPG Music Vol. 2` | 18 | AlkaKrab (royalty-free, mas proíbe redistribuir as-is) | Não commitar sem autorização por escrito |
| `TopfHelm_Medieval_RPG_Music_Pack` | 3 | Grátis apenas para uso não-comercial, com atribuição | Não commitar sem revisar a licença |

---

## 2. Destinos pendentes (com candidatos ou bases no novo lote)

Esta é a lista original de 55 destinos, mantida para acompanhar a aprovação. O mapeamento atual por arquivo está em `busca_2026_11_09/COBERTURA_55_DESTINOS.csv`. As pastas finais continuam vazias por orientação do usuário.

### P1 — Combate, materiais e inimigos (26)

- `sfx/player/armas/_default/`
- `sfx/materiais/carne/machado_guerra/`
- `sfx/materiais/osso/machado_guerra/`
- `sfx/materiais/osso/soco/`
- `sfx/materiais/fungo/{_default,espada_longa,machado_guerra,soco}/`
- `sfx/materiais/etereo/{_default,espada_longa,machado_guerra,soco}/`
- `sfx/inimigos/_default/hit/_default/`
- `sfx/inimigos/skeleton/hit/espada_longa/`
- `sfx/inimigos/globin/hit/{_default,espada_longa,machado_guerra,soco}/`
- `sfx/inimigos/mushroom/hit/{espada_longa,machado_guerra}/`
- `sfx/inimigos/flying_eye/hit/{_default,espada_longa,machado_guerra}/`
- `sfx/inimigos/boss_carrasco/hit/{espada_longa,machado_guerra,quebra_guarda}/`

> `fungo/soco`, `etereo/soco` e `osso/soco` constam como promovidos na documentação, mas não existem no repositório atual; por isso entram nesta lista.

### P2 — Boss e projéteis (15)

- `sfx/inimigos/mushroom/ataque/`
- `sfx/inimigos/mushroom/esporo/`
- `sfx/inimigos/boss_carrasco/entrada/`
- `sfx/inimigos/boss_carrasco/morte/`
- `sfx/projeteis/bomba/{disparo,voo}/`
- `sfx/projeteis/esporo/{disparo,voo,impacto}/`
- `sfx/projeteis/olho/{disparo,voo,impacto}/`
- `sfx/projeteis/boss/{disparo,voo,impacto}/`

> `boss_carrasco/ataque/` e `bomba/impacto/` já têm candidatos baixados. Se `projeteis_magico_disparo_01` for aprovado para `boss/disparo`, esse item sai da lista de download.

### P3 — Mundo, movimento e ambiência (14)

- `sfx/player/movimento/pulo/`
- `sfx/player/movimento/passos/{terra,metal,_default}/`
- `sfx/player/movimento/pouso/{terra,metal,_default}/`
- `sfx/mundo/{tochas,mecanismos}/`
- `sfx/interacao/eco_profano/`
- `sfx/inimigos/{skeleton,mushroom}/passos/`
- `ambiencia/sala_descanso/`
- `ambiencia/arena_boss/`

### Fora de pastas (opcionais, sem arquivo no projeto)

- som de troca de sala;
- som de vitória contra boss.

### Gatilhos de código ainda ausentes

- pulo do jogador;
- entrada do Boss Carrasco e quebra de guarda;
- rugido do Boss Carrasco;
- asas do Flying Eye;
- leitura de `boss_carrasco/ataque/normal/` (o ataque atual só consulta arquivos diretamente em `ataque/`);
- leitura de `mushroom/esporo/`;
- chamada de `play_projectile`;
- leitura de `interacao/eco_profano/` (a coleta atual usa `eco_pickup` em `interacao/itens/`);
- tochas e mecanismos;
- sistema de música;
- sistema de ambiência.

> `inimigos/_default/hit/_default/` só é consultado quando o ID do inimigo é `_default`. Não é um fallback compartilhado dos inimigos nomeados; estes passam do hit específico para o material e o combate genérico.
