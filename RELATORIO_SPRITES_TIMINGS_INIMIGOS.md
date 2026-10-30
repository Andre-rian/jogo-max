# Relatório: sprites e timings dos inimigos

> Escopo: mapear as spritesheets dos inimigos, como elas viram animação, quanto tempo cada fase dura e onde o timing atual se afasta do que o sprite comunica.
> Base analisada: branch `combate`, commit `0b1be30` + alterações locais. **As seções 1-15 descrevem o estado anterior à implementação R1/R2; a seção 16 registra a implementação aplicada.**
> Os números das seções 1-15 foram extraídos do código e dos PNGs do projeto antes das mudanças. A seção 16 é a referência para o comportamento atual.

---

## 0. Premissas

- O jogo roda a **60 FPS** (`settings.py:9`, `main.py:142`).
- **1 tick = 1 frame de jogo = 16,67 ms**.
- Em `AnimatedSprite`, `velocidade` significa **ticks por frame da animação** (`core/animated_sprite.py:16`). Exemplo: 5 significa 5 ticks (83 ms) para trocar de frame.
- Duração de uma animação: `frames * velocidade`.
- Ataques usam uma `InstanciaAtaque`: `frame = tick // velocidade`, `duracao_animacao_ticks = total_frames * velocidade` e `duracao_ticks = duracao_animacao_ticks + recuperacao_ticks` (`core/combat/ataque.py:39-44`, `core/combat/tipos.py:94-101`).
- Janelas de golpe são inclusivas: `frame_inicio <= frame <= frame_fim` (`core/combat/tipos.py:69-70`).
- Fases de um ataque:
  - **Startup**: do tick 0 até o tick anterior ao primeiro frame ativo.
  - **Active**: frames da janela.
  - **Recovery**: do frame seguinte ao último frame ativo até o fim da animação e, depois dela, pelos `recuperacao_ticks`.
- As medidas de pixel usam a máscara do frame (`pygame.mask`). Elas são um proxy objetivo de onde o corpo/arma se estende, mas **não substituem uma inspeção visual humana** para saber a intenção artística de cada frame.

---

## 1. Resumo executivo

1. **8 de 9 ataques corpo-a-corpo dos inimigos têm recovery igual a zero.** O golpe termina praticamente junto com o último frame ativo. O inimigo não fica vulnerável depois de errar ou acertar.
2. **A maior parte dos ataques tem startup muito longo para o tanto de active que oferece.** Globin/Mushroom/Boss ficam 500-600 ms telegrafando, mas o golpe só existe por 133-200 ms e acaba imediatamente.
3. **O deslocamento durante o ataque não é controlado.** Globin normal anda **120 px** (3 px/tick x 40 ticks) durante o golpe; FlyingEye mordida avança ~80 px antes do primeiro frame ativo e o dash ~83 px. Mushroom, Skeleton e Boss ficam parados. `ModoMovimento`/`lunge` existem, mas são ignorados. Em distâncias curtas, o FlyingEye passa do player e erra; o Globin normal pode acertar com o corpo já à frente dele.
4. **O alcance real da hitbox é maior que os ranges usados pela IA.** Exemplos: Boss ~146 px do centro com IA disparando a 90-120 px; Mushroom forte ~84 px com IA disparando a 50 px; Globin dash ~68 px (+14 de deslocamento) com IA disparando a 55 px; Skeleton ~55 px com IA disparando a 48 px.
5. **A hurtbox dos inimigos é a máscara da animação atual.** Durante o ataque ela vira a máscara do golpe (arma/efeito incluídos). A hurtbox do player, por outro lado, é sempre a máscara do idle (`entities/player.py:1030-1038`). Isso é uma assimetria grande.
6. **O knockback residual é sistêmico.** Em inimigos com gravidade, a velocidade horizontal não zera quando o knockback termina; o Boss pode deslizar ~80 px depois dos 12 frames de knockback do player. A alteração local corrigiu só o Mushroom.
7. **Globin e Mushroom patrulham usando a animação de Idle enquanto andam.** O personagem desliza sem ciclo de passos.
8. **A planilha do Skeleton tem 13 frames de caminhada, mas o código usa 11.** Dois frames únicos são descartados.
9. **As durações de morte não conversam com as animações.** Globin/Mushroom seguram o último frame por ~467 ms; FlyingEye por ~600 ms; Boss por ~1.467 ms.

> Correção: R1 (recovery) e R2 (controle de deslocamento) foram implementados. Os itens 1 e 3 descrevem o estado anterior; para o comportamento atual, ver seção 16.

---

## 2. Como o timing funciona hoje

Ordem por frame (`core/game_scene.py` e `entities/inimigo_base.py`):

```text
entidades atualizam posição/IA
  -> máscaras são recalculadas (player e inimigos vivos)
  -> CombatSystem resolve hitboxes do frame
  -> ataque avança 1 tick (frame = tick // velocidade)
```

Consequências práticas:

- O frame ativo é resolvido **antes** de o ataque avançar naquele tick.
- Um ataque de 8 frames com `velocidade=5` dura 40 ticks (667 ms).
- A janela `6-7` ocupa os ticks 30 a 39. Ou seja: 30 ticks de startup (500 ms), 10 ticks de active (167 ms) e **0 ticks de recovery**.
- `ModoMovimento`, `lunge`, `prioridade` e `cancelavel_apos_frame` existem nos tipos, mas **não são aplicados pelo CombatSystem**. `ModoMovimento` só é consultado no Player (`entities/player.py:477-480`).

---

## 3. Inventário de sprites

Base: `assets/sprites/enemies/monsters/`. "BBox opaca" é o retângulo de pixels não transparentes do primeiro frame da animação; "Exibição" é o tamanho do frame já escalado.

### 3.1 Globin

Rect lógico: **30 x 44**.

| Animação | Arquivo | Célula | Frames | Escala | Exibição | BBox opaca | Ticks/frame | Ciclo | Loop |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Patrulha | goblin/Idle.png | 150x150 | 4 | 1 | 150x150 | 33x36 | 10 | 40 ticks / 667 ms | sim |
| Perseguir | goblin/Run.png | 150x150 | 8 | 1 | 150x150 | 35x36 | 6 | 48 ticks / 800 ms | sim |
| Ataque normal | goblin/Attack.png | 150x150 | 8 | 1 | 150x150 | 33x36 | 5 | 40 ticks / 667 ms | não |
| Ataque dash | goblin/Attack2.png | 150x150 | 8 | 1 | 150x150 | 45x30 | 5 | 40 ticks / 667 ms | não |
| Bomba | goblin/Attack3.png | 150x150 | 12 | 1 | 150x150 | 33x36 | 5 | 60 ticks / 1000 ms | não |
| Take hit | goblin/Take Hit.png | 150x150 | 4 | 1 | 150x150 | 33x36 | 4 | 16 ticks / 267 ms | sim |
| Morte | goblin/Death.png | 150x150 | 4 | 1 | 150x150 | 43x21 | 8 | 32 ticks / 533 ms | sim |

Observação: a patrulha usa `Idle.png` mesmo com `vel.x = 1,9`, então o Globin anda sem animação de passos.

### 3.2 Mushroom

Rect lógico: **36 x 60**.

| Animação | Arquivo | Célula | Frames | Escala | Exibição | BBox opaca | Ticks/frame | Ciclo | Loop |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Patrulha | mushroom/Idle.png | 150x150 | 4 | 2 | 300x300 | 46x74 | 10 | 40 ticks / 667 ms | sim |
| Perseguir | mushroom/Run.png | 150x150 | 8 | 2 | 300x300 | 50x72 | 6 | 48 ticks / 800 ms | sim |
| Ataque normal | mushroom/Attack.png | 150x150 | 8 | 2 | 300x300 | 46x74 | 5 | 40 ticks / 667 ms | não |
| Ataque forte | mushroom/Attack2.png | 150x150 | 8 | 2 | 300x300 | 46x74 | 5 | 40 ticks / 667 ms | não |
| Esporo | mushroom/Attack3.png | 150x150 | 11 | 2 | 300x300 | 50x74 | 5 | 55 ticks / 917 ms | não |
| Take hit | mushroom/Take Hit.png | 150x150 | 4 | 2 | 300x300 | 46x74 | 4 | 16 ticks / 267 ms | sim |
| Morte | mushroom/Death.png | 150x150 | 4 | 2 | 300x300 | 46x74 | 8 | 32 ticks / 533 ms | sim |

