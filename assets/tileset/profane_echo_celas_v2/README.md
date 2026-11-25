# Celas — narrativa e contraste

Set da revisão artística I.2.3b. Substitui visualmente os quatro sprites de
`../profane_echo_celas/` neste mapa e acrescenta contagem de dias, esqueleto sentado
e porta de saída aberta. A versão anterior continua preservada.

Arte gerada/editada pela ferramenta integrada `image_gen.imagegen`. Prompts completos
e caminhos originais: [geracao.json](../../../docs/mapas/previews/i23b/geracao.json).
Fontes copiadas sem alteração em [fontes/](../../../docs/mapas/previews/i23b/fontes/).

| Sprite | Dimensão final | IDs locais por linha |
|---|---|---|
| cama_pedra | 96×32 | 0,1,2 |
| fissura_profana | 64×96 | 3,4 / 11,12 / 19,20 |
| umidade | 64×64 | 5,6 / 13,14 |
| rachadura | 32×64 | 7 / 15 |
| marcas_dias | 64×32 | 24,25 |
| esqueleto_sentado | 64×64 | 26,27 / 34,35 |
| porta_saida | 96×128 | 28,29,30 / 36,37,38 / 44,45,46 / 52,53,54 |

Atlas `decoracao_celas_v2.png`: RGBA, 256×224, oito colunas, sem margem/espaçamento.
TSX: `../tilesets/Profane Echo - celas narrativa.tsx`. `firstgid=7100` no mapa atual;
outros mapas podem atribuir outro valor. Use composições completas; espaços transparentes
no centro da porta pertencem à abertura, não são tiles ausentes.

O [manifesto](manifesto.json) documenta IDs, hashes das fontes e normalização.
O empacotamento corta apenas margens transparentes, preserva proporção/alpha e reduz
por vizinho mais próximo. Cama, esqueleto e porta ficam apoiados na borda inferior.
Para reproduzir a partir das fontes incluídas:

```powershell
python scripts/empacotar_decoracao_i23b.py
```

Fissura e marcas usam `decoracao` para preservar o contraste, sem o tint da camada
de fundo. Umidade, rachadura comum e porta usam `decoracao_fundo`. Cama e esqueleto
usam `decoracao`. Todos são visuais, sem colisão, interação, animação ou eventos.
Não aplicar o set inteiro em toda cela: ver a [distribuição narrativa](../../../docs/mapas/REVISAO_ARTISTICA_CELAS_I23B.md).
