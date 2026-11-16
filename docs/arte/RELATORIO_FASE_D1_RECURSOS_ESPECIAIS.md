# Relatório — Fase D.1: refinamento dos recursos especiais

Data: 15/11/2026
Branch: `sprites`
Status: **M042 integrada ao ID 5**; M025, M023 e Eco aprovados; M052 descartada.
Escopo: refinar as propostas de Umbrita, Abissita e Nyxita, criar um Eco Profano
original e simular os ícones no inventário. A integração funcional ficou limitada
à Umbrita no ID 5.

## 1. Decisões aplicadas

- **Umbrita:** M042 aprovada e integrada ao ID 5; M052 foi refinada na mesma
  rodada para comparação direta no inventário real.
- **Abissita:** M025 recebeu a paleta azul-petróleo/ciano.
- **Nyxita:** M023 recebeu a paleta violeta quase preto com acentos magenta.
- **Eco Profano:** proposta original em pixel art 24×24, sem usar ou copiar os
  assets do lygame.

Aprovação final registrada: **M042** para Umbrita, **M025** para Abissita,
**M023** para Nyxita e **Eco Profano original**. **M052 foi descartada** e fica
arquivada como alternativa visual.

## 2. Método dos minerais

As quatro silhuetas foram extraídas da spritesheet do Beast em 24×24, sem
alteração de forma. A comparação de alpha confirmou **0 pixels de diferença**
entre original e refinado para M042, M052, M025 e M023.

A intervenção foi um remapeamento manual de paleta, preservando contorno,
facetas e distribuição de luz. As rampas principais ficaram assim:

| Recurso | Contorno | Realce | Médio | Sombra |
|---|---|---|---|---|
| Umbrita M042 | `#ead8cc` | `#b08a78` | `#8a6266` | `#3a2430` / `#241820` |
| Umbrita M052 | `#ead8d0` | `#b08a80` | `#8a626a` | `#422838` / `#2c1c2a` |
| Abissita M025 | `#c8f0ee` | `#9ff8ff` / `#55d0e0` | `#2b93ac` | `#0b3760` / `#061722` |
| Nyxita M023 | `#d8c8e6` | `#e8a1f2` / `#c052e8` | `#5a1a8c` | `#28103f` / `#160b2a` |

Leitura de cor média:

- M042: hue ~1°, umber quente e malva.
- M052: hue ~342°, malva mais frio; mesma silhueta de geodo.
- M025: hue ~192°, azul-petróleo com ciano.
- M023: hue ~280°, violeta com magenta.

## 3. Eco Profano original

O Eco foi desenhado do zero em 24×24, com:

- silhueta assimétrica de chama/essência, com corpo vazado;
- cauda curvada para a esquerda;
- núcleo de losango separado do corpo, em ciano e branco-azulado;
- três fragmentos de eco no canto superior esquerdo e três no inferior direito;
- corpo em azul-violeta, contorno frio no topo/direita e violeta na base/esquerda.

O desenho tem **196 pixels opacos**: 177 no corpo, 13 no núcleo e 6 nos
fragmentos. A solução evita deliberadamente o formato sólido do `SoulFragment`
do lygame; nenhum pixel do lygame foi usado.

Paleta: `#d8ffff`, `#7fe7e7`, `#9fe8f0`, `#c0b0f0`, `#7a63c8`, `#5744a0`,
`#3d2f78`, `#2a2058`, `#19123a`, `#b894ff`.

## 4. Comparação no inventário real

As capturas de M042 e M052 usam o **inventário real**, aba Materiais, com o item
ID 5 (Umbrita) e quantidade 1. A troca de sprite foi feita apenas em memória,
substituindo o caminho no mapa de sprites antes da renderização; nenhum arquivo
de `itens.json`, código do inventário ou sprite aprovado foi editado.

As duas capturas são idênticas fora do ícone. A diferença entre elas ficou
limitada à área `(206,76)–(253,105)`, com 1.288 pixels alterados, todos dentro do
slot do ícone. Após a integração, uma nova captura usando o mapa real do ID 5 foi
comparada à prévia de M042 e ficou **idêntica (0 pixels de diferença)**.

- M042: umber quente, mais “pedra”; **aprovada**.
- M052: malva frio, mais “geodo”; **descartada**, mantida apenas como
  alternativa documentada.
- Ambas mantêm a silhueta original e o contorno claro.

## 5. Legibilidade sobre o grafite LY005

Fundo de teste: `#1e1f25` (interior do painel LY005). Métricas calculadas sobre
todos os pixels opacos do sprite:

| Sprite | Contraste mediano | Máximo | Pixels ≥ 2:1 | Pixels ≥ 3:1 |
|---|---:|---:|---:|---:|
| Umbrita M042 | 1,90:1 | 11,89:1 | 40% | 37% |
| Umbrita M052 | 1,96:1 | 11,92:1 | 40% | 40% |
| Abissita M025 | 4,59:1 | 15,79:1 | 64% | 60% |
| Nyxita M023 | 1,53:1 | 13,84:1 | 43% | 37% |
| Eco Profano | 3,48:1 | 15,39:1 | 69% | 51% |

