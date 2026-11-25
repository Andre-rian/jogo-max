# PROFANE ECHO — Fase F.3: chefe, notificações e polimento da HUD

Data: 16/11/2026. Branch: `sprites`.
Implementação e verificações concluídas. Publicação autorizada no pedido F.3;
o recibo remoto é conferido após o commit, conforme seção Git abaixo.

## Preparação e diagnóstico

Clone limpo de `https://github.com/Andre-rian/jogo-max.git`, branch `sprites`,
HEAD e remoto em `c5f67921094b5ef9d28069469626e28b97d3afcc` (F.2).
Nenhum arquivo modificado ou não rastreado preexistente neste checkout.
Nenhum `AGENTS.md` encontrado no repositório ou ancestrais. Relatórios F.0,
F.1 e F.2 lidos; código e testes F.1/F.2 conferidos. A suíte inicial teve
231 aprovados e 1 ignorado, resultado esperado do clone público sem LY015.

Problemas confirmados:

- Notificação antiga em y=600..664 cruzava painel/nome do chefe em y=634..688.
  A proposta de movê-la a y=528..592 também cruzaria o prompt em y=570.
- Camadas de HP atual e atrasado tinham a mesma cor. Display zero reiniciava
  a animação; troca de identidade e ausência do chefe não limpavam o estado.
- Preenchimento admitia valores acima do máximo e divisão por zero.
- Prompt e mensagem não tinham fundo próprio; fade dos ícones/bordas de
  notificação escurecia as cores em vez de desaparecer por transparência.
- Nomes e quantidades longos podiam se sobrepor ou sair dos painéis.

## Implementação e decisões visuais

Proposta C preservada: grafite, bordas azul-acinzentadas, detalhe violeta,
texto claro e pixel art sem interpolação. Reutilizados `desenhar_painel`,
`obter_trilho` da F.1 e `obter_sprite_de_item`; nenhum asset novo.

**Chefe:** painel normal de 480×64 no rodapé, trilho 448×16, interior 442×10.
Vida vermelha `(184,51,65)`, dano atrasado rosa dessaturado `(191,126,144)`.
O dano acumulado fica protegido dentro do painel. Suavização continua a
2 unidades por atualização, indicação de dano por 120 ticks. Proporções
limitadas a 0..1 apenas no desenho; máximo não positivo deixa trilho vazio.
A primeira apresentação usa o HP atual, sem inventar dano anterior.
Identidade nova ou reapresentação após `None` reinicia o estado visual.
Ao receber `None`, nada é desenhado. A cena continua decidindo quando remover
o chefe; nenhuma regra de morte/IA/combate foi alterada.

**Notificação:** 340×64 para itens comuns, até 460 px de largura conforme
nome/quantidade. Quebra em linhas sem abreviar valores; cresce para cima.
Sprites IDs 1–5 já existentes, 48×48 pelo cache nearest-neighbor; desenho
procedural anterior como fallback. Nome e quantidade ficam em linhas
separadas. Duração de 210 desenhos, fade nos últimos 60, mesma cadência
histórica em `desenhar` (não transferida para `atualizar`). Alpha aplicado ao
painel completo, incluindo ícone, texto e borda.

**Mensagens/prompts:** fundos grafite dimensionados pelo texto, quebra de
linha para nomes extensos e cache somente dos dois conteúdos atuais.
Prompt mantém o texto em y=570 (painel começa 8 px antes). Mensagem mantém
âncora em y=260 e mesmo timer padrão de 180 atualizações/fade `timer * 5`.
Conteúdo, substituição, limpeza, prioridade e condições permanecem iguais.

### Geometria real em 1280×720

| Componente | Retângulo normal (x, y, largura, altura) | Decisão |
|---|---|---|
| Notificação | (470,476,340,64) | Borda inferior fixa em 540, cresce para cima |
| Prompt `[E] Abrir porta` | (573,562,135,30) | Texto na posição histórica y=570 |
| Mensagem de recuperação de Ecos | (437,260,407,37) | Centro superior preservado |
| Chefe | (400,636,480,64) | 20 px de margem inferior; nome longo pode aumentar altura |
| Poção F | (20,636,148,64) | F.2 intacta |
| Ecos | Alinhado à direita em x+w=1260, y+h=700 | F.2 intacta, largura máxima 360 |
| Status | (20,20,276,88) | F.1 intacta, stamina com 8 px úteis |

