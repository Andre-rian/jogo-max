# _inbox — caixa de entrada de novos sons

Jogue aqui qualquer áudio novo baixado, **sem editar e sem renomear**. Nada desta pasta é carregado pelo jogo.

## O que acontece depois

1. Eu inspeciono os arquivos com `tools/preparar_sons.py inspecionar`.
2. Você ouve e aprova os candidatos.
3. Se for compilação longa, eu fatio com `fatiar`.
4. Eu movo para a pasta de categoria em `_entrada/` e monto/atualizo o `promocao_etapaN.csv`.
5. `preparar_sons.py promover` converte para WAV 44,1 kHz mono, normaliza e coloca em `assets/sons/sfx/...`.

## Regras rápidas

- Pode manter o nome original aqui; a renomeação acontece só na promoção.
- Um arquivo por som, se possível. Se vier um pack, pode jogar a pasta inteira.
- Se souber a origem (Freesound, Kenney etc.), deixe no nome do arquivo — ajuda a deduzir a fonte.
- Formatos aceitos: `.wav`, `.mp3`, `.ogg`, `.flac`, `.aiff`, `.aif`.

## Categorias de destino (depois da triagem)

| Pasta | Conteúdo |
|---|---|
| `1_combate_player/` | soco, espada, machado, impactos orgânicos |
| `2_materiais/` | osso, carne, fungo, etéreo, metal |
| `3_inimigos/` | hits, ataques e mortes por inimigo |
| `4_boss_projeteis/` | boss_carrasco e projéteis |
| `5_mundo_movimento/` | passos, pouso, portas, mecanismos, tochas |
| `6_ui/` | UI épica (confirmar, erro, navegar, pausa) |
| `7_ambiencia_musica/` | ambiência e música |
| `_revisar/` | dúvidas, loops e ambiência bruta |