Leitura:

- **M025** é o mais legível: grande área de ciano e azul médio.
- **M042/M052** dependem do contorno ósseo e dos realces quentes; a silhueta
  permanece clara, mas o interior é escuro por intenção.
- **M023** é o mais escuro; o contorno lilás e a ponta magenta sustentam a
  leitura. Se a avaliação preferir mais presença, uma próxima rodada pode
  clarear levemente os médios sem mudar a forma.
- **Eco** tem boa cobertura de contraste graças ao núcleo ciano e ao contorno
  frio; o corpo vazado ajuda a separar a silhueta do fundo.

## 6. Arquivos gerados

### Versionáveis

| Arquivo | Conteúdo | Dimensão | Licença |
|---|---|---|---|
| `docs/arte/propostas_recursos/recurso_m042_d1.png` | Umbrita M042 refinada (integrada ao ID 5) | 24×24 | Beast CC0 |
| `docs/arte/propostas_recursos/recurso_m052_d1.png` | Umbrita M052 refinada (alternativa descartada) | 24×24 | Beast CC0 |
| `docs/arte/propostas_recursos/recurso_m025_d1.png` | Abissita M025 refinada | 24×24 | Beast CC0 |
| `docs/arte/propostas_recursos/recurso_m023_d1.png` | Nyxita M023 refinada | 24×24 | Beast CC0 |
| `docs/arte/propostas_recursos/eco_profano_d1.png` | Eco Profano original | 24×24 | Original do projeto |
| `docs/arte/propostas_recursos/refinamentos_d1.png` | Folha comparativa com escalas, paletas e contraste | 1600×1120 | Beast CC0 + original |
| `docs/arte/propostas_recursos/slots_inventario_d1.png` | Simulação de slots 60×60 / ícone 48×48 | 1600×430 | Beast CC0 + original |

A Umbrita M042 foi copiada para `assets/sprites/itens/materiais/umbrita.png`
(24×24) e mapeada ao ID 5. As demais propostas continuam apenas em
`docs/arte/propostas_recursos/`.

### Locais, não versionáveis

| Arquivo | Conteúdo | Dimensão |
|---|---|---|
| `docs/arte/previews/recursos_d1_ly005_umbrita_m042.png` | Inventário real com M042 | 860×576 |
| `docs/arte/previews/recursos_d1_ly005_umbrita_m052.png` | Inventário real com M052 | 860×576 |
| `docs/arte/previews/recursos_d1_comparativo_ly005.png` | Prévia comparativa completa | 1600×1290 |

As capturas locais contêm o painel LY005 (lygame, redistribuição proibida) e são
cobertas por `docs/arte/previews/*ly005*.png` no `.gitignore`. As folhas
versionáveis não contêm pixels do lygame.

## 7. Validação

- Nenhum item, ID ou mecânica novo foi criado.
- `itens.json` e `core/inventario.py` não foram alterados.
- `ui/sprites_itens.py` recebeu apenas a entrada do ID 5 apontando para
  `materiais/umbrita.png`.
- Nenhum sprite aprovado foi sobrescrito.
- Nenhuma imagem original de pack foi modificada.
- Nenhum commit foi criado.
- `tests/test_inventario_sprites.py`: **11 passed**.
- Suíte completa: **170 passed**.
- `git diff --check`: OK.
- Dimensões, margens, alpha e área de diferença do inventário validadas por
  script; nenhuma prancha tem conteúdo encostando na borda.
- A captura do inventário com o ID 5 real ficou idêntica à prévia aprovada.

## 8. Decisão registrada e próximos passos

Aprovação em 15/11/2026:

1. Umbrita: **M042** aprovada e integrada ao ID 5; M052 descartada.
2. Abissita: **M025** aprovada e ainda não integrada.
3. Nyxita: **M023** aprovada e ainda não integrada.
4. Eco Profano: **proposta original** aprovada e ainda não integrada.

A única integração funcional desta etapa foi a Umbrita:

- `recurso_m042_d1.png` foi copiado para
  `assets/sprites/itens/materiais/umbrita.png`;
- `ui/sprites_itens.py` ganhou a entrada `5` no mapa;
- nenhum item ou ID novo foi criado;
- a captura real ficou idêntica à prévia aprovada.

Pendências fora do escopo D.1:

- **Abissita, Nyxita e Eco:** não existem itens/IDs correspondentes em
  `itens.json`; a integração exigiria criar itens, IDs e possivelmente mecânicas.
- **M052:** permanece apenas como alternativa documentada, sem uso no jogo.
- Nenhum commit foi criado.
