# Relatório de feedback dos sons — Profane Echo

> Data: 2026-10-30  
> Origem: avaliação de escuta do usuário após a integração dos SFX.  
> Status: opiniões registradas; nenhuma alteração de áudio foi feita nesta etapa.

## 1. Passos do jogador

- O som de passos está agradável, mas não combina com o ambiente atual.
- O ambiente é de pedra/tijolos, e o som parece adequado para piso de madeira.
- Seria interessante ter passos específicos para pedra/tijolos.
- A mesma observação vale para o som de queda/pouso, que também precisa refletir o material do piso.

Arquivos atuais relacionados:

- `assets/sons/player/passo_1.wav`
- `assets/sons/player/passo_2.wav`
- `assets/sons/player/passo_3.wav`
- `assets/sons/player/pouso.wav`

Direção sugerida:

- criar variações por material de piso, começando por pedra/tijolos;
- manter as variações atuais de madeira para salas ou áreas com esse material;
- alinhar o pouso ao mesmo material dos passos.

## 2. Impacto e morte dos inimigos

- O som dos inimigos está bom no geral.
- O som de impacto poderia variar conforme o inimigo que recebe o dano.
- Atualmente Skeleton e Globin usam o mesmo som de acerto, o que não parece coerente.
- O som de morte está um pouco longo e acaba ultrapassando a tela de morte.

Arquivos atuais relacionados:

- `assets/sons/combate/acerto_1.wav`
- `assets/sons/combate/acerto_2.wav`
- `assets/sons/combate/acerto_3.wav`
- `assets/sons/combate/inimigo_morre.wav`

Direção sugerida:

- criar famílias de impacto por tipo de inimigo, por exemplo:
  - Skeleton: ossos, madeira seca, cliques;
  - Globin: corpo mole, tecido, impacto mais abafado;
- encurtar a cauda da morte ou cortar o som quando a tela de morte terminar;
- manter alguma variação dentro de cada família para evitar repetição.

## 3. Interface

- Os sons de UI estão bons por enquanto.
- Ainda assim, o usuário gostaria de algo mais épico.
- O resultado atual soa “amiguinho” demais para a proposta do jogo.

Arquivos atuais relacionados:

- `assets/sons/ui/menu_navegar.wav`
- `assets/sons/ui/menu_confirmar.wav`
- `assets/sons/ui/menu_voltar.wav`
- `assets/sons/ui/menu_erro.wav`
- `assets/sons/ui/pausa_abrir.wav`
- `assets/sons/ui/pausa_fechar.wav`
- `assets/sons/ui/inventario_abrir.wav`
- `assets/sons/ui/inventario_fechar.wav`
- `assets/sons/ui/salvar.wav`

Direção sugerida:

- tornar a UI mais grave, ritualística e espectral;
- reduzir a sensação de botão “fofo” ou casual;
- manter navegação curta e discreta, mas com confirmações mais imponentes.

## 4. Impactos em geral

- Os sons de impacto soam muito robóticos.
- A sensação é de efeito de jogo de nave, distante de algo humano.
- A proposta pede impactos mais orgânicos, físicos e viscerais.

Direção sugerida:

- usar camadas de corpo, tecido, osso, pedra e ar;
- evitar tons sintéticos, bipes e transientes excessivamente limpos;
- variar ataque, textura e cauda para reduzir a repetição robótica;
- revisar principalmente os acertos, dano do jogador e impactos de UI.

## 5. Prioridades sugeridas

1. Passos e pouso específicos para pedra/tijolos.
2. Impacto de dano por tipo de inimigo.
3. Encurtar ou cortar o som de morte conforme a tela de morte.
4. Redesenhar a UI para uma identidade mais épica e ritualística.
5. Substituir impactos robóticos por camadas mais orgânicas e humanas.

## 6. Observação

Este documento registra percepções de escuta. As soluções dependem de novos assets ou de edição dos arquivos existentes, o que está fora da integração inicial de SFX.
