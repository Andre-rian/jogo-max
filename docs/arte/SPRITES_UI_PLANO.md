# PROFANE ECHO — Plano de sprites para UI, inventário, HUD e menus

> **Documento de referência e instruções para agente de desenvolvimento (Python + Pygame)**  
> Atualizado em 15/11/2026 — revisão 3 (Fase C concluída)  
> **Estado:** a Fase C (inventário) foi concluída; as demais telas seguem o planejamento abaixo. Consulte `RELATORIO_FASE_C_SPRITES.md` para o resultado executado.  
> **Decisão atual:** LY005 1× aprovado e adotado como moldura preferencial do inventário, com fallback automático. Pacotes originais continuam locais e fora do Git quando a licença restringir redistribuição.

## 1. Contexto do projeto

**Profane Echo** é um jogo 2D de fantasia sombria (*dark fantasy*), em pixel art, com exploração lateral e referências de atmosfera a soulslikes/metroidvanias. O protagonista é um cavaleiro aprisionado em um castelo e a identidade narrativa gira em torno do **Eco Profano**, uma essência ligada a memórias e experiências de seres.

O objetivo desta frente é **dar acabamento visual à interface existente**, substituindo elementos provisórios por sprites pixel art consistentes, sem reconstruir o sistema de menu/inventário nem alterar mecânicas. A identidade visual já presente usa preto, tons escuros, azul-acinzentado e roxo espectral.

### Telas atuais descritas pelo responsável

**Menu / seleção de saves:**
- Título grande “PROFANE ECHO”; composição de fundo escuro com círculos roxos grandes e partículas.
- Três caixas de save (“Slot 1/2/3 — Novo Jogo”) com borda fina.
- Seleção destacada e ajuda de teclado na parte inferior.
- Problemas/oportunidades: o círculo roxo pode competir com o título e os saves; contraste do texto secundário; molduras ainda simples; símbolos de teclas aparecem como quadrados em alguns pontos.

**Inventário:**
- Abas: **Equipamentos**, **Itens**, **Chaves** e **materias** (corrigir exibição para **Materiais**, caso apropriado).
- Coluna de equipamento: mão direita, mão esquerda e armadura.
- Área principal ampla atualmente sem ícones e frequentemente com “Nenhum item”.
- Área de status com nível, vigor, resistência, força, destreza.
- Rodapé com instruções de navegação/TAB/ESC; alguns símbolos de teclado não renderizam corretamente.
- Oportunidade: criar grade de itens e ícones, estados dos slots, descrição do item selecionado, sem remover abas, status nem controles existentes.

> **Importante:** as imagens das telas foram enviadas na conversa; o agente deve analisar as versões atuais no repositório e não assumir que uma captura antiga representa fielmente o código atual.

## 2. Objetivos e limites

### Objetivos
1. Unificar o estilo dos ícones de itens, equipamentos, materiais e recursos.
2. Introduzir sprites de slots, seleções, botões, abas e molduras da interface.
3. Adicionar prompts visuais de teclado; manter preparado o suporte futuro a controle.
4. Garantir boa legibilidade, escala pixel-perfect e desempenho no Pygame.
5. Manter mapeamento consistente entre dados de item e ícone exibido.
6. Registrar origem e licenças dos assets efetivamente utilizados.

### Fora do escopo imediato
- Refatoração geral do sistema de UI.
- Modificação de combate, inventário lógico, salvamento, movimentação ou áudio.
- Introdução obrigatória de novas telas, habilidades, suporte funcional a gamepad ou novos tipos de item.
- Implementação completa da HUD antes da conclusão do inventário.
- Trocar todos os textos por uma fonte decorativa sem teste de legibilidade e acentos.

