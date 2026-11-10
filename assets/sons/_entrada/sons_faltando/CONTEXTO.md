# Continuação da revisão de sons

Atualizado em **2026-11-10**, após a revisão geral e a limpeza de `_entrada`.
Este é o ponto de retomada. Instruções antigas de promoção e contagens anteriores
ficam no histórico do Git; não devem ser executadas como pendências atuais.

## Estado verificado

- **460 áudios:** 248 finais e 212 em triagem/fontes/reservas.
- Todos decodificados pelo SDL_mixer, sem erros, silêncio total ou ponteiros LFS
  restantes. Foram recuperados 222 arquivos que estavam apenas como ponteiros,
  conferindo tamanho e SHA256 antes de repor o conteúdo.
- **76 arquivos retirados de `_entrada` (313,32 MiB):** 17 cópias exatas,
  37 fontes antigas já processadas, 11 recortes substituídos pelas prévias,
  9 cortes automáticos de pulo não utilizados e 2 rejeitados.
- Preservados os **17 áudios em pastas `_uteis`**, as 42 fatias com instrução de
  guardar, a fatia 003 usada na receita do pulo, 4 fontes longas de passos,
  fontes dos lotes recentes, músicas, evidências de licença e backups de correções.
- Nenhum áudio final foi alterado ou removido nesta limpeza. As 8 famílias de
  duplicatas finais atendem contextos diferentes; não há duplicatas na mesma pasta.
- As variações de interface e de abertura de porta já integradas passaram a ser escolhidas por evento,
  mantendo separados abrir/fechar, volumes, cooldowns e canal de UI.

Relatório, critérios e recuperação:
[REVISAO_GERAL_2026_11_10.md](../../../../docs/audio/REVISAO_GERAL_2026_11_10.md).
Lista de remoções com hash e commit de recuperação:
[LIMPEZA_ENTRADA.csv](../../../../docs/audio/auditoria_geral/LIMPEZA_ENTRADA.csv).

## Onde a avaliação parou

1. [OBSERVACOES.md](avaliacao_15_mp3/OBSERVACOES.md) contém as decisões do usuário
   sobre os 15 MP3. **11 aprovados continuam aguardando comprovação de origem**;
   originais e prévias estão preservados. A receita pendente é
   `tools/promocao_lote4_pendentes.csv`.
2. Rugido do Boss e morte do Globin já foram integrados com novas fontes CC0
   verificadas. Os originais antigos continuam disponíveis para comparação.
3. O ataque do Skeleton (09), rejeitado por impacto embutido, foi removido.
   Sua avaliação e hash histórico permanecem registrados. O disparo mágico (15)
   está reservado em `_uteis/magico/`.
4. Os **66 arquivos de `busca_2026_11_09/` já foram usados** nos lotes 1–3;
   `CANDIDATOS.csv` registra os destinos concluídos. São fontes para manutenção,
   não uma fila de 66 sons ainda por promover.
5. `tools/promocao.csv` é histórico e teve suas linhas desativadas. As tabelas
   `promocao_lote1.csv` até `promocao_lote4.csv` também registram trabalho concluído.

## Próximos passos

- Consultar [STATUS_SONS.md](../../../../docs/audio/STATUS_SONS.md) para as
  **11 pastas finais vazias** e
  [GUIA_CONTINUACAO_AUDIO.md](../../../../docs/audio/GUIA_CONTINUACAO_AUDIO.md)
  para os gatilhos já implementados. Asas do Flying Eye ainda não têm arquivo final.
- Confirmar fonte, licença exata, autor e URL dos 11 aprovados antes da promoção.
  `LIVRE`, nomes semelhantes e semelhança sonora não comprovam a origem.
- Buscar outro ataque sem impacto embutido para o Skeleton e as variantes de
  ataque do Boss. Manter novas buscas organizadas aqui até a avaliação.
- Revisar a música do Boss por escuta: a decodificação apresenta saturação.
  Permanecem 42 finais sem registro de licença e 116 com rótulo genérico `LIVRE`.
- Conferir a mixagem em gameplay. A auditoria técnica não substitui a escuta.

## Conferência local

```bash
.venv/bin/python tools/auditar_sons.py
.venv/bin/python -m pytest -ra
```

O inventário atual é `docs/audio/auditoria_geral/ARQUIVOS.csv` e o resumo é
`RESUMO.json`, na mesma pasta. Para novos clones, recuperar o LFS antes de ouvir
as fontes. Nesta máquina, o binário verificado está em `.venv/bin/git-lfs` e os
filtros foram configurados somente neste repositório.