A patrulha também usa Idle andando (`vel.x = 1,0`), então o Mushroom desliza em idle.

### 3.3 FlyingEye

Rect lógico: **30 x 30**. Não tem gravidade.

| Animação | Arquivo | Célula | Frames | Escala | Exibição | BBox opaca | Ticks/frame | Ciclo | Loop |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Voo | flying_eye/Flight.png | 150x150 | 8 | 2 | 300x300 | 82x62 | 6 | 48 ticks / 800 ms | sim |
| Mordida | flying_eye/Attack.png | 150x150 | 8 | 2 | 300x300 | 82x62 | 5 | 40 ticks / 667 ms | não |
| Dash | flying_eye/Attack2.png | 150x150 | 8 | 2 | 300x300 | 82x62 | 4 | 32 ticks / 533 ms | não |
| Projétil | flying_eye/Attack3.png | 150x150 | 6 | 2 | 300x300 | 50x46 | 4 | 24 ticks / 400 ms | não |
| Take hit | flying_eye/Take Hit.png | 150x150 | 4 | 2 | 300x300 | 82x62 | 3 | 12 ticks / 200 ms | sim |
| Morte | flying_eye/Death.png | 150x150 | 4 | 2 | 300x300 | 82x62 | 6 | 24 ticks / 400 ms | sim |

### 3.4 Skeleton

Rect lógico: **30 x 48**. É o único com spritesheets fora do padrão 150x150.

| Animação | Arquivo | Célula | Frames | Escala | Exibição | BBox opaca | Ticks/frame | Ciclo | Loop |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Patrulha | skeleton/Skeleton Walk.png | 22x33 | **11 de 13** | 3 | 66x99 | 54x96 | 8 | 88 ticks / 1.467 ms | sim |
| Perseguir | skeleton/Skeleton Walk.png | 22x33 | **11 de 13** | 3 | 66x99 | 54x96 | 5 | 55 ticks / 917 ms | sim |
| Idle | skeleton/Skeleton Idle.png | 24x32 | 11 | 3 | 72x96 | 66x96 | 8 | 88 ticks / 1.467 ms | sim |
| Ataque | skeleton/Skeleton Attack.png | 43x37 | 18 | 3 | 129x111 | 66x96 | 4 | 72 ticks / 1.200 ms | não |
| Take hit | skeleton/Skeleton Hit.png | 30x32 | 8 | 3 | 90x96 | 66x96 | 2 | 16 ticks / 267 ms | sim |
| Morte | skeleton/Skeleton Dead.png | 33x32 | 15 | 3 | 99x96 | 66x96 | 6 | 90 ticks / 1.500 ms | sim |

A folha `Skeleton Walk.png` tem **286 px de largura / 22 px por frame = 13 frames**. O código passa `n_frames=11`, então os frames 11 e 12 (ambos com pixels diferentes dos demais) nunca aparecem. O ciclo fica truncado e pode gerar um "pulo" na passada.

Existe também `Skeleton React.png` (4 frames de 22x32) que **não é carregado por nenhum código**.

### 3.5 Boss (Carrasco Esquelético)

Rect lógico: **50 x 90**.

| Animação | Arquivo | Célula | Frames | Escala | Exibição | BBox opaca | Ticks/frame | Ciclo | Loop |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Parado | esqueletos/Idle.png | 150x150 | 4 | 2 | 300x300 | 90x102 | 8 | 32 ticks / 533 ms | sim |
| Perseguir | esqueletos/Walk.png | 150x150 | 4 | 2 | 300x300 | 90x102 | 8 | 32 ticks / 533 ms | sim |
| Ataque normal | esqueletos/Attack.png | 150x150 | 8 | 2 | 300x300 | 90x102 | 6 | 48 ticks / 800 ms | não |
| Varrido | esqueletos/Attack2.png | 150x150 | 8 | 2 | 300x300 | 66x98 | 6 | 48 ticks / 800 ms | não |
| Projétil | esqueletos/Attack3.png | 150x150 | 6 | 2 | 300x300 | 108x108 | 6 | 36 ticks / 600 ms | não |
| Escudo | esqueletos/Shield.png | 150x150 | 4 | 2 | 300x300 | 80x92 | 8 | 32 ticks / 533 ms | sim |
| Take hit | esqueletos/Take Hit.png | 150x150 | 4 | 2 | 300x300 | 90x102 | 8 | 32 ticks / 533 ms | sim |
| Morte | esqueletos/Death.png | 150x150 | 4 | 2 | 300x300 | 90x106 | 8 | 32 ticks / 533 ms | sim |

### 3.6 Player (referência de comparação)

Rect lógico: **38 x 64**. Os frames têm célula 120x80 com escala 1,7 (exibição 204x136), mas o corpo opaco do idle é **36x65**, praticamente igual ao rect. Ou seja: no player, o sprite visual e o rect lógico estão alinhados; nos inimigos, não.

---

## 4. Timings dos ataques

### 4.1 Inimigos

| Ataque | Frames | Ticks/frame | Duração | Duração ms | Janela | Startup | Startup ms | Active | Active ms | Recovery | Recovery ms |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| Globin normal | 8 | 5 | 40 | 667 | 6-7 | 30 | 500 | 10 | 167 | 0 | 0 |
| Globin dash | 8 | 5 | 40 | 667 | 6-7 | 30 | 500 | 10 | 167 | 0 | 0 |
| Globin bomba | 12 | 5 | 60 | 1000 | — | — | — | — | — | — | — |
| Mushroom normal | 8 | 5 | 40 | 667 | 6-7 | 30 | 500 | 10 | 167 | 0 | 0 |
| Mushroom forte | 8 | 5 | 40 | 667 | 6-7 | 30 | 500 | 10 | 167 | 0 | 0 |
| Mushroom esporo | 11 | 5 | 55 | 917 | — | — | — | — | — | — | — |
| FlyingEye mordida | 8 | 5 | 40 | 667 | 3-7 | 15 | 250 | 25 | 417 | 0 | 0 |
| FlyingEye dash | 8 | 4 | 32 | 533 | 6-7 | 24 | 400 | 8 | 133 | 0 | 0 |
| FlyingEye projétil | 6 | 4 | 24 | 400 | — | — | — | — | — | — | — |
| Skeleton normal | 18 | 4 | 72 | 1200 | 6-8 | 24 | 400 | 12 | 200 | 36 | 600 |
| Boss normal | 8 | 6 | 48 | 800 | 6-7 | 36 | 600 | 12 | 200 | 0 | 0 |
| Boss varrido | 8 | 6 | 48 | 800 | 6-7 | 36 | 600 | 12 | 200 | 0 | 0 |
| Boss projétil | 6 | 6 | 36 | 600 | — | — | — | — | — | — | — |

Ataques sem janela (bomba, esporo, projéteis) não causam dano por hitbox: eles apenas spawnam um projétil em um frame específico.

Ressalvas importantes:

- **Skeleton**: o f6 é só corpo; a espada só aparece em f7. Na prática, a janela de espada é **f7-f8 = 8 ticks / 133 ms**, não 12 ticks / 200 ms.
- **FlyingEye**: mordida e dash usam hitbox de rect 50x40, não a máscara. O "active" listado é o tempo em que essa hitbox fica ligada.
- **Globin normal e FlyingEye**: o tempo de startup listado é o tempo até a janela ligar, mas o corpo se desloca nesse intervalo (seção 6.3). O tempo até o golpe "chegar" depende da distância.

### 4.2 Player (comparação)

| Ataque | Frames | Ticks/frame | Duração ms | Janelas | Startup ms | Active ms | Recovery ms |
|---|---:|---:|---:|---|---:|---:|---:|
| Espada normal | 4 | 5 | 333 | 1-2 | 83 | 167 | 83 |
| Espada pesado | 6 | 5 | 500 | 2-3 | 167 | 167 | 167 |
| Espada combo | 10 | 4 | 667 | 1-2 e 6-7 | 67 / 400 | 133 / 133 | 133 |
| Machado normal | 3 | 12 | 600 | 1-2 | 200 | 400 | 0 |
| Machado pesado | 3 | 12 | 600 | 1-2 | 200 | 400 | 0 |
| Machado combo | 6 | 12 | 1200 | 1-2 e 4-5 | 200 / 800 | 400 / 400 | 0 |
| Soco | 3 | 15 | 750 | 1-2 | 250 | 500 | 0 |

