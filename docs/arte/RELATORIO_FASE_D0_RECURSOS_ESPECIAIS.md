# Relatório — Fase D.0: curadoria dos recursos especiais

Data: 15/11/2026
Branch: `sprites`
Status: curadoria concluída; **aguardando escolha visual do responsável**.
Escopo: propor sprites para Umbrita, Abissita, Nyxita e Eco Profano sem integrar
nada ao jogo, sem alterar o inventário e sem criar itens, IDs ou sistemas novos.

## 1. Método

- Revista a spritesheet `beast_crafting_materials/resources_outlined.png`
  (264×264, grade 11×11, células de 24×24, 105 células ocupadas).
- Os IDs `M001`–`M105` seguem a ordem de leitura do catálogo existente; as
  coordenadas `(gx,gy)` identificam a célula original.
- A triagem priorizou silhueta de mineral (lasca, geodo, gema ou bloco),
  contraste em 24×24 e possibilidade de diferenciar os três recursos por cor e
  forma, sem depender de detalhe fino.
- Para o Eco Profano foram verificados os packs de itens já recebidos. Não há
  candidato CC0 semanticamente adequado; os melhores achados estão no lygame
  (licença restrita, uso local).
- Nenhum arquivo original foi alterado; nenhuma imagem foi promovida para
  `assets/sprites/itens/`.

## 2. Candidatos — minerais

### Umbrita (+1 a +4)

| ID | Célula | Leitura de forma | Paleta dominante | Observação |
|---|---|---|---|---|
| **M042** | (3,4) | rocha em camadas, larga e irregular | cinza-azulado, marrom e magenta | **Principal:** já tem tom terroso; boa base para umber/roxo suave |
| M052 | (3,5) | geodo largo com cavidade escura | cinza, magenta e azul-escuro | Alternativa mais “cristalina”; a cavidade ajuda a diferenciar de Abissita |
| M013 | (2,1) | massa escura arredondada | azul-escuro, cinza e preto | Alternativa compacta; lembra pedra polida/obsidiana |

### Abissita (+5 a +8)

| ID | Célula | Leitura de forma | Paleta dominante | Observação |
|---|---|---|---|---|
| **M025** | (5,2) | lasca diagonal, pontiaguda | azul profundo, ciano e preto | **Principal:** silhueta mais distinta das outras duas |
| M026 | (6,2) | gema oval vertical | azul-escuro e ciano | Alternativa limpa; perde a leitura de “lasca” |
| M083 | (6,8) | bloco cristalino largo | azul-acinzentado, violeta e preto | Alternativa robusta; precisa de cuidado para não competir com Nyxita |

### Nyxita (+9)

| ID | Célula | Leitura de forma | Paleta dominante | Observação |
|---|---|---|---|---|
| **M023** | (3,2) | cristal vertical, pontiagudo | violeta, magenta e preto | **Principal:** formato mais “cristal” e leitura clara em 24×24 |
| M015 | (4,1) | gema oval facetada | violeta, azul e branco | Alternativa lapidada; mais “gema” que “cristal bruto” |
| M048 | (9,4) | lasca pequena | violeta, cinza e azul | Alternativa compacta; pode ficar fraca no grid |

## 3. Avaliação de adaptação

**Pequenas adaptações de paleta e detalhe são suficientes**, desde que a forma
principal de cada recurso seja mantida e a paleta seja claramente separada:

- **Umbrita:** M042 com rampa umber/malva, sombra quase preta e brilho quente
  discreto. Ajustar 1–2 pixels da camada superior para sugerir veio de minério.
- **Abissita:** M025 com azul-petróleo profundo, borda ciano e núcleo mais claro.
  Reforçar as facetas diagonais; não usar magenta.
- **Nyxita:** M023 com violeta quase preto, borda magenta e highlight lilás.
  Preservar a ponta vertical; evitar azul dominante.

A diferenciação final deve combinar **silhueta + cor**, não apenas cor:

| Recurso | Silhueta desejada | Cor dominante | Detalhe de leitura |
|---|---|---|---|
| Umbrita | massa/geodo irregular | umber, malva, cinza quente | veio interno e cavidade |
| Abissita | lasca diagonal | azul-petróleo/ciano | facetas e borda luminosa |
| Nyxita | cristal vertical | violeta/negro | ponta e reflexo magenta |

## 4. Estudo de paleta no catálogo

O catálogo inclui uma linha de estudo com o candidato principal de cada mineral:
original ao lado de uma rampa automática por luminância, em 24×24 e 48×48.
As rampas usadas foram:

- Umbrita: `#100c12`, `#261c22`, `#422c34`, `#62444c`, `#8c6868`, `#c4aa9e`.
- Abissita: `#040e1a`, `#092032`, `#103a52`, `#1e607a`, `#449eb0`, `#9adee0`.
- Nyxita: `#07050f`, `#160d26`, `#2d1844`, `#4c286a`, `#7a4896`, `#c690e6`.

Essas imagens são **estudos de prévia**, não sprites finais. O remapeamento
automático preserva a forma e serve para avaliar se a paleta basta; ajustes
manuais de contorno, facetas e brilho ainda são necessários.

## 5. Eco Profano

Não foi encontrado ícone CC0 adequado para “essência ligada às memórias dos
seres”. Os ícones do Beast são materiais/objetos; os ícones do Quintino são
genéricos e não têm leitura semântica de alma/eco. Os melhores candidatos estão
no lygame:

| Candidato | Arquivo original | Leitura | Licença |
|---|---|---|---|
| **Principal** | `FunctionIcons/Items&Resources/SoulFragment.png` | fragmento espectral violeta com núcleo ciano | lygame: uso no jogo; **não redistribuir** |
| Alternativa | `FunctionIcons/Items&Resources/SealedOrb.png` | orbe selado, violeta/âmbar | lygame: uso no jogo; **não redistribuir** |
| Alternativa | `FunctionIcons/Items&Resources/SpiritPowder.png` | pó espiritual violeta | lygame: uso no jogo; **não redistribuir** |

`SoulFragment.png` é o mais próximo do conceito e o mais legível em 24×24, mas
tem 32×32 nativo. Se for escolhido, a integração futura deve testar o downscale
para 24×24 ou redesenhar a silhueta nessa grade para não perder o núcleo ciano.

Como o lygame não pode ser versionado, a adoção exigiria uma destas rotas:

1. manter o arquivo apenas localmente, com fallback para um ícone original; ou
2. criar um ícone original inspirado na direção visual, sem copiar o asset.

**Direção original de fallback (sem criar o sprite definitivo agora):** silhueta
assimétrica de chama/fragmento, núcleo violeta escuro, borda ciano-espectral,
2–3 filamentos laterais e brilho interno de 1–2 px. Sem rosto, caveira ou símbolo
explícito. Cores de referência: `#2a1738`, `#684e71`, `#b1e5df`, `#e8f7f2`.

## 6. Escalas comparadas

- **24×24:** tamanho nativo dos minerais Beast e alvo dos ícones do inventário.
- **48×48:** escala usada no grid do inventário (`TAMANHO_NATIVO × ESCALA`).
- **26×26:** tamanho dos ícones equipados.
- **4×/3×:** ampliação apenas para inspeção visual.
- **Eco:** 32×32 nativo no lygame; o catálogo mostra 32, 24 (alvo), 48, 26 e 3×.

## 7. Licenças e versionamento

- **Beast Crafting Materials:** CC0; os candidatos minerais e o catálogo
  `recursos_especiais_minerais.png` podem ser versionados.
- **lygame:** uso permitido no jogo, redistribuição proibida; os candidatos do
  Eco e o catálogo combinado `recursos_especiais_fase_d0.png` são locais.
- O `.gitignore` foi atualizado para ignorar o catálogo combinado e futuros
  catálogos `recursos_especiais_eco*.png`.
- Nenhum arquivo original de pack foi modificado.

## 8. Arquivos gerados

- [`recursos_especiais_minerais.png`](catalogos/recursos_especiais_minerais.png)
  — somente Beast/CC0, 1600×1480, versionável.
- [`recursos_especiais_fase_d0.png`](catalogos/recursos_especiais_fase_d0.png)
  — catálogo completo com Eco/lygame, 1600×1894, local e ignorado pelo Git.
- [`CATALOGO_SPRITES.md`](catalogos/CATALOGO_SPRITES.md) — índice atualizado.

## 9. Pendências

1. Escolher o candidato de cada mineral (ou pedir mais opções).
2. Aprovar, rejeitar ou ajustar as rampas de paleta propostas.
3. Decidir a rota do Eco Profano: candidato local do lygame ou direção original.
4. Só depois integrar no inventário; a Umbrita ID 5 permanece intocada até a
   aprovação.
5. Nenhum commit foi criado.

## 10. Continuidade

A Fase D.1 refinou as escolhas indicadas nesta curadoria e substituiu os
candidatos locais do Eco por uma proposta original. As pendências 1–3 foram
resolvidas em 15/11/2026: M042 (Umbrita), M025 (Abissita), M023 (Nyxita) e Eco
original aprovados; M052 descartada. A Umbrita M042 foi integrada ao ID 5; os
demais continuam como propostas. Ver
[`RELATORIO_FASE_D1_RECURSOS_ESPECIAIS.md`](RELATORIO_FASE_D1_RECURSOS_ESPECIAIS.md).
