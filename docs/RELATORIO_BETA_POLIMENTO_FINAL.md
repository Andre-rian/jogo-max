# Profane Echo — polimento final da beta

Entrega de 24/11/2026, para a apresentação de 25/11/2026.

As quatro fases foram preservadas e a campanha foi concluída por teclado simulado, com física, IA e combate reais: **7.799 atualizações até o encerramento e retorno ao menu, 400 testes aprovados**. O percurso inclui os cinco itens e as três aquisições de frascos. Não houve teletransporte ou comando de teste no trajeto principal.

Antes de editar, conferi `RELATORIO_BETA_NOVOS_ITENS.md`, o catálogo, as classes e os sprites do OpenCode. Os 20 testes de `test_itens_beta_cinco.py` passaram nessa verificação inicial. IDs, efeitos e assets dessa entrega foram preservados.

> **Atualização posterior (24/11/2026):** a Espada Longa passou a causar **25** por golpe simples e **40** por combo. O dano de 33/52 e a contagem de golpes descritos abaixo registram o estado desta entrega de polimento, antes do ajuste final. Os valores medidos após a correção estão em [`RELATORIO_BETA_AJUSTE_DANO_ECOFOCO.md`](RELATORIO_BETA_AJUSTE_DANO_ECOFOCO.md), com o mesmo HP de inimigos e 200 HP do jogador preservados.

## Portas e transições

O vão da porta das celas mostrava os tijolos da camada de fundo. Além disso, a transição ocorria na coluna 125, depois da porta. Agora cada passagem tem um objeto `transicao` no TMX, com área e lado explícitos. O vão recebe um fundo escuro sob a moldura existente; a colisão foi verificada como livre.

A troca usa `Conexoes`, exige movimento em direção à passagem e acontece quando o centro do jogador cruza o vão. Paredes comuns, bordas e a mesma coordenada em outra altura não acionam transições. Os spawns ficam fora dos gatilhos, sobre piso seguro, com proteção breve contra retorno imediato.

| Ligação | Porta de saída: coluna inicial da arte | Spawn ao avançar | Spawn ao retornar |
|---|---:|---|---|
| Celas ↔ Arsenal | Celas: 121 | Arsenal: (160, 576) | Celas: (3808, 768) |
| Arsenal ↔ Corredores | Arsenal: 67 | Corredores: (160, 576) | Arsenal: (2048, 576) |
| Corredores ↔ Arena | Corredores: 107 | Arena: (160, 576) | Corredores: (3328, 576) |

Coordenadas de spawn são pixels do canto superior esquerdo do jogador. As portas de entrada das fases 2–4 ficam na coluna 1. O retorno da arena funciona antes do encontro; durante a batalha, a barreira existente fecha o próprio vão.

As únicas alterações em colisões foram **15 células nas antigas aberturas externas**: seis no Arsenal, seis nos Corredores e três na Arena. Nenhuma célula de colisão das celas mudou. Fundo, escadas e plataformas permaneceram idênticos em todos os mapas. A auditoria por célula está em [validacao.json](beta/polimento/validacao.json).

## Curadoria visual

O anexo desta sessão continha texto. As evidências comparáveis foram capturadas no renderer do jogo antes das alterações e novamente depois, com os mesmos enquadramentos.

| Caso | Classificação | Correção ou motivo |
|---|---|---|
| Moldura e grade aberta das celas | Manter | Arte existente preservada; corrigido o fundo visível no vão e alinhado o gatilho. |
| Acessos por bordas nas fases 2–4 | Substituir por asset apropriado | Reutilizada a porta de ferro existente, com abertura legível. |
| Três prateleiras incompletas e fragmentos de armadura no Arsenal | Remover | 21 células decorativas pareciam plataformas ou recortes sem continuidade. |
| Caixas e barris apoiados, correntes de parede, rachaduras e decoração narrativa das celas | Manter | Composição coerente; sem novas colisões ou preenchimento de espaços vazios. |
| Galerias de exploração | Manter | Plataformas reais acessíveis pelas escadas; subida e descida verificadas. |
| Barril e saco dentro dos degraus dos Corredores | Remover | Duas células decorativas sobrepostas à pedra. |
| Tocha atravessando a escada da segunda galeria | Manter, reposicionar | Coluna 62 → 58; sprite e comportamento preservados. |
| Barril e saco no ponto do terceiro frasco | Remover | Duas células liberadas para distinguir o pickup no chão. |
| Seis barris/sacos decorativos na Arena | Remover | Maior legibilidade dos atores durante a luta. |
| Círculos amarelos dos pickups | Substituir por asset apropriado | Sprites do registro de itens, sem círculos genéricos. |

Os pickups são apoiados na superfície sólida ou plataforma abaixo da posição original. A margem transparente do ícone é recortada somente na cópia usada para desenhar; os pixels visíveis ficam junto ao chão, inclusive para a pequena Lasca de Umbrita. A área de interação acompanha a posição. O mesmo ajuste cobre drops de inimigos, descartes e pickups restaurados de saves anteriores. Os PNG originais permanecem intactos.