O player também tem casos de recovery zero (machado e soco), mas o caso mais grave é o dos inimigos, porque o ataque deles é justamente a janela em que o player precisa punir.

---

## 5. Onde o golpe aparece visualmente

Método: para cada frame, medi a bounding box dos pixels não transparentes e o "right" (extensão para a direita). O frame de pico visual é aquele em que a arma/efeito se estende mais.

| Ataque | Pico visual | Janela registrada | Leitura |
|---|---|---|---|
| Globin normal | f6-f7: 88x46 e 87x46 (idle: 33x36) | 6-7 | Alinhado |
| Globin dash | f6-f7: 77x29 e 79x25 | 6-7 | Alinhado |
| Globin bomba | f6-f8: 36-40 px de largura; f10: 50 px | spawn em f6 | Alinhado com o início do gesto |
| Mushroom normal | f6-f7: 100x84 e 102x84 (idle: 46x74) | 6-7 | Alinhado |
| Mushroom forte | f6-f7: 84x76 e 110x76 | 6-7 | Alinhado |
| Mushroom esporo | f7: 94x88; f8: 94x90; f9: 102x96 | spawn em f6 | **Spawn 1 frame (83 ms) antes do gesto visual** |
| FlyingEye mordida | f3-f7: corpo varia de 82x50 a 66x48 | 3-7 | Janela alinhada ao sprite, mas o inimigo já avançou ~80 px antes dela; a hitbox real é 50x40, menor que o corpo |
| FlyingEye dash | **f5: 82x90 e 3.516 px**; f6: 62x76; f7: 66x90 | 6-7 | **Window começa 1 frame (67 ms) depois do pico visual; o dash já avançou ~83 px** |
| FlyingEye projétil | f3: 66x48 (f2: 36x28) | spawn em f3 | Alinhado |
| Skeleton normal | **f7: 120x108 e 5.580 px** (f6: 66x99; f8: 93x57) | 6-8 | **f6 é corpo, não espada; o golpe da arma só aparece em f7-f8** |
| Boss normal | f6-f7: 160x106 | 6-7 | Alinhado |
| Boss varrido | f6-f7: 178x174 e 15.728 px | 6-7 | Alinhado, mas com hitbox enorme |
| Boss projétil | f3: 80x90 (f2: 50x100) | spawn em f3 | Alinhado |

Conclusões:

- A maioria das janelas está, sim, alinhada ao frame em que a arma aparece. O problema principal **não é o frame ativo estar errado**; é o que acontece depois dele (nada) e o deslocamento do corpo até ele (seção 6.3).
- Skeleton e FlyingEye dash são os dois casos em que o início da janela não coincide exatamente com o pico visual.
- Globin, Mushroom, Skeleton e Boss usam `usar_mascara_animacao=True` por padrão, então a hitbox é a máscara do frame inteiro. No Skeleton, o frame 6 é só o corpo; a espada só entra em f7. Na prática, a janela "de espada" é f7-f8, não f6-f8.
- O FlyingEye é a exceção: mordida e dash usam `HitboxSpec(usar_mascara_animacao=False, inflar_rect=(20, 10))`. `pygame.Rect.inflate(20, 10)` soma 20 à largura e 10 à altura **totais**, então o rect lógico 30x30 vira **50x40** (+10 px por lado na horizontal, +5 na vertical). A hitbox não é a máscara de 82x62; é **menor que o corpo visual**, ao contrário dos outros inimigos.

---

## 6. Alcance real x alcance que a IA usa

A IA mede distância **entre centros** (`abs(player.rect.centerx - self.rect.centerx)`). O dano é resolvido pela hitbox. Para Globin, Mushroom, Skeleton e Boss, a hitbox é a máscara do frame; para o FlyingEye, é um rect de **50x40** (30x30 inflado em 20/10), ou seja, **+25 px** do centro para cada lado, mais o deslocamento da seção 6.3.

Abaixo, o alcance a partir do centro do inimigo no frame ativo mais longo, assumindo que ele olha para a direita. "Efetivo" soma ~18 px (metade da hurtbox do player idle, que tem 36 px de largura).

| Ataque | Range da IA (centro) | Alcance da hitbox | Deslocamento até o active | Alcance efetivo vs player | Leitura |
|---|---:|---:|---:|---:|---|
| Globin normal | 80 | +44 (f6) | +93 | ~+155 (fim: ~+181) | **lunge de 120 px; passa muito do range** |
| Globin dash | 55 | +68 (f7) | +14 | ~+100 | **+45 além do range** |
| Mushroom normal | 50 | +70 (f7) | 0 | ~+88 | **+38** |
| Mushroom forte | 50 | +84 (f7) | 0 | ~+102 | **+52** |
| FlyingEye mordida | < 60 | +25 (rect 50x40) | +80 | ~+124 (varre até ~+224) | erra muito perto e alcança muito longe |
| FlyingEye dash | 60-200 | +25 (rect 50x40) | +83 | ~+127 | erra muito perto e **não alcança acima de ~127** |
| Skeleton normal | 48 | +55 (f7) | 0 | ~+73 | **+25** |
| Boss normal | 90 | +146 | 0 | ~+164 | **+74** |
| Boss varrido | 120 | +146 | 0 | ~+164 | **+44** |

Além disso, a máscara pode atingir **atrás** do centro. Exemplos no frame de pico:

- Boss normal/varrido: esquerda a -14 / -32 px do centro.
- Skeleton f7: esquerda a -65 px (f8: -44 px). No f6 o lado direito da máscara fica em **-8 px**, ou seja, a janela começa com a espada ainda atrás do centro.
- Mushroom forte f7: esquerda a -26 px.
- Mushroom normal f7: esquerda a -32 px.
- Globin normal f6-f7: esquerda a -44 px.

Isso significa que o ataque não é "só na frente": o corpo inteiro do inimigo participa da hitbox. Visualmente pode parecer que o player foi acertado pelas costas ou por cima. No FlyingEye, a hitbox de rect é simétrica: 35 px para cada lado.

### 6.3 Deslocamento durante o ataque

O `movimento` da `DefinicaoAtaque` (padrão `REDUZIDO`) e o campo `lunge` **não são aplicados**. Quem move o inimigo durante o ataque é o `vel.x` que sobrou da IA ou que o próprio `_iniciar_ataque` define. Isso gera deslocamentos muito diferentes entre inimigos:

| Inimigo / ataque | Deslocamento até o active | Deslocamento total | Como | Consequência |
|---|---:|---:|---|---|
| Globin normal | +93 px (f6) | **+120 px** | `vel.x = 3` por 40 ticks, sem decay | O corpo termina 120 px à frente. A hitbox de -44..+44 atrás do centro cobre a faixa de ~30 a ~182 px do ponto inicial. |
| Globin dash | +14 px (f6) | +14 px | `vel.x = 4` com decay de 0,8/tick | O dash para cedo; a hitbox cobre ~0 a ~99 px do ponto inicial. |
| Globin bomba | 0 | 0 | `vel.x = 0` | Parado. |
| Mushroom normal/forte/esporo | 0 | 0 | `vel.x = 0` na IA | Parado. |
| FlyingEye mordida | **+80 px** (t15/f3) | +180 px no eixo x, -55 px no eixo y | 6 px/tick na direção do player; sobe a partir de f7 | A hitbox de 50x40 varre ~+55..+205 px. Abaixo de ~36 px do centro inicial, o corpo já passou e o ataque erra. |
| FlyingEye dash | **+83 px** (t24/f6) | +83 px | 9 px/tick com decay de 0,92 por 20 ticks | A hitbox só aparece depois que o dash parou. Abaixo de ~39 px, erra; acima de ~127 px, não alcança. |
| FlyingEye projétil | 0 | 0 | sem movimento de ataque | Parado. |
| Skeleton normal | 0 | 0 | `vel.x = 0` na IA | Parado. |
| Boss normal/varrido/projétil | 0 | 0 | `vel.x = 0` na IA | Parado. |