Retângulos de texto dependem das fontes do sistema. Testes incluem nomes
extensos, quantidades de 60 dígitos e uma fonte maior de 26 px. São faixas
fixas simples, sem gerenciador de layout. Notificações e prompts têm intervalo
de 22 px; chefe e Ecos têm pelo menos 20 px de separação horizontal.
Nenhum posicionamento de poção, Ecos ou status precisou mudar.

## Preservação, desempenho e compatibilidade

Nenhuma alteração em inventário, menus, saves, áudio, mundo, movimento,
progressão, aprimoramento, atributos ou combate. Os módulos `status.py`,
`trilho_status.py`, `pocao.py` e `ecos.py` permanecem byte a byte iguais à F.2.
A única integração em `Hud` encaminha também `boss_atual=None` ao componente.
Dados funcionais e log foram comparados antes/depois; nenhum save foi criado.

Painéis/textos só são recompostos quando o conteúdo ou largura muda.
Não há carregamento ou escala de imagens por frame; falhas continuam em cache.
Alpha dos sprites é preservado. O trilho opcional reutiliza o fallback F.1,
sem dependência de packs lygame. Todos os testes rodaram sem esses packs.
Medição de 600 desenhos da HUD após aquecimento está nas evidências JSON
(abaixo de 1 ms por frame nesta máquina). Não é benchmark do jogo inteiro
nem garantia de desempenho em outros computadores.

## Testes

Ambiente: Linux, Python 3.12.14, pygame-ce 2.5.8, numpy 2.5.4,
pytest 9.2.0; dependências exatas de `requirements-dev.txt`, em `.venv` local.
Nenhuma dependência ou arquivo requirements alterado.

- Base: **231 aprovados, 1 ignorado**.
- Final: **263 aprovados, 1 ignorado**, incluindo **32 novos casos F.3**.
- Ignorado: inspeção do LY015 opcional ausente. Testes de fallback executados.
- `git diff --check`: sem erros.

Comando:

```sh
.venv/bin/python -m pytest -o addopts='' --tb=short -p no:cacheprovider -q
```

Cobertura F.3: 100/50/10/0% e valores inválidos de HP; dano acumulado,
suavização, expiração e zero estável; cura observada; troca e reapresentação
do mesmo chefe; ausência via `Hud`; cinco sprites existentes; nomes,
quantidades e fade integral; simultaneidade dos seis componentes com duas
fontes; invariância dos dados funcionais; mensagens temporárias, substituição
e limpeza; assets ausentes/corrompidos; cache durante 60 desenhos; clip do
chamador. A suíte completa inclui combate real e regressões F.1/F.2.

## Capturas e comparações

[Comparativo compacto 1×](previews/hud_f3_comparativo.png),
[evidências](previews/hud_f3_evidencias.json),
[gerador reproduzível](gerar_previews_f3.py) e
[índice de capturas](previews/README.md).

Execução: `.venv/bin/python docs/arte/gerar_previews_f3.py`.
Requer histórico Git contendo o commit F.2 para carregar o renderer anterior.
O script usa `Gamescene.desenhar`, mapas/sprites reais e SDL dummy a 1280×720.
Não importa `main`, não inicializa gerenciador de saves nem logging em arquivo.
São capturas reais do renderer com cenários controlados, não uma sessão manual.

Onze cenários pareados: exploração com item; prompt com item; mensagem com
item; chefe cheio; ataque real de espada (290/300); dano controlado até 150/300;
50% estabilizado; 10%; chefe com item; HUD completa durante combate; zero.
A redução adicional de HP, quantidades, buff e mensagens é preparada em memória;
o caso de zero mantém a instância para inspecionar o trilho, sem alterar a regra
de remoção do chefe na cena.

