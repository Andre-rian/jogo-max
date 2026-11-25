# PROFANE ECHO — Fase I.2.3: curadoria e decoração

Entrega de 22/11/2026. Curadoria aplicada ao `bloco_celas_esquecidas.tmx`, com quatro
sprites novos integrados e validações concluídas. Apenas o TMX existente foi alterado
nesta etapa; os demais arquivos da entrega são novos. Alterações anteriores do
workspace foram preservadas. Sem `git add`, commit ou push.

## Leitura do estado inicial

A base encontrada já incluía a limpeza da I.2.2. Camas feitas de blocos, símbolo usado
como rachadura, portas falsas do corredor, recortes incompletos e entulho flutuante
já haviam sido retirados naquela etapa. Não foram contabilizados novamente como
remoções desta entrega. O antes real está em `previews/i23/mapa_antes.tmx.txt` e nas
capturas `antes_*.png`.

Os pontos fracos restantes eram a ausência de uma cama reconhecível, pouca indicação
de umidade e a falta de rachaduras próprias, incluindo uma marca discreta do Eco.
Grades, correntes, arco da saída, recipientes, ossos, entulho apoiado e tochas tinham
leitura suficiente e foram mantidos. A grade elevada da cela fechada continua sendo
uma abertura gradeada na parede; não recebeu interação nem passagem.

| Caso auditado | Categoria solicitada | Decisão aplicada |
|---|---|---|
| Antiga cama em blocos opacos | Remover | Já removida na I.2.2; não reintroduzida |
| Recortes soltos, falsas portas e entulho flutuante | Remover | Ausentes no estado inicial; nenhuma nova remoção necessária |
| Grades, arco, correntes e teia composta | Substituir por tile existente | Correções da I.2.2 já presentes e preservadas |
| Cama ausente na cela inicial | Criar novo tile decorativo | Cama de pedra com travesseiro e pano rasgado, 96×32 |
| Paredes sem umidade | Criar novo tile decorativo | Mancha azul-esverdeada escura, 64×64, cinco aplicações |
| Rachadura comum ausente | Criar novo tile decorativo | Fenda irregular sem símbolo, 32×64, quatro aplicações |
| Falta de detalhe profano junto à passagem | Criar novo tile decorativo | Uma fissura 64×96, com poucos pontos violetas |

Nesta etapa foram preenchidas 37 células antes vazias. Nenhuma célula decorativa
preexistente foi substituída ou apagada: a limpeza anterior foi suficiente. Evitou-se
acrescentar uma coleção de novos objetos apenas para preencher espaço.

## Assets e aplicação

Fontes geradas com a skill `imagegen`, ferramenta integrada `image_gen.imagegen`,
em quatro chamadas com transparência. Prompts completos e caminhos de origem:
[`geracao.json`](previews/i23/geracao.json). Originais preservados em
[`fontes/`](previews/i23/fontes/). O empacotamento só recorta margens transparentes,
reduz proporcionalmente por vizinho mais próximo e alinha à grade; não desenha arte.

Sprites finais e atlas em [`assets/tileset/profane_echo_celas/`](../../assets/tileset/profane_echo_celas/).
O [manifesto](../../assets/tileset/profane_echo_celas/manifesto.json) documenta dimensões,
origens, hashes, recortes e IDs locais. [Folha ampliada](previews/i23/atlas_ampliado.png).

Coordenadas abaixo são coluna/linha do TMX, começando em zero:

| Composição | Camada | Posições |
|---|---|---|
| Cama de pedra | decoracao | (5,11), base em y=384 |
| Fissura profana | decoracao_fundo | (69,7), lado direito da cela destruída, perto do acesso opcional |
| Umidade | decoracao_fundo | (3,2), (45,9), (27,13), (94,13), (115,13) |
| Rachadura comum | decoracao_fundo | (18,6), (30,6), (60,18), (105,18) |

A cama ocupa três tiles, com pés no piso e espaço em relação ao spawn. Os detalhes de
parede são discretos e não cobrem escadas, plataformas ou tochas. Há uma única fissura
profana; não é portal, objeto coletável nem indicação de uma mecânica nova.
O pequeno brilho faz parte da imagem e não usa luz ou efeito adicional em runtime.

## Integração e preservação