Números medidos simulando `atualizar()` + `avancar()` do ataque tick a tick, com o player parado e sem sólidos no caminho.

Leituras:

- **Globin normal não é um corte parado; é um avanço de 120 px.** A janela ativa só começa depois de ~93 px de deslocamento. O `Alcance_conectar = 35` e o `ModoMovimento.REDUZIDO` sugerem que a intenção era outra.
- **FlyingEye mordida/dash dependem da distância.** A mordida é disparada com `dist < 60`; o dash com `60-200` (e 40% de chance abaixo de 60). O corpo avança 80-83 px antes do active. Em distâncias curtas (≲35-40 px), ele passa do player e a hitbox nasce atrás dele. No dash, acima de ~127 px ele também não alcança. É um "lunge" sem controle de contato.
- **Mushroom, Skeleton e Boss são os únicos previsíveis**, porque zeram `vel.x` antes de atacar. A diferença de sensação entre eles e o Globin/FlyingEye é estrutural, não de sprite.
- O `lunge` existe em `DefinicaoAtaque` e é passado em `_registrar_ataque`, mas nenhum inimigo o utiliza. O Combate não aplica `ModoMovimento`.

Observação importante: as constantes `Alcance_conectar`, `Alcance_conectar_dash`, `Alcance_conectar_forte` e `Alcance_conectar_varrido` existem nos inimigos, mas **não são usadas em nenhum lugar do código**. Elas dão a falsa impressão de que o alcance é controlado por elas.

---

## 7. Reações: hitstun, knockback e recuperação

O `duracao_hit` do evento começa a contar no instante do hit e **corre em paralelo ao knockback** (`entities/inimigo_base.py:232-238` chama `_atualizar_hit_flash`). Por isso:

```text
tempo total travado = max(knockback, hitstun) + recuperação
```

O player aplica o mesmo knockback em todos os tiers: `forca_x=4`, `frames=12` (`entities/player.py:288-295`). As constantes `KB_FORCA_X`, `KB_FORCA_Y` e `KB_FRAMES` de cada inimigo **não são usadas quando o player acerta**, porque o evento já traz o knockback do player.

| Inimigo | Anim de hit | HITSTUN | Recuperação | KB recebido | Deslize residual | Lockout total |
|---|---:|---:|---:|---:|---:|---:|
| Globin | 16 ticks / 267 ms | 16 / 267 ms | 8 / 133 ms | 12 | 4 frames (~16 px) | 24 ticks / 400 ms |
| Mushroom | 16 / 267 ms | 16 / 267 ms | 24 / 400 ms | 12 | 4 frames (~16 px) | 40 ticks / 667 ms |
| FlyingEye | 12 / 200 ms | 12 / 200 ms | 0 | 12 | 0 (voo desacelera 0,85/frame) | 12 ticks / 200 ms |
| Skeleton | 16 / 267 ms | 16 / 267 ms | 0 | 12 | 4 frames (~16 px) | 16 ticks / 267 ms |
| Boss | 32 / 533 ms | 32 / 533 ms | 0 | 12 | **20 frames (~80 px)** | 32 ticks + 40 de imunidade (84 no total, contando os 12 de KB) |

Leituras:

- As animações de hit foram claramente dimensionadas para o hitstun: Globin/Mushroom 4x4 = 16, Skeleton 8x2 = 16, FlyingEye 4x3 = 12, Boss 4x8 = 32. Se você mudar `velocidade` ou o número de frames do Take Hit, o hitstun precisa ser recalculado, senão a animação congela no último frame ou é cortada.
- O deslize residual acontece porque `_atualizar_hitsun_parado` move com `vel.x`, mas não zera a velocidade quando o knockback acaba (`entities/inimigo_base.py:167-176`). A alteração local corrigiu isso só no Mushroom (`entities/monsters/mushroom.py:149-153`).
- O Boss é o caso mais grave: 12 frames de knockback + 20 frames de hitstun deslizando a 4 px/frame = ~80 px extras. Se a intenção é que ele seja pesado, isso contradiz as constantes `KB_FORCA_X = 1` e `KB_FRAMES = 6` dele, que não são aplicadas.
- A alteração local adiciona 8 ticks de retomada no Mushroom. Isso leva o lockout até a perseguição plena para **48 ticks (800 ms)**, contra 24 ticks (400 ms) do Globin. Pode ser a razão de a sensação ainda não agradar: o problema estrutural é a ausência de recovery, não só a velocidade de retorno.

---

## 8. Morte

| Inimigo | Animação de morte | `Duracao_morte` | Tempo segurando o último frame |
|---|---:|---:|---:|
| Globin | 32 ticks / 533 ms | 60 / 1.000 ms | 28 ticks / 467 ms |
| Mushroom | 32 / 533 ms | 60 / 1.000 ms | 28 / 467 ms |
| FlyingEye | 24 / 400 ms | 60 / 1.000 ms | 36 / 600 ms |
| Skeleton | 90 / 1.500 ms | 90 / 1.500 ms | 0 |
| Boss | 32 / 533 ms | 120 / 2.000 ms | **88 / 1.467 ms** |

O `_atualizar_morte` só avança a animação enquanto `not anim_atual.terminou` (`entities/inimigo_base.py:215-223`). Como as animações de morte são `loop=True`, elas param no último frame quando terminam; o `Duracao_morte` é que decide quanto tempo o corpo fica na tela.

Recomendação: ou `Duracao_morte = duracao_da_animacao`, ou adicionar um hold explícito e opcional, com o mesmo valor para todos os inimigos do mesmo tipo. Hoje o Boss fica quase 1,5 s parado no último frame.

---

## 9. Hurtbox e escala

A hurtbox dos inimigos é recalculada todo frame a partir de `anim_atual` (`core/game_scene.py:785-792`, `entities/entity.py:249-256`). O `_offset_mask` de cada inimigo é o mesmo `_offset_desenho` usado para desenhar. Portanto a hurtbox é exatamente a máscara do sprite desenhado, incluindo arma/efeito.

O player é diferente: `atualizar_mask` sempre usa `animacoes[Parado]` (`entities/player.py:1030-1038`), independentemente do ataque, do hit ou da morte. Isso mantém a hurtbox do player estável e previsível.

| Inimigo | Rect lógico | Frame exibido | BBox opaca | BBox / Rect |
|---|---:|---:|---:|---:|
| Globin | 30x44 | 150x150 | 33x36 | 1,10x / 0,82x |
| Mushroom | 36x60 | 300x300 | 46x74 | 1,28x / 1,23x |
| FlyingEye | 30x30 | 300x300 | 82x62 | **2,73x / 2,07x** |
| Skeleton (walk) | 30x48 | 66x99 | 54x96 | 1,80x / 2,00x |
| Skeleton (idle) | 30x48 | 72x96 | 66x96 | 2,20x / 2,00x |
| Boss | 50x90 | 300x300 | 90x102 | 1,80x / 1,13x |
| Player (idle) | 38x64 | 204x136 | 36x65 | 0,95x / 1,02x |

Durante o ataque, a hurtbox dos inimigos muda drasticamente:

| Inimigo / frame | BBox comparada | BBox no ataque | Aumento |
|---|---|---|---|
| Globin f6 | 33x36 | 88x46 | +55 px de largura |
| Mushroom f7 | 46x74 | 102x84 | +56 px de largura |
| FlyingEye dash f6 | 82x62 | 62x76 | muda de forma; corpo comprimido |
| Skeleton f7 | 54x96 | 120x108 | +66 px de largura |
| Boss normal f6 | 90x102 | 160x106 | +70 px de largura |
| Boss varrido f6 | 90x102 | 178x174 | +88 px de largura e +72 de altura |

Isso tem duas consequências:

1. O inimigo fica **muito mais fácil de acertar** justamente no frame em que está atacando, porque a arma/efeito também é hurtbox.
2. Para Globin, Mushroom, Skeleton e Boss, o alcance do golpe e a hurtbox usam a mesma máscara. Um ataque "grande" (Boss varrido, 178x174) é ao mesmo tempo uma hurtbox gigante. O FlyingEye é a exceção: usa hitbox de rect 50x40, mas a hurtbox continua sendo a máscara de 82x62.

O caso do FlyingEye é o mais desproporcional em repouso: hurtbox de 82x62 contra um rect de 30x30. É por isso que ele pode ser acertado de longe e também por isso que a hitbox de contato dele precisa ser um rect inflado separado.

