# Relatorio Fase H - Auditoria Sonora

## Escopo e metodo
- Base de evidencia: `_audio_files_measured.json` (456 arquivos medidos), `_audio_calls.json` (177 chamadas registradas) e `docs/audio/ui_files_measured.csv` / `docs/audio/ui_calls.csv`.
- Medidas consideradas: duracao, pico (`peak_dbfs`) e RMS (`rms_dbfs`) por arquivo; eventos/chamadas e categorias por runtime (`core/audio.py`, `assets/sons/_config/audio.json`).
- Validacao de codigo: `python -m py_compile ...` e `python -m pytest -q --tb=short` apos correcoes; `git diff --check` sem problemas.
- Sem `git add/commit/push`; sem alteracao em saves, combate, mapas, Ecofocos, `calabouco_2.tmx`, HUD G.1/prompt E, ou assets restritos.

## Resumo quantitativo
| Metrica | Valor |
|---|---:|
| total_files | 456 |
| total_calls | 177 |
| ui_calls | 0 |
| dup_groups | 10 |
| dup_files | 22 |
| ui_problems | 14 |

## Volumes/categorias (base atual)
| Camada | Valor | Fonte |
|---|---:|---|
| master | 0.8 | `assets/sons/_config/audio.json` |
| sfx | 1.0 | `assets/sons/_config/audio.json` |
| categoria combat | 0.8 | `assets/sons/_config/audio.json` |
| categoria player | 0.9 | `assets/sons/_config/audio.json` |
| categoria interaction | 0.7 | `assets/sons/_config/audio.json` |
| categoria ui | 0.7 | `assets/sons/_config/audio.json` |
| categoria music | 0.35 | `assets/sons/_config/audio.json` |
| categoria ambience | 0.4 | `assets/sons/_config/audio.json` |
| Preferencias usuario | 0-100% por geral/musica/efeitos/interface/ambiencia | `configuracoes_usuario.json` via `core/preferencias.py` + `core/audio.py` |

## Problema definitivo de hover/navegacao (antes/depois)
| Item | Antes | Depois | Evidencia |
|---|---|---|---|
| Hover inventario/menu/pausa | `ui_move` tocava variante aleatoria da pasta UI; `navegar_02.wav` (1.0s, pico -6.0005 dBFS, RMS -29.3242) podia ser selecionado e soar alto/longo em hover | UI usa arquivo canonico por evento; fallback deterministico apenas se canonico invalido; sem rotacao aleatoria em UI | `core/audio.py` (`play_sfx`), `tests/test_audio_auditoria.py` |
| Repeticao imediata UI | Variantes alternavam | Mesma acao UI reproduz som canonico estavel; cooldown/instancias continuam | `tests/test_audio_auditoria.py::test_ui_usa_arquivo_canonico_sem_variacao_aleatoria` |
| Canonico UI invalido | Podia cair em selecao por prefixo/variante | Se canonico invalido, nao substitui por outro evento/prefixo; registra falha e nao toca | `tests/test_audio_auditoria.py::test_ui_canonico_invalido_nao_substitui_outro_evento` |