- Novo TSX: `assets/tileset/tilesets/Profane Echo - celas decoracao.tsx`.
- Atlas RGBA 256×96, 24 slots de 32×32, 15 ocupados e nove transparentes reservados.
- `firstgid=7000`, intervalo 7000–7023. O maior intervalo anterior termina em 6086.
- `decoracao`: três células adicionadas. `decoracao_fundo`: 34 células adicionadas.
- Nenhum atributo de camada, tint, ordem de desenho ou propriedade do mapa mudou.
- `fundo`, `colisao`, `plataformas`, `escadas`, `objetos` e `referencias` preservados,
  assim como as propriedades do mapa. Nenhuma exceção de alinhamento foi necessária.
- Spawn, checkpoints, eventos, transições, lógica, progressão e código de gameplay
  não foram alterados. Os 61 arquivos registrados no baseline mantiveram SHA-256 e
  mtime, incluindo assets anteriores, módulos protegidos, `jogo.log` e `saves.db`.

O TMX já era não rastreado e `jogo.log` já aparecia modificado no Git antes desta tarefa.
Esses estados não significam que o log tenha sido tocado aqui. O baseline e a validação
documentam a preservação durante a I.2.3.

## Previews

Capturas feitas pelo renderer do jogo, sem iniciar `main`, logging ou saves:

- [Visão geral antes](previews/i23/antes_visao_geral.png) e [depois](previews/i23/depois_visao_geral.png).
- [Spawn antes/depois](previews/i23/comparativo_cela_spawn.png).
- [Cela fechada antes/depois](previews/i23/comparativo_cela_fechada.png).
- [Cela destruída antes/depois](previews/i23/comparativo_cela_destruida.png).
- [Passagem opcional antes/depois](previews/i23/comparativo_passagem.png).
- [Corredor oeste](previews/i23/comparativo_corredor_oeste.png), [galeria](previews/i23/comparativo_galeria.png),
  [corredor leste](previews/i23/comparativo_corredor_leste.png) e [saída](previews/i23/comparativo_saida.png).
- [Render nativo do Tiled](previews/i23/tiled_depois.png), sem entidades adicionadas pelo jogo.
- [Capturas do percurso](previews/i23/jogo/) com oito marcos, visão completa e colisões.

O recorte estreito da passagem e a saída não receberam nova composição diretamente;
seus comparativos registram a preservação. A fissura está visível no recorte da cela
destruída. Os renders completos conservam resolução nativa; a visão geral é reduzida.

## Validação executada

| Verificação | Resultado |
|---|---|
| `python -m py_compile scripts/empacotar_decoracao_i23.py scripts/previews_celas_i23.py` | Passou |
| `python -m pytest -q --tb=short` | 297 testes passaram, exit code 0 |
| Validador TMX existente (`scripts/gerar_bloco_celas.py`, somente leitura) | Sem erros |
| `tmxrasterizer.exe` do Tiled | Render gerado, exit code 0 |
| Percurso por inputs reais, sem teleporte/dash | Ida e volta completas, oito marcos, 3290 frames, seis saltos/drops |
| Comparação XML das sete estruturas protegidas e atributos do mapa | Idênticos ao baseline |
| SHA-256 e mtime dos 61 arquivos protegidos | Idênticos ao baseline |
| Intervalos GID e carregamento de todos os novos tiles pelo renderer | Sem sobreposição; todos os recortes usados têm pixels visíveis |
| `git diff --check` | Passou |

Evidências: [baseline](previews/i23/baseline.json), [validação](previews/i23/validacao.json),
[aplicações](previews/i23/aplicacoes.json) e [percurso](previews/i23/jogo/percurso.json).
Os PNGs legados ainda produzem o aviso de perfil `iCCP` no carregamento; não impediu
renderização nem testes e não foram regravados.

## Arquivos desta entrega e revisão visual

Alterado: `assets/maps/bloco_celas_esquecidas.tmx`.

Novos: o TSX citado, quatro sprites individuais, atlas, manifesto e README em
`assets/tileset/profane_echo_celas/`; `scripts/empacotar_decoracao_i23.py`;
`scripts/previews_celas_i23.py`; este relatório e as evidências em `previews/i23/`.
Nenhum módulo de gameplay ou teste foi alterado nesta fase.

As capturas foram inspecionadas após integração. Não há pendência técnica conhecida.
Aprovação estética final pelo usuário permanece aberta, sobretudo para o contraste
deliberadamente baixo da umidade e da fissura no monitor usado para jogar. Não houve
playtest humano presencial; o percurso foi automatizado com física e câmera reais.

Para próximas áreas, reutilizar composições completas, apoiar objetos no piso e manter
umidade/rachaduras como detalhes de fundo. Não preencher os nove slots vazios do atlas
por engano nem presumir que 7000 será o firstgid de outros mapas. Prefira poucos pontos
de narrativa ambiental a repetir a fissura violeta em todas as paredes.