---

## 10. Problemas priorizados

### P0 - afetam diretamente a leitura do combate

1. **Recovery zero em 8 de 9 ataques corpo-a-corpo.**
   - Globin normal/dash, Mushroom normal/forte, FlyingEye mordida/dash, Boss normal/varrido.
   - O ataque termina no mesmo frame em que a hitbox desliga. Não existe janela de punição.
   - Referências: `entities/monsters/globin.py:69-81`, `entities/monsters/mushroom.py:83-96`, `entities/monsters/flying_eye.py:86-98`, `entities/monsters/skeleton_boss.py:91-103`.

2. **Deslocamento do ataque sem controle.**
   - Globin normal anda 120 px (3 px/tick x 40 ticks); a janela ativa começa após ~93 px.
   - FlyingEye mordida avança ~80 px antes do active e o dash ~83 px; em distâncias curtas (≲35-40 px) o corpo passa do player e a hitbox nasce atrás dele.
   - Mushroom, Skeleton e Boss param antes de atacar; a diferença de sensação é estrutural.
   - `ModoMovimento`, `lunge` e `Alcance_conectar*` são declarados, mas não aplicados.
   - Referências: `entities/monsters/globin.py:158-172`, `entities/monsters/flying_eye.py:153-213`, `entities/inimigo_base.py:240-246`.

3. **Alcance real muito maior que o range que dispara a IA.**
   - Boss normal: +74 px; Boss varrido: +44 px; Mushroom forte: +52 px; Globin dash: +45 px; Skeleton: +25 px.
   - O jogador é acertado por golpes que "não deveriam" alcançar, porque a IA decide com distância de centro e a hitbox é a máscara inteira (ou, no FlyingEye, um rect de 50x40).
   - O Globin normal cobre ~30-182 px do ponto inicial por causa do deslocamento.
   - Constantes `Alcance_conectar*` são mortas.

4. **Hurtbox do inimigo = máscara do ataque; hurtbox do player = idle.**
   - Assimetria que muda o tamanho do alvo durante o ataque e faz a arma/efeito contar como corpo.
   - O FlyingEye é o caso extremo: hurtbox de 82x62 e hitbox de 50x40; o corpo é maior que o golpe.
   - Referências: `core/game_scene.py:785-792`, `entities/entity.py:249-256`, `entities/player.py:1030-1038`.

### P1 - consistência e previsibilidade

5. **Globin e Mushroom patrulham com Idle andando.**
   - `_patrulhar` troca `estado` para `Patrulha` (Idle), mas mantém `vel.x` de patrulha.
   - Referências: `entities/monsters/globin.py:126-134`, `entities/monsters/mushroom.py:136-144`.

6. **Deslize residual de knockback em todos os inimigos com gravidade.**
   - Boss chega a ~80 px extras. Foi corrigido só no Mushroom.
   - Referência: `entities/inimigo_base.py:167-176` e `entities/inimigo_base.py:232-238`.

7. **Configuração morta ou enganosa.**
   - `Alcance_conectar*` não é usado.
   - `KB_FORCA_X/Y` e `KB_FRAMES` dos inimigos não são usados no dano vindo do player.
   - `ModoMovimento`, `lunge`, `prioridade` e `cancelavel_apos_frame` não são aplicados aos inimigos.
   - `DanoSpec.stagger` e `hitstop` são usados, mas `hitstop` só existe no Boss e no player.

8. **Skeleton Walk com 13 frames, mas só 11 carregados.**
   - Dois frames únicos são descartados; o ciclo de caminhada fica truncado.
   - Referência: `entities/monsters/skeleton.py:31-32`.

### P2 - polimento

9. **Durações de morte inconsistentes.** Boss segura o último frame por ~1,47 s.
10. **Esporo do Mushroom spawna no frame 6, mas o gesto visual começa no frame 7.** Diferença de 83 ms.
11. **FlyingEye dash tem o pico visual no frame 5, mas a janela começa no frame 6.** Diferença de 67 ms.
12. **Escalas e células heterogêneas.** 150x150 com escala 1 ou 2; Skeleton com 22x33/43x37 e escala 3; player 120x80 com escala 1,7. Não existe uma razão "pixels do mundo por pixel do sprite" comum.
13. **Animações de hit e morte com `loop=True`.** Hoje o guard de `terminou` impede o loop, mas a semântica correta seria `loop=False`.

---

## 11. Recomendações

### R1. Adicionar recovery explícito por ataque (maior impacto, menor refatoração)

Hoje o fim do ataque é o fim da spritesheet. Uma opção mínima é adicionar `recuperacao_ticks` em `DefinicaoAtaque` e somar em `duracao_ticks`:

```python
duracao_ticks = total_frames * velocidade + recuperacao_ticks
```

Como `frame` é limitado ao último frame (`min(tick // velocidade, total_frames - 1)`), o sprite simplesmente segura o último frame durante o recovery. Isso cria a janela de punição sem mexer nas spritesheets nem nas janelas ativas.

Valores iniciais sugeridos:

| Arquétipo | Recovery sugerido |
|---|---:|
| Leve (Globin) | 6-10 ticks / 100-167 ms |
| Comum (Mushroom, FlyingEye) | 12-18 ticks / 200-300 ms |
| Pesado (Skeleton) | já tem 36 ticks / 600 ms |
| Boss | 30-45 ticks / 500-750 ms |

### R2. Controlar o deslocamento do ataque

Hoje o `vel.x` que sobrou da IA (ou que o `_iniciar_ataque` define) move o inimigo durante todo o ataque. O mínimo é decidir, por ataque, entre:

- **parado** (Mushroom, Skeleton, Boss já fazem isso);
- **lunge curto no startup**, parando antes ou no início do active;
- **lunge contínuo**, com velocidade e taxa de desaceleração explícitas.

Uma implementação simples é adicionar à `DefinicaoAtaque` um `frame_de_parada` ou um `deslocamento_ticks` e, no `_atualizar_ataque_em_curso`, zerar `vel.x` quando o frame chegar lá:

```python
if ataque.frame < definicao.frame_de_parada:
    mover_com_colisao(rects_solidos)
else:
    self.vel.x = 0
```

Regras práticas:

- Globin normal: hoje anda 120 px. Ou vira um lunge curto (ex.: 20-30 px no startup), ou a janela ativa precisa acompanhar o deslocamento. Não deixe o corpo passar 120 px com a hitbox só no fim.
- FlyingEye mordida/dash: o lunge deve terminar quando a hitbox nasce, não 80 px depois. O `Vel_ataque` e o `_dash_timer` precisam ser dimensionados junto com o range que dispara a IA.
- Use `Alcance_conectar*` como validação: se o deslocamento + hitbox ultrapassa o range de disparo, o ataque vai acertar fora da faixa pretendida.
- Se o ataque for interrompido por hit, pare o movimento junto (`vel.x = 0`) para não continuar deslizando durante o knockback.

### R3. Separar hurtbox de animação

Escolher uma das duas abordagens:

- **Mais simples:** inimigos usam sempre a máscara de um frame neutro (Idle) como hurtbox, como o player faz. O ataque continua usando a máscara do frame atual como hitbox (o FlyingEye já usa rect 50x40 e não muda).
- **Mais precisa:** criar um `HurtboxSpec` por inimigo (rect ou máscara dedicada), independente da animação.

Isso estabiliza o tamanho do alvo e evita que a arma/efeito conte como corpo.

### R4. Patrulha com animação de caminhada

Usar `Run/Walk` quando `abs(vel.x) > 0` e `Idle` apenas quando `vel.x == 0`. Para o Globin/Mushroom, isso resolve o deslize em idle sem precisar de sprite nova.

### R5. Normalizar escala e offset

Definir um alvo de "altura opaca do sprite / altura do rect" por arquétipo (por exemplo, 1,0-1,3). Hoje:

- Player: 1,02
- Globin: 0,82
- Mushroom: 1,23
- FlyingEye: 2,07
- Skeleton: 2,00
- Boss: 1,13

O FlyingEye e o Skeleton estão com o dobro da altura do rect; o Globin é menor que o rect. Ajustar `escala` e `_offset_desenho` deixaria o corpo visual, a hurtbox e os ranges de IA na mesma régua.

