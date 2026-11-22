# RELATORIO FASE H.3 - POLIMENTO VISUAL MENUS

## Escopo
Polimento visual pontual em menus/UI (Ecofoco, Opcoes, inventario/pausa/HUD consistencia), sem alterar gameplay, combate, audio/musica, saves, mapas, prompts G.1 ou mecanicas de Ecofoco/level-up. Sem git add/commit/push.

## Problemas identificados e causas tecnicas

### 1) Menu do Ecofoco - circulo/halo roxo gigante
- **Sintoma**: halo roxo grande/opaco cobrindo menu Ecofoco.
- **Causa tecnica**: `ui/estilo.py:adicionar_brilho` mutava superficies cacheadas com `set_alpha()` e depois usava `BLEND_ADD`; isso destr?i alpha per-pixel do cache radial e pode gerar artefato opaco. `desenhar_eco_profano` desenhava halo grande (`raio*2`) sem controle de intensidade/raio por contexto.
- **Correcao**: `adicionar_brilho`/`_aplicar_brilho_alpha` agora copiam a superficie cacheada antes de aplicar alpha global; `desenhar_eco_profano` ganhou `intensidade_halo` e `raio_halo`. `core/menu_fogueira.py` usa halo discreto com `alpha_real=True, intensidade_halo=0.10, raio_halo=13/14`.
- **Arquivos**: `ui/estilo.py`, `core/menu_fogueira.py`.

### 2) Textos/caracteres do Ecofoco
- **Sintoma**: textos corrompidos (ex. `Subir N...vel`, `Resist...ncia`, `For...a`).
- **Causa tecnica**: strings com mojibake/encoding corrompido no fonte.
- **Correcao**: normalizados labels visiveis para `Subir de n?vel`, `Resist?ncia`, `For?a`; info compacta usa `N?vel`. Nao alterou IDs internos de atributos/chaves.
- **Arquivo**: `core/menu_fogueira.py`.

### 3) Menu de Opcoes - textos/controles cortados
- **Sintoma**: labels/valores de audio cortados, principalmente em escalas grandes.
- **Causa tecnica**: layout fixo em pixels (`slider_x=conteudo.left+230`, `slider_w=360`, `painel 860x430`), sem responsividade por escala/largura; botoes e preview com alturas fixas.
- **Correcao**: `_layout_opcoes` agora calcula painel/conteudo/abas/preview/botoes por escala e fontes; sliders usam `label_w/valor_w/gap/row_h` responsivos; labels com clip, foco por linha, valor percentual ancorado ? direita; preview de acessibilidade com quebra de linha e clip. `Restaurar padr?es` responsivo.
- **Arquivo**: `core/menu.py`.

### 4) Revisao de consistencia visual limitada
- **Menu inicial/slots/opcoes/pausa/inventario/ecofoco/HUD**: verificados por smoke render/capturas. Ecofoco level-up compacto recebeu layout responsivo e hitboxes de mouse alinhadas (`_layout_levelup/_rects_levelup_*`), evitando desalinhamento ao escalar.
- **Nao alterado**: gameplay, combate, audio/musica, saves, mapas, prompts G.1, mecanicas Ecofoco/level-up.

## Capturas (apos H.3)
- Opcoes Audio: `docs/arte/previews/h3_opcoes_audio_100.png`, `h3_opcoes_audio_125.png`, `h3_opcoes_audio_150.png`
- Opcoes Acessibilidade: `docs/arte/previews/h3_opcoes_acessibilidade_100.png`, `h3_opcoes_acessibilidade_125.png`, `h3_opcoes_acessibilidade_150.png`
- Ecofoco menu: `docs/arte/previews/h3_ecofoco_menu_100.png`, `h3_ecofoco_menu_125.png`, `h3_ecofoco_menu_150.png`
- Ecofoco level-up: `docs/arte/previews/h3_ecofoco_levelup_100.png`, `h3_ecofoco_levelup_125.png`, `h3_ecofoco_levelup_150.png`
- Inventario: `docs/arte/previews/h3_inventario_100.png`, `h3_inventario_125.png`, `h3_inventario_150.png`
- HUD: `docs/arte/previews/h3_hud_100.png`, `h3_hud_125.png`, `h3_hud_150.png`
- Menu principal: `docs/arte/previews/h3_menu_principal_100.png`
- Slots: `docs/arte/previews/h3_slots_100.png`
- Pausa: `docs/arte/previews/h3_pausa_100.png`

> Antes/depois: n?o havia capturas H3 anteriores no worktree; usar capturas G/H existentes para compara??o hist?rica se necess?rio.

## Testes e validacao
- `python -m py_compile ui\estilo.py core\menu.py core\menu_fogueira.py` ? OK.
- Smoke render SDL dummy: Opcoes/Ecofoco/Inventario/HUD em 100/125/150% ? OK (capturas geradas).
- `python -m pytest -q --tb=short` ? **294 passed, 0 failed** (exit 0).
- `git diff --check` ? sem erros; warnings LF?CRLF em arquivos tocados/preexistentes.

## Pendencias para revisao manual
- Confirmar visualmente em runtime real (n?o dummy) que n?o h? halo opaco no Ecofoco em diferentes GPUs/drivers.
- Validar leitura/espacamento dos sliders de ?udio em 150% com mouse e teclado.
- Validar navega??o mouse/teclado no level-up compacto (hitboxes +/-/Confirmar) em 150%.
- Confirmar que textos acentuados aparecem corretamente com as fontes instaladas no ambiente alvo.


## Complemento - Fogueira espectral e polimento extra

### Menu de pausa (`ui/overlays.py`)
- Fundo escurecido com vinheta e painel central sutil.
- Brilho difuso atr?s do t?tulo (alpha real, sem disco opaco).
- Halo discreto no item selecionado; part?culas pequenas roxas/cinzas discretas.
- Bot?es com largura/altura consistentes, sele??o clara.

### Menu Ecofoco (`core/menu_fogueira.py`)
- Glow espectral discreto no topo, part?culas suaves subindo, painel/bot?es mais espa?ados.
- Mantidos t?tulos/subt?tulos, navega??o mouse/teclado, l?gica de descanso/level-up.

### Fogueira espectral no cen?rio (`entities/objetos/fogueira.py`)
- Chama azul/violeta (n?cleo claro, intermedi?rio azul-espectral, borda violeta), pulso lento.
- Part?culas azuladas/violetas ascendentes leves, determin?sticas por fogueira/frame.
- Luz ambiente localizada com `Surface` RGBA + `BLEND_RGBA_ADD`, sem c?rculo s?lido opaco; acompanha c?mera/posi??o da fogueira.
- Estados preservados: apagada (brasa fria) / ativa (chama+part?culas+luz). Intera??o E, checkpoint, descanso, menu e evolu??o preservados.

### Capturas adicionais
- `docs/arte/previews/h3_fogueira_acesa_100.png`
- `docs/arte/previews/h3_pausa_polida_100.png`
- `docs/arte/previews/h3_ecofoco_menu_polido_100.png`

### Limita??es
- Fogueira usa desenho procedural pixel-art simples (sem novo sprite externo) para garantir recolora??o espectral; documentado.
- Luz ? localizada/otimizada, n?o sistema global de ilumina??o.
- Valida??o visual final em runtime real ainda recomendada.
