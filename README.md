# 🎮 Projeto de P.O.O. — Profane Echo

## 1. Informações Gerais

**Nome do jogo:** Profane Echo

**Gênero:** Aventura, Plataforma e Metroidvania

**Estilo:** Ação e exploração em 2D

**Ambientação:** Castelo medieval, composto por calabouços, corredores, grandes salões e diferentes andares.

---

# 2. Conceito do Jogo

**Profane Echo** é um jogo de aventura e plataforma com elementos de **Metroidvania**, no qual o jogador controla um cavaleiro habilidoso que foi capturado por um reino e mantido como escravo nos calabouços de um castelo.

O objetivo principal é **escapar do castelo**, enfrentando inimigos e explorando seus diferentes ambientes. Durante a fuga, o jogador poderá recuperar armas e outros recursos, além de enfrentar o **rei do castelo**, que será o principal inimigo da aventura.

O jogador deverá avançar pelos diferentes andares do castelo, derrotando inimigos, superando obstáculos e chegando às áreas necessárias para continuar sua fuga.

---

# 3. História

O protagonista é um cavaleiro habilidoso que foi capturado pelo exército de um reino desconhecido e levado para um enorme castelo.

Preso nos calabouços e obrigado a viver como escravo, o cavaleiro encontra uma oportunidade para escapar.

Sem suas armas e cercado pelos perigos do castelo, ele precisará lutar para recuperar seus equipamentos e encontrar uma saída.

Durante sua fuga, enfrentará esqueletos dos mortos que foram deixados nos calabouços, guardas do castelo e outras criaturas.

Ao chegar ao topo do castelo, o cavaleiro deverá enfrentar o próprio **rei**, responsável por manter aquele reino sob seu domínio.

---

# 4. Objetivo do Jogador

O objetivo principal é:

> **Escapar do castelo e derrotar o rei que governa o reino.**

Para isso, o jogador deverá:

* Explorar os diferentes ambientes do castelo;
* Derrotar inimigos;
* Recuperar armas e outros itens;
* Encontrar os caminhos para os próximos andares;
* Chegar às escadas que levam à próxima fase;
* Derrotar o chefe final;
* Sobreviver até conseguir escapar do castelo.

O jogo **não possuirá sistema de pontuação**.

---

# 5. Jogabilidade

O jogador controla um cavaleiro capaz de:

* Andar para a esquerda e para a direita;
* Pular;
* Atacar com sua espada;
* Realizar Dash;
* Esquivar de ataques;
* Explorar o mapa;
* Enfrentar inimigos;
* Coletar itens e melhorias.

O personagem possuirá principalmente dois atributos:

### ❤️ Vida (PV)

O jogador começará com:

**100 pontos de vida.**

Ao receber ataques dos inimigos, seus pontos de vida serão reduzidos.

Durante o jogo, será possível aumentar a quantidade máxima de vida através de melhorias encontradas pelo mapa.

Quando a vida chegar a **0**, o personagem morrerá e retornará ao último checkpoint.

### ⚡ Stamina

A stamina será utilizada para determinadas ações do personagem, principalmente ações que exigem maior esforço, como o Dash.

---

# 6. Controles

| Tecla      | Ação                       |
| ---------- | -------------------------- |
| **A**      | Movimentar para a esquerda |
| **D**      | Movimentar para a direita  |
| **Espaço** | Pular                      |
| **ESC**    | Abrir o menu               |
| **A + A**  | Dash para a esquerda       |
| **D + D**  | Dash para a direita        |

O Dash será ativado quando o jogador pressionar duas vezes rapidamente a tecla correspondente à direção.

Exemplo:

**A → A = Dash para a esquerda**

**D → D = Dash para a direita**

---

# 7. Inimigos

O jogo possuirá diferentes tipos de inimigos, cada um com comportamentos e características próprias.

### 💀 Esqueletos

São os restos dos mortos encontrados nos calabouços.

Podem possuir pouca ou muita vida e apresentar diferentes comportamentos.

### 🛡️ Guardas

São soldados responsáveis pela proteção do castelo.

Possuem comportamento mais agressivo e podem perseguir o jogador.

### 🐺 Lobos

Inimigos rápidos capazes de perseguir o jogador e realizar ataques rápidos.

### 👑 Rei

Será o inimigo final do jogo.

O rei estará localizado no topo do castelo e será responsável pela batalha final.

---

# 8. Comportamento dos Inimigos

Os inimigos poderão possuir diferentes comportamentos.

Por exemplo:

* Inimigos com muita vida que permanecem em determinada posição;
* Inimigos rápidos que perseguem o jogador;
* Inimigos que atacam quando o jogador se aproxima;
* Inimigos que utilizam projéteis;
* Inimigos com comportamentos específicos.

Quando o jogador for atingido por um inimigo, perderá pontos de vida.

O comportamento diferente entre os inimigos tem como objetivo tornar a exploração e os combates mais variados.

---

# 9. Estrutura do Mapa

O jogo será ambientado em um grande castelo.

A progressão ocorrerá através dos diferentes andares do castelo.

A proposta inicial é possuir entre **3 e 4 fases**.

### Fase 1 — Calabouço

Será a primeira área do jogo e também funcionará como uma espécie de tutorial.

O jogador aprenderá os principais controles e mecânicas enquanto tenta escapar do calabouço.

### Fase 2 — Interior do Castelo

Representará as áreas intermediárias do castelo.

O jogador encontrará corredores, salões, guardas e outros obstáculos.

### Fase 3 — Topo do Castelo

Será a área final da aventura.

O jogador deverá atravessar o topo do castelo até chegar ao rei.

### Fase 4 — Área Final

Uma possível quarta fase poderá ser adicionada posteriormente, dependendo do desenvolvimento do projeto.

---

# 10. Estrutura dos Ambientes

Os mapas serão formados principalmente por:

* Corredores;
* Calabouços;
* Grandes salões;
* Escadas;
* Paredes;
* Colunas;
* Plataformas;
* Áreas de combate;
* Áreas de exploração.

As paredes, colunas e outros elementos do cenário funcionarão como limites físicos do mapa, impedindo que o jogador atravesse áreas que não fazem parte do caminho.

---

# 11. Progressão

Para avançar de uma fase para outra, o jogador deverá encontrar um ponto específico do mapa.

Na primeira versão do projeto, esse ponto será representado pelas **escadas**.

Exemplo:

```text
Calabouço
    ↓
Exploração
    ↓
Combate
    ↓
Encontrar as escadas
    ↓
Próximo andar
```

---

# 12. Itens e Melhorias

Os inimigos poderão deixar itens após serem derrotados.

Além disso, melhorias poderão ser encontradas durante a exploração do mapa.

Entre as possibilidades estão:

* Aumento da vida máxima;
* Recuperação de vida;
* Armas;
* Equipamentos;
* Outros itens de suporte.

Na primeira versão, o sistema de itens será mantido de maneira mais simples para permitir que o foco seja o funcionamento básico do jogo.

---

# 13. Condição de Vitória

O jogador vence ao conseguir concluir sua fuga do castelo.

Para isso, deverá avançar pelas fases e, principalmente, enfrentar e derrotar o rei do castelo.

```text
Início
  ↓
Calabouço
  ↓
Interior do Castelo
  ↓
Topo do Castelo
  ↓
Batalha contra o Rei
  ↓
Fuga do Castelo
  ↓
Vitória
```

---

# 14. Condição de Derrota

A principal condição de derrota será a morte do personagem.

Quando:

```text
Vida = 0
```

o jogador morrerá e retornará ao último checkpoint disponível.

---

# 15. Menu do Jogo

Ao pressionar **ESC**, o jogador poderá abrir o menu do jogo.

Inicialmente, o menu contará com a opção:

* **Sair do jogo**

Outras opções poderão ser adicionadas posteriormente.

---

# 16. Primeira Versão / MVP

Para a primeira versão do projeto, o objetivo será desenvolver somente o **início da primeira fase: o calabouço**.

O objetivo é criar uma versão mínima, porém jogável, capaz de demonstrar as principais mecânicas do projeto.

### Funcionalidades mínimas

* Inicialização do jogo;
* Personagem jogável;
* Movimentação para esquerda e direita;
* Pulo;
* Dash;
* Sistema básico de ataque;
* Sistema de vida;
* Stamina;
* Pelo menos um inimigo;
* Colisão entre personagem e inimigos;
* Dano;
* Morte do personagem;
* Primeiro mapa do calabouço;
* Paredes e limites do cenário;
* Primeiro checkpoint;
* Sistema básico de itens;
* Menu através da tecla ESC.

O objetivo dessa primeira entrega **não será ter o jogo completo**, mas sim construir a base necessária para que as próximas funcionalidades possam ser adicionadas.

---

# 17. Organização dos Arquivos

A estrutura inicial do projeto será organizada da seguinte forma:

```text
jogo-max/
│
├── main.py
├── settings.py
├── itens.json
├── saves.db
├── save_manager.py
│
├── core/
│   ├── __init__.py
│   ├── camera_player.py
│   ├── game_scene.py
│   ├── animated_sprite.py
│   └── inventario.py
│
├── entities/
│   ├── __init__.py
│   ├── entity.py
│   ├── player.py
│   │
│   ├── monsters/
│   │   ├── __init__.py
│   │   ├── skeleton.py
│   │   ├── globin.py
│   │   ├── mushroom.py
│   │   ├── flying_eye.py
│   │   └── skeleton_boss.py
│   │
│   ├── projeteis/
│   │   ├── __init__.py
│   │   ├── projetil.py
│   │   ├── bomba.py
│   │   ├── esporo_mushroom.py
│   │   ├── projetil_flying_eye.py
│   │   └── projetil_boss.py
│   │
│   └── objetos/
│       ├── __init__.py
│       ├── item.py
│       ├── bau.py
│       ├── fogueira.py
│       ├── pocao.py
│       └── drop.py
│
├── world/
│   ├── __init__.py
│   ├── tile_map.py
│   └── rooms.py
│
├── ui/
│   ├── __init__.py
│   └── hud.py
│
└── assets/
    ├── sprites/
    │   ├── player/
    │   │   └── knight/
    │   ├── enemies/
    │   │   └── monsters/
    │   │       ├── skeleton/
    │   │       ├── esqueletos/
    │   │       ├── goblin/
    │   │       ├── mushroom/
    │   │       └── flying_eye/
    │   └── objetos/
    │       └── baus/
    │
    └── tileset/
        └── calabouço/
```

---

# 18. Organização da POO

A estrutura do projeto também permitirá aplicar os principais conceitos de **Programação Orientada a Objetos**.

Uma possível hierarquia será:

```text
Entity
  │
  ├── Player
  │
  └── Monster
       │
       ├── Skeleton
       ├── Goblin
       ├── Mushroom
       ├── FlyingEye
       └── SkeletonBoss
```

A classe `Entity` poderá concentrar características comuns, como:

* Posição;
* Vida;
* Velocidade;
* Colisão;
* Receber dano;
* Estado do personagem.

A classe `Player` poderá acrescentar:

* Stamina;
* Inventário;
* Ataque;
* Pulo;
* Dash;
* Controle do jogador.

Já os monstros poderão herdar de uma classe comum e implementar seus próprios comportamentos.

Por exemplo:

```text
Monster
   │
   ├── Skeleton → ataque corpo a corpo
   ├── Goblin → perseguição
   ├── Mushroom → ataque com esporos
   └── FlyingEye → ataque à distância
```

Isso permitirá utilizar conceitos importantes da disciplina, como:

* **Classes e objetos**
* **Herança**
* **Encapsulamento**
* **Polimorfismo**
* **Abstração**
* **Métodos abstratos**

---

# 19. Bibliotecas

Para a primeira versão, serão utilizadas as bibliotecas necessárias para executar o jogo e implementar suas mecânicas básicas.

A escolha definitiva das bibliotecas dependerá da tecnologia utilizada no desenvolvimento.

A estrutura do projeto será preparada para permitir a expansão das funcionalidades sem precisar reorganizar completamente o código.

---

# 20. Melhorias Futuras

Após a conclusão da primeira versão, o projeto poderá receber diversas melhorias.

### Novos mapas

* Novos andares;
* Novos ambientes;
* Novos tipos de salas;
* Novas áreas do castelo;
* Novos desafios.

### Progressão do personagem

* Sistema de níveis;
* Experiência;
* Atributos;
* Melhorias permanentes.

### Equipamentos

* Novas armas;
* Diferentes espadas;
* Armaduras;
* Equipamentos especiais.

### Economia

* Sistema de moedas;
* Loja;
* Compra de melhorias;
* Itens especiais.

### Novos inimigos

* Novos tipos de monstros;
* Novos comportamentos;
* Inimigos mais fortes;
* Novos chefes.

### Outros sistemas

* Mais checkpoints;
* Sistema de salvamento mais completo;
* Mais itens;
* Novas habilidades;
* Novos ataques;
* Mais fases.

---

# 21. Objetivo do Projeto

O objetivo principal do projeto **Profane Echo** é desenvolver um jogo de plataforma e aventura utilizando os conceitos de **Programação Orientada a Objetos** estudados na disciplina.

A primeira versão terá como foco a construção da base do jogo, principalmente a primeira área do calabouço, permitindo demonstrar o funcionamento das classes, objetos, herança, encapsulamento, polimorfismo e abstração através das diferentes entidades e sistemas do jogo.

A partir dessa base, novas mecânicas e conteúdos poderão ser adicionados gradualmente até que o projeto alcance sua versão completa.