### R6. Centralizar timing em milissegundos

Criar constantes em ms e derivar ticks/frames:

```text
ticks = round(ms * 60 / 1000)
frames = ceil(ticks / velocidade)
```

Hoje os números estão espalhados em `HITSTUN_FRAMES`, `RECUPERACAO_HIT_FRAMES`, `KB_FRAMES`, `Cooldown_*` e `velocidade`, cada um em uma unidade diferente. Uma tabela única por inimigo reduz o risco de ajustar um valor e esquecer o outro.

### R7. Corrigir o knockback residual na base

Zerar `vel.x` quando `timer_knockback` chega a 0 em `Entity.atualizar_knockback`, ou aplicar um amortecimento nos últimos frames. Isso resolve Globin, Skeleton e Boss de uma vez. Alternativa: fazer o player usar o `KB_FORCA_X/KB_FRAMES` do alvo, ou um multiplicador de peso por inimigo.

### R8. Alinhar morte e hitstun às animações

- `Duracao_morte = animacao_morte.duracao` ou hold explícito.
- `HITSTUN_FRAMES` derivado de `Take Hit` (ou documentado como "mínimo").
- `loop=False` em hit e morte.

### R9. Correções pontuais

- `Skeleton Walk`: `n_frames=13`.
- Esporo do Mushroom: spawn em `frame >= 7`.
- FlyingEye dash: decidir se a janela deve começar em 5 ou se o frame 5 é wind-up.
- Skeleton: decidir se a janela é 6-8 (corpo + espada) ou 7-8 (só espada).

### R10. Debug de timing

O projeto já tem debug de hitbox/hurtbox (`core/combat/debug.py`). Vale adicionar no overlay:

```text
estado | tick | frame | fase (startup/active/recovery) | janela ativa | vel.x
```

Isso permite comparar o que o código acha que está acontecendo com o que o sprite mostra.

---

## 12. Metas de timing sugeridas

Faixas de referência para um jogo de ação 2D. Não são regras rígidas; servem para comparar com o estado atual.

| Arquétipo | Startup | Active | Recovery | Total |
|---|---:|---:|---:|---:|
| Leve (Globin) | 250-350 ms | 100-150 ms | 150-250 ms | 500-750 ms |
| Comum (Mushroom, FlyingEye) | 350-500 ms | 120-200 ms | 200-350 ms | 650-1.050 ms |
| Pesado (Skeleton) | 500-700 ms | 150-250 ms | 400-600 ms | 1.050-1.500 ms |
| Boss | 600-900 ms | 200-300 ms | 500-800 ms | 1.300-2.000 ms |

Comparação com o estado atual:

| Inimigo | Startup atual | Active atual | Recovery atual | Leitura |
|---|---:|---:|---:|---|
| Globin | 500 ms | 167 ms | 0 | Startup alto, active ok, falta recovery |
| Mushroom | 500 ms | 167 ms | 0 | Idem; forte tem alcance acima do range |
| FlyingEye mordida | 250 ms | 417 ms | 0 | Active excessivo, falta recovery |
| FlyingEye dash | 400 ms | 133 ms | 0 | Falta recovery |
| Skeleton | 400 ms | 200 ms | 600 ms | Formato bom; só ajustar alinhamento da janela |
| Boss | 600 ms | 200 ms | 0 | Telegrafado, mas sem punição |

Se a intenção é manter os ataques bem telegrafados, o caminho mais conservador é **não mexer no startup** e apenas adicionar recovery. Isso preserva a leitura atual e cria a janela de resposta que hoje não existe.

---

## 13. Plano de teste sugerido

### Automatizado

1. Para cada ataque com janela:
   - `fase_em(frame_inicio - 1) == STARTUP`
   - `fase_em(frame_inicio) == ACTIVE`
   - `fase_em(frame_fim) == ACTIVE`
   - `fase_em(frame_fim + 1) == RECOVERY` (quando existir)
2. `duracao_ticks == total_frames * velocidade + recuperacao_ticks`.
3. `HITSTUN_FRAMES >= duracao_animacao_hit` para todos os inimigos.
4. `Duracao_morte` compatível com a animação de morte (ou hold documentado).
5. Skeleton com 13 frames carregados.
6. Esporo spawna no frame 7.
7. Knockback residual: após `timer_knockback == 0`, `vel.x == 0` em todos os inimigos com gravidade.
8. Hurtbox de inimigo atacando igual à hurtbox neutra (se R3 for adotada).
9. Deslocamento do ataque dentro do orçamento definido (parado, lunge curto ou lunge contínuo).

### Manual / playtest

- Medir o tempo entre o início do ataque e o primeiro frame em que o player pode reagir visualmente.
- Medir o tempo entre o fim do active e o fim do ataque (janela de punição percebida).
- Testar o Mushroom após o knockback: ele deve parar de deslizar, fazer a recuperação e só então retomar a perseguição, sem "arranque" de 0 para 2,0.
- Testar o Boss: confirmar se o deslize de ~80 px é intencional.
- Testar a patrulha de Globin/Mushroom: os pés devem acompanhar o movimento.
- Testar o Skeleton: a caminhada não deve "pular" ao reiniciar o ciclo.

---

## 14. Referências de código

| Assunto | Arquivo / linha |
|---|---|
| `velocidade` = ticks/frame | `core/animated_sprite.py:16` |
| Avanço de frame e `terminou` | `core/animated_sprite.py:65-80`, `124-129` |
| `duracao_ticks` | `core/combat/tipos.py:85-95` |
| Fases startup/active/recovery | `core/combat/tipos.py:109-118` |
| Janela inclusiva | `core/combat/tipos.py:69-70` |
| `frame = tick // velocidade` | `core/combat/ataque.py:39-44` |
| Ordem de atualização e máscaras | `core/game_scene.py:781-792` |
| Hurtbox do player = idle | `entities/player.py:1030-1038` |
| Offset da máscara do player | `entities/player.py:1017-1028` |
| Knockback e hitstun | `entities/inimigo_base.py:167-176`, `232-238`, `322-389` |
| Recuperação pós-hit | `entities/inimigo_base.py:273-301` |
| Dano/knockback do player | `entities/player.py:288-295` |
| Construção da hitbox por máscara | `core/combat/colisao.py:42-79` |
| Globin: ataques e IA | `entities/monsters/globin.py:56-134` |
| Globin: `_iniciar_ataque` e deslocamento | `entities/monsters/globin.py:158-172` |
| Mushroom: ataques, IA e alteração local | `entities/monsters/mushroom.py:64-153` |
| FlyingEye: ataques e IA | `entities/monsters/flying_eye.py:69-136` |
| FlyingEye: lunge e dash | `entities/monsters/flying_eye.py:153-213` |
| Atualização do ataque na base (movimento) | `entities/inimigo_base.py:240-246` |
| Skeleton: 13 frames vs 11 | `entities/monsters/skeleton.py:31-34` |
| Boss: ataques e timings | `entities/monsters/skeleton_boss.py:76-103` |
| Cooldowns e ranges da IA | constantes `Cooldown_*` e `Alcance_*` em cada inimigo |

---

## 15. Conclusão

O material de sprite está bom o suficiente para sustentar timings melhores. O que falta não é "animação mais rápida ou mais lenta": é **arquitetura de tempo**.

O padrão atual é:

```text
startup longo -> active -> fim do ataque (sem recovery)
```

O padrão que dá leitura e punição é:

```text
startup longo -> active curto -> recovery explícito
```

Se for para escolher uma única alavanca de tempo, escolha o **recovery explícito** (R1). Ele resolve o problema mais visível, não exige sprite nova, não muda o alcance dos golpes e cria a janela de resposta que hoje inexiste. Se for para escolher uma alavanca de movimento, escolha o **controle do deslocamento** (R2): é ele que faz o Globin normal e o FlyingEye passarem do player antes do golpe existir. Em seguida, separe a hurtbox da animação (R3) e normalize a escala (R5); isso vai fazer os números de alcance e de tempo finalmente corresponderem ao que o jogador vê.

---

## 16. Implementação R1/R2 (aplicada)

Esta seção registra o que foi implementado depois das medições das seções 1-15.

### 16.1 Arquitetura de tempo (R1)

