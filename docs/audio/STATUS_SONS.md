# Status dos sons — revisão de 2026-11-10

Relatório desta limpeza: [REVISAO_GERAL_2026_11_10.md](REVISAO_GERAL_2026_11_10.md).

Guia para continuar o trabalho: [GUIA_CONTINUACAO_AUDIO.md](GUIA_CONTINUACAO_AUDIO.md).

Base: árvore local de `assets/sons/`, código atual e registros de licença. Este
arquivo substitui a contagem anterior de 55 destinos vazios, que antecedia as
promoções dos lotes 1–3 já presentes no workspace.

## Resultado da revisão dos 15 MP3

- **2 destinos integrados com fontes CC0 verificadas:** rugido do Boss e morte do
  Globin. Foram utilizadas novas cópias das prévias HQ do Freesound; os MP3
  antigos permanecem preservados, sem licença presumida.
- **11 aprovados aguardam comprovação de origem/licença**, com prévias editadas
  e tabela de promoção preparada.
- **1 rejeitado e removido na limpeza:** ataque do Skeleton com impacto embutido; avaliação e hash histórico preservados.
- **1 reservado para o futuro:** disparo mágico em `_uteis/magico/`.
- Há **13 prévias editadas** dos originais para comparação. O impacto em carne
  usa pico de -12 dBFS; os demais, -3 dBFS. Silêncios foram aparados, portanto
  alguns arquivos ficaram menores que os limites de corte pedidos.

Veja [observações e decisões](../../assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/OBSERVACOES.md),
[pesquisa de licenças](../../assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/LICENCAS_PESQUISADAS.md)
e [prévias/durações](../../assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/PREVIAS.csv).

## Código

Implementado nesta revisão:

- Rugido do Boss uma vez ao detectar o jogador.
- Gatilho de asas do Flying Eye com intervalo de 144 ticks, volume baixo e
  supressão de novos disparos durante morte, hit, knockback e fora do alcance.
  **Ainda silencioso:** o arquivo de asas não foi promovido por falta de fonte.
- Ataques consultam `ataque/<tipo>/` antes de `ataque/` e do fallback.
  Isso habilita `normal`, `varrido` e `projetil` do Boss quando houver arquivos.
- Promoção recusa licença vazia, `LIVRE`, `VERIFICAR` e `PENDENTE`;
  exige autor/URL e atribuição para CC BY. Aceita `pico_db` por arquivo e
  preserva o delimitador do CSV ao marcar linhas concluídas.

Já estavam implementados no workspace: pulo do jogador, entrada/quebra de
guarda do Boss, esporo do Mushroom, eventos de projéteis, Eco Profano,
mecanismos, tochas e disparo de ambiência na entrada da sala.

A revisão geral adicionou loops persistentes de ambiência/tochas e reprodução
das quatro músicas por contexto, com volumes separados. Corrigiu gatilhos
duplicados, cooldowns de projéteis, fallbacks e o silêncio inicial da espada.
Nesta rodada também foram habilitadas as 13 variações de UI e a variação de
abrir porta já existentes, mantendo cada ação separada. A mixagem por escuta
continua pendente; veja o guia de continuação.

## Inventário atual

- **460 áudios ao todo; 212 em `_entrada`**, após retirar 76 sobras (313,32 MiB).
- Recuperados 222 ponteiros LFS; todos os arquivos restantes decodificam.
- Preservados os 17 áudios em `_uteis` e todas as reservas anotadas.
- 8 grupos de duplicatas finais entre contextos diferentes; nenhum dentro da mesma pasta.

- **248 arquivos** em `sfx/`, `ambiencia/` e `musica/`.
- Os **37 arquivos de ESPECIFICACOES** existem.
- **11 pastas finais sem áudio direto:**

| Pasta sob `sfx/` | Situação |
|---|---|
| `player/armas/machado_guerra/` | Prévia pronta; fonte pendente |
| `materiais/metal/soco/` | Prévia pronta; fonte pendente |
| `inimigos/flying_eye/asas/` | Prévia e gatilho prontos; fonte pendente |
| `inimigos/flying_eye/ataque/` | Prévia pronta; fonte pendente |
| `inimigos/flying_eye/morte/` | Prévia pronta; fonte pendente |
| `inimigos/flying_eye/passos/` | Opcional; Flying Eye tem `TEM_PASSOS = False` |
| `inimigos/skeleton/ataque/` | Candidato rejeitado; usa fallback |
| `inimigos/boss_carrasco/ataque/normal/` | Variante sem arquivo; usa fallback |
| `inimigos/boss_carrasco/ataque/varrido/` | Variante sem arquivo; usa fallback |
| `inimigos/boss_carrasco/ataque/projetil/` | Variante sem arquivo; usa fallback |
| `inimigos/boss_carrasco/hit/_default/` | Fallback local opcional; demais hits existem |

## Licenças além deste lote

A auditoria dos arquivos finais encontrou **42 sem registro** em
`LICENCAS.csv` e **116 com o rótulo genérico LIVRE**. Esse rótulo não identifica
a licença aplicável. A relação por arquivo, com origem/autor/URL existentes,
está em [AUDITORIA_LICENCAS.csv](AUDITORIA_LICENCAS.csv). Não foram inventados
créditos nem removidos os áudios preexistentes.

Os créditos documentados do lote de 66 candidatos e dos pacotes de música
continuam em suas pastas. Eles não comprovam a licença dos 15 MP3 renomeados.

## Validação

A auditoria atual decodificou os **460 arquivos sem erro**; as 37 especificações
estáticas existem. **159 testes passaram** e `git lfs fsck` passou. Os hashes dos 248 áudios finais e dos
17 áudios `_uteis` permaneceram iguais. A suíte inclui os testes anteriores e
regressões de variações de UI/interação; resultado registrado no relatório da
revisão. Escuta em gameplay permanece necessária.
