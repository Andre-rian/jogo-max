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
| Pontos de Vida (PV) | 100 | Aumenta automaticamente conforme o jogador sobe de **level** |
| Stamina | — | Utilizada em ações como dash e ataque |

Se a barra de vida chegar a zero, o jogador **morre** e retorna ao **último checkpoint**.

### 📈 Sistema de níveis (Levels)
O jogador evolui através de um sistema de **levels**. A cada level ganho, seus **Pontos de Vida máximos aumentam**, tornando-o mais resistente para enfrentar as fases seguintes do castelo.

### 🎒 Inventário
O jogador conta com um **sistema de inventário**, onde itens, poções e equipamentos recuperados ao longo do jogo podem ser armazenados e gerenciados.

---

## ⌨️ Controles

| Tecla | Ação |
|---|---|
| `A` | Mover para a esquerda *(2x rápido = dash para a esquerda)* |
| `D` | Mover para a direita *(2x rápido = dash para a direita)* |
| `Espaço` | Pular |
| `ESC` | Abrir menu do jogo (com opção de sair) |

---

## 👹 Inimigos

| Inimigo | Comportamento |
|---|---|
| Esqueleto | Morto-vivo do calabouço |
| Guarda do castelo | Patrulha e defende o território |
| Lobo | Mais rápido, persegue o jogador |
| **Rei do castelo** | Chefe final (*boss*) |

> Alguns inimigos possuem mais vida e ficam parados, enquanto outros são mais rápidos e perseguem o jogador ativamente — cada tipo com um comportamento único.

---

## 🏰 Fases e progressão

O mapa está situado dentro de um castelo. Conforme o jogador avança, ele **sobe os andares** do castelo, cada um representando uma fase:

1. **Calabouço** — fase tutorial
2. **Meio do castelo**
3. **Topo do castelo**

Os caminhos são formados por corredores, com colunas e paredes intransponíveis delimitando os limites do mapa. Os itens são obtidos derrotando os próprios inimigos que os carregam.

Para avançar de fase, o jogador precisa alcançar um ponto específico do mapa (ex: escadas).

### Condições de jogo
- ✅ **Vitória:** fugir do castelo, derrotando o rei
- ❌ **Derrota:** morte do jogador (retorna ao último checkpoint com vida zerada)
- 🚫 Não há sistema de pontuação

---

## 📁 Estrutura do projeto

```
jogo-max/
├── main.py
├── settings.py
├── itens.json
├── saves.db
├── save_manager.py
├── core/
│   ├── __init__.py
│   ├── camera_player.py
│   ├── game_scene.py
│   ├── animated_sprite.py
│   └── inventario.py
├── entities/
│   ├── __init__.py
│   ├── entity.py
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
│       ├── fogueira.py
│       ├── pocao.py
│       └── drop.py
├── world/
│   ├── __init__.py
│   ├── tile_map.py
│   └── rooms.py
├── ui/
│   ├── __init__.py
│   └── hud.py
└── assets/
    ├── sprites/
    │   ├── player/knight/
    │   ├── enemies/monsters/
    │   │   ├── skeleton/
    │   │   ├── esqueletos/
    │   │   ├── goblin/
    │   │   ├── mushroom/
    │   │   └── flying_eye/
    │   └── objetos/baus/
    └── tileset/calabouço/
```

---

## 🚀 Requisitos

- **Python 3.x**
- **Pygame**

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
