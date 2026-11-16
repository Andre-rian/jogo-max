# PROFANE ECHO — Fase F.0: auditoria e curadoria visual da HUD

Data: 15/11/2026. **Estudo entregue para escolha visual; nenhuma integração autorizada ou realizada.**

## Entrega e leitura das imagens

- [Comparativo A/B/C](previews/hud_f0_comparativo_abc_restrito.png): exploração e chefe, seis quadros nativos de 1280×720, prancha 3840×1560. Abrir os arquivos individuais a 100% para julgar os pixels.
- [A minimalista](previews/hud_f0_proposta_a_exploracao_restrito.png), [B medieval sombria](previews/hud_f0_proposta_b_exploracao_restrito.png), [C híbrida](previews/hud_f0_proposta_c_exploracao_restrito.png).
- Capturas reais: [exploração](previews/hud_f0_captura_exploracao_restrito.png), [combate comum](previews/hud_f0_captura_combate_restrito.png), [chefe](previews/hud_f0_captura_boss_restrito.png), [vida baixa](previews/hud_f0_captura_vida_baixa_restrito.png), [machado e buff da raiz](previews/hud_f0_captura_machado_raiz_restrito.png).
- [Estados e contraste](previews/hud_f0_legibilidade_estados_restrito.png), [sequência de combate real](previews/hud_f0_movimento_atual_restrito.png), [sprites medidos](previews/hud_f0_curadoria_sprites_restrito.png), [triagem Kibyra](previews/hud_f0_kibyra_triagem_restrito.png).
- Existem **15 mockups individuais**, seguindo `hud_f0_proposta_{a,b,c}_{exploracao,combate,vida_baixa,machado_raiz,boss}_restrito.png`.
- [Evidências](previews/hud_f0_evidencias.json): valores capturados, sala, zoom, equipamento e métricas de transparência. [Gerador offline](gerar_previews_f0.py).

Todas as imagens desta rodada ficam **apenas locais**, cobertas pela regra existente `docs/arte/previews/*restrito*.png`. Essa classificação conservadora inclui as capturas puras; não significa que todas contenham UI de terceiros restrita. Nenhum arquivo foi adicionado ao índice e nenhum commit foi criado. Capturas anteriores `hud_f0_atual_*` já existiam e foram preservadas, sem assumir sua procedência como evidência desta rodada.

## 1. Estrutura e dados reais

O ponto de entrada da interface é `ui/hud/hud.py:Hud`. `core/game_scene.py:Gamescene` cria o objeto, atualiza seus temporizadores e chama `hud.desenhar(tela, player, boss_atual)` em `desenhar`. Os componentes são:

| Arquivo / classe | Conteúdo e origem | Geometria atual em 1280×720 |
|---|---|---|
| `ui/hud/status.py:BarrasStatus` | `player.hp/hp_max`, `stamina/stamina_max`; espera de recarga por `stamina_delay` e `_frame_atual`; buff por `buff_stamina_duracao` | Painel (20,20), 256×44; medalhão raio 22; HP (72,24), 200×16; stamina (72,46), 200×10 |
| `ui/hud/pocao.py:SlotPocao` | `player.pocao.cargas/cargas_max`; tecla F, flash de uso e frasco vetorial | Slot (20,630), 52×52; cargas em círculos y=692, passo 16 |
| `ui/hud/ecos.py:IndicadorEcos` | `player.ecos`; símbolo procedural `ui.estilo.desenhar_eco_profano` | Centro do Eco (1082,678), raio solicitado 15; número a partir de x=1106, sem painel |
| `ui/hud/boss.py:BarraBoss` | `boss.nome`, `hp`, `hp_max`; valor visual suavizado e dano acumulado | Barra (440,660), 400×18; fundo (410,634), 460×54; nome y=638; dano x=848 |
| `ui/hud/mensagens.py:Mensagens` | Chamadas de objetos/cena para mensagens e interação | Mensagem central y=260, duração padrão 180 ticks; prompt contextual y=570 |
| `ui/hud/notificacao.py:NotificacaoItem` | Objeto item: nome, `icone`, quantidade; ícones desenhados proceduralmente | (470,600), 340×64; duração 210 desenhos, fade nos últimos 60 |
| `ui/hud/debug_painel.py:DebugPainel` | Estado, posição, velocidade, cooldown do dash, chão e stamina | x=1040, y=320; desativado por `settings.DEBUG=False` |

### Sistemas confirmados

