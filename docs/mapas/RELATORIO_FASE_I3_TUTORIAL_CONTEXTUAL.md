# PROFANE ECHO — Fase I.3: tutorial contextual das celas

Implementação concluída em 23/11/2026, pronta para avaliação visual e funcional.
O modo `python main.py --teste-celas` apresenta dicas pequenas sobre a cabeça do
personagem, sem texto explicativo, pop-up, pausa ou condição para avançar.

## Arquitetura

`core/tutorial_contextual.py` contém `TutorialContextual`, um observador do estado
do jogador. Ele seleciona um grupo de teclas, observa deslocamento/estado físico e
mantém conclusões apenas na memória. Não escreve no jogador, no mapa ou nos saves.

O desenho continua em `ui/prompts_teclas.py`, usando **PromptTeclaMundo da G.1**.
O controlador apenas dispõe um ou dois componentes lado a lado, centralizados em
`player.rect.centerx`, com a âncora quatro pixels acima do topo do rect. A transformação
pela câmera, a flutuação e o desenho dos sprites são compartilhados com o prompt E.
Não foi criado outro renderizador de teclas nem alterado o HUD.

`Gamescene` cria o controlador ao carregar as celas **somente quando `sala_teste`
identifica o modo experimental**. Atualiza as dicas após a física e a seleção de
interação, e as desenha na mesma surface de mundo, antes da escala final da câmera.
Trocar de sala elimina o controlador anterior. Uma nova entrada nas celas/reinício da
sessão cria dicas novas, inclusive após recarregamento da sala no respawn.

Recursos normal/pressionado são carregados em cache na criação. A geometria é lida
uma vez: células contíguas de escada viram corredores verticais; superfícies sólidas
sem um tile imediatamente acima são candidatas a degraus. Nenhuma leitura de TMX ou
PNG ocorre no ciclo normal de cada frame. Não há chamada de áudio no controlador.

## Ativação e conclusão

| Dica | Ativação | Conclusão |
|---|---|---|
| A/D | Início da sessão, enquanto ainda não demonstrou movimento | 64 px acumulados de deslocamento horizontal real, com A ou D na direção do deslocamento e apoio no frame anterior; dash/knockback não contam |
| S | Próximo ao topo de uma escada real | 24 px de deslocamento vertical real no estado de escalada, com W/S |
| W | Próximo à base de uma escada real | Mesma regra de uso real de escada |
| W/S | Trecho intermediário da escada, onde ambas as direções fazem sentido | Mesma regra |
| Espaço | Em apoio, com um degrau sólido à frente a até 80 px, entre 8 e 64 px acima dos pés | Salto real iniciado nesse contexto, seguido de pouso sobre o trecho elevado, após avançar pela sua borda |

Andar apenas para a direita é suficiente para concluir A/D. KEYDOWN sozinho, empurrar
uma parede ou cair pela escada não concluem as dicas. Pressionar Espaço sem stamina
altera a aparência da tecla, mas não conclui pulo. Pular no spawn, longe de um obstáculo,
não solicita nem conclui o tutorial de pulo.

A primeira escada fica na coluna 21. A dica S aparece na aproximação pelo piso da
primeira cela; quem optar por cair recebe W na base quando ainda não aprendeu escalada.
O primeiro trecho de pulo aparece no corredor, antes dos degraus que começam na coluna
34, linha 25. Esses pontos são encontrados na geometria; nenhum marcador foi adicionado
ao TMX. O algoritmo também atende os demais degraus e escadas existentes caso uma dica
tenha sido ignorada antes. Dicas contextuais têm preferência sobre a dica de movimento.

Conclusões não abrem portas, não ativam transições e não controlam o percurso. O teste
com controlador desativado mantém o percurso original completo de 3290 frames.

## Aparência e prioridades

- Uma dica/grupo coerente por vez; teclas quadradas de 16×16 e intervalo de três pixels.
- Espaço usa a barra da própria folha, compactada para 48×16 em cache, mantendo a altura
  das letras. Não é um painel ou um texto de instrução.
- Entrada em oito frames; desaparecimento em até 12 frames. Flutuação discreta herdada
  da G.1. Os objetos dos prompts são reutilizados, sem reiniciar animações a cada frame.
- Tutorial usa `entrada_real=True`: somente a tecla realmente segurada fica pressionada,
  e soltar restaura imediatamente o estado normal. Não existe pulso automático simulando
  input no tutorial. O comportamento periódico original de interação permanece disponível.
- **E tem prioridade absoluta** quando o gerenciador da G.1 seleciona uma interação válida.
  O tutorial é ocultado imediatamente; o desenho também revalida E antes de decidir.
- Pausa, inventário, menu de fogueira e morte suprimem estado visual e desenho. Não contam
  movimento oculto para conclusão. Ao retornar, a seleção contextual pode reaparecer.
- Nenhum objeto interativo foi acrescentado às celas. O teste de prioridade instancia
  um `Bau` real apenas na fixture, sem gravar ou modificar o mapa.

A folha `gdb-keyboard-2.png` já existente foi inspecionada. Alguns recortes de mundo
eram provisórios: A/D/K apontavam para teclas diferentes e Espaço não tinha estados
distintos. Foram corrigidos e W/S cadastrados. O estado normal de E foi preservado;
seu estado pressionado agora usa o **E do segundo bloco**, 112 px abaixo, em vez de
recortar D da primeira linha inferior. O gerenciador de interação e a ação E não foram
alterados. Recortes do HUD ficaram intactos; nenhum PNG foi editado.

