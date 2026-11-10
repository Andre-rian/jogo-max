# Revisão geral e limpeza de áudio — 2026-11-10

A revisão conferiu a árvore de áudio, os registros de triagem, as receitas de
promoção e os caminhos usados pelo jogo. **76 arquivos foram retirados de
`_entrada` (313,32 MiB)**. Nenhum áudio final foi alterado, removido ou promovido.

## Problemas corrigidos

- **222 ponteiros LFS sem conteúdo local:** recuperados do mesmo repositório,
  verificando tamanho e SHA256 de cada objeto. A tentativa de `git lfs pull`
  falhou na conexão; o download por `media.githubusercontent.com` funcionou.
  O cache LFS foi preenchido com os objetos verificados e `git lfs fsck` passou.
  O binário Git LFS 3.8.1 foi conferido contra o checksum oficial e instalado na
  `.venv/bin/`; os filtros foram configurados apenas neste repositório.
- **14 variantes finais nunca escolhidas:** 13 de interface (confirmar, erro,
  navegar e abrir pausa) e uma de abrir porta. `play_sfx` agora consulta variantes
  numeradas da mesma ação para UI/interações. Abrir e fechar continuam separados;
  um arquivo inválido não impede uma alternativa válida. Canal, grupo, volume,
  cooldown e limites continuam sendo os do evento original.
- **Registros desatualizados:** o contexto apontava para tarefas já concluídas e
  caminhos anteriores à consolidação. `CONTEXTO.md`, status, guia e planilhas
  foram sincronizados. Os 66 candidatos da busca constam como fontes utilizadas,
  com seus destinos efetivos. A receita antiga `tools/promocao.csv` foi desativada
  para evitar repetir promoções com nomes anteriores.

## Limpeza de `_entrada`

| Motivo | Arquivos |
|---|---:|
| Cópias byte a byte de arquivos preservados em `_uteis` ou fontes anotadas | 17 |
| Fontes da triagem antiga já processadas, com finais/fatias selecionadas preservados | 37 |
| Recortes experimentais substituídos pelas prévias atuais | 11 |
| Recortes automáticos de pulo não utilizados; compilação original preservada | 9 |
| Rejeitados: passos `770072` e ataque 09 do Skeleton | 2 |
| **Total** | **76** |

O manifesto [LIMPEZA_ENTRADA.csv](auditoria_geral/LIMPEZA_ENTRADA.csv) registra
cada caminho, motivo, referência preservada, tamanho, SHA256 e commit anterior
à limpeza. As decisões sobre rejeitados vêm de `_entrada/LEIA-ME.md` na revisão
anterior e de `avaliacao_15_mp3/OBSERVACOES.md`.

Preservados: **17 áudios em `_uteis`** (16 na raiz e o disparo mágico), 42 fatias
explicitamente reservadas, a fatia 003 da receita do pulo, 4 fontes longas de
passos, os 66 originais dos lotes recentes, 13 prévias editadas, 11 aprovados
aguardando comprovação de origem, fontes de música, evidências e backup da espada.
Os hashes dos áudios finais e das reservas `_uteis` foram conferidos antes/depois.

### Recuperação

Os removidos estão no Git/LFS do commit indicado no manifesto. Há também uma
cópia local verificada em
`/tmp/jogo-max-revisao-audio-2026-11-10/removidos.tar`.
Esse backup em `/tmp` é temporário; o histórico Git/LFS é a referência duradoura.
Os objetos LFS correspondentes também estão no cache local do repositório.

Para recuperar um arquivo, use o caminho e o commit do manifesto com
`git restore --source=<commit> --worktree -- '<caminho>'` e depois
`git lfs checkout -- '<caminho>'`, com Git LFS instalado. Não restaurar a pasta
inteira sobre a revisão atual.

## Resultado técnico

| Medida | Resultado final |
|---|---:|
| Áudios analisados | 460 |
| Áudios finais | 248 |
| Triagem, fontes e reservas | 212 |
| Erros de decodificação / silêncio total / ponteiros LFS restantes | 0 |
| Grupos de duplicatas por bytes e por PCM final | 8 |
| Duplicatas dentro da mesma pasta final | 0 |
| Especificações estáticas com arquivo existente | 37/37 |
| Pastas finais vazias | 11 |
| Registros de licença duplicados / apontando para final ausente | 0 |

Antes da limpeza havia **536 arquivos**, incluindo 4 fatias reservadas que não
constavam na auditoria antiga de 532. As quatro foram incluídas nesta conferência.
Depois da recuperação LFS, todos os 536 decodificaram; após a limpeza, os 460
restantes foram verificados novamente. Medição pelo SDL_mixer em 44,1 kHz,
16 bits, estéreo, sem saída física de áudio.

Os 8 grupos de duplicatas finais foram mantidos: atendem inimigos, armas ou
materiais diferentes na cascata. Apagar uma cópia mudaria a seleção/fallback.
Não há cópias exatas redundantes restantes na triagem.

Inventário e medições: [ARQUIVOS.csv](auditoria_geral/ARQUIVOS.csv).
Caminhos das duplicatas e alertas: [RESUMO.json](auditoria_geral/RESUMO.json).

## Pendências confirmadas

- `musica/boss/boss_01.mp3`: pico de 0 dBFS e **0,121454% de amostras saturadas**
  na decodificação usada pelo jogo. Requer escuta e revisão da fonte; diminuir
  o volume de reprodução não recupera amostras já limitadas. Arquivo preservado.
- **42 finais sem registro de licença e 116 com `LIVRE`**; permanecem listados em
  [AUDITORIA_LICENCAS.csv](AUDITORIA_LICENCAS.csv). Nenhuma licença foi presumida.
- **11 destinos vazios**, com fallbacks quando disponíveis, detalhados em
  [STATUS_SONS.md](STATUS_SONS.md). Os 11 aprovados do lote legado ainda aguardam
  comprovação de origem. O ataque rejeitado do Skeleton precisa de substituto.
- `sfx/ui/inicio/inicio_01.wav` continua reservado na árvore final sem gatilho.
  A limpeza solicitada foi aplicada em `_entrada`; não foi criado um evento
  novo de início para esse stinger.
- Mixagem, timbre e transições precisam de escuta em gameplay. Não foi realizada
  avaliação artística por escuta nesta revisão técnica.

## Verificação

- Auditoria completa dos arquivos com `tools/auditar_sons.py`.
- **159 testes passaram** (`.venv/bin/python -m pytest -ra`), incluindo regressões para alternância de variantes, separação
  abrir/fechar, arquivo inválido, volume aplicado e variação de porta.
- Preservação dos hashes finais e `_uteis`, conferência das referências atuais
  das tabelas e integridade Git LFS.
- Alterações preexistentes de ambiente/inicialização e conteúdo já preparado
  para commit preservados. Nenhum commit ou push feito nesta revisão.
