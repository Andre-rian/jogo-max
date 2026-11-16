# Prévias de arte

## Fase F.2 — poção e Ecos Profanos

- [Comparativo compacto, 1×](hud_f2_comparativo.png): cargas 3/1/0, flash,
  zero/137/19 e 60 dígitos, fundos escuro/claro. Somente CC0 e arte original.
- [Evidências de cinco cenários reais](hud_f2_evidencias.json) e
  [relatório completo](../RELATORIO_FASE_F2_HUD.md).
- Reprodução: `python docs/arte/gerar_previews_f2.py`.
- Dez capturas completas `hud_f2_*_local.png`, 1280×720, ficam apenas locais;
  todas usam fallback de LY015. Gerador não importa `main` nem usa saves.
- `hud_f2_publicacao_local.json` registra o hash e a confirmação remota após o
  push; recibo local ignorado para não gerar um commit apenas com o próprio hash.
- As exclusões preexistentes de `hud_f0_atual_*`, `hud_f0_evidencias.json` e
  `hud_f0_integridade_inicio.json` foram preservadas fora do commit F.2.

## Fase F.1 — integração experimental do painel de status

[Relatório e capturas antes/depois](../RELATORIO_FASE_F1_HUD.md).
[Comparação das alturas 6/8/10](hud_f1_alturas_6_8_10_restrito.png).
Stamina de 8 px úteis selecionada experimentalmente. Todas as imagens
`hud_f1_*_restrito.png` permanecem locais, cobertas pelo `.gitignore`.
O restante da HUD não foi modernizado nesta etapa. Reprodução na raiz:
`python docs/arte/gerar_previews_f1.py`; teste com janela real:
`python docs/arte/gerar_previews_f1.py --fullscreen`.

## Fase F.0 — auditoria da HUD

Entrega: [relatório](../RELATORIO_FASE_F0_HUD.md),
[comparativo A/B/C](hud_f0_comparativo_abc_restrito.png) e
[estados de legibilidade](hud_f0_legibilidade_estados_restrito.png).
Os novos arquivos `hud_f0_captura_*_restrito.png` são renderizações reais
do jogo em cenários controlados; `hud_f0_proposta_*_restrito.png` são
composições offline sobre esses mesmos quadros. Todas as imagens desta
rodada permanecem locais e ignoradas pelo Git. Os `hud_f0_atual_*`
preexistentes foram preservados e não são evidência desta execução.
Valores e dimensões estão em `hud_f0_evidencias.json`; o manifesto
`hud_f0_integridade_inicio.json` registra os hashes usados para confirmar
que código, assets, banco e log não foram alterados.
Reprodução na raiz: `python docs/arte/gerar_previews_f0.py`.

Diretório temporário para capturas e comparações visuais geradas durante cada
etapa. As imagens da Fase C foram removidas em 15/11/2026 após a aprovação
visual, para evitar que arquivos antigos sejam confundidos com novas prévias.
Referências a capturas nos relatórios históricos (Fases A/B/C) descrevem
arquivos que já não existem neste diretório.

## Fase E.2.1 - legibilidade dos prompts de tecla

Versionáveis (fallback sem assets lygame):

- `menu_e21_comparativo_rodape_fallback.png` (1068×410)
- `menu_e21_comparativo_slot_fallback.png` (858×608)
- `menu_e21_comparativo_modal_fallback.png` (978×818)
- `menu_e21_ajustado_fallback_vazio.png` (1280×720)
- `menu_e21_ajustado_fallback_ocupado.png` (1280×720)
- `menu_e21_ajustado_fallback_confirmar_delete.png` (1280×720)

Locais, não versionáveis (contêm moldura lygame):

- `menu_e21_comparativo_rodape_lygame.png` - atual × A (+25%) × B (+50%)
- `menu_e21_comparativo_slot_lygame.png` - atual × A × B
- `menu_e21_comparativo_modal_lygame.png` - atual × A × B
- `menu_e21_candidato_{a,b}_lygame_ocupado.png`
- `menu_e21_candidato_{a,b}_lygame_confirmar_delete.png`
- `menu_e21_ajustado_lygame_{vazio,ocupado,confirmar_delete}.png`

## Fase E.2 - molduras, prompts e alerta do menu

Versionáveis (fallback sem assets lygame):

- `menu_e2_fallback_vazio.png` (1280×720)
- `menu_e2_fallback_ocupado.png` (1280×720)
- `menu_e2_fallback_confirmar_delete.png` (1280×720)

Locais, não versionáveis (contêm moldura lygame):

- `menu_e2_lygame_vazio.png` (1280×720)
- `menu_e2_lygame_ocupado.png` (1280×720)
- `menu_e2_lygame_confirmar_delete.png` (1280×720)
- `menu_e2_comparativo_lygame.png` (1840×860) - E.1 antes × E.2 depois
- `menu_e2_estados_molduras_lygame.png` (1080×360) - quatro estados da moldura

As capturas ocupadas usam dados sintéticos em memória; `saves.db` não é escrito.
As imagens com lygame ficam fora do Git.

## Fase E.1 - correção dos halos do menu

Versionáveis (capturas reais de `MenuInicial`, sem assets restritos):

- `menu_e1_antes_vazio.png` (1280×720)
- `menu_e1_antes_ocupado.png` (1280×720)
- `menu_e1_antes_confirmar_delete.png` (1280×720)
- `menu_e1_depois_vazio.png` (1280×720)
- `menu_e1_depois_ocupado.png` (1280×720)
- `menu_e1_depois_confirmar_delete.png` (1280×720)
- `menu_e1_comparativo.png` (1400×1360) - antes/depois dos três estados

As capturas ocupadas usam dados sintéticos em memória; `saves.db` não é escrito.

## Fase E.0 - menu e seleção de saves

Versionáveis (sem assets restritos):

- `menu_e0_atual_vazio.png` (1280×720)
- `menu_e0_atual_ocupado.png` (1280×720)
- `menu_e0_atual_confirmar_delete.png` (1280×720)
- `menu_e0_legibilidade.png` (1600×1080) - variantes de halo/faixa escura
- `menu_e0_prompts.png` (1600×620) - prompts de teclado

Locais, não versionáveis (AbyssOwl/Kibyra/lygame):

- `menu_e0_mock_abyssowl_restrito.png`
- `menu_e0_mock_lygame_restrito.png`
- `menu_e0_molduras_restrito.png`
- `menu_e0_botoes_restrito.png`
- `menu_e0_kibyra_icones_restrito.png`

O padrão `docs/arte/previews/*restrito*.png` bloqueia esses arquivos no Git.

Prévias históricas da Fase D.1: `recursos_d1_ly005_umbrita_m042.png`,
`recursos_d1_ly005_umbrita_m052.png` e `recursos_d1_comparativo_ly005.png`.
Todas contêm o painel LY005 e permanecem apenas locais.

Regras:

- Gerar capturas a partir da tela/classe real do jogo, não de montagens manuais.
- Nomear com a fase/data e remover ou substituir imagens obsoletas ao concluir a
  etapa.
- Não versionar imagens que contenham assets restritos. O `.gitignore` bloqueia
  nomes com `lygame`, `ly005`, `ly006` e `*restrito*`; ainda assim, confira antes
  de commitar.
- Capturas apenas com assets CC0/próprios podem ser versionadas quando forem
  úteis como documentação.
- Licenças e origens: `docs/arte/ASSETS_UI_ORIGENS.md` e
  `assets/sprites/_entrada/CREDITOS_E_LICENCAS.md`.
