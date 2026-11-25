# PROFANE ECHO — Fase F.2: poção, Ecos e consolidação

Data: 15/11/2026. Branch: `sprites`.
Implementação e validações concluídas; publicação autorizada pelo usuário.

## Diagnóstico e consolidação

Não foi encontrado `AGENTS.md` no repositório nem nos diretórios ancestrais.
Foram lidos o prompt anexado, a estrutura real e os relatórios C, D, E, F.0 e F.1.
O ambiente foi verificado sem pressupor acesso ao histórico do OpenCode.

Ao iniciar, `HEAD` e `origin/sprites` apontavam para
`73f5808638159c04c00d6fba70b853548d26e255`:
`feat(ui): moderniza inventário, menus e painel híbrido da HUD`.
`git ls-remote origin refs/heads/sprites` confirmou esse mesmo hash no GitHub.
Portanto, as fases anteriores já estavam commitadas e publicadas; não havia
código legítimo pendente dessas fases para adicionar novamente.

Pendências locais preexistentes, preservadas fora do staging F.2:

- Cinco exclusões de `docs/arte/previews/hud_f0_atual_*.png`.
- Exclusões de `hud_f0_evidencias.json` e `hud_f0_integridade_inicio.json`.
- Alteração em `jogo.log`, que já era rastreado apesar do `.gitignore`.

Nenhum desses arquivos foi restaurado, removido ou incluído no novo commit.
`saves.db` permanece ignorado. Os hashes do banco e do log antes/depois são
idênticos e estão nas [evidências](previews/hud_f2_evidencias.json).

F.1 mantida integralmente: proposta C, grafite, bordas frias, vida vermelha,
stamina verde com **8 pixels úteis**, espera, buff, cache e fallback LY015.
`status.py` e `trilho_status.py` não foram modificados.

## Implementação

### Poção F

`ui/hud/pocao.py` usa o sprite M095 já aprovado, via `obter_sprite_item(2)`.
Essa consulta resolve apenas a arte: os dados continuam vindo exclusivamente
de `player.pocao.cargas/cargas_max`, nunca do estoque ID 2 do inventário.

- Painel 148×64, a 20 px das margens esquerda/inferior da superfície recebida.
- M095 em 48×48, escala inteira 2× pelo cache existente; nenhum original editado.
- Tecla F e contagem `atual / máximo` sobre grafite; frasco escurecido no zero.
- Painéis normal/flash e frasco vazio preparados uma vez por instância; texto
  refeito apenas quando as cargas/máximo mudam.
- Frasco procedural se M095 estiver ausente ou ilegível.
- Flash mantém 12 ticks e decremento em `atualizar`. A API `Hud.flash_pocao`
  permanece disponível.

A inspeção encontrou a API do flash sem chamadas no caminho real da tecla F.
O slot agora observa redução das cargas com cooldown ativo no mesmo objeto
de poção e inicia o flash visual. Recarregar ou trocar o jogador não o dispara.
Nenhuma atribuição é feita à poção/jogador. Cura de 40%, cooldown de 90 ticks,
cargas e restrições de uso permanecem em `entities/objetos/pocao.py`, intacto.

### Ecos Profanos

`ui/hud/ecos.py` usa uma cópia binária do símbolo original aprovado na D.1 em
`assets/sprites/itens/ecos/eco_profano.png`: 24×24, 196 pixels opacos, escala 1×.
Não foi criado item/ID; a fonte do contador continua sendo `player.ecos`.

- Painel grafite com bordas azul-acinzentadas e filete violeta.
- Margens direita/inferior de 20 px calculadas pela superfície recebida.
- Largura mínima 196 px, crescendo até 360 px na resolução lógica do jogo.
  Números que excedem a área de texto quebram em linhas sem abreviação,
  arredondamento ou remoção de dígitos. Testado até **60 dígitos**.