### Restrições do agente
- **Inspecionar o repositório primeiro:** descobrir arquivos e classes existentes de menu, inventário, HUD, itens, caminhos de assets, resolução e escala.
- **Não presumir que os packs foram baixados ou aprovados.** Os links abaixo são candidatos, não um inventário local. O responsável fará a primeira triagem e informará os elementos selecionados.
- **Não baixar ou modificar assets automaticamente sem autorização e licença verificada.** Se arquivos não existirem, preparar estrutura/mapeamento e relatar pendências.
- Preservar a UI e suas funcionalidades atuais; implementação incremental e reversível.
- Sem novas dependências obrigatórias; usar Pygame e código existente.
- Sem commits, renomeações massivas ou exclusões de assets sem autorização.
- Não incorporar arquivos cujos direitos de uso/redistribuição estejam incertos.

## 3. Direção de arte proposta

**Estilo:** pixel art medieval sombria, decadente, sóbria, legível. Referências de materiais: ferro envelhecido, pedra escura, pergaminho gasto e brilho espectral.

**Paleta-base indicativa** (não impor hexadecimais antes de avaliar os sprites atuais):
- Preto e grafite para áreas principais.
- Azul-acinzentado para divisórias/bordas discretas.
- Roxo profundo e lilás dessaturado para magia, seleção e Eco Profano.
- Branco envelhecido/cinza claro para textos.
- Dourado apagado apenas para sinalização especial.

**Regras visuais:**
- Silhueta do item reconhecível em tamanho pequeno.
- Bordas e brilhos não podem competir com a informação.
- Seleção deve ser clara mesmo sem depender apenas de cor (contorno, marca ou mudança de forma).
- Evitar misturar ícones excessivamente diferentes em contorno, iluminação, perspectiva e densidade de detalhe.
- Preservar fundo transparente e pixels nítidos.

## 4. Packs candidatos e papéis sugeridos

| Pack / criador | URL | Uso sugerido | Situação de licença / observação |
|---|---|---|---|
| **Crafting Materials — Beast Pixels** | https://beast-pixels.itch.io/crafting-materials | Materiais, minerais, gemas, base para Umbrita/Abissita/Nyxita | **CC0**, conforme página do criador. Ícones com versões/contornos e arquivo-fonte. |
| **Weapons and Tools — Beast Pixels** | https://beast-pixels.itch.io/weapons-and-tools | Ícones de equipamentos, ferramentas, escudos | **CC BY 4.0**; crédito obrigatório. Ícones-base 24×24 e variações. |
| **Free Assorted Icons — Quintino Pixels** | https://quintino-pixels.itch.io/assorted-icons | Itens diversos, consumíveis, chaves, complementos de inventário | **CC0**, conforme título/página. Conferir conteúdo do pacote baixado. |
| **Free Pixel Art Skill Icons — Quintino Pixels** | https://quintino-pixels.itch.io/free-pixel-art-skill-icons-pack | Habilidades/status no futuro | **ATENÇÃO:** a descrição diz que crédito não é necessário, mas o metadado da página indica **CC BY 4.0**. Registrar como **licença a esclarecer** e, por prudência, dar crédito até confirmar com o autor. Tamanhos 24/48/96 px. |
| **Raven Fantasy Icons — Clockwork Raven** | https://clockworkraven.itch.io/raven-fantasy-icons | Biblioteca complementar para itens raros/especiais | A página distingue pacote grátis e premium e regras específicas para uso pessoal e comercial. **Conferir o escopo exato da licença para a edição utilizada antes de integrar.** Não presumir acesso ao conteúdo premium. |
| **Antiquity Print — SciGho** | https://ninjikin.itch.io/font-antiquity-script | Títulos secundários, pergaminhos, textos especiais | **CC BY 4.0**; requer crédito. Arquivos TTF e spritesheet. Testar caracteres em português (ã, ç, é etc.). Não substituir a fonte principal sem testes. |
| **Pixel Keyboard UI Buttons — greedy_toad** | https://greedy-toad.itch.io/pixel-keyboard-ui-buttons | Prompts de teclas; estados pressionado/solto | PNG/Aseprite. **Licença não está claramente especificada na página consultada**: confirmar antes de integrar ou redistribuir. |
| **Gamepad UI / Controller Prompts — greatdocbrown** | https://greatdocbrown.itch.io/gamepad-ui | Prompts de teclado/mouse e, futuramente, controles | **CC0**, conforme página consultada anteriormente. Há opção de download gratuito; usar somente os arquivos efetivamente disponibilizados pela edição baixada. **Preferência inicial para prompts.** |
| **Gothic Pixel UI — AbyssOwl** | https://abyssowl.itch.io/gothic-pixel-ui | **Candidato principal** a molduras do inventário, slots, barras, bordas e painéis do menu | Há edição gratuita; conteúdo e condições de uso da edição escolhida devem ser conferidos antes de integrar. **Prioridade de avaliação visual: alta.** |
| **Free Medieval Fantasy UI Pack — Kibyra** | https://kibyra.itch.io/free-medieval-fantasy-ui-pack | Botões, divisores, componentes de HUD e complementos de UI | Alternativa para preencher lacunas do Gothic Pixel UI; confirmar licença e conteúdo do download. Não misturar elementos com estilos conflitantes. |
| **Dark Fantasy Free Pixel Art Assets — lygame** | https://lygame.itch.io/dark-fantasy-free-pixel-art-assets | Ícones extras, objetos e eventuais componentes de UI | Recurso complementar, não necessariamente substituto dos Beast Pixels. Conferir a licença e o conteúdo efetivamente incluído. |
| **Xianxia Pixel UI — ruins0707** | https://ruins0707.itch.io/xianxia-pixel-ui | Elementos especiais ou referências ornamentais opcionais | Estilo oriental distinto da identidade gótica principal. **Não** adotar como padrão global; avaliar caso a caso e verificar licença. |

