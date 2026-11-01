# Áudio do Profane Echo

Esta pasta usa **fallback em cascata**: o jogo procura o som mais específico e desce para o genérico quando a pasta não existe ou está vazia. Adicionar uma variação é só soltar um arquivo com nome numerado na pasta certa.

## Estrutura

```text
assets/sons/
├── _config/
│   ├── audio.json          # volumes, cooldowns e limites por evento
│   └── LICENCAS.csv        # arquivo, origem, licença e atribuição
├── _entrada/               # sons crus aguardando edição/aprovação
├── sfx/
│   ├── player/
│   │   ├── armas/{espada_longa,machado_guerra,soco,_default}/
│   │   ├── movimento/passos/{pedra,madeira,terra,metal,_default}/
│   │   ├── movimento/pouso/{pedra,madeira,terra,metal,_default}/
│   │   ├── movimento/{pulo,dash}/
│   │   ├── dano/  morte/  pocao/
│   ├── inimigos/
│   │   ├── _default/{hit/_default,ataque,morte}/
│   │   ├── skeleton/{hit/<arma>,hit/_default,ataque,morte,passos}/
│   │   ├── globin/{...}
│   │   ├── mushroom/{...,esporo}
│   │   ├── flying_eye/{...,asas}
│   │   └── boss_carrasco/{hit/...,ataque/...,entrada,rugido,morte}
│   ├── materiais/{osso,carne,fungo,etereo,metal}/{espada_longa,machado_guerra,soco,_default}/
│   ├── combate/generico/
│   ├── projeteis/{bomba,esporo,olho,boss}/{disparo,voo,impacto}/
│   ├── mundo/{portas,baus,fogueira,tochas,mecanismos}/
│   ├── interacao/{itens,equipar,eco_profano}/
│   └── ui/{navegar,confirmar,voltar,erro,pausa,inventario,salvar}/
├── ambiencia/{calabouco,sala_descanso,arena_boss}/
└── musica/{menu,exploracao,descanso,boss}/
```

## Regras de nome

- ASCII minúsculo, sem acento, espaço ou parênteses.
- Variações numeradas: `hit_01.wav`, `hit_02.wav`, `swing_01.wav`, `step_01.wav`, `land_01.wav`, `morte_01.wav`.
- O jogo sorteia entre todos os arquivos de áudio da pasta; não é preciso registrar cada variação no código.
- Pasta `_default/` é o fallback local. Prefixo `_` significa "não é uma arma/material/inimigo".
- SFX curtos: WAV PCM 16-bit, 44,1 kHz, mono, pico entre -3 e -1 dBFS.
- Música e ambiência: OGG.

## Cascata de resolução

Impacto da espada em Skeleton:

1. `sfx/inimigos/skeleton/hit/espada_longa/`
2. `sfx/inimigos/skeleton/hit/_default/`
3. `sfx/materiais/osso/espada_longa/`
4. `sfx/materiais/osso/_default/`
5. `sfx/combate/generico/`

Morte usa a mesma lógica com `morte/`. O ataque do jogador usa `sfx/player/armas/<arma>/` e cai para `sfx/player/armas/_default/` e `sfx/combate/generico/`.

Passos e pouso usam o material do piso da sala (`MATERIAL_PISO` em `world/niveis.py`): `passos/<material>/` e `pouso/<material>/`, com `_default/` como reserva.

## Entrada de novos arquivos

`_entrada/` é a área de triagem. Os arquivos ali **não são carregados pelo jogo**. Consulte `docs/audio/RELATORIO_NOVOS_SONS.md` para saber o destino sugerido de cada candidato. Só mova para `sfx/`, `ambiencia/` ou `musica/` depois de editar, normalizar e registrar a licença.

## Promoções recentes

- Etapa 1: `player/movimento/passos/pedra/step_01..06.wav` e `player/movimento/pouso/pedra/land_01..03.wav`, convertidos para WAV 44,1 kHz mono. Licenças em `_config/LICENCAS.csv`.

## Configuração

`_config/audio.json` concentra volumes e limites. `_config/LICENCAS.csv` deve ser preenchido antes de qualquer arquivo novo entrar no jogo.