- Na resolução 1280×720, o painel permanece à direita da barra atual de chefe.
- Texto/painel refeitos somente ao mudar quantidade ou largura da tela.
- Ícone carregado uma vez, inclusive cache de falhas; sem leitura/escala por frame.
- Halo e fragmentos reaproveitam `desenhar_eco_profano`; a composição RGBA usa
  `alpha_real=True`, preservando o pulso sem círculos sólidos. O sprite substitui
  apenas a área central procedural. Sem ícone, o símbolo procedural completo
  continua disponível.
- `_frame_hud` mantém a cadência anterior: incremento uma vez por desenho.

Foram reutilizados `desenhar_painel`, `desenhar_eco_profano`, o carregador central
e o cache de sprites. Não há arquitetura paralela de HUD nem dependência nova.
Inventário, menus, chefe, combate, progressão, áudio e salvamento não receberam
alterações de runtime. F.3 não foi iniciada.

## Validação

Ambiente observado: Python 3.14.7, pygame-ce 2.5.7, pytest 9.2.0.
Dependências instaladas preservadas; nenhuma alteração nos requirements.

| Verificação | Resultado |
|---|---|
| Base antes da implementação | 204 testes passaram |
| Suíte final local | **232 passaram** |
| Cópia pública: `git archive HEAD` + arquivos F.2, sem packs locais | **231 passaram, 1 ignorado** |
| Único caso ignorado na cópia pública | Inspeção dos pixels/margens do LY015 opcional; testes de fallback executados |
| Novos casos F.2 | 28 testes |
| `git diff --check` | Sem erros |
| Banco e log | SHA-256 inalterados |
| Cinco capturas pareadas da cena real | Pixels fora das áreas de poção/Ecos idênticos |

Comando da suíte final:

```text
python -m pytest -o addopts='' --tb=short -p no:cacheprovider -q
```

Cobertura: vida cheia/baixa, stamina cheia/vazia (incluindo 24 casos F.1),
poção 3/1/0, estoque ID 2 divergente, cura/cooldown reais, flash e expiração,
recarga/troca do jogador, zero/137/19 e 60 dígitos, quatro superfícies
(320×240, 640×480, 1280×720, 1920×1080), clip do chamador, cache em 60 desenhos,
assets ausentes/corrompidos/dimensão inválida, halo, cópia exata da arte,
exploração e ataque real ao chefe. Estados funcionais são comparados antes/depois.

O teste anterior de molduras de menu exigia o pack lygame instalado. Foi
ajustado para gerar duas imagens sintéticas no diretório temporário do teste e
continuar validando os quatro estados/paletas. Nenhuma imagem restrita foi
embutida nos testes nem houve alteração no código do menu.

A primeira exportação de validação encontrou o limite de comprimento de
caminho do Windows em um áudio antigo de nome longo. A cópia foi refeita em
diretório temporário mais curto, com sucesso; nenhum arquivo foi renomeado no
repositório. Não foi necessário contornar falhas de gameplay ou de testes.

## Capturas e evidências

- [Comparativo 1×](previews/hud_f2_comparativo.png): 1136×832, ~58 KB; cinco
  estados dos componentes, antes/depois, fundos sintéticos claro/escuro.
  O último estado demonstra o problema antigo de clipping e a quebra em linhas
  na F.2. Nenhum redimensionamento de texto ou sprites na prancha.
- [Evidências JSON](previews/hud_f2_evidencias.json).
- [Gerador reproduzível](gerar_previews_f2.py):
  `python docs/arte/gerar_previews_f2.py`.

As dez capturas completas locais `hud_f2_<cenario>_<antes|depois>_local.png`
usam `Gamescene.desenhar`, SDL dummy e fallback de LY015. Cenários:
exploração, vida baixa/stamina vazia, uso real de poção, zero cargas/Ecos grandes
e chefe com ataque real (290/300 HP). Valores de vida baixa/Ecos são preparados
em memória; não representam progresso de uma sessão de usuário.

Comparações partem do mesmo quadro de mundo, com cópias dos componentes antigos
e nenhum tick de gameplay entre as duas imagens. As áreas excluídas da
comparação são `(16,626,156,78)` e `(896,610,384,110)`. Dados do jogador e HP do
chefe permanecem iguais durante o desenho. O gerador não importa `main`, não
instancia o gerenciador de saves nem configura logging em arquivo.