### Decisões recomendadas (provisórias, sujeitas à triagem visual)
- **Identidade dos painéis e molduras:** testar **Gothic Pixel UI (AbyssOwl)** como referência principal. Não substituir a UI toda automaticamente.
- **Botões e componentes complementares:** considerar **Kibyra** somente quando harmonizar com AbyssOwl; evitar misturar bordas, espessuras e níveis de detalhe incompatíveis.
- **Ícones de itens:** manter **Beast Pixels** (armas/materiais) como base; **Quintino Assorted** e **lygame** como complementos. Comparar escala, contorno, iluminação e paleta antes de combinar.
- **Biblioteca de reserva:** **Raven Fantasy**, apenas após verificação da edição e licença aplicáveis.
- **Temática especial:** **Xianxia** é opcional para interfaces ritualísticas, memórias ou Ecos, e não para toda a interface medieval.
- **Teclas/controles:** **greatdocbrown** na edição gratuita efetivamente disponível; **greedy_toad** como alternativa com licença conferida. São prompts de entrada, **não** substitutos para botões/molduras de UI.
- **Fonte:** Antiquity Print apenas como teste para textos especiais, sem comprometer acentos ou legibilidade.
- **Ícones de habilidades:** adiar até o sistema precisar deles.

### Estado das escolhas

| Área | Candidato preferencial | Estado |
|---|---|---|
| Inventário — moldura externa, abas e slots | AbyssOwl Gothic Pixel UI | **A avaliar após download** |
| Botões do menu e saves | AbyssOwl; Kibyra como complemento | **A avaliar após download** |
| Equipamentos e minérios | Beast Pixels | **A avaliar após download** |
| Consumíveis, chaves e itens secundários | Quintino Assorted; lygame | **A avaliar após download** |
| Prompts de teclado | greatdocbrown (versão gratuita) | **A avaliar após download** |
| Interfaces sobrenaturais especiais | Xianxia (opcional) | **Sem decisão** |

**Não presumir que algum pack contém todos os elementos planejados.** Só marcar uma escolha como definitiva após receber os arquivos reais, conferir uso permitido e visualizar as sprites na escala do jogo.

## 5. O que ainda falta procurar

Com os novos candidatos, há opções também para **molduras, painéis e botões**, mas **ainda não sabemos se cobrem todos os estados e dimensões necessários**. Essa lacuna só se fecha depois de inspecionar o conteúdo real dos downloads.

