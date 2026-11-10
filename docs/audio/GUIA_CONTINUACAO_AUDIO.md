# Guia para continuar a revisão de áudio

Atualizado em **2026-11-10**, branch `som`. Orientações para quem continuar o
trabalho, no formato de um guia de agente. Este arquivo registra o estado da
revisão; não substitui as decisões de escuta do usuário em OBSERVACOES.md.

## Revisão e limpeza mais recentes

Ver [REVISAO_GERAL_2026_11_10.md](REVISAO_GERAL_2026_11_10.md).
Foram recuperados 222 ponteiros LFS e retirados 76 arquivos sem função na
triagem (313,32 MiB), com manifesto e recuperação. Restam 460 áudios: 248 finais
e 212 em `_entrada`. Os 17 arquivos em `_uteis` foram preservados.
A seleção de variantes de UI/interação agora utiliza 14 finais antes ignorados.

## Leia primeiro

- [Status e destinos ainda vazios](STATUS_SONS.md).
- [Decisões sobre os 15 MP3](../../assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/OBSERVACOES.md).
- [Pesquisa e evidências de licença](../../assets/sons/_entrada/sons_faltando/avaliacao_15_mp3/LICENCAS_PESQUISADAS.md).
- [Inventário técnico completo](auditoria_geral/ARQUIVOS.csv) e
  [resumo com caminhos das duplicatas e pendências](auditoria_geral/RESUMO.json).
- [Auditoria de créditos](AUDITORIA_LICENCAS.csv) e registro oficial em
  `assets/sons/_config/LICENCAS.csv`.

## O que foi feito

O conjunto desta entrega inclui as promoções dos lotes 1–3 que já estavam no
workspace quando começou a investigação dos 15 MP3, além das correções abaixo.
As tabelas `tools/promocao_lote1.csv` até `promocao_lote4.csv` registram os destinos;
linhas cuja origem começa com `#` já foram processadas.

### Arquivos e licenças

- Preservados 14 dos 15 MP3 originais; o rejeitado 09 foi removido na limpeza,
  com hash e recuperação no manifesto. O disparo mágico ficou em
  `_entrada/sons_faltando/_uteis/magico/` para uso futuro.
- Preparadas 13 prévias editadas em `avaliacao_15_mp3/previas_editadas/`, com
  duração e parâmetros em `PREVIAS.csv`. Impacto em carne tem pico de -12 dBFS;
  os demais usam -3 dBFS. Prévias não são carregadas pelo jogo.
- Integrados rugido do Boss e morte do Globin a partir de **novas cópias de
  fontes CC0 verificadas** do Freesound (IDs 497056 e 249813). Evidências e hashes
  estão em `pesquisa_licencas/`. Similaridade sonora não comprova a origem dos
  antigos MP3: eles continuam sem licença individual confirmada.
- Corrigido o silêncio inicial de aproximadamente 0,47 s do swing 02 da espada:
  o destino passou de MP3 para WAV mono/44,1 kHz/16 bits, pico -3 dBFS e fades.
  Duração passou de 2,350 s para 1,804 s. Original preservado em
  `_entrada/_originais_corrigidos/`; detalhes em
  [CORRECAO_ESPADA.json](auditoria_geral/CORRECAO_ESPADA.json).
  A edição não resolve a licença pendente desse som.
- `tools/preparar_sons.py` agora exige licença específica, autor e URL, além de
  atribuição para CC BY; rejeita rótulos como LIVRE/PENDENTE. Aceita `pico_db`
  por linha e preserva o delimitador ao marcar promoções concluídas.

### Reprodução e integração

- `core/audio.py`: música por contexto (menu, exploração, descanso e Boss),
  volumes próprios para música/ambiência, loops persistentes de ambiente e
  tochas, canais reservados e interrupção dos sons do mundo ao trocar de sala.
- Cascata tenta outra variante se um arquivo falhar; cooldown não aciona um
  fallback indevido. Eco Profano e mecanismos usam fallback específico.
- Ataques rápidos podem interromper a cauda do swing anterior. Configurações
  de volume/cooldown/limite de vozes também valem para os SFX estáticos.
- Disparo, voo e impacto de projéteis têm grupos separados. Bomba não dispara
  som de voo depois de explodir; impacto consulta as variantes de bomba.
- Removido o gatilho duplicado do ataque de esporo do Mushroom.
- Boss ruge uma vez ao detectar o jogador; ataques consultam `ataque/<tipo>/`.
- Flying Eye tem gatilho de asas a cada 144 ticks, com supressão durante morte,
  hit, knockback e fora do alcance. **Ainda falta promover o áudio de asas.**
- `core/game_scene.py` e `main.py`: seleção de trilha/ambiente conforme sala,
  fogueira e Boss, retorno à música do menu e encerramento do áudio na saída.
  Pausa agora interrompe a atualização do mundo. Corrigido o identificador
  `esqueleto_boss` no carregamento TMX para usar seu construtor e som de entrada.

## Resultado da auditoria

| Verificação | Resultado |
|---|---:|
| Arquivos de áudio em toda a árvore | 460 |
| Finais (`sfx`, `ambiencia`, `musica`) | 248 |
| Triagem, fontes, prévias e backups | 212 |
| Erros de decodificação | 0 |
| Grupos com bytes idênticos em toda a árvore | 8 |
| Grupos com PCM idêntico entre arquivos finais | 8 |
| Pastas finais vazias | 11 |
| Arquivos finais sem registro de licença | 42 |
| Registros finais com licença genérica | 116 |
| Créditos duplicados ou apontando para arquivo inexistente | 0 |