- `DefinicaoAtaque` ganhou `recuperacao_ticks`.
- `duracao_ticks` agora é `duracao_animacao_ticks + recuperacao_ticks`.
- `InstanciaAtaque.fase` retorna `RECOVERY` quando `tick >= duracao_animacao_ticks`, mesmo que o último frame da animação ainda esteja dentro de uma janela ativa.
- `InstanciaAtaque.janelas_ativas()` retorna vazio durante `RECOVERY`. Sem isso, a hitbox continuaria ligada enquanto o inimigo estivesse parado no último frame.

Valores aplicados:

| Inimigo / ataque | Animação | Recovery | Duração total |
|---|---:|---:|---:|
| Globin normal | 40 ticks | 12 | 52 ticks / 867 ms |
| Globin dash | 40 ticks | 12 | 52 ticks / 867 ms |
| Globin bomba | 60 ticks | 12 | 72 ticks / 1.200 ms |
| Mushroom normal | 40 ticks | 12 | 52 ticks / 867 ms |
| Mushroom forte | 40 ticks | 12 | 52 ticks / 867 ms |
| Mushroom esporo | 55 ticks | 12 | 67 ticks / 1.117 ms |
| FlyingEye mordida | 40 ticks | 8 | 48 ticks / 800 ms |
| FlyingEye dash | 32 ticks | 8 | 40 ticks / 667 ms |
| FlyingEye projétil | 24 ticks | 8 | 32 ticks / 533 ms |
| Skeleton normal | 72 ticks | 8 | 80 ticks / 1.333 ms |
| Boss normal | 48 ticks | 12 | 60 ticks / 1.000 ms |
| Boss varrido | 48 ticks | 12 | 60 ticks / 1.000 ms |
| Boss projétil | 36 ticks | 12 | 48 ticks / 800 ms |

Observação: no Skeleton, o "recovery total" depois do active é maior que 8 ticks porque a animação já tem 9 frames (36 ticks) depois de f8. Os 8 ticks são adicionados ao fim.

### 16.2 Controle de deslocamento (R2)

`ModoMovimento` passou a ser aplicado de verdade em `InimigoBase._aplicar_movimento_ataque`:

- `TRAVADO`: `vel.x = 0` durante todo o ataque.
- `REDUZIDO`: usa `lunge` como **distância total em pixels**, distribuída em passos inteiros durante o startup. Ao chegar no primeiro frame ativo, para.
- `LIVRE`: mantém a velocidade definida pelo ataque (usado pelo dash do Globin).

Mudanças por ataque:

| Ataque | Antes | Depois |
|---|---|---|
| Globin normal | +120 px, hitbox só no fim | lunge de **28 px** no startup; para no active |
| Globin dash | ~+14 px | inalterado (~+14 px), `LIVRE` |
| Globin bomba | parado | parado, `TRAVADO` |
| Mushroom normal/forte/esporo | parado | parado, `TRAVADO` |
| Skeleton normal | parado | parado, `TRAVADO` |
| Boss normal/varrido/projétil | parado | parado, `TRAVADO` |
| FlyingEye mordida | +80 px até o active, +180 px no total | lunge de **30 px**; para e depois sobe |
| FlyingEye dash | +83 px | inalterado (+83 px) |
| FlyingEye projétil | parado | parado |

Ajuste de IA do FlyingEye:

- `Alcance_medio` caiu de **200** para **120**.
- Abaixo de 60 px, o FlyingEye agora usa **sempre mordida** (antes havia 40% de chance de dash).
- Resultado: o dash só é disparado na faixa em que ele realmente alcança.

### 16.3 Alcance efetivo simulado (com o player parado)

| Ataque | Faixa da IA | Alcance efetivo | Leitura |
|---|---:|---:|---|
| Globin normal | < 80 | 0-80 | lunge de 28 px; acerta em todo o range da IA |
| Globin dash | < 55 | 0-99 | inalterado; acerta em todo o range |
| FlyingEye mordida | < 60 | 0-70 | lunge de 30 px; não passa mais do alvo |
| FlyingEye dash | 60-120 | 40-120 | acerta na faixa em que é disparado |
| Mushroom normal/forte | 50 | ~88/~102 | parado; alcance não mudou |
| Skeleton | 48 | ~73 | parado; alcance não mudou |
| Boss normal/varrido | 90/120 | ~164/~182 | parado; alcance não mudou |

### 16.4 Verificação

- `py -m pytest -q` -> **41 passed** (5 testes novos em `tests/test_enemy_regressions.py`).
- `py -m compileall -q entities core tests` -> limpo.
- Testes novos:
  - `test_ataques_de_inimigos_tem_recuperacao_explicita`
  - `test_recuperacao_nao_mantem_hitbox_ativa`
  - `test_globin_normal_limita_lunge_e_acerta_no_range_da_ia`
  - `test_flying_eye_mordida_acerta_de_perto_e_limita_lunge`
  - `test_flying_eye_usa_mordida_de_perto_e_dash_na_distancia_media`

### 16.5 Arquivos alterados

- `core/combat/tipos.py`
- `core/combat/ataque.py`
- `entities/inimigo_base.py`
- `entities/monsters/globin.py`
- `entities/monsters/mushroom.py`
- `entities/monsters/flying_eye.py`
- `entities/monsters/skeleton.py`
- `entities/monsters/skeleton_boss.py`
- `tests/test_enemy_regressions.py`

As seções 1-15 continuam válidas como diagnóstico do estado anterior. Para o comportamento atual, use esta seção.

## 17. Reação ao dano (aplicada)

Esta seção substitui os números de hitstun/knockback das seções 7 e 10 para o comportamento atual.

### 17.1 Base comum

- `core/combat/tipos.py` ganhou `ReacaoDano` (knockback, duração de hit, recuperação, invencibilidade de stagger, animação, interrupção de ataque, hiper armor e flash de guarda).
- `InimigoBase._reacao_ao_dano(...)` é o hook por inimigo. O padrão usa os atributos da classe.
- O hitstun agora é **derivado da animação de hit** (`anim_hit.duracao_ticks`) quando `HITSTUN_FRAMES = None`.
- `Entity.atualizar_knockback` zera `vel.x` ao terminar o knockback: não existe mais deslize residual durante o hitstun.
- Animações de hit e morte usam `loop=False` em todos os inimigos; o último frame permanece visível.
- `AnimatedSprite.duracao_ticks` expõe `total_frames * velocidade`.
- Hits durante o hitstun da quebra da guarda do Boss causam dano, mas não contam para o próximo ciclo.

### 17.2 Mushroom

| Propriedade | Valor atual |
|---|---:|
| Knockback | 2 px/tick × 4 ticks = **8 px** |
| Hitstun | **16 ticks** (4 frames × 4) |
| Recovery pós-hit | **0 ticks** |
| Retomada em velocidade de patrulha | **8 ticks** |
| `anim_hit.loop` | `False` |

Resultado: fim do knockback → hitstun até 16 ticks → retomada curta de 8 ticks → perseguição plena. Não há mais os ~467 ms imóvel nem a IA voltando só aos ~667 ms.

### 17.3 Boss (Carrasco Esquelético)

A guarda conta **golpes válidos**, com dedupe por identidade da fonte + nome/canal da janela.

| Golpe | Knockback | Hitstun | Interrompe ataque | Flash |
|---|---:|---:|---|---:|
| 1.º | 0 px | 0 ticks | não | 6 ticks |
| 2.º | 0 px | 0 ticks | não | 6 ticks |
| 3.º (parado) | 2 px/tick × 6 = **12 px** | **24 ticks** | sim | 6 ticks |
| 3.º (atacando) | 2 px/tick × 6 = **12 px** | **16 ticks** | sim | 6 ticks |

- O terceiro golpe ignora o hiper armor do ataque e quebra a guarda.
- Os dois primeiros não deixam o Boss invulnerável e não pausam a IA.
- O contador reseta após **180 ticks (~3 s)** sem golpe válido.
- Na quebra, o cooldown de ataque é limitado a **45 ticks (~0,75 s)**, para o Boss voltar a pressionar logo depois do hitstun.
- Não existe mais a imunidade de stagger de 40 ticks.
- O flash é um contorno **dourado** desenhado sobre o frame atual, não um tint azul.

### 17.4 Verificação

