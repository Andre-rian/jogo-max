# Decoração das Celas — I.2.3

Arte original gerada com `image_gen.imagegen`, solicitando RGBA transparente.
Quatro chamadas independentes; fontes copiadas sem alteração e prompts completos em
[`docs/mapas/previews/i23`](../../../docs/mapas/previews/i23/geracao.json).
Não são recortes dos packs anteriores.

| Sprite | Dimensão | IDs locais, por linha |
|---|---|---|
| cama_pedra.png | 96×32 | 0, 1, 2 |
| fissura_profana.png | 64×96 | 3, 4 / 11, 12 / 19, 20 |
| umidade.png | 64×64 | 5, 6 / 13, 14 |
| rachadura.png | 32×64 | 7 / 15 |

`decoracao_celas.png`: atlas RGBA de 256×96, oito colunas, 24 slots de 32×32,
sem margem nem espaçamento. Nove slots vazios ficam reservados; não pintá-los no mapa.
No Bloco das Celas, o `firstgid` é 7000; em outro mapa, o Tiled pode atribuir outro.
O TSX está em `../tilesets/Profane Echo - celas decoracao.tsx`.

São composições decorativas: pintar todas as células do sprite na ordem indicada,
sem colisão ou objetos de interação. Cama em `decoracao`, com a base no piso;
manchas e rachaduras em `decoracao_fundo`. A fissura aparece uma única vez neste mapa.

O empacotamento usa recorte dos limites do alpha, redução proporcional por vizinho
mais próximo e alinhamento em células. Não redesenha a arte, não substitui o alpha
e não adiciona efeitos. A cama é alinhada à borda inferior. O manifesto registra
dimensões originais, recortes, deslocamentos, hashes e composição dos GIDs.

Para reproduzir o atlas a partir das fontes já incluídas no repositório:

```powershell
python scripts/empacotar_decoracao_i23.py
```

Esse comando grava os sprites, atlas, manifesto e folha de inspeção; não grava o TMX.
O mapa editável continua sendo a fonte de verdade, sem gerador de layout ativo.