- **Vida:** `Entity.receber_dano`, `Player`, combate central e poção alteram HP. Máximo inicial 200 = 50 + 10×15. **Vigor é atributo**, não recurso consumível nem terceira barra.
- **Stamina:** máximo inicial 130 = 30 + Resistência×10. Pulo, dash e ataques gastam stamina; `_atualizar_stamina` regenera após espera. Raiz Amarga, ID 4, acelera a regeneração por 180 ticks. Há indicador de buff na HUD.
- **Ecos:** quantidade funcional em `Player.ecos`, ganhos e perda na cena, recuperação em `DropEco.atualizar`, gasto em `MenuFogueira` e persistência em save. Não é preciso inventar um item/ID para trocar apenas o símbolo desse contador. A ressalva de D.1 sobre ausência de item Eco não implica ausência da moeda funcional.
- **Poção F:** objeto `Pocao` próprio com 3 cargas, cura de 40% do máximo e cooldown 90 ticks. O contador de cargas não é a quantidade do consumível ID 2 no inventário. Não unificar os dois dados na integração visual.
- **Armas:** Espada Longa ID 1 e Machado de Guerra ID 3 são equipáveis; `arma_equipada`, `arma_id`, `inventario['mao_direita']` e cálculo de dano existem. A HUD não tem slot permanente de arma; apenas notificação de coleta. Os mockups mantêm essa limitação.
- **Chefe:** `EsqueletoBoss` / Carrasco Esquelético, máximo 300 observado; `boss_atual` é fornecido pela cena. Existe também barra acima de inimigos no mundo, independente da HUD.

### Dados não exibidos e sistemas ausentes

Dados funcionais fora da HUD: arma equipada/dano/requisitos, quantidades de materiais e consumíveis, atributos e custo de evolução na fogueira, cooldown de poção, cooldown de dash (somente debug), duração numérica do buff e Ecos perdidos. Não acrescentados como slots ou barras neste estudo.

Não foi localizado sistema de mana nos módulos de jogo examinados. Slots de mão esquerda e armadura estão marcados como futuros em `Player.inventario`. Abissita e Nyxita têm arte aprovada, mas não constam dos cinco itens de `itens.json`. Não aparecem nas propostas. Não foi criado estudo de recursos futuros.

## 2. Renderização, resolução e riscos atuais

`settings.py` fixa 1280×720 e 60 FPS. A cena é desenhada numa superfície de tamanho `Screen / camera.zoom` e ampliada com `pygame.transform.scale`; zoom normal 1,35 e alvo de chefe 1,0 com transição. **HUD é desenhada depois dessa escala**, em coordenadas de tela, sem zoom da câmera. As fontes são `SysFont`, com fallback do sistema: texto 14, título 18/28; não são fontes pixel-perfect garantidas entre máquinas.

Inventário e menu de fogueira são desenhados antes da HUD; pausa e morte ficam acima. Layout usa constantes importadas de `settings`, sem anchors responsivos baseados na superfície recebida. Fullscreen/escalas externas precisam de teste específico.

Problemas observados no código, sem correção nesta fase:

1. Notificação (y=600..664) intercepta fundo/nome/barra do chefe (y=634..688). O chefe é desenhado depois e pode cobri-la.
2. HP só limita proporção mínima, não máxima; divisão pressupõe máximo positivo. Stamina idem. Não transformar essas observações em alteração de regras nesta fase.
3. Borda da stamina é desenhada dentro do ramo de preenchimento: desaparece quando vazia. Aviso `...` pode ocupar a região da vida.
4. Barra do chefe pinta valor suavizado e real com a mesma cor; a distinção de dano atrasado é pobre. Estado visual não é explicitamente reiniciado por identidade do chefe e inicializa quando display==0.
5. Ecos e prompts sem fundo dependem do cenário. Número longo pode extrapolar a margem direita. Cargas adicionais poderiam ultrapassar o slot.
6. Notificação e animação dos Ecos avançam em `desenhar`, enquanto outros temporizadores avançam em `atualizar`; capturar/redesenhar influencia o estado visual. O gerador copia o mundo no mesmo desenho, evitando novo tick para cada proposta.

## 3. Método e capturas controladas

Renderização real de `Gamescene.desenhar` com SDL dummy, sem janela e sem importar `main` ou instanciar `Savemaneger`. Não são pinturas de cenários nem screenshots de uma sessão manual. O gerador importa os módulos reais e usa os mapas, sprites, física, ataques e HUD existentes. Não há callback de salvamento. Áudio não é inicializado pelo gerenciador do jogo.