- `python -m pytest -q` -> **47 passed**.
- `python -m compileall -q core entities tests` -> limpo.
- Testes novos/ajustados:
  - hitstun derivado de `anim_hit` para Globin, Mushroom, Skeleton e FlyingEye;
  - Mushroom sem pausa artificial e com knockback total de 8 px;
  - guarda do Boss: 1.º/2.º golpes sem stagger, quebra no 3.º (24/16 ticks), hits no hitstun da quebra não contam, timeout de 180 ticks e dedupe da mesma janela.

### 17.5 Arquivos alterados

- `core/combat/tipos.py`
- `core/combat/__init__.py`
- `core/animated_sprite.py`
- `entities/entity.py`
- `entities/inimigo_base.py`
- `entities/monsters/mushroom.py`
- `entities/monsters/skeleton_boss.py`
- `entities/monsters/globin.py`
- `entities/monsters/skeleton.py`
- `entities/monsters/flying_eye.py`
- `tests/test_enemy_regressions.py`

## 18. IA agressiva do Boss — Fases 1 e 2 (aplicadas)

Objetivo: eliminar as janelas mortas em que o Boss ficava em `Patrulha` parado esperando o cooldown global.

### 18.1 Loop de decisão

- A IA reavalia a ação a cada **8 ticks** (`Decisao_ticks`).
- O estado padrão agora é **Pressionar** (`Perseguir`), não `Patrulha`.
- Só fica imóvel durante startup, recovery, escudo e quebra de guarda.
- Ao sair do hitstun, `_tempo_decisao` é zerado e o Boss escolhe uma ação imediatamente.

### 18.2 Cooldowns independentes

| Ação | Cooldown |
|---|---:|
| Espada (normal/varrido) | **90 ticks** |
| Escudo | **120 ticks** |
| Projétil | **180 ticks** |
| Duração do escudo | 90 ticks |

- O cooldown da espada não bloqueia mais escudo ou projétil.
- Durante o escudo, espada e projétil continuam esfriando; o escudo não congela mais a IA.
- Na quebra de guarda, o cooldown da espada continua limitado a **45 ticks**.

### 18.3 Pressionar e micro-ajustes

- Longe: aproxima em velocidade cheia.
- Perto da faixa de ataque: aproxima mais devagar.
- Dentro da faixa, mas com a espada em cooldown: faz pequenos ajustes laterais/para frente.
- Muito perto: dá um pequeno passo para trás para recuperar espaço de espada.
- O escudo só é considerado quando a espada não está disponível ou quando o jogador está atacando; não passou a ser a ação padrão.

### 18.4 Recomposição pós-quebra

- O 3.º golpe agenda **10 ticks** de recomposição depois do hitstun (`Recomposicao_apos_quebra`).
- Durante a recomposição o Boss usa a pose de **idle**, não a de caminhada.
- Ao terminar, `_tempo_decisao` é zerado e ele escolhe a próxima ação imediatamente.

### 18.5 Verificação

- `python -m pytest -q` -> **51 passed**.
- `python -m compileall -q core entities tests` -> limpo.
- Testes novos:
  - Boss pressiona em vez de ficar parado com a espada em cooldown;
  - projétil funciona independentemente do cooldown da espada;
  - escudo não congela os cooldowns de espada/projétil;
  - recomposição de 10 ticks após a quebra volta a decidir imediatamente.

### 18.6 Próxima fase

- **Fase 3 (opcional):** fúria progressiva por número de quebras.

## 19. Tempos de hit dos inimigos terrestres (aplicado)

Escopo: **Globin, Mushroom e Skeleton**. Boss e IA intocados.

### 19.1 Knockback

Regra nova: o **perfil do inimigo** define o knockback da reação. O evento de dano informa o golpe, mas não sobrescreve mais `KB_FORCA_X`, `KB_FORCA_Y` e `KB_FRAMES` da classe.

Consequência prática:

| Inimigo | Knockback efetivo |
|---|---:|
| Globin | 4 px × 12 = **48 px** |
| Mushroom | 2 px × 4 = **8 px** |
| Skeleton | 4 px × 12 = **48 px** |
| FlyingEye | 6 px × 14 = **84 px** (perfil próprio, agora respeitado) |

O `vel.x` continua sendo zerado ao fim do knockback, sem deslize residual.

### 19.2 Hitstun e recuperação

| Inimigo | Animação de hit | Hitstun | Recovery | Total até voltar à IA |
|---|---:|---:|---:|---:|
| Globin | 4 frames × 5 = **20 ticks** | **20 ticks** (333 ms) | 8 ticks | 28 ticks (~467 ms) |
| Mushroom | 4 frames × 5 = **20 ticks** | **20 ticks** (333 ms) | 0 | 20 ticks + retomada de 8 |
| Skeleton | 8 frames × 3 = **24 ticks** | **24 ticks** (400 ms) | 6 ticks | 30 ticks (500 ms) |

- Globin e Skeleton usam `HITSTUN_FRAMES = None`; o hitstun é derivado da animação de hit.
- A animação de hit termina junto do hitstun, sem loop.
- Mushroom mantém recovery zero e retomada de 8 ticks.

### 19.3 Hitstop do player

| Tipo de golpe | Antes | Agora |
|---|---:|---:|
| Normal / pesado | 1 tick | **3 ticks** (~50 ms) |
| Combo | 2 ticks | **4 ticks** (~67 ms) |

Dano, alcance, velocidade máxima e agressividade da IA não foram alterados.

### 19.4 Verificação

- `python -m pytest -q` -> **54 passed**.
- `python -m compileall -q core entities tests` -> limpo.
- Testes novos:
  - perfil do inimigo manda no knockback mesmo com evento do player;
  - hitstun terrestre derivado da animação;
  - hitstop do player em 3/4 ticks.

## 20. Velocidade e deslizamento dos inimigos terrestres (aplicado)

Escopo: **Globin, Mushroom e Skeleton**. Boss, FlyingEye e Player mantêm o movimento inteiro anterior.

### 20.1 Velocidades novas

| Inimigo | Patrulha antes | Patrulha agora | Perseguição antes | Perseguição agora |
|---|---:|---:|---:|---:|
| Skeleton | 1,5 | **1,0** | 3,0 | **2,0** |
| Globin | 1,9 | **1,2** | 3,0 | **2,4** |
| Mushroom | 1,0 | **0,8** | 2,0 | **1,5** |

Referência: o Player continua em **4,0 px/tick**.

### 20.2 Correções de base

- `Entity` agora possui resíduo fracionário no eixo X para velocidades decimais.
- O resíduo é zerado quando `vel.x == 0`, ao colidir e ao iniciar knockback.
- O movimento subpixel é opt-in (`USAR_MOVIMENTO_SUBPIXEL`), ativado apenas em Globin, Mushroom e Skeleton.
- Boss, FlyingEye e Player continuam usando o movimento inteiro anterior.
- A patrulha não mantém mais a velocidade de perseguição quando o Player sai do alcance.
- Globin e Mushroom não andam mais com a animação de idle: usam `Run.png` em cadência reduzida durante a patrulha.
- Mushroom usa o estado `Patrulha` durante os 8 ticks de retomada, exibindo a animação de deslocamento lento.
- Skeleton: walk de patrulha passou de 8 para 10 ticks/frame para aproximar o passo da velocidade reduzida.

### 20.3 Distância por ciclo após o ajuste

| Inimigo | Ciclo de perseguição | Distância por ciclo |
|---|---:|---:|
| Skeleton | Walk 11 × 5 = 55 ticks | 2,0 × 55 = **110 px** |
| Globin | Run 8 × 6 = 48 ticks | 2,4 × 48 = **115,2 px** |
| Mushroom | Run 8 × 6 = 48 ticks | 1,5 × 48 = **72 px** |

Antes: Skeleton 165 px, Globin 144 px e Mushroom 96 px por ciclo.

### 20.4 Verificação

- `python -m pytest -q` -> **58 passed**.
- `python -m compileall -q core entities tests` -> limpo.
- Testes novos:
  - movimento subpixel preserva 0,8 / 1,2 / 2,4 px por tick;
  - patrulha não mantém velocidade de perseguição;
  - Globin e Mushroom usam animação de patrulha em movimento;
  - movimento subpixel permanece limitado aos três inimigos terrestres.