Os oito grupos finais compartilham áudio entre contextos/pastas diferentes;
não há duplicata PCM dentro da mesma pasta final. Não apagar automaticamente:
os caminhos participam da cascata. Backups, fontes e prévias também podem ser
duplicados intencionalmente. As medições PCM usam SDL_mixer a 44,1 kHz estéreo;
não substituem escuta e não detectam toda semelhança entre gravações editadas.

## Pendências e como resolver

### 1. Confirmar as licenças

Dos 15 candidatos, restam **11 aprovados aguardando origem/licença**, um ataque
do Skeleton rejeitado por conter impacto embutido e um disparo mágico reservado.
Use `tools/promocao_lote4_pendentes.csv` como fila. Para cada aprovado:

1. Localize a fonte exata usando os registros e arquivos de `_entrada`, incluindo
   os créditos dos pacotes. Nome parecido ou correspondência sonora não bastam.
2. Guarde URL, autor, licença específica, evidência e hash do arquivo obtido.
   Se a origem antiga não puder ser provada, obtenha uma nova fonte verificável
   e trate-a como substituição, preservando o original.
3. Atualize a linha da tabela com a fonte, os créditos e a edição apropriada.
   Não troque PENDENTE por uma licença presumida para liberar o comando.
4. Faça dry-run, ouça a prévia, promova e confira o registro em LICENCAS.csv.

Há ainda **42 finais sem registro e 116 marcados LIVRE**, incluindo músicas e
sons anteriores a esta revisão. Audite cada linha de AUDITORIA_LICENCAS.csv;
registre a licença comprovada ou substitua a fonte. Não declarar o acervo
inteiro como liberado enquanto essas pendências existirem.

### 2. Preencher os destinos necessários

As 11 pastas estão listadas em STATUS_SONS.md e RESUMO.json. Priorize asas,
ataque e morte do Flying Eye, machado de guerra e impacto de soco em metal,
cujos candidatos dependem de licença. Procure outro ataque para o Skeleton,
sem impacto embutido, e variantes normal/varrido/projétil para o Boss.
O jogo usa fallbacks onde disponíveis. Passos do Flying Eye são opcionais
(`TEM_PASSOS = False`); hit `_default` local do Boss também não é obrigatório.

### 3. Qualidade e escuta em gameplay

- `musica/boss/boss_01.mp3`: pico 0 dBFS e 0,121454% de amostras saturadas na
  decodificação. Ouvir e buscar uma fonte com mais margem, com licença
  comprovada. Baixar o volume não recupera distorção já gravada.
- Ouvir menu → exploração → descanso/fogueira → Boss → morte do Boss → menu.
  Conferir loops, transições, volumes e ausência de reinício a cada atualização.
- Conferir tochas ao entrar/sair de salas, combate rápido, tiros que acertam
  imediatamente, explosão antecipada de bomba e coleta de Eco Profano.
- Conferir sincronização do rugido, morte do Globin e espada; ajustar no
  `audio.json` ou na edição da fonte, preservando os créditos.
- Testar pausa e retomada, volume de música separado do de SFX e execução com
  `PROFANE_AUDIO=0`. Os testes dummy não comprovam a mixagem por escuta.

### 4. Problema de mapa identificado durante os testes

Fora do escopo sonoro: `_resolver_spwan` em `core/game_scene.py` chama
`_spwanar_fallback`, que não existe, quando faltam spawns TMX correspondentes.
Isso pode causar AttributeError nesses mapas. O teste de áudio preserva os
spawns reais do mapa e adiciona o Boss. Para corrigir o problema de mapa,
unificar o caminho de fallback com `_spwan_fallback_grid` e `_spawn_seguro`,
testando mapas sem spawn e entradas laterais antes de alterar esse fluxo.

## Procedimento de manutenção

Execute a partir da raiz do projeto, com as dependências do projeto instaladas:

```powershell
python tools/auditar_sons.py
python -m pytest -ra
git diff --check
git lfs fsck
```

Somente depois de preencher fontes e licenças verificadas da tabela pendente:

```powershell
python tools/preparar_sons.py promover tools/promocao_lote4_pendentes.csv --dry-run
python tools/preparar_sons.py promover tools/promocao_lote4_pendentes.csv
```

O dry-run dessa tabela **deve recusar as linhas ainda PENDENTE**. Não usar
`--sobrescrever` sem conferir o destino. Não reativar linhas concluídas `#`:
isso pode criar variantes adicionais sem necessidade. Após uma promoção,
regenere o inventário e mantenha a auditoria de créditos e este guia atualizados.

Preserve originais e evidências; mantenha `_entrada` fora da reprodução do jogo.
Use Git LFS para os formatos de entrada definidos em `.gitattributes` e confirme
que o checkout contém arquivos reais, não ponteiros LFS sem download.

## Validação desta entrega

**159 testes passaram** em 2026-11-10 (`python -m pytest -ra`). A auditoria
decodificou os 460 arquivos sem erro. A revisão anterior também verificou o
carregamento das 37 especificações e a preservação dos hashes dos 15 originais.
Os testes novos cobrem promoção/licenças, rugido/asas, cascata, loops, música,
cooldowns, projéteis, pausa e entrada do Boss por TMX. Escuta manual completa
em gameplay e saneamento das licenças continuam pendentes.
