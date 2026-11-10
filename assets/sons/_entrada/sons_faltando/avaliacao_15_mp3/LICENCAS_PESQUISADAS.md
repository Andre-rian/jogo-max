# Pesquisa de origem e licenças — 2026-11-09

Foram examinados os Markdown, CSV, textos de licença e nomes de arquivos de
`assets/sons/`, a documentação em `docs/audio/` e o commit de entrada `9b73e1c`.
O commit contém somente os 15 MP3, já com nomes descritivos em português.
O quadro geral de créditos em `_entrada/CREDITOS_E_LICENCAS.md` não registra
esses arquivos. Os registros completos de `busca_2026_11_09/` pertencem a outro
lote de 66 candidatos; as licenças de `musicas/` pertencem aos respectivos pacotes.

Os MP3 não têm cabeçalho ID3 nem fluxo `Zone.Identifier` que indique o site de
download. Os hashes dos 15 originais foram preservados em
[originais_sha256.json](pesquisa_licencas/originais_sha256.json).

## Fontes verificadas usadas no jogo

| Destino | Obra / autor | Fonte e licença | Edição final |
|---|---|---|---|
| Rugido do Boss | Low Monster Roar — Robson220pl | [Freesound 497056](https://freesound.org/people/Robson220pl/sounds/497056/), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | 3,20 s, fade de 300 ms, -3 dBFS |
| Morte do Globin | Goblin Death.wav — spookymodem | [Freesound 249813](https://freesound.org/people/spookymodem/sounds/249813/), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | limite de 1,30 s; silêncio aparado resulta em 0,686 s, -3 dBFS |

Foram baixadas as **prévias públicas HQ**, não os WAV originais autenticados.
As duas páginas indicam CC0. As cópias utilizadas e os hashes estão em
`pesquisa_licencas/`; os créditos finais estão em `assets/sons/_config/LICENCAS.csv`.
Os WAV finais são mono, PCM 16-bit, 44,1 kHz.

Os MP3 antigos e as prévias baixadas não têm hashes iguais. A comparação dos
espectrogramas indicou correlação de 0,968 para o Boss e 0,979 para o Goblin,
após alinhar o atraso de codificação. Isso é evidência de semelhança, não prova
de identidade binária nem de procedência. **A promoção usa as cópias recém-obtidas
das fontes verificadas**, sem atribuir retroativamente CC0 aos arquivos antigos.
Os JSON de comparação registram método, durações e resultados.

## Pistas encontradas, ainda sem vinculação comprovada aos MP3

As licenças nesta tabela descrevem a página consultada, não comprovam a licença
do arquivo local. Nome, duração ou descrição semelhantes não bastam para promover.
O download direto do Pixabay retornou HTTP 403; não foi possível comparar os bytes.

| Arquivo local | Página candidata | Autor informado | Licença da página |
|---|---|---|---|
| `espada_escudo_hit_01.mp3` | [Sword Slash With Metal Shield Impact](https://pixabay.com/sound-effects/film-special-effects-sword-slash-with-metal-shield-impact-185433/) | DavidDumaisAudio | Pixabay Content License |
| `flying_eye_asas_01.mp3` | [flapping](https://pixabay.com/sound-effects/nature-flapping-39306/) | snail-legs (Freesound) | Pixabay Content License |
| `flying_eye_ataque_bite_01.mp3` | [monster bite](https://pixabay.com/sound-effects/horror-monster-bite-44538/) | soundmast123 (Freesound) | Pixabay Content License |
| `metal_soco_hit_01.mp3` | [Metal Punch](https://pixabay.com/sound-effects/film-special-effects-metal-punch-142334/) | Universfield | Pixabay Content License |
| `armas_espada_longa_swing_03.mp3` | [Sword Slash and Swing](https://pixabay.com/sound-effects/film-special-effects-sword-slash-and-swing-185432/) | DavidDumaisAudio | Pixabay Content License |

O [monster bite 571967 no Freesound](https://freesound.org/people/soundmast123/sounds/571967/)
tem duração divergente nas páginas consultadas; a correspondência não foi confirmada.
Não foi usado para liberar o arquivo local.

Para os demais arquivos não foi encontrada uma fonte individual suficientemente
identificável. O [resumo oficial do Pixabay](https://pixabay.com/service/license-summary/)
permite edição e uso, mas restringe redistribuição isolada do conteúdo; não é CC0
nem MIT. Uma página candidata não autoriza trocar a licença do arquivo local.

## Edição e promoção

As escolhas artísticas de `OBSERVACOES.md` foram mantidas. Há 13 WAV para escuta
em `previas_editadas/`, com medidas e destinos em [PREVIAS.csv](PREVIAS.csv).
São prévias dos MP3 antigos, incluindo 03 e 07 para comparação; não são carregadas
pelo jogo e não ganham licença por terem sido editadas.

- `tools/promocao_lote4.csv`: duas fontes verificadas, já promovidas.
- `tools/promocao_lote4_pendentes.csv`: onze aprovados, com cortes/fades/pico
  definidos e licença `PENDENTE`; o script recusa todos enquanto faltar comprovação.
- 09 (ataque do Skeleton) foi rejeitado por impacto embutido e removido na limpeza de 2026-11-10. O hash histórico continua em `originais_sha256.json`; recuperação em `docs/audio/auditoria_geral/LIMPEZA_ENTRADA.csv`.
- 15 (disparo mágico) continua reservado em `_uteis/magico/`.

Para liberar uma linha pendente, confirmar a correspondência com a fonte exata,
preencher licença, autor, URL e atribuição quando exigida, executar `--dry-run`
e só então promover. Usar uma alternativa licenciada exige registrar essa nova
origem; não alterar a procedência do MP3 antigo.