| Cenário | Preparação e resultado |
|---|---|
| Exploração | Cena normal, sala 1, sem arma, 12 atualizações e câmera estabilizada; 200/200 HP, 130/130 stamina, 3 cargas, 0 Ecos |
| Combate comum | Arena de teste já existente, chefe removido somente da instância; espada, aproximação do esqueleto e ataque real; 120/130 stamina |
| Vida baixa | Mesmo cenário: estado controlado em memória de 40/200 HP, 26/130 stamina, 1/3 cargas, 137 Ecos; não é alegado que esses valores resultaram de dano/coleta nessa sessão |
| Machado/raiz | Equipar ID 3, usar ID 4 pelo método real e disparar notificação existente do machado em memória; buff 180; demonstra ausência de indicador permanente de arma |
| Chefe | Sala 5 real, posição de entrada explícita e aproximação controlada, ataque de espada; chefe 290/300 e dano 10; câmera em transição, zoom ~1,1399 |

O carregamento da sala 5 sem posição explícita falhou: `_resolver_spwan` chama `_spwanar_fallback`, método ausente. O teste prosseguiu com o parâmetro existente `posiçao_spwan`; nenhum código funcional foi corrigido. O mapa da arena tem fundo preto: isso é o renderer real, não apagamento de fundo no mockup.

Para as propostas, um hook temporário na **instância em memória** copia a superfície imediatamente antes de desenhar a HUD; a HUD original é então desenhada normalmente e capturada. Os mockups compõem novos elementos nessa cópia limpa, sem apagar partes do cenário ou alterar arquivos do jogo. Números e estados vêm do mesmo snapshot.

## 4. Curadoria técnica

Prefixos de origem:

- **AB:** `assets/sprites/_entrada/ui/abyssowl_gothic_pixel_ui/split_assets/frames and bars/`
- **LY:** `assets/sprites/_entrada/itens/lygame_dark_fantasy/UI/`
- **KB:** `assets/sprites/_entrada/ui/kibyra_medieval_fantasy_ui/UI Icons/`
- **Beast:** `assets/sprites/_entrada/itens/beast_crafting_materials/resources_outlined.png` e `beast_weapons_tools/weapon_and_tools_outlined.png`.

| ID | Arquivo | Dimensão | Transparência medida / avaliação |
|---|---|---|---|
| AB026 | `54x16px_bar_01.png` | 54×16 | 420 transparentes; alternativa compacta, cantos mais pesados |
| **AB027** | `54x20px_bar_02.png` | 54×20 | 500 transparentes; escolhida para B, pontas ornamentadas legíveis em 2× |
| AB028 | `56x16px_bar_02.png` | 56×16 | 464 transparentes; ponta afilada, alternativa horizontal |
| AB029 | `60x24px_bar_01.png` | 60×24 | 480 transparentes; maior massa ornamental, desaconselhada para as duas barras pequenas |
| AB030–032 | `bar_fill_01.png` a `bar_fill_03.png` | 4×6 cada | Todos os 24 pixels opacos; texturas para repetição, sem 9-slice; paleta dourada exige remapeamento por recurso |
| LY014 | `ProgressBar.png` | 42×6 | Todos os 252 pixels opacos; preenchimento candidato, preservar/repetir região central |
| **LY015** | `ProgressTrack.png` | 48×12 | Todos os 576 pixels opacos; escolhido para C, desenhar preenchimento depois do trilho |
| **M095** | `pocao_vida.png` final; célula Beast (0,10) | 24×24 | 267 opacos; recomendado para slot F, sem confundir cargas com estoque |
| M067 | `raiz_amarga.png` final; célula (8,6) | 24×24 | 326 opacos; candidato para futura representação do buff existente |
| A017 | `espada_longa.png` final; célula armas (0,2) | 24×24 | 269 opacos; notificação de espada, sem propor seletor novo |
| **A045** | `machado_guerra.png` final; célula armas (4,5) | 24×24 | 331 opacos; usado na notificação dos mockups |
| **Eco D.1** | `docs/arte/propostas_recursos/eco_profano_d1.png` | 24×24 | 196 opacos, 380 transparentes; recomendado para o contador já funcional |

Os arquivos finais Beast ficam em `assets/sprites/itens/consumiveis/` e `equipamentos/`. Nenhum dos candidatos medidos tem alpha intermediário. Os IDs são os do catálogo, não novos IDs de itens.

