# jogo-max
jogo do projeto da materia p.o.o

nome do jogo: Profane Echo

o estilo do jogo sera um aventura e plataforma, o genero pode ser chamado tambem de metroidvania

o ambiente do jogo sera em um castelo, com calabouçõs ,grandes salões e ects

a ideia do jogo é sair/ fugir desse castelo derrotando quem quiser lhe impedi

Para vencer o jogador dever fugir do castelo, no caminho recuperando suas armas de voltar e derrotando o rei daquele castelo

O personagem é um cavaleiro habilidoso que foi capturado por esse reino e aprisionado no calabouço do castelo, sendo mantido como um escravo.
o player se movimento para esquedar ou direita, podendo pular e dar dash para esquivar de ataques, pode ataca com sua espada.
possuindo os atributos de vida e stamina

os inimigos serao esqueletos dos mortos no calabouço, guardas do castelos, lobos, e o inimigo final o rei do castelo

o comportamento deles irao varia alguns com mais vida que ficam parados, outros mais rapidos que perseguem o player e ect
se colidir com o inimigo sua vida ira diminui

o mapa como mencinado anteriomente sera situado em um castelo, com a medida que o jogador avança de fase são os andares do castelo que o player sobe, o jogo esta cotado para ter 3-4 fase a primeira o calabouço- tutorial, a segunda o meio do castelo, e a terceira o topo do castelo, os caminhos serao corredores, as paredes que nao poderao ser atravessadas vao desde de colunas a paredes normais, os itens ficaram com os proprios inimigos a serem derrotados


o jogo nao tera um sistema de pontuaçao

o jogador começara com uma quantidade de 100 pontos de vida ou pv, esse numero podera ser aumentado com o decorre do jogo pegando melhorias no mapa, como citado antes o jogador perde vida se levar hits dos inimigos, e se a barra de vida for zerada, o player morre e retorna a ultimo checkpoint

sobre as teclas serao basicas a tecla a para ir a esquerda e ser for clicada 2 vezes no tempo certo o jogador dara um dash para a direçao da tecla, a tecla d para ir a direita e ser for clicada 2 vezes no tempo certo o jogador dara um dash para a direçao da tecla, a tecla do espaço sera para pular, e a tecla esc sera para abrir o menu do jogo que tera a opçao de sair

o jogo começa no calabouço, e para passar de fase tera que chegar no local espesifico no caso as escadas, a condiçao de derrota seria ser morto, oque acontece durante a partida é o player sofre tentativas de homicidios durante a jogatina

regras nao tem muito oq citar os limites do mapa serão as parede que nao tera como passar


sobre a organização dos arquivos tenho a parte dessa fase inicial do projeto

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
│   └── monsters/
│       ├── __init__.py
│       ├── skeleton.py
│       ├── globin.py
│       ├── mushroom.py
│       ├── flying_eye.py
│       └── skeleton_boss.py
│   └── projeteis/
│       ├── __init__.py
│       ├── projetil.py
│       ├── bomba.py
│       ├── esporo_mushroom.py
│       ├── projetil_flying_eye.py
│       └── projetil_boss.py
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

o minimo que queremos entrega na primeira versão seria a parte inicial da fase 1(calabouço)
o minino para o jogo rodar seria as bibliotecas


melhorias futuras sao muitas
mapas diferentes, sistema de levels do player, outras armas e armaduras, sistema de uma loja para trocar moedas por melhorias e etc
