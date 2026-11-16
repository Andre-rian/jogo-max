# PROFANE ECHO — Fase F.1: painel de status híbrido

Status: **integrado e preservado na consolidação F.2**.
Referência: [auditoria F.0](RELATORIO_FASE_F0_HUD.md), proposta C escolhida pelo usuário.

Atualização de 15/11/2026: a continuidade F.2 confirma a proposta C e a stamina
de 8 px úteis. `status.py` e `trilho_status.py` permanecem sem alterações.
As fases anteriores já estavam no commit `73f5808638159c04c00d6fba70b853548d26e255`
da branch `sprites`, também presente no remoto ao iniciar esta rodada.
Resultados atuais e publicação: [relatório F.2](RELATORIO_FASE_F2_HUD.md).
Os registros abaixo descrevem a execução histórica da F.1.

## Resultado

Somente `BarrasStatus` mudou de aparência. Painel grafite (276×88) em (20,20), bordas frias, filete violeta discreto, números de vida fora do preenchimento, vida vermelha e stamina verde. Stamina usa **8 pixels úteis**, escolhidos após comparar 6/8/10 no tamanho nativo. Vida mantém 6 pixels úteis da proposta C.

| Altura útil de stamina | Resultado da inspeção a 1× |
|---|---|
| 6 px | Mais fina, leitura menos evidente nos níveis baixos |
| **8 px** | Melhor presença sem aumentar o painel; configuração experimental escolhida |
| 10 px | Legível, mas pesa mais que a vida e reduz o respiro perto do indicador de buff |

As três variantes cabem no mesmo painel. A escolha de 8 px é uma avaliação visual desta rodada, não um estudo com usuários. O símbolo verde da Raiz Amarga e o aviso de espera ficam na faixa inferior, protegidos pelo fundo grafite. Condições de exibição, fase do piscar e valores dos temporizadores não mudaram.

## Capturas reais antes/depois

| Cenário | Comparativo nativo lado a lado |
|---|---|
| Exploração | [Antes/depois](previews/hud_f1_exploracao_comparativo_restrito.png) |
| Combate comum | [Antes/depois](previews/hud_f1_combate_comparativo_restrito.png) |
| Vida baixa | [Antes/depois](previews/hud_f1_vida_baixa_comparativo_restrito.png) |
| Stamina vazia, durante espera | [Antes/depois](previews/hud_f1_stamina_vazia_comparativo_restrito.png) |
| Stamina regenerando | [Antes/depois](previews/hud_f1_regenerando_comparativo_restrito.png) |
| Buff da Raiz Amarga | [Antes/depois](previews/hud_f1_buff_raiz_comparativo_restrito.png) |
| Chefe | [Antes/depois](previews/hud_f1_chefe_comparativo_restrito.png) |

Cada comparativo tem 2560×756, com dois quadros de 1280×720 e rótulos externos. Arquivos individuais: `hud_f1_<cenario>_antes_restrito.png` e `hud_f1_<cenario>_depois_restrito.png`.

- [Comparação 6/8/10, estados cheio/meio/baixo/vazio a 1×](previews/hud_f1_alturas_6_8_10_restrito.png). Os doze quadros completos também estão em `hud_f1_altura_<6|8|10>_estado_<0..3>_restrito.png`.
- [Fallback procedural](previews/hud_f1_fallback_restrito.png): classe integrada com `usar_asset=False`, sobre o mesmo cenário, apenas status para inspeção isolada.
- [Movimentação](previews/hud_f1_movimento_sequencia_restrito.png): seis quadros separados por oito ticks; arquivos `hud_f1_movimento_0..5_restrito.png` preservam 1280×720. A prancha reduz para 640×360, não serve para avaliar pixel-perfect.
- [Fullscreen: superfície renderizada](previews/hud_f1_fullscreen_restrito.png) e [metadados](previews/hud_f1_fullscreen.json).

### Método