**9-slice e pixel-perfect:** para barras horizontais, 3-slice é suficiente e evita deformar a altura. B preserva 12 px de cada ponta de AB027, repete coluna central e aplica 2× inteiro (altura 40). C preserva 5 px de LY015 a 1× (altura 12). São margens experimentais demonstradas nas prévias, não metadados oficiais de slice. AB026/028/029 exigem validar separadamente a largura das pontas antes de escolher margens. 9-slice seria útil para painéis bidimensionais, não para texturas 4×6 ou ícones. Nenhuma escala fracionária/interpolação foi aplicada aos sprites das propostas. Preenchimentos dos mockups são cores sólidas; AB030–032 e LY014 foram medidos e catalogados, mas **não aplicados** às barras propostas.

**Kibyra:** triagem dos 64 ícones do primeiro conjunto. KB009 (`icon9.png`, poção), KB017 (`icon17.png`, espada), KB020 (`icon20.png`, escudo) e KB023 (`icon23.png`, elmo) medidos, 32×32, alpha binário. Poção e espada são alternativas sem vantagem sobre Beast aprovado; escudo/elmo têm compatibilidade temática, mas não representam equipamento funcional atual, portanto ficam fora dos mockups. O dourado saturado e as bases quadradas destoam da paleta fria; nenhum KB recomendado para integração F.1 neste momento. Não se apresenta essa triagem como revisão exaustiva dos 208 arquivos.

**Eco original:** preservados os 196 pixels opacos, núcleo ciano, corpo violeta vazado e fragmentos. Usado 1× no contador, sem redesenho ou criação de item. Mantém identidade D.1 e diferencia Ecos do verde de stamina e vermelho de vida.

## 5. Comparação visual e legibilidade

| Critério | A — Minimalista | B — Medieval sombria | C — Híbrida |
|---|---|---|---|
| Estrutura | Retângulos simples, borda 1 px | AB027 em metal frio, molduras duplas ornamentadas | LY015, grafite, detalhe violeta e pequenos cantos |
| Painel superior | 252×88 | 308×116 | 276×88 |
| Barras | 228×12, interior 8 px | 284×40, interior 12 px | 252×12, interior 6 px |
| Ocupação dos três painéis permanentes | ~4,30% | ~5,77% | ~4,53% |
| Vantagem | Leitura direta e menor ornamentação | Identidade medieval mais evidente | Maior proximidade com inventário/menu frio |
| Custo | Menos personalidade | Mais cenário coberto; duas barras ornamentadas disputam atenção | Interior fino demanda avaliação humana a 100% |

Percentuais são áreas retangulares dos painéis, excluindo ornamentos externos e texto; barra/painel de chefe acrescenta ~3,98 pontos percentuais em todas. Não são medições de pixels opacos. Painéis existentes são menores: A é minimalista entre as propostas, não uma redução garantida da área atual.

Todos conservam vida vermelha, stamina verde, tecla F, cargas, Ecos e dados do chefe. As cargas passam de bolinhas para `atual / máximo`, reapresentando a mesma informação. Cruz decorativa é removida. Notificação proposta sobe para y=528..592, deixando intervalo até o painel de chefe y=621; não foi acrescentado atalho para arma.

**Estados:** prancha nativa apresenta 100%, 50%, 10% e 0%, em fundo escuro e claro sintéticos explicitamente separados das capturas reais. Valor numérico fora do preenchimento e extensão da barra distinguem os estados sem depender somente de cor. Trilho permanece visível no zero. As cores sólidas sacrificam textura em favor da leitura; são decisão de estudo, não requisito final.

**Contraste:** painéis opacos grafite isolam texto e barras do fundo claro/escuro. Vermelho/verde são diferenciados também por posição, tamanho e rótulo de vida. Os detalhes azuis e roxos ficam na estrutura, evitando sugerir mana. Avisos fora do painel e o buff ainda precisam de acabamento: são menos protegidos do fundo que os valores principais.

**Sobreposição:** nas capturas selecionadas, painéis ficam afastados dos corpos centrais dos combatentes. Cobrem cenário nas bordas, como escadas e paredes; a proposta B cobre mais. Isso não garante ausência de obstrução em todas as salas ou posições. A nova notificação evita a colisão geométrica com o chefe; a coexistência de notificação, prompt e mensagem central ainda requer cenário dedicado em F.1.

**Movimento:** seis frames reais espaçados por oito atualizações mostram combate/animação e mudança de câmera sem deslocar a HUD. A prancha reduz esses frames para 640×360 apenas para leitura da sequência; não serve para julgar pixel-perfect. As propostas foram avaliadas como imagens estáticas sobre quadros reais, não implementadas para jogar. Teste perceptivo em movimento a 60 FPS, fullscreen e diferentes monitores permanece pendente.

