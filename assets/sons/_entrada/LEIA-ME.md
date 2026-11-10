# Entrada de sons

Área de fontes, avaliação e reservas. **Nada aqui é carregado pelo jogo.**
Ponto de retomada: [sons_faltando/CONTEXTO.md](sons_faltando/CONTEXTO.md).

## Organização após a limpeza de 2026-11-10

| Pasta | Áudios | Função |
|---|---:|---|
| `_uteis/` | 16 | Reservas escolhidas pelo usuário |
| `_fatias/` | 43 | 42 cortes marcados para guardar + fatia 003 da receita do pulo |
| `_originais_corrigidos/` | 1 | Original do swing de espada antes da correção |
| `5_mundo_movimento/passos_pedra/` | 4 | Fontes longas reservadas para cortes alternativos |
| `sons_faltando/avaliacao_15_mp3/` | 28 | 13 originais, 13 prévias e 2 fontes verificadas |
| `sons_faltando/_uteis/magico/` | 1 | Disparo mágico reservado |
| `sons_faltando/busca_2026_11_09/` | 66 | Fontes já usadas pelos lotes 1–3, com créditos e receitas |
| `sons_faltando/musicas/` | 53 | Fontes de música e alternativas preservadas |

Total: **212 áudios**. `_inbox/` recebe arquivos novos. Diretórios vazios com
`.gitkeep` são marcadores de organização.

## Limpeza aplicada

Foram removidos **76 arquivos (313,32 MiB)**: cópias idênticas fora de `_uteis`,
fontes antigas cujo material selecionado já está nos destinos finais/fatias
reservadas, recortes experimentais substituídos e rejeitados. Os rejeitados
foram `770072...footsteps-knight...` (decisão da triagem de 2026-11-07) e o ataque
09 do Skeleton (decisão em `avaliacao_15_mp3/OBSERVACOES.md`).

Os 17 áudios das duas áreas `_uteis` foram preservados. Também permanecem
fontes pendentes, músicas, anotações, créditos e evidências. Não foi feita
promoção nova nem alteração dos áudios finais.

Cada remoção tem hash, motivo, referência preservada e commit de recuperação em
[LIMPEZA_ENTRADA.csv](../../../docs/audio/auditoria_geral/LIMPEZA_ENTRADA.csv).
Inventário técnico atual: [ARQUIVOS.csv](../../../docs/audio/auditoria_geral/ARQUIVOS.csv).
Os relatórios de 2026-10/11-07 são históricos; não representam a fila atual.

## Fluxo para novos sons

1. Guardar o download original em `_inbox/` ou no lote de `sons_faltando/`, com
   URL, autor e licença exata.
2. Ler as observações nos nomes e nos arquivos Markdown antes de editar.
3. Ouvir, registrar a decisão e preparar cortes/prévias fora da árvore final.
4. Promover somente os aprovados com origem comprovada; registrar os créditos
   em `../_config/LICENCAS.csv` e conferir os destinos.
5. Validar o resultado em gameplay.

```bash
.venv/bin/python tools/preparar_sons.py inspecionar assets/sons/_entrada/_inbox
.venv/bin/python tools/preparar_sons.py promover tools/promocao_lote4_pendentes.csv --dry-run
```

A receita pendente permanece bloqueada enquanto faltarem os dados de origem.
`tools/promocao.csv` é histórico, com linhas desativadas; não reutilizar seus
nomes antigos. Não promover compilações longas inteiras: o jogo reproduz o
arquivo completo. Os finais usam nomes ASCII e numerados.
