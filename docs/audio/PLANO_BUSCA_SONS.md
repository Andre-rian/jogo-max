# Plano de busca dos sons remanescentes

> **Registro histórico anterior à revisão de 2026-11-10.** Para o estado atual,
> consultar [STATUS_SONS.md](STATUS_SONS.md) e
> [ARQUIVOS.csv](auditoria_geral/ARQUIVOS.csv).

> Preparado em 2026-11-09. Atualização: usuário deu OK para pesquisa/download, com todos os candidatos restritos a `sons_faltando`.
> Primeiro lote concluído: 66 candidatos em `assets/sons/_entrada/sons_faltando/busca_2026_11_09/`; nenhum áudio promovido e nenhum código alterado.

O [guia do lote](../../assets/sons/_entrada/sons_faltando/busca_2026_11_09/LEIA-ME.md) e o [status atualizado](STATUS_SONS.md) registram o resultado. Os 55 destinos têm sugestões: 18 com candidato de uso mais direto e 37 com bases que exigem edição/adaptação. Todos aguardam avaliação por escuta.

## Base conferida antes da busca

Profane Echo é um metroidvania em Python/Pygame, ambientado em calabouços de um castelo. A direção registrada em `RELATORIO_FEEDBACK_SONS.md` pede impactos físicos e orgânicos e uma identidade sombria. A segunda rodada pede preservar poção, espada, morte citada pelo usuário e escudo do Boss. Usar os sons já aprovados como referência de timbre e volume.

Conferência da árvore e do código:

| Item | Situação |
|---|---|
| Caminhos de `ESPECIFICACOES`, em `core/audio.py` | 37 de 37 presentes |
| Arquivos na árvore final `sfx/` | 162; presença não equivale a aprovação por escuta |
| Fila da seção 2 de `STATUS_SONS.md` | 55 destinos: P1 = 26, P2 = 15, P3 = 14 |
| `_entrada/sons_faltando/`, excluindo músicas | 15 efeitos já baixados |
| `_entrada/_fatias/` | 42 fatias em 8 pastas |
| `_entrada/_uteis/` | 16 fontes guardadas |
| Fontes de passos | 4 fontes anotadas para cortes alternativos; a pasta `5_mundo_movimento/passos_pedra/` contém 12 áudios ao todo |
| Música | 53 faixas em triagem e 4 na árvore final; sem sistema de reprodução integrado |
| Ambiência | 1 MP3 bruto de calabouço na árvore final; sem integração |

A lista detalhada de destinos continua em [STATUS_SONS.md](STATUS_SONS.md). A planilha [APROVACAO_SONS_ENTRADA.csv](APROVACAO_SONS_ENTRADA.csv) já organiza os candidatos locais; não confundir essa aprovação com a autorização para pesquisar novos arquivos.

## Ordem de execução após o OK

1. Revisar o mapeamento local e as anotações de escuta para retirar da busca o que já puder ser aproveitado. Manter os 15 efeitos baixados na fila de aprovação existente.
2. Pesquisar os materiais e impactos de P1, começando por fungo, etéreo, osso e carne. Os materiais cobrem vários inimigos pela cascata; depois procurar variações específicas dos inimigos.
3. Buscar os ataques e eventos do Boss e os projéteis de P2, identificando os que ainda dependem de integração.
4. Buscar movimento, mundo e ambiências de P3. Terra e metal ficam por último: todas as salas atuais usam pedra em `world/niveis.py`.
5. Apresentar cada lote com arquivos candidatos, destino, origem e pendências de corte ou integração. Atualizar o status conforme os resultados reais.

## Revisão local antes de baixar

São hipóteses de reaproveitamento, não novas aprovações:

| Pendência | Fontes locais a conferir |
|---|---|
| `osso/soco`, `osso/machado_guerra` e impactos do Skeleton/Boss | `_entrada/2_materiais/osso/` e `_entrada/_uteis/osso/`; o relatório antigo sugere `192146` para `osso/soco` |
| `carne/machado_guerra` e hits do Globin | `_entrada/2_materiais/carne/` e as fontes orgânicas de `_entrada/1_combate_player/` |
| Impactos de fungo | `395330...fist-clenching-2...ogg`, anotado como possível cogumelo derretendo; confirmar se serve para hit ou apenas outro efeito |
| Ataque normal do Boss | `_entrada/_fatias/impactos_geral.../` e `_entrada/_uteis/impactos/`; já mapeados no status |
| Disparo mágico | `projeteis_magico_disparo_01.mp3`; escolher entre Boss, esporo ou olho antes de excluir qualquer destino da busca |

Arquivos antigos podem duplicar fontes já usadas ou ter sido rejeitados. Conferir os registros e a escuta antes de reutilizar. As pastas vazias de fungo/soco, etereo/soco e osso/soco continuam pendentes apesar de menções antigas a promoções.

## Lotes e termos de pesquisa

Os termos abaixo orientaram a pesquisa. As fontes efetivamente usadas estão em `busca_2026_11_09/FONTES.csv`.

