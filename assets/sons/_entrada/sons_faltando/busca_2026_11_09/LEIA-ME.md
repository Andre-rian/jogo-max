# Candidatos de áudio — busca de 2026-11-09

**Atualização de 2026-11-10:** os 66 arquivos originais foram utilizados nas
promoções dos lotes 1–3. Permanecem aqui como fontes para reprodução das edições,
com hashes, autoria e licenças. Não são carregados diretamente pelo jogo.

`CANDIDATOS.csv` agora registra `fonte_utilizada_em_promocao` e os
`destinos_promovidos` conferidos na árvore final. Os campos de opinião do usuário
não foram preenchidos automaticamente. As receitas concluídas estão em
`tools/promocao_lote1.csv` a `tools/promocao_lote3.csv`; o pulo usa a fatia 003 da fonte.

## Como consultar

1. [ESCUTA.md](ESCUTA.md) e [ESCUTA.m3u8](ESCUTA.m3u8) permitem ouvir as fontes.
2. [CANDIDATOS.csv](CANDIDATOS.csv) relaciona fontes e destinos já utilizados.
3. [COBERTURA_55_DESTINOS.csv](COBERTURA_55_DESTINOS.csv) é o mapeamento histórico
   da busca, anterior às promoções. As pendências atuais estão em
   [STATUS_SONS.md](../../../../../docs/audio/STATUS_SONS.md).

Os dados de prioridade e recomendações de edição abaixo registram a busca
original de 2026-11-09. Não são uma nova fila de promoção.

## Organização

| Pasta | Arquivos | Conteúdo |
|---|---:|---|
| `2_inimigos/` | 19 | Globin, Flying Eye, Mushroom, Skeleton e Boss |
| `3_materiais/` | 12 | Carne, osso, fungo e texturas etéreas |
| `4_player/` | 14 | Swing genérico, pulo, passos e pousos |
| `5_projeteis/` | 12 | Disparos, impactos e base de ar para voo |
| `6_mundo/` | 6 | Fogo, mecanismos e Eco Profano |
| `7_ambiencia/` | 3 | Arena do Boss e sala de descanso |

Por prioridade: 22 arquivos de P1, 18 de P2 e 26 de P3. Os 55 destinos estão mapeados: **18 têm candidato de uso mais direto e 37 têm bases para edição/adaptação**. A existência do mapeamento não significa que o destino está resolvido.

## Pontos para ouvir com atenção

- **Etéreo:** os vocais de Shade são texturas para compor um impacto. Avaliar se combinam com o Flying Eye e com a proposta sombria.
- **Hits por arma:** as bases compartilhadas de carne, osso e fungo precisam ser escolhidas e diferenciadas; não são versões prontas de espada, machado e soco.
- **Voo dos projéteis:** existe uma única base de ar em `5_projeteis/voo_compartilhado/`, referenciada por quatro destinos. Avaliar corte para passagem ou loop discreto e camadas específicas por projétil.
- **Pulo:** o arquivo é uma compilação de esforços de 12,52 s; será preciso escolher um trecho.
- **Pouso metálico:** a fonte é descrita como pouso de ciborgue/nave. É uma alternativa provisória; pode não combinar com o cavaleiro.
- **Terra:** os passos incluem vegetação e cascalho; o pouso também é em cascalho. Confirmar qual textura faz sentido para os pisos futuros.
- **Fogo e ambiências:** conferir as emendas antes de usar loops. Fogo pode servir tanto à tocha quanto à sala de descanso, com ajustes diferentes.

## Fontes e licenças

[FONTES.csv](FONTES.csv) registra as 20 fontes, autores e URLs de download/licença. [CREDITOS_E_LICENCAS.md](CREDITOS_E_LICENCAS.md) reúne os créditos; os arquivos originais de licença dos passos estão em `licencas/footsteps/`.

O lote contém 53 arquivos CC0 e 13 CC BY 3.0. Para os arquivos CC BY, preservar os créditos registrados no CSV ao integrar ou distribuir. O nome/pasta local foi alterado, mas o conteúdo de áudio foi preservado.

As duas prévias públicas HQ são identificadas por `origem=previa_hq`:

- `3_materiais/osso/osso_soco_hit_previa_hq_192146.mp3`;
- `4_player/movimento/pouso/terra/pouso_cascalho_previa_hq_819656.mp3`.

O WAV antigo de osso em `_entrada/2_materiais/osso/` contém somente um ponteiro Git LFS. A fonte antiga foi preservada; a prévia foi baixada para permitir a avaliação neste lote.

## Conferência realizada

- Os 66 áudios passaram por leitura de metadados e decodificação integral, sem erros, amostras inválidas ou arquivos inteiramente silenciosos.
- Duração, codec, canais, taxa, pico e SHA-256 estão no CSV.
- Nenhum dos 66 arquivos duplica exatamente outro arquivo do lote.
- Os 381 arquivos preexistentes monitorados mantiveram seus hashes, incluindo a árvore final, configuração e o conteúdo anterior de `sons_faltando`.
- A reprodução no jogo não foi testada: este lote permanece fora da árvore carregada pelo jogo.
