# Plano de Progressão do Calabouço — Fase I.0

Comparação documental entre progressão atual e mapa conceitual fornecido em texto. Sem alterações de gameplay/mapas.

## 1. Progressão atual (implementada)

```text
calabouço_1 --(direita)--> calabouço_2 --(direita)--> calabouço_3 --(direita)--> calabouço_4 --(direita)--> calabouço_5
   ^                          ^                          ^                          ^                     (boss)
   |                          |                          |                          |
(esq=None)              (esq=1)                    (esq=2)                    (esq=3)                (dir=None)
```

- Conexões reais: lineares, apenas esquerda/direita, definidas em `world/niveis.py:Conexoes`.
- Salas 1-2: TMX. Salas 3-5: grade Python fallback.
- Sala 4: descanso/fogueira. Sala 5: boss esqueleto, parede boss (tile 8) abre ao derrotar.
- Sem chaves, elevador, atalhos, portas trancadas, salas opcionais/secretas, verticalidade complexa.

## 2. Mapa conceitual alvo (texto do usuário)

- Início do calabouço.
- Corredor da espada.
- Área central de distribuição.
- Caminhos superiores e inferiores.
- Dois chefes.
- Elevador trancado.
- Portas com chaves.
- Salas opcionais.
- Atalhos desbloqueáveis.
- Áreas secretas.
- Percurso até a saída do calabouço.

> Comparação visual completa depende da imagem conceitual; esta análise usa apenas a descrição textual fornecida.

## 3. Gap analysis

| Elemento conceitual | Estado atual | Gap | Prioridade |
|---|---|---|---|
| Início do calabouço | calabouço_1 existe (TMX básico) | Precisa narrativa/encaminhamento e conexão ao hub | Alta |
| Corredor da espada | Não identificado | Criar sala/trecho dedicado com pickup/decoração | Alta |
| Área central de distribuição | Não existe | Criar hub com múltiplas saídas e sinalização | Alta |
| Caminhos superiores/inferiores | Linear horizontal | Exigir verticalidade, escadas/plataformas/conexões verticais | Alta |
| Dois chefes | 1 boss (sala 5) | Projetar segundo boss, arena, gate, recompensa | Média |
| Elevador trancado | Não existe | Requer asset, objeto, estado persistido, animação/trigger | Média |
| Portas com chaves | Porta existe em código, sem fluxo chave/fechadura TMX completo | Definir item chave, lock, UI, persistência | Média |
| Salas opcionais | Não existem | Criar após hub e conexões estáveis | Futura |
| Atalhos desbloqueáveis | Não existem | Requer portas/interruptores/persistência | Futura |
| Áreas secretas | Não existem | Requer convenção de tiles/colisão falsa/parede secreta | Futura |
| Saída do calabouço | Não existe | Definir sala final/transição de área | Média/Futura |

## 4. Riscos técnicos antes da implementação

- `game_scene.py` assume transições por borda esquerda/direita; mapa conceitual pode exigir transições por portas/objetos/coordenadas específicas.
- Carregamento atual mistura TMX e fallback Python por sala; expandir sem padronizar aumenta inconsistência.
- Nomenclatura `spwan` e propriedades de inimigo (`tipo` vs `type`) devem ser normalizadas antes de criar muitos mapas.
- GIDs de plataforma hardcoded; reordenação de tileset pode quebrar plataformas.
- Persistência atual por `(col,linha)` funciona em sala fixa; mudanças grandes de layout podem invalidar estados antigos (aceitável em dev, mas registrar).

## 5. Ordem recomendada de implementação (primeira região)

1. **Normalizar convenções Tiled/loader**: aceitar `spawn`/`spwan`, `tipo`/`type`; documentar `_template.tmx`; validar warnings de camadas ausentes.
2. **Definir setor inicial**: `início -> corredor da espada -> área central` como 3 salas TMX pequenas/coesas, reutilizando tilesets existentes.
3. **Padronizar transições**: decidir se mantém bordas esquerda/direita ou adiciona objetos de saída/porta com destino; implementar sem quebrar saves/dev flow.
4. **Migrar salas 3-5 para TMX** após estabilizar convenções, preservando gameplay atual.
5. **Adicionar mecânicas de bloqueio**: porta trancada + chave + estado persistido; depois elevador.
6. **Expandir para segundo chefe, opcionais, atalhos e segredos** com checklist de validação por sala.

## 6. Primeira região recomendada

- **Região:** Setor de Entrada do Calabouço.
- **Escopo mínimo:** 3 salas TMX (Início, Corredor da Espada, Pré-Hub/Hub inicial), conexão linear clara, 1 Ecofoco, 1 baú/espada, sem novos sistemas complexos.
- **Critério de pronto:** carregamento TMX sem warning crítico, spawns corretos, transições bidirecionais, colisões/escadas/plataformas válidas, sem regressão nos testes.
