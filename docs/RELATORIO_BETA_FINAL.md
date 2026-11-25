# PROFANE ECHO — Beta final

Entrega de 24/11/2026 para revisão antes da apresentação de 25/11/2026.

A campanha está integrada: **Bloco das Celas → Antigo Arsenal → Corredores Profundos → Arena do Chefe → Fim da Beta**. O teste automatizado percorreu o caminho com teclado simulado, física, IA e combate reais, derrotou os sete inimigos e retornou ao menu. A suíte completa passou com **350 testes**.

## Fases e conteúdo

| Fase | Mapa | Conteúdo |
|---|---|---|
| 1 — Bloco das Celas Esquecidas | `assets/maps/bloco_celas_esquecidas.tmx`, 128×32 tiles | Início oficial, spawn aprovado, tutorial I.3 de movimento/escada/pulo e saída pelo corredor inferior. TMX preservado integralmente. |
| 2 — Antigo Arsenal dos Guardas | `assets/maps/antigo_arsenal_guardas.tmx`, 72×24 | Baú da Espada Longa, suportes vazios, armaduras decorativas, caixas, barris, correntes, tochas, galeria acessível por escada; Skeleton e Globin separados. |
| 3 — Corredores Profundos | `assets/maps/corredores_profundos.tmx`, 112×24 | Degraus, duas galerias com escadas/plataformas, tochas espaçadas, ruínas, baú e itens; Globin, Skeleton, Mushroom e Flying Eye; Ecofoco antes da arena. |
| 4 — Arena do Chefe | `assets/maps/arena_chefe.tmx`, 48×24 | Piso contínuo, espaço aberto, tochas, fissuras espectrais e Carrasco Esquelético existente. Entrada se fecha durante o encontro e libera na derrota. |

Os três mapas novos reutilizam os tilesets das celas. Nenhuma imagem, música, biblioteca de áudio ou dependência foi adicionada/substituída. `scripts/gerar_mapas_beta.py` reproduz somente esses três mapas: não modifica os antigos. Após editar os novos mapas manualmente no Tiled, não executar esse gerador sem querer substituir essas edições.

As conexões permitem retorno entre áreas; a arena permite voltar antes do encontro. A saída das celas usa o trecho antes da parede externa, sem redesenhar o TMX aprovado. Spawns de retorno, câmera e sólidos são atualizados na troca de sala. O frame da transição não continua usando as colisões da sala anterior.

## Espada, recompensas e animações

- A Espada Longa fica no primeiro baú do Arsenal, coluna 10. É coletada pela interação E, equipada automaticamente se não houver outra arma equipada e dispara o prompt animado **K** sobre o personagem. O primeiro inimigo fica na coluna 29.
- O início da beta usa Destreza 10, atendendo ao requisito da espada. Antes, o valor inicial 9 aplicava a penalidade de dano. A arma, as animações de ataque, as hitboxes e o swing aprovado foram preservados.
- A arma equipada não fica duplicada na lista de equipamentos. Recolher a mesma arma também não duplica a posse. Se a espada tiver sido perdida, retornar ao Arsenal permite recuperá-la; não é necessário reiniciar a campanha.
- Arsenal: Raiz Amarga fixa na coluna 40; baú com Poção de Vida na galeria, coluna 43. Corredores: baú com Poção de Vida na coluna 27, poção fixa na coluna 65, Umbrita na coluna 70 e Raiz Amarga na coluna 100. Os Globins mantêm seu drop existente de Raiz Amarga.
- Ecos continuam usando as recompensas existentes. Corrigido `escos_drop` do Skeleton para que ele efetivamente entregue seus 20 Ecos.
- `_LadderClimb.png` já existia: seus seis quadros agora representam a escalada, centralizados na escada. Não houve alteração da velocidade/física de escalada. As escadas dos mapas novos se estendem dois tiles acima dos patamares, conforme o contrato da física existente.
- O Ecofoco mantém sua aparência azul-violeta. E abre o menu; **Descansar** restaura vida, stamina e cargas de poção, e recria os inimigos dos TMX. O checkpoint usa a posição livre do jogador, evitando respawn enterrado no chão.

O boss preserva IA, ataques, animações, guarda, quebra de guarda, knockback, hitstun, barra de vida e música. Os testes confirmam bloqueio frontal e dano pelas costas nas duas direções. A música de boss começa apenas no encontro real. Na derrota, a transição musical existente é chamada, projéteis são removidos, o combate para e a animação de morte precede a conclusão:

> PROFANE ECHO — Fim da Beta  
> O caminho para o topo do castelo apenas começou.

O botão retorna ao menu por clique, Enter, Espaço ou Esc. A conclusão é salva automaticamente quando a sessão possui slot e o salvamento está disponível; carregar esse progresso retorna à tela final.

## Persistência e correções de integração

Baús e Ecofocos novos usam `(sala, coluna, linha)`. Os pares antigos continuam reconhecidos na campanha antiga, sem afetar os objetos da beta. Saves antigos continuam nas salas `calabouço_*`; não são convertidos à força para outra campanha.

O banco recebe uma coluna opcional `estado_jogador` ao ser aberto pela versão nova. Ela preserva checkpoint separado da posição salva, atributos/nível, recursos, drops ativos e registros de inimigos mortos. As colunas e os slots anteriores permanecem. Saves antigos não contêm atributos históricos que nunca foram gravados; nesses casos continuam os valores padrão legados. A migração foi testada em banco sintético, sem abrir o banco pessoal.

Também foram corrigidos:

- Inventário aberto agora suspende o mundo e pode ser aberto/fechado com I; continua disponível pela pausa.
- Consumíveis usam as chaves reais de inventário, aplicam cura e diminuem a quantidade corretamente. Descartar uma unidade não duplica o drop nem mantém a quantidade antiga.
- O frasco recarregável funciona pelo inventário e não oferece descarte, que antes acessaria um `id` inexistente.
- Drops fixos são identificados por sua chave persistente, evitando duplicação de posições fracionárias.
- Respawn limpa knockback/invencibilidade residuais e restaura stamina.
- F6 reinicia a arena somente no modo de teste de combate.
- Falha de salvamento não exibe “Jogo salvo”.
- O HUD não corta os últimos dígitos da vida máxima.
- Nomes corrompidos nas chaves de ambiência/música das salas antigas foram corrigidos, mantendo os contextos e arquivos de áudio aprovados.

## Validação executada

| Verificação | Resultado |
|---|---|
| `python -m pytest -q --tb=short` | **350 testes passaram**, código de saída 0; 320 anteriores + 30 casos da beta. |
| `git diff --check` | Sem erros de whitespace. O Git apenas informa sua conversão normal de LF/CRLF. |
| Compilação por `py_compile` | 15 módulos alterados/novos compilados. |
| `validar_mapas_diretorio()` | 7 TMX, nenhum erro. Quatro avisos preexistentes: `plataformas` ausente em `calabouco_1`; `escadas`, `plataformas` e `decoracao` ausentes em `calabouco_2`. |
| Quatro TMX da beta + conexões | Nenhum erro ou aviso. |
| `python scripts/validar_beta_final.py --capturas` | Percurso completo aprovado em **5.000 atualizações**, sem teletransportar o personagem da partida principal nem reduzir a vida dos inimigos. Chefe derrotado; personagem termina com 150/200 HP. |
| Persistência | SQLite temporário: save/load, posição atual distinta do checkpoint, atributos, poções, drops, inventário, conclusão e migração do formato antigo. |
| Movimento e exploração | Ida/volta nas celas, transições de retorno, galeria com baú, descida por plataforma, todas as escadas novas, spawns e câmera em três níveis de zoom. |
| Combate e interface | Sete mortes por combate real no percurso, guarda direcional, término musical por chamada, bloqueio de combate após vitória, inventário, consumíveis, pausa e retorno real de `Jogo` ao menu. |

O percurso principal usa SDL dummy e teclado simulado. A morte é **induzida em outra cena carregada do banco temporário** para testar respawn, sem interromper a partida que enfrenta o chefe. Alguns testes unitários posicionam personagens diretamente para isolar escadas, spawns e guarda; isso não é apresentado como uma partida humana. O teste não mede tempo de apresentação: 5.000 atualizações não incluem leitura, decisões e exploração de uma pessoa. Detalhes dos marcos: [percurso.json](beta/percurso.json).

Capturas geradas pelo renderer real e revisadas visualmente:

- [Celas](beta/capturas/01_celas.png)
- [Arsenal e prompt K](beta/capturas/02_arsenal.png) · [Inventário](beta/capturas/02b_inventario.png)
- [Corredores e Ecofoco](beta/capturas/03_corredores.png) · [Galeria](beta/capturas/03a_galeria.png) · [Menu do Ecofoco](beta/capturas/03b_ecofoco_menu.png)
- [Arena do chefe](beta/capturas/04_arena.png)
- [Fim da Beta](beta/capturas/05_fim_beta.png)

## Como iniciar e demonstrar

1. Na raiz do repositório, executar `python main.py` e iniciar **Novo jogo em um slot vazio**. Continuar um save antigo mantém a campanha antiga.
2. Nas celas, seguir à direita até a primeira escada, descer com S e percorrer o corredor inferior, saltando os degraus. Continuar até a saída no extremo direito.
3. No Arsenal, abrir o primeiro baú com E. Usar K para atacar; segurar e soltar carrega o combo existente. A/D move, Espaço pula, W/S usa escadas, S+Espaço desce das plataformas, F usa a poção, I abre o inventário e Esc abre a pausa.
4. Avançar pelos encontros e entrar nos Corredores. A galeria à esquerda oferece uma poção extra. Perto do fim, interagir com o Ecofoco e escolher **Descansar** antes de seguir à arena. Para registrar progresso antes do chefe, usar **Esc → Salvar** nessa área segura.
5. Entrar na arena, enfrentar o Carrasco, contornar o escudo e administrar stamina/poções. Após a derrota, aguardar a conclusão e selecionar **Voltar ao menu principal**.

`python main.py --teste-celas` continua abrindo a sessão experimental isolada, sem slot. `python main.py --teste-combate` mantém a arena de testes; F6 reinicia esse modo. Nenhum desses modos é necessário para a campanha beta.

## Revisão manual pendente e preservação

A entrega está pronta para revisão manual. Ainda é necessário jogar uma sessão com janela, teclado e saída de som reais no computador da apresentação para avaliar conforto do combate, volume/transições percebidas, legibilidade e fluidez. O teste automatizado confirma os eventos de áudio; não substitui escuta humana. A decoração das fases novas é simples, com suportes vazios e armaduras existentes; não houve produção de sprites exclusivos nem iluminação nova. Pode aparecer o aviso não fatal `libpng: iCCP: known incorrect sRGB profile` de assets existentes.

As alterações locais anteriores foram preservadas. Hashes antes/depois confirmam que `jogo.log`, `saves.db`, `configuracoes_usuario.json`, `bloco_celas_esquecidas.tmx`, `calabouco_1.tmx` e `calabouco_2.tmx` não foram alterados nesta operação. O Git já mostrava `jogo.log` modificado antes do início. Nenhum `git add`, commit ou push foi realizado. Todos os saves de validação foram criados em diretórios temporários.