| Ponto | Antes | Depois |
|---|---|---|
| Saída das celas | [Captura](beta/polimento/antes/01_celas_saida.png) | [Captura](beta/polimento/depois/01_celas_saida.png) |
| Entrada do Arsenal | [Captura](beta/polimento/antes/02_arsenal_entrada.png) | [Captura](beta/polimento/depois/02_arsenal_entrada.png) |
| Galeria e pickups do Arsenal | [Captura](beta/polimento/antes/03_arsenal_galeria.png) | [Captura](beta/polimento/depois/03_arsenal_galeria.png) |
| Saída do Arsenal | [Captura](beta/polimento/antes/04_arsenal_saida.png) | [Captura](beta/polimento/depois/04_arsenal_saida.png) |
| Segunda galeria dos Corredores | [Captura](beta/polimento/antes/05_corredores_galeria.png) | [Captura](beta/polimento/depois/05_corredores_galeria.png) |
| Saída dos Corredores | [Captura](beta/polimento/antes/06_corredores_saida.png) | [Captura](beta/polimento/depois/06_corredores_saida.png) |
| Entrada da Arena | [Captura](beta/polimento/antes/07_arena_entrada.png) | [Captura](beta/polimento/depois/07_arena_entrada.png) |

Esses sete comparativos usam posicionamento de câmera/ator para inspeção visual; não constituem prova de deslocamento. As capturas de [percurso](beta/polimento/percurso) vêm da partida contínua por inputs.

## Balanceamento

A Espada Longa inicial causa **33 de dano por golpe simples** e **52 por impacto de combo**. Esses valores e os 200 HP iniciais do jogador foram mantidos. A vida dos inimigos foi ajustada apenas nas salas da beta; os perfis nativos da campanha legada e da arena de testes continuam disponíveis.

| Inimigo | HP anterior → novo | Golpes simples anteriores → novos | Dano ao jogador, preservado |
|---|---:|---:|---|
| Globin | 40 → 85 | 2 → 3 | 10 normal; 15 dash; 20 bomba |
| Flying Eye | 60 → 80 | 2 → 3 | 15 mordida; 12 dash; 15 projétil |
| Mushroom | 80 → 145 | 3 → 5 | 12 normal; 20 forte; 8 esporo |
| Skeleton | 60 → 150 | 2 → 5 | 15 |
| Carrasco Esquelético | 300 → 495 | 10 → 15 | 25 normal; 30 varrido; 20 projétil |

Os totais de golpes consideram impactos simples conectados, sem guarda. Combos continuam encerrando encontros em menos ações: na partida registrada foram dois impactos nos Globins/Flying Eye e quatro nos Skeletons/Mushroom. Portanto, a referência de três golpes do Globin não significa três combos.

O perigo aumenta pela duração dos encontros e pelo acesso gradual à cura. Não foi necessário elevar o dano inimigo: o percurso perdeu 59 HP antes do Ecofoco, e o chefe causou 220 de dano acumulado, exigindo duas curas de 80 HP. A vitória terminou com 140/200 HP e um frasco restante.

Velocidades, animações, alcance, hitboxes, IA, hitstun, knockback e i-frames foram preservados. Permanecem, por exemplo, os cooldowns principais de 300 ticks do Globin, 150 do Flying Eye, 120 do Mushroom, 90 do Skeleton e 90 do chefe. A guarda direcional, a quebra no terceiro golpe e seus tempos continuam cobertos pelas regressões existentes.

O chefe durou **2.232 atualizações, aproximadamente 37,2 segundos a 60 Hz**, com 11 impactos aplicados, incluindo combos. Esse resultado mede uma estratégia automatizada específica; a percepção humana de dificuldade deve ser confirmada no ensaio.

## Frascos e itens

O sistema existente é de **cargas recarregáveis**, com cura de 40% e limite de três. Uma nova partida da beta agora começa em **0/0**. Cada pickup marcado como frasco libera uma unidade de capacidade e entrega uma carga, sem adicionar outra poção consumível ao inventário. Não há poções em baús da beta.

| Aquisição | Local | Coordenada de origem em tiles | Apoio |
|---|---|---|---|
| Frasco 1 | Arsenal, depois da espada e do primeiro Skeleton | (36, 19) | Piso, y=640 |
| Frasco 2 | Corredores, segunda galeria opcional, escada da coluna 62 | (65, 12) | Plataforma, y=416 |
| Frasco 3 | Corredores, trecho acessível antes do Ecofoco e da porta do chefe | (102, 19) | Piso, y=640 |

Descansar no Ecofoco restaura somente a capacidade adquirida: 0, 1, 2 ou 3. Morrer conserva a capacidade e as cargas restantes; a recarga continua vinculada ao descanso, conforme o comportamento anterior. As chaves de coleta por sala impedem reaparecimento ao retornar, morrer ou carregar.