O [gerador F.1](gerar_previews_f1.py) usa `Gamescene.desenhar`, módulos de jogo e HUD reais. O renderer antigo está preservado como [referência pré-F.1](referencias/status_antes_f1.py), sem ser importado pelo jogo. Em um único quadro do mundo, uma cópia rasa dos componentes da HUD renderiza o status antigo; depois a instância atual renderiza a HUD integrada. Não há atualização de gameplay entre antes/depois. Os temporizadores dos componentes antigos são isolados da instância atual.

Comparação binária de todos os pixels fora de `(18,18,282,94)`: **idênticos nos sete cenários**. Poção, Ecos, chefe, mensagens e mundo não mudaram entre as imagens pareadas. A área excluída cobre o status antigo e novo, incluindo seus indicadores.

Exploração usa cena normal. Combate comum usa arena de teste preexistente, aproximação controlada e ataque real de espada. Vida baixa e stamina zero são configurações de teste em memória; regeneração é obtida após 45 atualizações reais, chegando a ~4,4/130 com delay zero. Raiz ID 4 é usada pelo método existente, com buff 180. Chefe usa sala 5 e ataque real, preservando a barra antiga. Posição de entrada explícita contorna o problema de spawn já documentado em F.0; não foi corrigido código de mundo.

Movimento usa entrada D em memória por 48 atualizações, com posições x de 154 a 286 registradas nas [evidências](previews/hud_f1_evidencias.json). Não importa `main`, não instancia o gerenciador de saves e não inicializa o gerenciador de áudio. Nenhuma sessão modifica progresso persistente.

## LY015, composição e fallback

Arquivo opcional: `assets/sprites/_entrada/itens/lygame_dark_fantasy/UI/ProgressTrack.png`. Caminho absoluto resolvido a partir do módulo; não depende do diretório de execução. O pack permanece ignorado no Git; nenhum sprite foi copiado para a árvore pública.

**Verificação de margens:** imagem local 48×12, completamente opaca. Interior x=3..44 e y=3..8. Colunas x=3..44 são idênticas por linha. Portanto, margens corretas para essa composição são **3 px**, substituindo a hipótese experimental de 5 px da F.0. As três cores encontradas foram (10,10,12), (32,32,35) e (129,39,36); o contorno vermelho é remapeado para azul-acinzentado somente em memória.

Composição horizontal 3-slice: preserva as pontas de 3 px, repete a coluna central uniforme até 252 px. Para obter interiores de 8/10 px, preserva as três linhas superiores/inferiores e repete linhas internas. Não usa interpolação nem escala fracionária. O preenchimento é desenhado **após** o trilho opaco, no interior de largura 246 px.

`trilho_status.py` mantém cache da origem, inclusive falha, e das superfícies compostas (até oito variantes). `BarrasStatus.__init__` obtém os trilhos prontos e cria o painel/aviso; `desenhar` faz blits e preenchimentos. Texto numérico só é renderizado novamente quando HP/máximo muda. Não há leitura de arquivo, redimensionamento ou recomposição do trilho a cada frame.

Arquivo ausente, ilegível/corrompido ou de dimensão inesperada resulta em trilho procedural, com mesmas dimensões e cores, sem placeholder magenta. Falha fica em cache: instalar o pack durante a sessão exige reiniciar o jogo ou limpar o cache antes de criar novo painel. Clones públicos funcionam sem o pack. O teste que inspeciona pixels do asset local é pulado quando ele está ausente; os testes de fallback não dependem do pack.

## Preservação funcional

- Nenhuma atribuição a campos do jogador no renderer. Proporções são limitadas **apenas para desenho** a 0..1; máximo não positivo resulta em preenchimento zero, sem alterar atributos.
- Dados continuam sendo `player.hp`, `hp_max`, `stamina`, `stamina_max`.
- Espera: mesma condição `stamina_delay > 0 and stamina < stamina_max`; mesma fase `_frame_atual % 20 < 10`.
- Buff: mesma condição `buff_stamina_duracao > 0` e mesmo símbolo procedural, apenas reposicionado.
- Borda da stamina sempre desenhada, inclusive vazia. Preenchimento nunca ultrapassa o interior; clip preexistente da superfície é preservado.
- Nenhuma alteração em atualização de HUD, combate, atributos, inventário, menus, poção, Ecos, notificações, chefe, áudio ou saves. Não há mana nem novo recurso.