## Variantes UI com desbalanceamento medido
Criterios de sinalizacao: pico > -4.0 dBFS, duracao > 1.0s, ou RMS > -16.0 dBFS.
| Arquivo | Duracao (s) | Pico (dBFS) | RMS (dBFS) | Problema | Acao |
|---|---:|---:|---:|---|---|
| assets/sons/sfx/ui/inicio/inicio_01.wav | 2.9971 | -3.0004 | -21.8899 | pico alto; longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_07.wav | 1.5000 | -3.0004 | -19.0261 | pico alto; longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_08.wav | 1.5000 | -3.0004 | -17.2327 | pico alto; longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_09.wav | 1.5000 | -3.0004 | -14.1245 | pico alto; longo; RMS alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_06.wav | 1.1814 | -3.0004 | -20.7876 | pico alto; longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/erro/erro_04.wav | 1.1521 | -3.0004 | -17.7750 | pico alto; longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_03.wav | 0.8234 | -3.0004 | -20.8824 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_04.wav | 0.7973 | -3.0004 | -17.5597 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/erro/erro_02.wav | 0.6289 | -3.0004 | -21.6328 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_02.wav | 0.6089 | -3.0004 | -18.9044 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/pausa/pausa_abrir_02.wav | 0.6000 | -3.0004 | -17.0863 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/confirmar/confirmar_05.wav | 0.5342 | -3.0004 | -18.1385 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/erro/erro_03.wav | 0.4144 | -3.0004 | -21.9258 | pico alto | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |
| assets/sons/sfx/ui/salvar/salvar_01.wav | 1.2000 | -6.3535 | -23.3791 | longo | Mitigado no runtime UI por selecao canonica; variante mantida em disco para auditoria/revisao manual. |