### Prioridade alta
- **Painéis/janelas redimensionáveis** com estética dark fantasy.
- **Bordas e molduras de slots de inventário** (vazio, selecionado, equipado e desabilitado).
- **Abas** (normal, selecionada e indisponível, se aplicável).
- **Botões do menu** com estados normal, selecionado/foco, pressionado e desabilitado.
- **Caixa de descrição/tooltip** com contorno legível.
- **Molduras dos slots de save**, mantendo os três slots e os textos existentes.

### Prioridade secundária
- Divisores, cursores, indicadores de raridade/quantidade, marcadores de item novo.
- Elementos de HUD: vida, Eco Profano, arma/item equipado, elementos futuros de recursos.
- Pequenos efeitos de seleção ou brilho espectral **discretos**.
- Ícones exclusivos da narrativa: Eco Profano e recursos de melhoria **Umbrita, Abissita e Nyxita**; adaptar/criar individualmente quando os packs não representarem bem o conceito.

### Critério técnico importante
Preferir painéis e molduras **9-slice / nine-patch**, cujos cantos mantêm tamanho constante enquanto bordas e miolo se expandem. Para pixel art, usar recorte e repetição ou escala inteira; evitar esticar elementos ornamentados indiscriminadamente. **Verificar se os packs baixados permitem 9-slice:** não presumir que toda moldura seja modular.

## 6. Estrutura de pastas PROPOSTA

**Atenção:** isto é uma proposta, não a árvore confirmada do repositório. Adaptar aos diretórios e convenções existentes, sem duplicar arquivos desnecessariamente.

```text
assets/
├── sprites/
│   ├── _entrada/                         # Pacotes originais, NÃO usados no jogo
│   │   ├── _inbox/                        # Downloads ainda sem classificação
│   │   ├── _revisar/                      # Arquivos ambíguos / não aprovados
│   │   ├── itens/
│   │   │   ├── beast_crafting_materials/
│   │   │   ├── beast_weapons_tools/
│   │   │   ├── quintino_assorted_icons/
│   │   │   ├── quintino_skill_icons/
│   │   │   ├── raven_fantasy_icons/
│   │   │   └── lygame_dark_fantasy/
│   │   ├── ui/
│   │   │   ├── abyssowl_gothic_pixel_ui/
│   │   │   ├── kibyra_medieval_fantasy_ui/
│   │   │   └── ruins_xianxia_pixel_ui/
│   │   ├── prompts/
│   │   │   ├── greatdocbrown_gamepad_ui/
│   │   │   └── greedy_toad_keyboard_ui/
│   │   ├── fontes/
│   │   │   └── antiquity_print/
│   │   └── README.md
│   │
│   ├── ui/
│   │   ├── menu/
│   │   │   ├── save_slots/              # normal, selecionado, indisponível
│   │   │   └── detalhes/
│   │   ├── inventario/
│   │   │   ├── paineis/
│   │   │   ├── slots/
│   │   │   ├── abas/
│   │   │   └── tooltips/
│   │   ├── botoes/                     # Estados visuais
│   │   ├── prompts/
│   │   │   ├── teclado/
│   │   │   └── controle/               # Reservado, não significa suporte ativo
│   │   ├── hud/
│   │   └── cursores/
│   │
│   ├── itens/
│   │   ├── equipamentos/
│   │   ├── consumiveis/
│   │   ├── chaves/
│   │   ├── materiais/
│   │   ├── ecos/
│   │   └── _default/                  # Ícone para item sem sprite
│   │
│   ├── habilidades/                   # Somente quando necessário
│   └── fx_ui/                         # Efeitos visuais opcionais
│
├── fontes/                             # Ou usar pasta de fontes JÁ existente
└── ...                                 # Preservar sprites de personagens/cenários

docs/
└── arte/
    ├── SPRITES_UI_PLANO.md            # Este documento, se adotado no repositório
    ├── ASSETS_UI_ORIGENS.md           # Autor, URL, versão, licença, crédito
    └── INVENTARIO_SPRITES.md          # Item/elemento → arquivo correspondente
```