Para cada cenário: dois quadros 1280×720 e um comparativo 2560×752 com rótulos
externos, sem redimensionar os pixels. **33 PNGs completos locais**, ignorados.
Antes/depois partem do mesmo quadro do mundo, sem tick de gameplay entre eles;
componentes antigos recebem cópias dos temporizadores. Pixels fora da região
(300,240,680,460), que abrange as três áreas modificadas, são idênticos em todos
os pares. Os dados do jogador/chefe são conferidos após cada captura.

O comparativo compacto versionado contém só os três componentes sobre fundo
claro sintético, com M095/CC0 e desenho próprio. As capturas completas foram
mantidas locais por prudência quanto aos assets de mundo. LY015 foi desativado
explicitamente no gerador; nenhum pack restrito ou preview dele foi adicionado.
Os sprites de armas já integrados são Beast Pixels, Weapons and Tools, CC BY
4.0; crédito e licença existentes continuam em `ASSETS_UI_ORIGENS.md`.
Nenhum sprite foi redistribuído ou modificado nesta fase.

## Arquivos da entrega

| Arquivo | Alteração |
|---|---|
| `ui/hud/boss.py` | Painel, camadas de vida, estado por identidade e cache |
| `ui/hud/notificacao.py` | Faixa separada, sprites existentes, texto e fade |
| `ui/hud/mensagens.py` | Contraste, quebra de linha e cache |
| `ui/hud/hud.py` | Encaminhamento da ausência do chefe |
| `ui/hud/apresentacao.py` | Helpers pequenos de painel e texto; nenhum layout global |
| `tests/test_hud_f3.py` | 32 casos novos |
| `docs/arte/gerar_previews_f3.py` | Capturas reais e validação de integridade |
| `docs/arte/previews/hud_f3_comparativo.png` | Comparativo publicável |
| `docs/arte/previews/hud_f3_evidencias.json` | Estados, retângulos e integridade |
| `docs/arte/previews/README.md` | Índice das capturas |
| `docs/arte/INVENTARIO_SPRITES.md` | Situação atual F.3 |
| `docs/arte/RELATORIO_FASE_F3_HUD.md` | Este relatório |
| `.gitignore` | Capturas completas/recibo F.3 locais |

## Pendências e limites

- Fullscreen não foi validado: a sessão não disponibilizou display, Xvfb ou
  ferramenta de desktop. O guia cloud-desktop foi consultado. Testada a
  superfície lógica 1280×720; avaliação física de escala/DPI e sessão
  prolongada ficam pendentes no computador do usuário.
- Fontes variam entre sistemas; textos de tamanho arbitrário não cabem em
  telas finitas. A matriz cobre os conteúdos atuais, nomes extensos e
  quantidades até 60 dígitos, não parágrafos ilimitados ou resoluções menores.
- Notificações ainda podem cobrir parte do cenário/atores quando estes passam
  pela faixa reservada, como qualquer HUD; reduziram-se as dimensões comuns
  após inspeção visual. Não há sobreposição entre os componentes testados.
- Persistem o spawn da sala 5 (`_spwanar_fallback` ausente), camada
  `plataformas` ausente na sala 1 e objeto de inimigo sem tipo. Capturas usam
  `posiçao_spwan` explícita existente. Corrigir mundo fica para estabilização.

## Git e publicação

Staging limitado aos 13 arquivos da tabela, após revisão do diff, licenças,
ignorados, integridade e suíte completa. Sem logs, saves, caches, packs ou
capturas completas. Branch confirmada como `sprites`; sem force, reset,
rebase ou merge na main.

Commit: `feat(hud): finalize boss bar and notification visuals`.
Após `git push origin sprites`, comparar `git rev-parse HEAD` com
`git ls-remote origin refs/heads/sprites`. Hash definitivo e confirmação real
ficam no recibo local ignorado `previews/hud_f3_publicacao_local.json` e na
resposta final, evitando um commit circular para registrar o próprio hash.
