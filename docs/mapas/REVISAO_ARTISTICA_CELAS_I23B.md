# Profane Echo — revisão artística das celas (I.2.3b)

Direção: três identidades ambientais, com a estrutura jogável existente. Referência
consultada: `referencias/imagem_referencia.webp`. A referência orienta a narrativa e
a leitura dos objetos; não substitui o layout aprovado.

## Composição

| Cena | Leitura pretendida | Escolhas |
|---|---|---|
| Cela 1 — confinamento | Um lugar onde alguém ainda conta os dias | Cama mais legível, marcas acima dela, grilhões e um único recipiente; retirada dos dois pequenos montes diante da cama |
| Cela 2 — outro prisioneiro | A contagem continuou, mas o prisioneiro não saiu | Esqueleto sentado perto da parede esquerda, duas aplicações de marcas acima dos restos, grade preservada; retirada dos ossos soltos e do barril |
| Cela 3 — primeiro mistério | Uma ruptura que não parece desgaste comum | Uma única fissura violeta, conduzida até o piso, com entulho concentrado na base; menos repetição de detritos no centro |
| Saída | Uma porta de ferro aberta, reconhecível | Composição completa de arco, ombreiras e folha aberta, substituindo arco pequeno e grade separados |

A fissura recebe o contraste mais forte. A cama ganha arestas azul-acinzentadas e
separação do pano; a rachadura comum ganha uma borda mineral; a umidade recebe
meios-tons verde-acinzentados. A cor violeta permanece exclusiva da fissura.
Esses ajustes estão nos sprites, sem aumentar o brilho global do mapa ou mudar luzes.
Após a inspeção no zoom real, marcas e fissura passaram para `decoracao`, preservando
suas cores sem o tint de `decoracao_fundo`. O tint existente não foi alterado. A fissura
conserva uma leve luminosidade integrada à imagem, sem adicionar efeito em runtime.

A ocupação decorativa total caiu de 150 para 137 células, mesmo com os novos sprites.
Na terceira cela restaram dois pequenos detritos junto à fissura e o par já existente
perto da escada. Foram retirados também uma corrente repetida da primeira cela e os
grilhões distantes da composição principal da segunda.

| Elemento | Coluna/linha inicial (base zero) | Camada |
|---|---|---|
| Cama | (5,11) | decoracao |
| Marcas da primeira cela | (6,9) | decoracao |
| Umidade junto à cama | (3,9) | decoracao_fundo |
| Esqueleto | (29,10), base no piso y=384 | decoracao |
| Marcas do outro prisioneiro | (29,8) e (31,9) | decoracao |
| Fissura única | (69,9), base no piso y=384 | decoracao |
| Detritos na base da fissura | (68,11) e (71,11) | decoracao |
| Porta aberta | (121,22), base no piso y=832 | decoracao_fundo |

As outras quatro manchas e quatro rachaduras comuns mantiveram suas posições, com
arte revisada. Alterações por célula e motivo: [alteracoes.json](previews/i23b/alteracoes.json).

## Arte e arquivos

Ferramenta integrada `image_gen.imagegen`, usando a skill `imagegen`: quatro edições
dos sprites anteriores e três gerações novas, todas solicitadas com alpha transparente.
Prompts e origem dos resultados em `previews/i23b/geracao.json`; fontes preservadas
em `previews/i23b/fontes/`. O processamento de integração apenas recorta as margens
transparentes, reduz por vizinho mais próximo e empacota a grade, sem redesenhar pixels.

Os arquivos anteriores são preservados. Novos sprites, atlas e manifesto em
`assets/tileset/profane_echo_celas_v2/`; TSX em
`assets/tileset/tilesets/Profane Echo - celas narrativa.tsx`. O atlas tem 256×224,
oito colunas e 56 slots de 32×32. Seu intervalo no mapa é 7100–7155, sem sobreposição.
O TMX continua sendo a fonte editável; o empacotador não o grava.

## Capturas para avaliação

As imagens individuais têm **1280×720, zoom 1,35**, produzidas por
`Gamescene.desenhar()`, com o mesmo redimensionamento do jogo e HUD. Não são imagens
ampliadas de um render geral.

