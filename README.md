# 🗡️ Profane Echo

> Projeto da matéria de **Programação Orientada a Objetos (POO)**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-Engine-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow?style=flat-square)
![Gênero](https://img.shields.io/badge/G%C3%AAnero-Metroidvania-blueviolet?style=flat-square)

---

## 📖 Sobre o projeto

**Profane Echo** é um jogo de **aventura e plataforma** no estilo **metroidvania**, ambientado em um castelo repleto de calabouços, grandes salões e corredores traiçoeiros.

O jogador controla um **cavaleiro habilidoso**, capturado por esse reino e aprisionado no calabouço do castelo como escravo. Para vencer, ele precisa **fugir do castelo**, recuperando suas armas pelo caminho e derrotando o **rei** que governa aquelas terras — enfrentando diversas tentativas de homicídio ao longo da jornada.

---

## 🎮 Gameplay

### Movimentação
- Andar para a **esquerda** ou **direita**
- **Pular**
- **Dash** (esquiva rápida) na direção do movimento, ativado ao pressionar a tecla de direção **duas vezes** em um curto intervalo de tempo

### Combate
- Ataque corpo a corpo com **espada**
- Vida (**PV**) e **stamina** como atributos principais
- Colisão com inimigos causa dano ao jogador

### Atributos do jogador
| Atributo | Valor inicial | Observações |
|---|---|---|
| Pontos de Vida (PV) | 200 | `50 + Vigor × 15` |
| Stamina | 130 | `30 + Resistência × 10` |
| Força | 10 | Aumenta o dano do ataque |
| Destreza | 9 | Aumenta o dano do ataque |

Se a barra de vida chegar a zero, o jogador **morre** e retorna ao **último checkpoint**.

### 📈 Atributos
O jogador possui **Vigor** (aumenta os PV máximos), **Resistência** (aumenta a stamina máxima), **Força** e **Destreza** (aumentam o dano). Os valores máximos de vida e stamina são calculados a partir desses atributos.

### 🎒 Inventário
O jogador conta com um **sistema de inventário**, onde itens, poções e equipamentos recuperados ao longo do jogo podem ser armazenados e gerenciados.

---

## ⌨️ Controles

| Tecla | Ação |
|---|---|
| `A` | Mover para a esquerda *(2x rápido = dash para a esquerda)* |
| `D` | Mover para a direita *(2x rápido = dash para a direita)* |
| `Espaço` | Pular |
| `K` | Atacar com a espada |
| `F` | Usar poção |
| `E` | Interagir (baús, portas, fogueiras) |
| `ESC` | Abrir menu do jogo (com opção de sair) |

---

## 👹 Inimigos

| Inimigo | Comportamento |
|---|---|
| Esqueleto | Morto-vivo do calabouço |
| Globin | Patrulha o território |
| Cogumelo | Solta esporos para atacar |
| Olho voador | Flutua e dispara projéteis |
| **Carrasco Esquelético** | Chefe final (*boss*) |

> Alguns inimigos possuem mais vida e ficam parados, enquanto outros são mais rápidos e perseguem o jogador ativamente — cada tipo com um comportamento único.

---

## 🏰 Fases e progressão

O mapa está situado dentro de um castelo, dividido em **5 calabouços** (`calabouco_1` a `calabouco_5`). Cada calabouço é um mapa construído no **Tiled** (formato `.tmx`), com camadas de fundo, colisão e decoração.

Os caminhos são formados por corredores, com colunas e paredes intransponíveis delimitando os limites do mapa. Para avançar para o próximo calabouço, o jogador precisa abrir a porta correta da sala.

### Condições de jogo
- ✅ **Vitória:** fugir do castelo, derrotando o Carrasco Esquelético
- ❌ **Derrota:** morte do jogador (retorna ao último checkpoint com vida zerada)
- 🚫 Não há sistema de pontuação

---

## 📁 Estrutura do projeto

```
jogo-max/
├── main.py
├── settings.py
├── save_manager.py
├── logging_config.py
├── itens.json
├── core/
│   ├── __init__.py
│   ├── camera.py
│   ├── game_scene.py
│   ├── animated_sprite.py
│   ├── navegacao.py
│   ├── recursos.py
│   ├── menu.py
│   ├── menu_fogueira.py
│   └── inventario.py
├── entities/
│   ├── __init__.py
│   ├── entity.py
│   ├── inimigo_base.py
│   ├── player.py
│   ├── monsters/
│   │   ├── __init__.py
│   │   ├── skeleton.py
│   │   ├── globin.py
│   │   ├── mushroom.py
│   │   ├── flying_eye.py
│   │   └── skeleton_boss.py
│   ├── projeteis/
│   │   ├── __init__.py
│   │   ├── projetil.py
│   │   ├── bomba.py
│   │   ├── esporo_mushroom.py
│   │   ├── projetil_flying_eye.py
│   │   └── projetil_boss.py
│   └── objetos/
│       ├── __init__.py
│       ├── item.py
│       ├── bau.py
│       ├── porta.py
│       ├── fogueira.py
│       ├── pocao.py
│       ├── drop.py
│       └── drop_eco.py
├── world/
│   ├── niveis.py
│   ├── rooms.py
│   ├── tile_map.py
│   └── tiles.py
├── ui/
│   ├── __init__.py
│   ├── estilo.py
│   ├── icones.py
│   ├── overlays.py
│   ├── particulas.py
│   └── hud/
│       ├── __init__.py
│       ├── hud.py
│       ├── status.py
│       ├── ecos.py
│       ├── pocao.py
│       ├── mensagens.py
│       ├── notificacao.py
│       ├── boss.py
│       └── debug_painel.py
└── assets/
    ├── maps/                   # calabouco_1.tmx (construído no Tiled)
    └── sprites/
        ├── player/knight/
        ├── enemies/monsters/
        │   ├── skeleton/
        │   ├── esqueletos/
        │   ├── goblin/
        │   ├── mushroom/
        │   └── flying_eye/
        └── objetos/
            ├── baus/
            └── portas/
```

---

## 🚀 Requisitos

- **Python 3.x**
- **pygame-ce** (Community Edition)

---

## 📦 Escopo da primeira entrega

O mínimo a ser entregue na primeira versão é a parte inicial da **Fase 1 (Calabouço)**, com o jogo rodando com as bibliotecas mínimas necessárias.

---

## 🔮 Melhorias futuras

- 🗺️ Mapas diferentes
- ⚔️ Outras armas e armaduras
- 🛒 Sistema de loja para trocar moedas por melhorias

---

<p align="center"><i>Profane Echo — escape, sobreviva, ressoe.</i></p>