## Sessão e preparação para o Arsenal

`concluidas` é um conjunto de identificadores em memória. O construtor aceita um
conjunto inicial para futura integração de progresso; esta fase não liga esse estado
ao sistema de saves nem altera seu formato.

O ponto de extensão `solicitar(identificador, teclas)` permite a uma futura sala pedir,
por exemplo, `solicitar("ataque", ("k",))`. O chamador deverá verificar a aquisição
da espada, definir o contexto e chamar `concluir("ataque")` após observar o ataque real.
`cancelar_solicitacao()` retira a solicitação externa. Prioridade de E e supressões
continuam válidas. **Nenhuma chamada de tutorial K ocorre nas celas.**

Para repetir a experiência desde o início, iniciar novamente `python main.py --teste-celas`.
Não foi criado um atalho de reinício: F6 continua com sua função anterior de teste de
combate e não é anunciado como reinício das celas.

## Capturas reais

Todas as imagens abaixo têm **1280×720, zoom 1,35** e foram produzidas por
`Gamescene.desenhar()` após inputs, física e acompanhamento normal da câmera. Não houve
teleporte do jogador, edição das imagens, HUD substituto ou câmera editorial no percurso.

- [A/D no spawn](previews/i3/01_ad_spawn.png).
- [D pressionado](previews/i3/02_d_pressionado.png) e [A pressionado](previews/i3/03_a_pressionado.png).
- [S no topo da escada](previews/i3/04_s_topo_escada.png) e [descida](previews/i3/05_s_descendo.png).
- [W na base](previews/i3/06_w_base_escada.png) e [subida](previews/i3/07_w_subindo.png).
- [Espaço antes do degrau](previews/i3/08_espaco_degrau.png) e [Espaço durante o salto](previews/i3/09_espaco_pressionado.png).
- [Retorno com dicas concluídas](previews/i3/10_retorno_sem_dicas.png).

[capturas.json](previews/i3/capturas.json) registra âncora do jogador, câmera, zoom,
teclas, estado pressionado, opacidade e conclusões de cada imagem.
[percurso.json](previews/i3/percurso.json) registra os oito marcos do percurso completo.
O script usa uma segunda sessão para demonstrar W após queda livre, sem simular uma
conclusão ou apagar progresso da primeira sessão.

Reprodução segura das capturas, sem inicializar `main`, configurar log ou abrir saves:

```powershell
python scripts/validar_tutorial_celas.py
```

## Validação

| Verificação | Resultado |
|---|---|
| `python -m pytest tests/test_fase_i3_tutorial.py -q --tb=short` | 23 testes novos passaram |
| `python -m pytest -q --tb=short` | **320 testes passaram**, exit code 0 |
| `py_compile` dos três módulos, script e teste da entrega | Passou |
| `git diff --check` | Passou; apenas avisos LF/CRLF em arquivos anteriormente modificados |
| Percurso com tutorial e capturas | Oito marcos, 3307 frames, três dicas concluídas; inclui inputs adicionais para mostrar A/D |
| Percurso com controlador desativado | Oito marcos, 3290 frames, mesma ida/volta original |
| 94 arquivos protegidos: hash e mtime | Preservados, incluindo mapas, arte, folha de teclas, física, câmera, gerenciador de interação, `main.py`, `jogo.log` e `saves.db` |

Os testes cobrem input visual, ausência de pulso falso, fade, conclusão por movimento,
parede bloqueando deslocamento, direções de escada, queda livre, pulo fora de contexto,
stamina insuficiente, conclusão ao vencer degrau, todas as supressões, prioridade real
de E, troca de sala, nova sessão, saves experimentais bloqueados, câmera em três zooms,
extensão explícita de K, ausência de sons e recortes sem fallback.

Evidências em [baseline.json](previews/i3/baseline.json) e
[validacao.json](previews/i3/validacao.json). Diffs desta etapa separados das mudanças
anteriores: [Gamescene](previews/i3/game_scene.diff) e [prompts](previews/i3/prompts_teclas.diff).
O aviso legado de perfil PNG `iCCP` ainda aparece no carregamento, sem impedir os testes.

## Arquivos e limites

Alterados: `core/game_scene.py`, `ui/prompts_teclas.py`.

Novos: `core/tutorial_contextual.py`, `tests/test_fase_i3_tutorial.py`,
`scripts/validar_tutorial_celas.py`, este relatório e `docs/mapas/previews/i3/`.
Nenhuma alteração de mapa, arquitetura, arte I.2.3b, colisão, física, inimigos, progressão,
música, HUD, inventário ou formato de save. Sem git add, commit ou push.

O detector de pulo foi projetado para os degraus sólidos existentes: não ensina salto
de abismo nem queda por plataforma. Conclusão de pulo exige pousar no trecho elevado;
o input isolado não basta. A direção de escada segue os controles W/S existentes.
O controlador funciona no ciclo fixo de atualização atual do jogo.

Capturas foram inspecionadas, mas a aprovação final da escala, leitura e ritmo das
dicas depende da avaliação humana no modo experimental. Os testes confirmam o
comportamento e a preservação técnica; não substituem essa avaliação.
