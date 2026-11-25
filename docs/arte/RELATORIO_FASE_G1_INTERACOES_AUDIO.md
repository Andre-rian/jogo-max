# Fase G.1 — Interações (prompts no mundo) e áudio UI

## Resumo
- Prompts de interação migrados para sprites de tecla animados no mundo (`ui/prompts_teclas.py`, `PromptTeclaMundo`), desenhados na superfície `vista` com aplicação de `camera.offset` antes do scale (acompanhamento de câmera/zoom). A tecla E é ancorada visualmente acima da cabeça do player quando há alvo disponível; a seleção/ativação interna continua no objeto-alvo. Mantém estados normal/pressionado, deslocamento discreto e pulso periódico.
- Seleção determinística de alvo único em `core/interacoes.py` (prioridade: baú, drop, drop_eco, fogueira, porta; ordem interna; proximidade) com supressão por contexto (pausa/inventário/menu fogueira/morte) e APIs de disponibilidade/âncora nos objetos.
- HUD de interação textual removido do fluxo de prompt (`ui/hud/mensagens.py`, `ui/hud/hud.py`); objetos expõem `tecla_prompt`, `disponivel_para_prompt`, `prompt_anchor_mundo`.
- Áudio UI ajustado para reduzir duplicações e alinhar eventos: navegação por movimento do mouse/teclado emite `ui_move` apenas em mudança real, confirmações válidas emitem `ui_confirm`, retorno/fechamento contextual emite `ui_back`, ações inválidas emitem `ui_error` quando apropriado; inventário (incl. menu de contexto) evita duplicar confirmação+erro e trata ESC/clique fora de forma consistente; pausa com feedback único em transições.
- Encoding/identificadores normalizados em pontos críticos (`cooldown_interacao`, nomes de pausa/desenho, métodos de confirmação), preservando `assets/maps/calabouco_2.tmx`, `.gitignore`, artefatos Fase G e referências.

## Áudio / mix
- Revisão conservadora sem alterações de normalização, compressor ou novo mixer. Níveis/eventos em `assets/sons/_config/audio.json` mantidos; não foram identificadas duplicações comprovadas que exigissem mudança segura de implementação (ex.: fases distintas de projétil, fallbacks condicionais).

## Evidências e capturas (locais)
- `docs/arte/previews/fase_g1_sem_interacao_local.png`
- `docs/arte/previews/fase_g1_tecla_e_normal_local.png`
- `docs/arte/previews/fase_g1_tecla_e_pressionado_local.png`
- `docs/arte/previews/fase_g1_prompt_camera_normal_local.png`
- `docs/arte/previews/fase_g1_prompt_camera_pressionado_local.png`
- `docs/arte/previews/fase_g1_prompts_bau_porta_ecofoco_local.png` (prompt sobre o player; objetos presentes na cena)
- Metadados adicionados em `docs/arte/previews/fase_g_evidencias.json` (seção `g1`).

## Divergências registradas
- `docs/arte/RELATORIO_FASE_G_MENUS_INTERACOES.md` e evidências prévias da Fase G preservados; capturas G.1 adicionadas como artefatos locais complementares. Relatório G pré-existente pode conter texto/encoding histórico não reescrito nesta etapa.
- Sem gerador/repositório de testes-fonte `fase_g` versionados encontrados (apenas artefatos/pycache pré-existentes); cobertura G.1 adicionada em `tests/test_fase_g1.py`.

## Validação
- `python -m pytest -q --tb=short`
- `python -m py_compile` (módulos alterados/relevantes)
- `git diff --check`

## Revisão manual recomendada
- Conferir percepção de volume/mix e ausência de duplicações audíveis em sessões reais (menus, inventário, fogueira, interações, combate/projéteis/ambiência).
- Validar posicionamento visual dos prompts com câmera/zoom em diferentes resoluções/fullscreen/DPI e alinhamento fino sobre baús, portas e Ecofocos em jogo.
- `jogo.log` permanece modificado pré-existente e não foi incluído.

## Ajuste posterior
- Posição visual do prompt alterada para acima da cabeça do player; `prompt_anchor_mundo` dos objetos permanece disponível para lógica interna/uso futuro.