**Nota sobre `_entrada/`:** semelhante à triagem de sons, guardar fontes e pacotes originais ali até inspeção. **Não renomear sprites dentro dos pacotes originais e não misturar arquivos de autores diferentes.** A categoria (`itens`, `ui`, `prompts`, `fontes`) é para triagem apenas; os arquivos aprovados vão para a árvore final, sem copiar o pack inteiro. Contudo, pacotes com restrição de redistribuição podem precisar ficar **fora do Git** (por exemplo, em pasta local ignorada). Somente versionar o que as licenças permitirem; não copiar uma coleção premium inteira para o repositório público.

### Nomes de arquivos finais

```text
ui/inventario/slots/slot_normal.png
ui/inventario/slots/slot_selecionado.png
ui/inventario/slots/slot_equipado.png
ui/inventario/slots/slot_desabilitado.png
ui/menu/save_slots/save_normal.png
ui/menu/save_slots/save_selecionado.png
ui/botoes/botao_normal.png
ui/botoes/botao_selecionado.png
itens/consumiveis/pocao_vida.png
itens/materiais/umbrita.png
itens/materiais/abissita.png
itens/materiais/nyxita.png
itens/ecos/eco_profano.png
itens/_default/item_desconhecido.png
```

Padrão: `snake_case`, sem acentos/espaços, nomes semânticos. **Não inventar nomes de itens ou identificadores no código**: alinhar ao cadastro real de itens.

## 6-A. Fluxo de download, escolha e aprovação pelo responsável

1. **Baixar somente os packs de interesse**, inclusive versões grátis disponíveis. Não é obrigatório adquirir edições pagas nem baixar tudo.
2. **Guardar cada pacote original separado**, preferencialmente como recebido (arquivos-fonte, PNGs, spritesheets, README e licença), na respectiva pasta de `_entrada/` ou, se restrito, em armazenamento local fora do Git.
3. **Inspecionar as prévias reais:** identificar imagens úteis, tamanho nativo, transparência, spritesheet, 9-slice possível e arquivos legíveis na escala do jogo.
4. **Fazer seleção visual antes de integrar:** anotar para cada candidato `pack / arquivo original / uso desejado / aprovado? / observação`. Pode anexar capturas ou indicar nomes de arquivos ao agente.
5. **Conferir licença da versão baixada e registrar** autor, URL, licença, condições de crédito e possíveis limites de redistribuição; não considerar a palavra “gratuito” como sinônimo de licença livre.
6. **Criar cópias aprovadas** em `assets/sprites/ui/`, `assets/sprites/itens/` etc., renomeando-as sem alterar originais. Não versionar pacotes completos por conveniência.
7. **Integrar em etapas** após autorização explícita: primeiro poucos ícones, depois slots/painéis e prompts, só então HUD e polimento.
8. **Testar no jogo** (legibilidade, estados normal/selecionado, escalonamento, cache, fallback, desempenho e navegação) antes de declarar a escolha definitiva.

### Modelo simples de seleção

| Pacote | Arquivo / região da spritesheet | Tela / função desejada | Estado | Licença verificada? |
|---|---|---|---|---|
| AbyssOwl | *(preencher após baixar)* | Moldura do inventário | Em avaliação | Não confirmado |
| AbyssOwl ou Kibyra | *(preencher)* | Botão de save selecionado | Em avaliação | Não confirmado |
| Beast Pixels | *(preencher)* | Espada equipada | Em avaliação | Não confirmado |
| greatdocbrown | *(preencher)* | Prompt de Enter / Esc / Tab | Em avaliação | Não confirmado |

O agente **não deve escolher arbitrariamente** todos os elementos de um pack. Se a seleção ainda não foi informada, produzir inventário de opções e proposta visual, mas aguardar a escolha do responsável para trocas amplas de UI.

## 7. Resolução, importação e renderização (Pygame)