## Testes e ambiente

- **Suíte completa: 204 testes aprovados**, incluindo 24 casos novos de HUD. Comando: `python -m pytest -q --tb=short -p no:cacheprovider`.
- Novos testes: preenchimentos de 0/10/50/100%, negativos e excedentes; alturas 6/8/10; borda vazia; máximo zero; preservação de dados e clip; espera e buff; arquivos ausentes/corrompidos; cache sem leitura/escala durante 60 desenhos; margens/pixels do LY015 local.
- Execução inicial encontrou restrições no diretório temporário/cache do pytest. Execução autorizada fora do sandbox e sem cacheprovider concluiu com sucesso. Um endereço incorreto de pixel na asserção inicial foi corrigido para a borda real, sem mudar o renderer para acomodar o teste.
- Python 3.14.7 / pygame-ce 2.5.7; nenhuma dependência nova.
- SHA-256 de 5.293 arquivos preexistentes: **apenas `ui/hud/status.py` mudou**. `saves.db`, `jogo.log`, assets e arquivos funcionais fora do escopo permaneceram intactos. Arquivos novos estão listados abaixo.
- `git diff --check` sem erros; 43 PNGs novos ignorados pelo Git. Nenhum commit nem staging.
- Avisos anteriores de mapa/PNG continuam presentes (camada plataformas ausente, objeto de inimigo sem tipo, perfil iCCP); não pertencem a esta integração.

### Fullscreen e limites

Teste real Windows, autorizado: 90 frames com `pygame.SCALED | pygame.FULLSCREEN`, superfície lógica **1280×720**, janela **1920×1080**. Execução e desenho concluíram sem erro. A captura salva a superfície lógica, não a saída física do monitor.

O sprite é pixel-perfect em 1× na superfície lógica. A relação 1920/1280 é 1,5: **não se afirma pixel-perfect na imagem física fullscreen**, que depende do escalonamento SDL já usado pelo jogo. Nenhuma configuração global de janela foi alterada para resolver isso. Aprovação perceptiva no monitor, diferentes DPIs e sessão prolongada continuam pendentes. As fontes continuam as fontes do sistema existentes, com possibilidade de variação entre máquinas.

## Arquivos desta etapa

| Arquivo | Papel |
|---|---|
| `ui/hud/status.py` | Único módulo preexistente de runtime alterado; painel híbrido |
| `ui/hud/trilho_status.py` | Novo helper local de apresentação, cache e fallback |
| `tests/test_hud_status.py` | Testes novos de renderização e preservação |
| `docs/arte/gerar_previews_f1.py` | Capturas reproduzíveis e validação de diferenças |
| `docs/arte/referencias/status_antes_f1.py` | Cópia documental do renderer anterior |
| `docs/arte/RELATORIO_FASE_F1_HUD.md` | Este relatório |
| `docs/arte/previews/README.md` | Índice atualizado |
| `docs/arte/previews/hud_f1_*.json` | Manifesto inicial, evidências de estados e fullscreen |
| `docs/arte/previews/hud_f1_*_restrito.png` | Capturas locais, não versionáveis |

## Pendências para aprovação

Validar a direção híbrida e a altura útil de 8 px em jogo; avaliar percepção em movimento/fullscreen no monitor do usuário. Os demais componentes da HUD seguem a aparência antiga por escopo explícito. A restrição de redistribuição do lygame registrada em F.0 permanece: assets e prévias derivadas ficam locais; o fallback oferece a versão pública. A integração não depende de resolver essa distribuição.