## Duplicatas exatas por assinatura (bytes/duracao/pico/RMS)
| Grupo | Arquivo | Bytes | Duracao (s) | Pico | RMS | Observacao |
|---:|---|---:|---:|---:|---:|---|
| 1 | assets/sons/_entrada/_uteis/efeitos/819290__johnmode__mystical-female-choir-swell-01(nao serve como musica ambiente, mas sim um efeito sonoro, pode ser util no futuro).wav | 2178464 | 7.5635 |  |  | Arquivo em _entrada; nao promovido/alterado automaticamente. |
| 1 | assets/sons/_entrada/_uteis/efeitos/819291__johnmode__mystical-female-choir-swell-02(nao serve como musica ambiente, mas sim um efeito sonoro, pode ser util no futuro.wav | 2178464 | 7.5635 |  |  | Arquivo em _entrada; nao promovido/alterado automaticamente. |
| 2 | assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/globin_morte_01.mp3 | 34560 |  |  |  | Arquivo em _entrada; nao promovido/alterado automaticamente. |
| 2 | assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/mushroom_default_hit_01.mp3 | 34560 |  |  |  | Arquivo em _entrada; nao promovido/alterado automaticamente. |
| 3 | assets/sons/sfx/inimigos/boss_carrasco/hit/espada_longa/boss_carrasco_espada_longa_hit_01.wav | 51884 | 0.5878 | -3.0004 | -22.5271 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 3 | assets/sons/sfx/inimigos/skeleton/hit/espada_longa/skeleton_espada_longa_hit_02.wav | 51884 | 0.5878 | -3.0004 | -22.5271 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 3 | assets/sons/sfx/materiais/osso/machado_guerra/osso_machado_guerra_hit_01.wav | 51884 | 0.5878 | -3.0004 | -22.5271 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 4 | assets/sons/sfx/inimigos/boss_carrasco/hit/machado_guerra/boss_carrasco_machado_guerra_hit_01.wav | 60804 | 0.6889 | -3.0004 | -19.0472 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 4 | assets/sons/sfx/materiais/osso/machado_guerra/osso_machado_guerra_hit_02.wav | 60804 | 0.6889 | -3.0004 | -19.0472 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 5 | assets/sons/sfx/inimigos/flying_eye/hit/espada_longa/flying_eye_espada_longa_hit_01.wav | 26332 | 0.2980 | -3.0004 | -12.9915 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 5 | assets/sons/sfx/inimigos/flying_eye/hit/machado_guerra/flying_eye_machado_guerra_hit_01.wav | 26332 | 0.2980 | -3.0004 | -12.9915 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 6 | assets/sons/sfx/inimigos/globin/hit/soco/globin_soco_hit_01.wav | 44144 | 0.5000 | -3.0004 | -25.2313 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 6 | assets/sons/sfx/materiais/carne/machado_guerra/carne_machado_guerra_hit_01.wav | 44144 | 0.5000 | -3.0004 | -25.2313 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 7 | assets/sons/sfx/inimigos/mushroom/hit/_default/mushroom_default_hit_01.wav | 29634 | 0.3355 | -3.0004 | -32.5328 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 7 | assets/sons/sfx/inimigos/mushroom/hit/espada_longa/mushroom_espada_longa_hit_01.wav | 29634 | 0.3355 | -3.0004 | -32.5328 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 7 | assets/sons/sfx/materiais/fungo/_default/fungo_default_hit_01.wav | 29634 | 0.3355 | -3.0004 | -32.5328 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 8 | assets/sons/sfx/inimigos/mushroom/hit/machado_guerra/mushroom_machado_guerra_hit_01.wav | 48164 | 0.5456 | -3.0004 | -27.4550 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 8 | assets/sons/sfx/materiais/fungo/espada_longa/fungo_espada_longa_hit_01.wav | 48164 | 0.5456 | -3.0004 | -27.4550 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 9 | assets/sons/sfx/inimigos/skeleton/hit/espada_longa/skeleton_espada_longa_hit_01.wav | 59256 | 0.6713 | -3.0004 | -26.7316 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 9 | assets/sons/sfx/materiais/osso/soco/osso_soco_hit_01.wav | 59256 | 0.6713 | -3.0004 | -26.7316 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 10 | assets/sons/sfx/materiais/etereo/_default/etereo_default_hit_01.wav | 37406 | 0.4236 | -3.0004 | -19.2541 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |
| 10 | assets/sons/sfx/materiais/etereo/soco/etereo_soco_hit_01.wav | 37406 | 0.4236 | -3.0004 | -19.2541 | Duplicata de conteudo; manter fora de mudanca automatica nesta fase (pode ser dependencia de evento/material). |

## Correcoes aplicadas (justificadas)
| Correcao | Justificativa | Arquivo(s) |
|---|---|---|
| UI canonical playback | Evita variantes UI com pico/duracao/RMS desbalanceados em hover/navegacao/confirmacao | `core/audio.py`, `tests/test_audio_auditoria.py` |
| Volumes por preferencia de usuario | Escala geral/musica/efeitos/interface/ambiencia sem elevar base do audio.json | `core/audio.py`, `core/preferencias.py`, `core/menu.py`, `main.py` |
| Menu Ecofoco/inventario responsivos a escala | Evita cortes/sobreposicoes em 125/150%; pixel art nao escalada | `core/inventario.py`, `core/menu_fogueira.py` |
| HUD responsivo a escala | Painel/slots/barras/notificacoes/mensagens adaptam altura/largura por fonte | `ui/hud/status.py`, `ui/hud/pocao.py`, `ui/hud/ecos.py`, `ui/hud/boss.py`, `ui/hud/notificacao.py`, `ui/hud/mensagens.py`, `ui/hud/hud.py` |
| Pausa responsiva | Opcoes/espacamento limitados a viewport em escala alta | `ui/overlays.py` |
| Pausa game_scene feedback | Evita recursao/duplicacao ao sair pela pausa | `core/game_scene.py` |

## Riscos/itens nao alterados
- Variantes UI desbalanceadas permanecem no disco; o runtime UI evita seleciona-las aleatoriamente. Remocao/substituicao de assets exige revisao manual de arte/audio.
- Duplicatas exatas fora de UI nao foram removidas automaticamente para evitar quebrar mapeamentos de inimigos/materiais/entrada.
- `_audio_calls.json` possui `ui_calls=0` por categoria textual; evidencias de chamadas UI foram cruzadas por caminho e por inspecao de codigo/testes.

## Evidencias
- Capturas 100/125/150%: `docs/arte/previews/fase_h_*_{padrao,grande,extra_grande}_local.png`
- Dados: `docs/audio/ui_files_measured.csv`, `docs/audio/ui_calls.csv`, `docs/audio/_faseh_ui_problems.csv`, `docs/audio/_faseh_dups.csv`