- **Proposta inicial:** usar 24×24 px como referência visual para ícones quando compatível com o pacote. **Não** converter todos os arquivos cegamente: packs podem ter 16×16, 24×24, 32×32 etc.
- Slots exibidos em aproximadamente 40×40 ou 48×48 px são uma **hipótese de layout**, a validar na resolução real do jogo.
- Carregar PNG com transparência; usar `convert_alpha()` depois de inicializar o display.
- Manter cache de `Surface` para não carregar ou escalar imagem a cada frame.
- Usar `pygame.transform.scale()` com **nearest-neighbor** e, de preferência, fatores de escala inteiros; não usar `smoothscale()` para pixel art.
- Se for spritesheet, descobrir tamanho do tile, margens e espaçamentos; recortar corretamente. Não assumir que uma imagem inteira corresponde a um único item.
- Preservar alpha/transparência e evitar halos nas bordas.
- Oferecer fallback (`item_desconhecido.png`) quando o arquivo não existir, gerando aviso controlado em vez de travar.
- Desenhar molduras/slots separadamente dos ícones de itens; não embutir o item na moldura.
- Suportar vários estados por componente: normal, selecionado, pressionado, desabilitado/equipado conforme aplicável.
- Para fontes, verificar a legibilidade em tamanhos reais e o suporte a caracteres `á à â ã é ê í ó ô õ ú ç` e símbolos usados nos menus; manter fonte de fallback.

### Mapeamento entre dados e sprites

Inspecionar como os itens são definidos atualmente. Preferir um **mapa explícito** por ID existente, por exemplo:

```python
# EXEMPLO ILUSTRATIVO — IDs e caminhos devem ser adaptados ao código real.
ICONE_POR_ITEM = {
    "umbrita": "assets/sprites/itens/materiais/umbrita.png",
    "abissita": "assets/sprites/itens/materiais/abissita.png",
    "nyxita": "assets/sprites/itens/materiais/nyxita.png",
}
```

Não associar ícones por nome de exibição, índice de inventário ou posição na spritesheet sem um registro claro. Não alterar as regras de equipamento, quantidade ou salvamento.

## 8. Proposta de composição do inventário

**Manter:** abas, coluna de equipamentos, área de status, funções de navegação, troca de aba, seleção, equipar/usar/voltar.

**Acrescentar em etapas:**
1. Ícones e molduras dos slots de mão direita, mão esquerda e armadura.
2. Grade de itens na área principal, respeitando abas e quantidade real de itens.
3. Contorno/marcador de seleção bem visível.
4. Nome, tipo e descrição do item selecionado em painel próprio, sem cobrir atributos.
5. Ícone de fallback para itens não mapeados.
6. Prompts gráficos de teclado substituindo caracteres que viram quadradinhos.

**Não assumir automaticamente** 4 colunas, 16 slots ou qualquer contagem fixa: dimensionar a grade a partir da resolução, do painel existente e das estruturas de dados do inventário.

## 9. Proposta de composição do menu inicial

- Preservar os três slots de save e as informações de jogo salvo/novo jogo.
- Testar moldura tematizada nos slots, incluindo estado selecionado.
- Melhorar contraste de textos auxiliares, sem comprometer a estética escura.
- Reavaliar a interferência visual dos círculos roxos no título e no conteúdo; não remover a arte automaticamente.
- Substituir símbolos ilegíveis das instruções por prompts gráficos claros.
- Priorizar legibilidade em tela cheia e na resolução real; suportar teclado.

## 10. HUD e identidade do Eco Profano (etapa posterior)

O **Eco Profano** deve ter símbolo e linguagem visual próprios: núcleo/energia espectral azul-violeta, poucos pixels, reconhecimento rápido. Se a HUD exibir um indicador que muda conforme a quantidade de Ecos, projetar estados discretos sem depender de efeitos pesados.

Os três recursos de melhoria — **Umbrita (+1 a +4), Abissita (+5 a +8), Nyxita (+9)** — merecem ícones diferenciados por silhueta ou detalhes, não apenas recolorações indistinguíveis. Não implementar novas regras de upgrade aqui.