## Origem e publicação dos assets

M095 é Beast Crafting Materials, CC0, já registrado e distribuído no projeto.
Eco é arte original D.1, sob a licença do repositório, sem pixels de lygame.
O sprite promovido tem 502 bytes e é idêntico à proposta.
Ver [origens](ASSETS_UI_ORIGENS.md) e [inventário](INVENTARIO_SPRITES.md).

O staging deve conter somente os 17 arquivos abaixo. Capturas completas ficam
ignoradas; o comparativo compacto contém apenas CC0/arte original. Não entram
saves, logs, caches, arquivos pessoais, packs restritos nem grandes capturas.

| Arquivo | Mudança |
|---|---|
| `.gitignore` | Capturas completas e recibo de publicação F.2 locais |
| `ui/hud/pocao.py` | Slot M095, cargas, flash, cache e fallback |
| `ui/hud/ecos.py` | Símbolo D.1, painel, números longos, cache e fallback |
| `assets/sprites/itens/ecos/eco_profano.png` | Cópia binária da arte aprovada |
| `tests/test_hud_recursos.py` | 28 casos F.2 |
| `tests/test_moldura_menu_lygame.py` | Teste independente do pack restrito |
| `docs/arte/gerar_previews_f2.py` | Capturas e preservação de dados |
| `docs/arte/referencias/pocao_antes_f2.py` | Renderer anterior, documental |
| `docs/arte/referencias/ecos_antes_f2.py` | Renderer anterior, documental |
| `docs/arte/previews/hud_f2_comparativo.png` | Comparativo publicável |
| `docs/arte/previews/hud_f2_evidencias.json` | Valores, integridade e comparação |
| `docs/arte/previews/README.md` | Índice das evidências |
| `docs/arte/INVENTARIO_SPRITES.md` | Situação atual da HUD e Eco |
| `docs/arte/ASSETS_UI_ORIGENS.md` | Origens efetivamente usadas |
| `docs/arte/RELATORIO_FASE_D1_RECURSOS_ESPECIAIS.md` | Continuidade do Eco sem novo ID |
| `docs/arte/RELATORIO_FASE_F1_HUD.md` | Consolidação e continuidade |
| `docs/arte/RELATORIO_FASE_F2_HUD.md` | Este relatório |

## Git e confirmação remota

Remoto conferido: `https://github.com/Andre-rian/jogo-max.git`.
Após revisar diff, licenças, lista de arquivos e staging, executar o commit na
`sprites`, `git push -u origin sprites` e comparar `git rev-parse HEAD` com
`git ls-remote origin refs/heads/sprites`. Não usar force, reset, rebase ou merge.

O hash definitivo e a resposta real do remoto são registrados **após** a
publicação em `previews/hud_f2_publicacao_local.json` (ignorado) e no relatório
final da conversa. Este documento não declara antecipadamente que o push
foi concluído. O estado final esperado preserva somente as oito pendências
locais preexistentes descritas acima, sem novos arquivos fora do staging.

## Pendências para a entrega

- Avaliação perceptiva no monitor/fullscreen e sessão prolongada continuam
  sendo testes manuais; esta rodada valida superfícies lógicas com SDL dummy.
- A extensão exata de números foi validada até 60 dígitos; isso não constitui
  suporte a inteiros de comprimento arbitrário em telas finitas.
- Permanecem os avisos anteriores de perfil PNG iCCP, camada `plataformas`
  ausente e inimigo sem tipo. O teste da sala 5 usa posição explícita para
  contornar o problema de spawn já documentado na F.0, sem alterar mundo.
- Sobreposição de notificação com a barra de chefe, registrada na F.0, continua
  fora desta fase. Nenhuma mudança da F.3 foi aplicada.
- As exclusões F.0 e a modificação anterior do log permanecem locais para
  decisão do responsável; não bloqueiam publicar os arquivos F.2 verificados.
