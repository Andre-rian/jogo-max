# Entrada de novos sons

Área de triagem dos sons baixados. **Nada aqui é carregado pelo jogo.** Os arquivos mantêm o nome original para preservar a autoria até serem editados, renomeados e promovidos para a árvore definitiva.

## Estrutura de triagem

```text
assets/sons/_entrada/
├── _inbox/                 # novos arquivos crus, sem triagem (comece aqui)
├── _fatias/                # gerado por preparar_sons.py fatiar (não mover)
├── _revisar/               # dúvidas, loops e ambiência bruta
├── _uteis/                 # aprovados como úteis, mas fora da promoção atual
│   ├── osso/  metal/  soco/  impactos/  passos/  passos_inimigos/
│   ├── menu/  efeitos/  inventario/  pouso/  ambiencia/
├── 1_combate_player/       # P1: soco, espada, machado, impactos orgânicos
│   ├── soco/
│   └── impactos_organicos/
├── 2_materiais/            # P1: impacto por material
│   ├── osso/  carne/  fungo/  etereo/  metal/
├── 3_inimigos/             # P1/P2: hits, ataques e mortes
│   ├── skeleton/  globin/  mushroom/  flying_eye/  mortes/
├── 4_boss_projeteis/       # P2: boss e projéteis
│   ├── boss_carrasco/  projeteis/
├── 5_mundo_movimento/      # P3: passos, pouso, portas, mecanismos, tochas
│   ├── passos_pedra/  pouso_pedra/  portas/  mecanismos/  tochas/
├── 6_ui/                   # P1/P3: interface
│   └── epica/
├── 7_ambiencia_musica/     # P3: ambiência e música
├── CREDITOS_E_LICENCAS.md
└── LEIA-ME.md
```

O número no início indica a prioridade no `docs/audio/SONS_FALTANDO.md`. A pasta vazia com `.gitkeep` é só um marcador de destino.

> **Observações nos nomes:** vários arquivos têm anotações entre parênteses no próprio nome (ex.: `...(funciona para caminhadas nao corridas).wav`). Elas são instruções de triagem — leia antes de mover/promover e só remova o texto depois de aplicar a decisão.

## Fluxo

1. Jogue os arquivos novos em `_inbox/` (sem editar).
2. Ouvir o candidato e confirmar a licença em `CREDITOS_E_LICENCAS.md` (licença livre dispensa autor).
3. Editar/cortar para um efeito curto e normalizar para WAV 44,1 kHz mono.
4. Renomear no padrão de **contexto completo**: `<contexto>_<ação>_<NN>.wav` (ex.: `carne_soco_hit_01.wav`, `movimento_passos_pedra_step_01.wav`). Os sons ainda em triagem seguem o mesmo padrão; ver `sons_faltando/CONTEXTO.md`.
5. Mover para `../sfx/...`, `../ambiencia/...` ou `../musica/...`.
6. Validar em jogo.

Ferramentas:

```bash
python tools/preparar_sons.py inspecionar assets/sons/_entrada/_inbox
python tools/preparar_sons.py fatiar <arquivo> --max 8 --dur-max 1.0
python tools/preparar_sons.py promover tools/promocao_etapa3.csv --dry-run
```

## Mapa da reorganização (nome antigo → novo)

| Antes | Agora |
|---|---|
| `murro/` | `1_combate_player/soco/` |
| `impactos_organicos/` | `1_combate_player/impactos_organicos/` |
| `impacto_esqueleto/` | `2_materiais/osso/` |
| `impacto_globin/` | `2_materiais/carne/` |
| `morte_inimigo/` | `3_inimigos/mortes/` |
| `passos_pedra/` | `5_mundo_movimento/passos_pedra/` |
| `pouso_pedra/` | `5_mundo_movimento/pouso_pedra/` |
| `ui_epica_ritualistica/` | `6_ui/epica/` |

O inventário técnico de cada arquivo continua em `docs/audio/RELATORIO_NOVOS_SONS.md` (escrito antes da reorganização; use a tabela acima para traduzir os caminhos).

## Regras

- Não promover compilações longas sem cortar. O jogo sorteia o arquivo inteiro.
- Evitar nomes com espaços, acentos, parênteses ou maiúsculas na pasta final.
- Licença livre não exige autor/URL; o registro em `LICENCAS.csv` é opcional.
- Em caso de dúvida, manter em `_revisar/`.

## Triagem aplicada em 2026-11-07

Promovidos para `../sfx/` (ver `assets/sons/_config/LICENCAS.csv`):

- **Skeleton:** hit genérico, machado, soco e duas mortes.
- **Osso:** hit genérico e espada longa (corte de ~2 s).
- **Carne:** hit genérico, golpe de soco e 4 variações de espada.
- **Mushroom:** morte (sem fatiar, conforme anotação).
- **Soco:** 3 swings (fatias de `232358`).
- **Boss Carrasco:** bloqueio de escudo.
- **UI:** navegar (`849...`) e pausa.
- **Mundo:** porta de pedra.
- **Passos:** madeira + 7 novas variações em pedra.

Não promovidos:

- `_uteis/` — 15 fontes boas, mas fora do escopo agora (hit em metal, impactos de chefe, passos de inimigos, menu, efeitos/choir, inventário, pouso alternativo, ambiência).
- `_fatias/` — **42 fatias citadas** em 8 pastas (metal, socos em metal e impactos de boss). O restante foi apagado. Inventário completo em `tools/inventario_sons_restantes.csv` e `docs/audio/INVENTARIO_SONS_RESTANTES.md`.
- `5_mundo_movimento/passos_pedra/` — as 4 fontes longas ficaram para cortes alternativos; os cortes `step_14..17` já foram promovidos.

Os originais já promovidos foram apagados de `_entrada/` (as cópias finais ficam em `../sfx/`); `_para_fatiar/` inteiro (19 fontes) e `_uteis/passos/770072...` também foram removidos após a 2ª triagem.

## Triagem aplicada em 2026-11-07 (2ª leva)

Promovidos para `../sfx/` (63 arquivos; ver `assets/sons/_config/LICENCAS.csv`):

- **UI:** `confirmar_02..09`, `erro_02..04` e `inicio_01` (stinger de início; ainda sem gatilho no código).
- **Metal:** `_default/hit_01..04`, `espada_longa/hit_01..06`, `machado_guerra/hit_01` e `combate/generico/block_02..03`.
- **Corpo:** `carne/soco/hit_02..09`, `osso/soco/hit_01..03`, `fungo/soco/hit_01..03`, `etereo/soco/hit_01..02`.
- **Inimigos:** `globin/ataque/ataque_01..03` e `boss_carrasco/hit/soco/hit_01..08`.
- **Movimento:** `pouso/pedra/land_04..08` e `passos/pedra/step_14..17` (um corte curto de cada fonte).
- **Combate genérico:** `hit_04..05`.

Mantidos: 42 fatias em `_fatias/`, 15 fontes em `_uteis/` e 4 fontes longas de passos.
Removidos: 97 fatias promovidas/não citadas, 14 pastas vazias de `_fatias/`, `_para_fatiar/` (19 fontes) e `_uteis/passos/770072...` (rejeitado).