## 11. Ordem recomendada de trabalho

### Etapa 0 — Auditoria sem alterações
- [ ] Localizar módulos/classes/telas reais de UI e inventário.
- [ ] Inventariar imagens e fontes já presentes.
- [ ] Descobrir resoluções, escalas, convenções e sistema de carregamento.
- [ ] Confirmar quais pacotes e arquivos foram efetivamente disponibilizados e **quais foram escolhidos pelo responsável**.
- [ ] Comparar AbyssOwl, Kibyra e outros UI packs em uma tela de teste antes de adotar molduras globais.
- [ ] Criar tabela de origem/licença, incluindo atribuições obrigatórias.
- [ ] Tirar capturas de referência das telas atuais.

### Etapa 1 — Ícones de inventário (**primeira implementação recomendada**)
- [ ] Selecionar uma família visual consistente.
- [ ] Mapear 3–6 itens **já existentes** no inventário, idealmente poção, equipamento, chave, recurso/eco e materiais quando disponíveis no código.
- [ ] Integrar carregamento/cache e ícone de fallback.
- [ ] Exibir os ícones sem alterar dados nem lógica de interação.
- [ ] Testar inventário vazio, equipado, itens empilhados e alternância de abas.

### Etapa 2 — Slots, seleção e painéis
- [ ] Comparar primeiro Gothic Pixel UI (AbyssOwl) e Kibyra, preservando unidade visual.
- [ ] Escolher sprites com normal/selecionado/equipado/desabilitado.
- [ ] Testar 9-slice para painéis; preservar dimensões e input.
- [ ] Introduzir descrição do item selecionado se o modelo de dados já oferecer descrição.

### Etapa 3 — Menu e prompts
- [ ] Adaptar molduras dos 3 saves.
- [ ] Incluir sprites de prompts para teclado, incluindo TAB/ENTER/ESC conforme as teclas verdadeiras.
- [ ] Revisar contraste, alinhamentos e texto truncado.

### Etapa 4 — HUD e polimento
- [ ] Definir iconografia do Eco Profano e recursos.
- [ ] Tratar animações discretas e transições sem penalidade de performance.
- [ ] Avaliar HUD e suporte visual a gamepad separadamente.

## 12. Critérios de aceitação para testes

- [ ] Inventário abre/fecha e troca de abas normalmente.
- [ ] Ícones correspondem ao **ID real** de cada item.
- [ ] Item sem ícone não trava o jogo.
- [ ] Itens/equipamentos preservam seleção e quantidade corretas.
- [ ] Slots selecionados/equipados/desabilitados são distinguíveis.
- [ ] Saves continuam aparecendo e sendo selecionados corretamente.
- [ ] Texto permanece legível; nomes longos não ultrapassam o painel.
- [ ] Nenhuma tecla essencial é apresentada como um quadrado vazio.
- [ ] Ícones não ficam borrados, deformados ou com transparência quebrada.
- [ ] Carga de imagens não é repetida a cada frame.
- [ ] Testes automatizados existentes continuam passando; adicionar testes locais para fallback/cache quando conveniente.
- [ ] Cada asset integrado tem origem e licença documentadas.
- [ ] Nenhuma funcionalidade preexistente foi removida.

## 13. Entregáveis esperados do agente

1. Relatório curto de auditoria com caminhos reais das classes e telas.
2. Lista dos arquivos de sprite disponíveis, selecionados pelo responsável e pendentes (não inventar conteúdo de packs não recebidos).
3. Proposta final de pastas adaptada ao repositório e tabela `ID do item → sprite`.
4. Implementação **apenas da etapa autorizada**, com diffs pequenos.
5. Capturas comparativas de antes/depois quando possível.
6. Lista de testes executados, resultados e problemas pendentes.
7. Registro de crédito/licença dos assets integrados.

**Orientação final:** não redesenhar o Profane Echo do zero. A meta é evoluir a interface existente para uma aparência dark fantasy consistente e funcional, com implementação modular e em etapas verificáveis.