O save registra `pocoes_max` junto às cargas e a identificação dos pickups de frasco. Saves anteriores, sem capacidade registrada, conservam seu limite de três e seus consumíveis; nenhuma migração modifica os arquivos pessoais durante os testes. O ID 2 continua válido como consumível antigo. Somente as três obtenções planejadas usam a aquisição de capacidade.

| ID oficial | Item e efeito preservado | Distribuição: uma unidade de cada |
|---:|---|---|
| 6 | Atadura Gasta: cura 12% da vida máxima | Baú opcional do Arsenal, (43, 14), acessível pela escada 38. |
| 7 | Cinzas de um Eco: concede 5 Ecos Profanos | Pickup nos Corredores, (31, 19), antes dos degraus. |
| 8 | Lasca de Umbrita: material sem uso atual | Pickup na segunda galeria dos Corredores, (69, 12). |
| 9 | Insígnia do Carcereiro: relíquia | Baú na passagem opcional das celas, (79, 11), via escada 54. |
| 10 | Anel da Vigília: relíquia não equipável | Baú na primeira galeria dos Corredores, (27, 13), via escada 23. |

Relíquias usam o armazenamento existente. Nenhum slot de acessório, upgrade ou efeito de equipamento foi criado.

## Validação técnica e campanha completa

| Verificação | Resultado |
|---|---|
| Suíte completa: `python -m pytest -ra` | **400 passed in 24.12s**, incluindo 30 novos casos de polimento. |
| Compilação com `py_compile` | 14 módulos/scripts/testes alterados compilados. |
| Validador TMX | Sete mapas, zero erros. Os quatro mapas da beta não têm avisos. |
| Mapas legados | Quatro avisos existentes de camadas opcionais ausentes em `calabouco_1/2`. |
| `git diff --check` | Código 0; somente avisos de conversão LF/CRLF da configuração do Git. |
| Portas | Seis travessias direcionais e retornos por input; spawn seguro, ausência de rebote e ausência de gatilhos em paredes comuns. |
| Frascos | Estados 0–3 testados em coleta, descanso, save/load, morte e retorno; sem duplicação. |
| Itens do OpenCode | Os 20 testes originais continuam aprovados; efeitos, inventário, relíquias e sprites preservados. |
| Combate | Encontros reais com todos os tipos e chefe completo; regressões de guarda, máscaras, hitstun, knockback e sons aprovadas. |

O script `python scripts/validar_beta_final.py --capturas` executou: novo jogo sem arma e sem frascos; desvio das celas pela Insígnia; porta e retorno ao Bloco; espada; primeiro combate; três frascos e os cinco itens; galerias; Ecofoco; arena; batalha completa; tela final; save/load da conclusão; retorno ao menu.

Save/load e morte induzida usam uma cena separada e SQLite temporário. Os testes isolados posicionam atores para verificar portas, apoio e contagem de golpes; a partida principal permanece contínua por teclado. Não foi necessário reduzir a vida do chefe, conceder cura artificial ou remover inimigos dessa partida.

Evidências: [registro do percurso e combates](beta/polimento/percurso.json), [primeiro frasco](beta/polimento/percurso/02a_primeiro_frasco.png), [segundo frasco](beta/polimento/percurso/03c_segundo_frasco.png), [terceiro frasco](beta/polimento/percurso/03d_terceiro_frasco.png), [inventário](beta/polimento/percurso/02b_inventario.png), [encerramento](beta/polimento/percurso/05_fim_beta.png) e [auditoria técnica](beta/polimento/validacao.json).

Os testes usam SDL dummy. As capturas foram inspecionadas visualmente, mas não houve sessão humana contínua nem escuta física de áudio nesta validação. O aviso `libpng: iCCP: known incorrect sRGB profile` permanece em assets preexistentes e não impediu renderização ou testes.

## Preservação e apresentação

Hashes SHA-256 confirmam **19 arquivos protegidos idênticos ao início da tarefa**, incluindo `saves.db`, `jogo.log`, configurações pessoais, `core/audio.py`, catálogo/classes dos itens, relatório do OpenCode e todos os PNG de itens. `entities/player.py` também está idêntico ao início deste polimento. Nenhum arquivo de música foi editado. Modificações preexistentes no workspace foram preservadas; não houve `git add`, commit ou push.

Para o ensaio de 25/11, iniciar uma **nova partida pelo menu normal** e confirmar a sensação dos controles e o áudio no equipamento da apresentação. Saves anteriores mantêm os recursos anteriores por compatibilidade e não demonstram a progressão 0/0. Não há bloqueador técnico conhecido nos caminhos validados; a avaliação humana de ritmo permanece como ensaio de apresentação.

Os TMX atuais são a fonte dos mapas. `scripts/polir_mapas_beta.py` registra correções locais idempotentes; não usar o antigo gerador inicial `scripts/gerar_mapas_beta.py` para preparar a apresentação, pois ele recria os mapas anteriores ao polimento. Para reproduzir a inspeção visual atual, executar `python scripts/capturar_polimento_beta.py depois`; preservar a pasta `antes` como evidência histórica.