Há dois tipos explicitamente separados em `antes/capturas.json` e `depois/capturas.json`:

- `jogo_*`: posições alcançadas por entradas de teclado, física e acompanhamento
  normal da câmera. Incluem spawn, vista da cela fechada antes da descida, aproximação
  da fissura e saída.
- `cela_*` e `saida`: enquadramentos editoriais da câmera, no mesmo renderer e zoom,
  para avaliar cada composição inteira. Não representam entrada do jogador na cela
  fechada. Nenhum jogador ou objeto do TMX foi reposicionado para obter esses quadros.

Os comparativos colocam antes sobre depois, mantendo os 1280×720 de cada quadro.
A segunda cela continua inacessível; seus restos ficam do lado esquerdo para serem
vistos da primeira cela antes da descida. A nova porta é visual: não conecta ao Arsenal
nem introduz interação. A aprovação artística continua sendo uma avaliação humana,
independente do resultado dos testes.

## Validação

Capturas principais, sem redução:

- [Confinamento — câmera do jogador](previews/i23b/depois/jogo_01_spawn.png).
- [Outro prisioneiro visto antes da descida](previews/i23b/depois/jogo_02_vista_cela_fechada.png).
- [Primeiro mistério — chegada à terceira cela](previews/i23b/depois/jogo_03_eco.png).
- [Fissura — aproximação](previews/i23b/depois/jogo_04_fissura.png).
- [Porta de saída — câmera do jogador](previews/i23b/depois/jogo_05_saida.png).

Comparativos editoriais em escala real: [cela 1](previews/i23b/comparativo_cela_1_confinamento.png),
[cela 2](previews/i23b/comparativo_cela_2_prisioneiro.png),
[cela 3](previews/i23b/comparativo_cela_3_eco.png) e [saída](previews/i23b/comparativo_saida.png).
[Atlas ampliado](previews/i23b/atlas_ampliado.png) e [render do Tiled](previews/i23b/tiled_depois.png).

| Verificação | Resultado |
|---|---|
| `python -m pytest -q --tb=short` | 297 testes passaram, exit code 0 |
| `py_compile` dos dois scripts novos | Passou |
| Validador TMX existente | Sem erros |
| Render nativo do Tiled | Exit code 0 |
| Percurso completo com física, teclado e câmera reais | 3290 frames, oito marcos, seis saltos/drops; ida e volta preservadas |
| XML protegido: atributos do mapa e sete estruturas | Idênticos ao baseline |
| 69 arquivos protegidos: SHA-256 e mtime | Idênticos, incluindo `jogo.log`, `saves.db`, código e assets anteriores |
| Novos GIDs e carregamento das superfícies 32×32 | Válidos, sem sobreposição de intervalos |
| Capturas individuais | 1280×720 e zoom 1,35 confirmados |
| `git diff --check` | Passou; apenas avisos de conversão LF/CRLF em arquivos anteriores |

Evidências: [baseline](previews/i23b/baseline.json), [validação](previews/i23b/validacao.json),
[saída dos comandos](previews/i23b/comandos_validacao.json) e
[percurso completo](previews/i23b/percurso/percurso.json). O aviso legado de perfil
PNG `iCCP` permanece, sem impedir os renders; os PNGs antigos não foram regravados.

Alterado nesta revisão: `assets/maps/bloco_celas_esquecidas.tmx`, apenas dados de
`decoracao`/`decoracao_fundo` e referência ao novo TSX. Atributos e ordem das camadas
foram preservados. Novos: sete sprites, atlas, manifesto e README em
`assets/tileset/profane_echo_celas_v2/`; TSX citado; scripts
`scripts/empacotar_decoracao_i23b.py` e `scripts/previews_celas_i23b.py`; este relatório
e evidências em `previews/i23b/`. Sem alterações de sistemas ou testes, sem `git add`,
commit ou push. Os arquivos já modificados no workspace não foram revertidos.

As imagens integradas foram inspecionadas e ajustadas após a captura. Não há pendência
técnica conhecida. A escolha artística está pronta para revisão do usuário; os testes
demonstram preservação técnica, não aprovação estética. O Arsenal permanece fora desta
entrega, assim como qualquer mudança na exploração ou nas transições.
