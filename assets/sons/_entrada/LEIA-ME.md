# Entrada de novos sons

Esta é a área de triagem dos sons baixados. **Nada aqui é carregado pelo jogo.** Os arquivos mantêm o nome original para preservar a autoria até serem editados, renomeados e promovidos para a árvore definitiva.

O inventário técnico e o destino sugerido de cada arquivo estão em `docs/audio/RELATORIO_NOVOS_SONS.md`.

## Fluxo

1. Ouvir o candidato e confirmar a licença em `CREDITOS_E_LICENCAS.md`.
2. Editar/cortar para um efeito curto e normalizar para WAV 44,1 kHz mono.
3. Renomear no padrão da pasta de destino (`hit_01.wav`, `swing_01.wav`, `step_01.wav`, `land_01.wav`, `morte_01.wav`).
4. Mover para `../sfx/...`, `../ambiencia/...` ou `../musica/...`.
5. Validar em jogo.

## Estrutura de triagem

```text
assets/sons/_entrada/
├── _revisar/                 # candidatos ambíguos, loops e ambiência
├── impacto_esqueleto/        # impactos em osso/Skeleton
├── impacto_globin/           # impactos em corpo mole/Globin
├── impactos_organicos/       # golpes, carne, metal e compilações
├── morte_inimigo/            # mortes de inimigos
├── murro/                    # soco do jogador
├── passos_pedra/             # passos em pedra (sequências e takes)
├── pouso_pedra/              # pouso em pedra
├── ui_epica_ritualistica/    # UI épica/ritualística
├── CREDITOS_E_LICENCAS.md
└── LEIA-ME.md
```

## Regras

- Não promover compilações longas sem cortar. O jogo sorteia o arquivo inteiro.
- Evitar nomes com espaços, acentos, parênteses ou maiúsculas na pasta final.
- Preencher autor, URL e licença antes de mover qualquer arquivo.
- Em caso de dúvida, manter em `_revisar/`.