Recomendação de direção: **C**, pelo parentesco com o inventário e uso contido de roxo espectral. Considerar interior de barra mais alto caso a leitura a 100% pareça fina. A é alternativa simples com menos dependência de licença; B serve caso se prefira maior ornamentação. **A escolha permanece com o usuário.**

## 6. Licenças e distribuição

Verificação em 15/11/2026; não confundir autorização de uso em jogo com autorização de distribuir fontes do pack em repositório.

- [AbyssOwl — página oficial](https://abyssowl.itch.io/gothic-pixel-ui): incentiva modificação, extensão e repetição. A edição local free v1.0.2 não traz licença formal; a página consultada não resolve os termos de redistribuição. AB continua local; confirmar termos antes de promover.
- [lygame — origem registrada](https://lygame.itch.io/dark-fantasy-free-pixel-art-assets): registro local em `ASSETS_UI_ORIGENS.md` informa uso comercial/não comercial permitido e redistribuição proibida. Nesta rodada a consulta web falhou; **não houve nova confirmação independente**. Manter imagens e assets locais.
- [Kibyra — página oficial](https://kibyra.itch.io/free-medieval-fantasy-ui-pack) e `Readme.txt`: uso pessoal/comercial permitido, crédito apreciado, redistribuição/revenda dos arquivos **as-is** proibida. O catálogo antigo descreve proibição também de modificados, mas esse alcance não aparece no Readme consultado. Não presumir autorização adicional; respeitar a instrução do usuário de manter prévias restritas fora do Git.
- [Beast Crafting Materials](https://beast-pixels.itch.io/crafting-materials): CC0 confirmado na página, abrange M095/M067. Armas A017/A045: `beast_weapons_tools/LICENSE.txt` estabelece CC BY 4.0, exigindo atribuição a Beast Pixels, link da licença e indicação de alterações. As prévias ampliam A045, preservando a arte. Crédito: **Weapons and Tools, Beast Pixels, CC BY 4.0**; [autor](https://beast-pixels.itch.io/), [licença](https://creativecommons.org/licenses/by/4.0/).
- Eco D.1: original do projeto conforme relatório D.1, sem pixels de lygame. Nenhum novo material externo foi baixado.

## 7. Verificação, limites e futura F.1

- Gerador executado com Python 3.14.7 e pygame-ce 2.5.7 já instalados; nenhuma dependência adicionada. Pillow não está instalado e não foi necessário.
- Cinco capturas reais, quinze propostas, comparativo, estados claros/escuros, sequência e curadoria gerados. Imagens inspecionadas visualmente; corrigida a ordem de composição offline do LY015 opaco e substituído glifo de buff não disponível por traço procedural.
- Conferência SHA-256 de **5.293 arquivos preexistentes** de código, PNGs, JSONs, banco e log: nenhum alterado pelo gerador. Inclui `saves.db`, `itens.json`, `jogo.log` e assets originais. Manifesto inicial em `previews/hud_f0_integridade_inicio.json`.
- `git diff --check`: sem erros. Alterações preexistentes no working tree preservadas. Nenhum teste de balanceamento foi necessário para uma entrega documental; não se alega execução da suíte pytest nesta fase.
- Conferência final: 25/25 imagens novas ignoradas por `git check-ignore`; todos os links locais deste relatório existem.
- Avisos preexistentes no carregamento: perfil PNG iCCP, ausência de camada `plataformas` na sala 1 e inimigo sem tipo no objeto 8. Registrados, sem consertos fora do escopo.
- Pendências: escolha A/B/C; termos de AbyssOwl e reconfirmação de lygame; avaliação humana a 100% e em movimento; resoluções/fullscreen; números grandes; simultaneidade de mensagens/loot/boss; vida do chefe em estados cheio/intermediário/baixo/zero e transição entre chefes. A matriz atual cobre estados das barras do jogador, não todos esses estados do chefe.

Depois da escolha, F.1 poderá integrar apenas apresentação: separar geometria de dados, preservar ordem e temporizadores, garantir clipping de preenchimento, cache de superfícies, anchors e fallback sem packs locais. Não ligar o slot F ao estoque de ID 2, não criar mana nem transformar Vigor em recurso. A troca do símbolo de Ecos pode consumir a arte D.1 sem novo item. Qualquer correção funcional identificada nesta auditoria deve ser discutida em escopo próprio.