| Lote | Destinos da lista | Direção e termos em inglês |
|---|---|---|
| P1 — arma genérica | `player/armas/_default` | Deslocamento de ar curto: `weapon whoosh`, `melee swing`; evitar impacto misturado ao swing |
| P1 — osso e carne | `osso/{machado_guerra,soco}`, `carne/machado_guerra` | Seco e quebradiço para osso; corpo/tecido para carne: `bone crunch`, `bone crack impact`, `heavy flesh hit`, `body impact` |
| P1 — fungo | `fungo/{_default,espada_longa,machado_guerra,soco}` | Úmido e fibroso: `wet squish impact`, `mushroom hit`, `slime impact`; golpes isolados |
| P1 — etéreo | `etereo/{_default,espada_longa,machado_guerra,soco}` | Espectral e curto: `ghost hit`, `ethereal impact`, `dark magic hit`; evitar estética de nave/bipes |
| P1 — inimigos | Hits listados de Skeleton, Globin, Mushroom e Flying Eye | `skeleton damage`, `goblin hurt`, `creature pain short`, `slime hurt`, `flying monster hurt`; coerência com os materiais |
| P1 — Boss e reserva genérica | Hits de espada/machado/quebra-guarda do Carrasco e `_default/hit/_default` | `armored skeleton hit`, `heavy bone impact`, `guard break`, `shield stagger`; distinguir dano de bloqueio |
| P2 — Mushroom | `mushroom/ataque`, `mushroom/esporo` | `spore release`, `organic spit`, `fungal burst`; separar ataque da criatura e disparo do projétil |
| P2 — Boss | `boss_carrasco/{entrada,morte}` | `monster entrance`, `giant creature death`, `heavy armor collapse`; presença grave sem cauda excessiva |
| P2 — bomba | `bomba/{disparo,voo}` | `throw whoosh`, `grenade throw`, `object flyby`; impacto já possui som e candidato extra |
| P2 — esporo, olho e Boss | `projeteis/{esporo,olho,boss}/{disparo,voo,impacto}` | `organic projectile`, `magic orb launch`, `energy flyby`, `dark magic impact`; famílias distintas e voo discreto |
| P3 — movimento | Pulo, passos e pousos em terra/metal/genéricos | `jump effort short`, `boots dirt footsteps`, `armored footsteps metal`, `heavy landing dirt`, `metal landing` |
| P3 — mundo e inimigos | Tochas, mecanismos, Eco Profano e passos de Skeleton/Mushroom | `torch fire loop`, `stone mechanism`, `lever pull`, `soul pickup`, `skeleton footsteps`, `wet creature footsteps` |
| P3 — ambiência | `ambiencia/{sala_descanso,arena_boss}` | `quiet campfire ambience loop`, `dark dungeon drone loop`, `boss arena ambience`; complementar a ambiência existente |

## Registro dos candidatos

Após o OK, iniciar por Freesound e OpenGameArt, procurando fontes originais com licença explícita. Preferir CC0; considerar CC BY com a atribuição registrada. Conferir os termos na página de cada arquivo no momento da pesquisa. Os nomes de sites e as licenças históricas dos relatórios não substituem essa conferência.

Baixar os novos candidatos em `assets/sons/_entrada/sons_faltando/`, em subpastas por categoria e destino. Nesta rodada, os arquivos foram agrupados em `busca_2026_11_09/`, com o registro em `CANDIDATOS.csv` no próprio lote (inclui campos adicionais de integridade e escuta):

```csv
id;prioridade;destino;arquivo_local;titulo;autor;url_fonte;licenca;atribuicao;duracao_s;tratamento;depende_codigo;status
```

Começar com 1–3 candidatos por família sonora. Um pack pode atender vários destinos; não duplicar artificialmente um mesmo efeito só para preencher pastas. Usar nomes ASCII em snake_case com contexto completo e numeração.

Critérios de seleção: golpe individual identificável, pouco silêncio, sem voz/música de fundo indesejada, cauda compatível com a ação e timbre coerente com o jogo. SFX finais: WAV PCM 16-bit, 44,1 kHz, mono, pico alvo de -3 dBFS; em geral até 1,5 s para ações curtas. Música/ambiência: OGG com loop adequado. A duração de entrada pode ser maior se houver um corte claramente aproveitável.

## Dependências para os áudios tocarem

O `AudioManager` indexa arquivos por pasta ao iniciar e escolhe as variações sem cadastro individual. Porém, uma pasta indexada só toca quando algum evento a consulta:

| Grupo | Situação atual |
|---|---|
| Hits, swings, ataques comuns, mortes, passos e pousos | Métodos e chamadas já existem para os destinos consultados pela cascata |
| `boss_carrasco/ataque/normal/` | Não é lida por `play_enemy_attack`, que só consulta arquivos diretamente em `ataque/`; as fatias não tocarão apenas por serem promovidas para `normal/` |
| `boss_carrasco/hit/quebra_guarda/` | Sem evento de áudio próprio para quebra de guarda |
| `inimigos/_default/hit/_default/` | Não é fallback compartilhado: só entra na cascata com ID de inimigo `_default` |
| Entrada/rugido do Boss e asas do Flying Eye | Sem gatilhos próprios |
| `mushroom/esporo/` | Sem leitura específica dessa pasta |
| Projéteis | `play_projectile` existe, mas não é chamado; a bomba usa `bomb_explosion` no impacto |
| Pulo | Sem gatilho de áudio |
| Tochas e mecanismos | Sem integração de áudio |
| `interacao/eco_profano/` | A coleta usa a chave fixa `eco_pickup`, apontando para `interacao/itens/` |
| Música e ambiência | Arquivos indexados, mas sem sistema de reprodução e troca por cena |

A pesquisa/download e a integração são etapas distintas. O OK para ir atrás dos áudios inicia a pesquisa e o armazenamento em triagem. Cortes, promoção e mudanças de código devem seguir a aprovação dos candidatos e o escopo combinado com o usuário.

## Próxima etapa

Avaliar os arquivos seguindo `busca_2026_11_09/ESCUTA.md` e registrar escolhas em `CANDIDATOS.csv`. Priorizar novas buscas nos destinos cujas bases não agradarem, principalmente timbre etéreo, diferenciação por arma, pouso metálico e voo dos projéteis. Cortes e promoção dependem de nova orientação; a instrução atual é manter tudo em triagem. Música nova, troca de sala e vitória do Boss continuam fora da busca principal.
