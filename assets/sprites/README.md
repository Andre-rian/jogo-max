# Sprites do Profane Echo

Esta pasta separa **sprites usados pelo jogo** de **pacotes em triagem**. Os
arquivos dentro de `_entrada/` não são carregados. A árvore final é organizada
por tela/função, não por autor.

## Estrutura

```text
assets/sprites/
├── _entrada/                     # pacotes originais e triagem (não usados no jogo)
│   ├── _inbox/                    # downloads ainda sem classificação
│   ├── _revisar/                  # arquivos ambíguos / não aprovados
│   ├── itens/                     # packs de ícones de itens
│   ├── ui/                        # packs de molduras, painéis e botões
│   ├── prompts/                   # packs de teclado e controle
│   ├── fontes/                    # fontes para teste
│   ├── LEIA-ME.md
│   └── CREDITOS_E_LICENCAS.md
│
├── ui/
│   ├── menu/
│   │   ├── save_slots/            # normal, selecionado, indisponível
│   │   └── detalhes/
│   ├── inventario/
│   │   ├── paineis/
│   │   ├── slots/
│   │   ├── abas/
│   │   └── tooltips/
│   ├── botoes/                    # normal, selecionado, pressionado, desabilitado
│   ├── prompts/
│   │   ├── teclado/
│   │   └── controle/              # reservado, não significa suporte ativo
│   ├── hud/
│   └── cursores/
│
├── itens/
│   ├── equipamentos/
│   ├── consumiveis/
│   ├── chaves/
│   ├── materiais/
│   ├── ecos/
│   └── _default/                  # ícone para item sem sprite
│
├── habilidades/                  # somente quando o sistema precisar
├── fx_ui/                        # efeitos visuais opcionais
│
├── enemies/                      # sprites existentes de inimigos
├── objetos/                      # sprites existentes de cenário/objetos
└── player/                       # sprites existentes do jogador
```

Diretórios sem arquivos usam `.gitkeep` como marcador.

## Regras de nome

- ASCII minúsculo, sem acento, espaço ou parênteses.
- `snake_case`, nome semântico, alinhado ao ID real do item no código.
- Estados como sufixo: `slot_normal.png`, `slot_selecionado.png`,
  `slot_equipado.png`, `slot_desabilitado.png`.
- Fallback de item: `itens/_default/item_desconhecido.png`.

## Entrada de novos arquivos

`_entrada/` é a área de triagem. O fluxo completo está em
[`_entrada/LEIA-ME.md`](_entrada/LEIA-ME.md). Resumo:

1. Guardar o pack original em `_entrada/` sem renomear.
2. Registrar autor, URL, versão e licença em
   [`_entrada/CREDITOS_E_LICENCAS.md`](_entrada/CREDITOS_E_LICENCAS.md).
3. Selecionar visualmente os elementos aprovados com o responsável.
4. Copiar só os aprovados para `ui/`, `itens/`, `habilidades/` ou `fx_ui/`.
5. Testar no jogo antes de considerar a escolha definitiva.

Pacotes com restrição de redistribuição ficam fora do Git. Não versionar packs
completos nem conteúdo premium.

### Moldura opcional LY005

O inventário usa `_entrada/itens/lygame_dark_fantasy/UI/Panel1.png` como moldura
preferencial quando o arquivo está presente localmente. Se ele faltar, a moldura
anterior é usada automaticamente. O pack lygame é restrito a uso no jogo (sem
redistribuição), então não deve ser versionado; o `.gitignore` já cobre o
diretório e as prévias derivadas. `Panel1_small.png` (LY006) fica reservado para
futuras interfaces menores.

## Integração técnica (Pygame)

- Carregar PNG com transparência usando `convert_alpha()` após inicializar o
  display.
- Manter cache de `Surface`; não carregar nem escalar a cada frame.
- Usar `pygame.transform.scale()` com escala inteira (nearest-neighbor), nunca
  `smoothscale()` para pixel art.
- Descobrir tile, margens e espaçamento antes de recortar spritesheets.
- Desenhar moldura e ícone separadamente.
- Oferecer fallback (`itens/_default/item_desconhecido.png`) sem travar.
- Preferir painéis 9-slice; não esticar elementos ornamentados.
- Mapear ícones por ID real de item, não por nome de exibição ou índice.

## Documentação

- Plano de sprites e UI: [docs/arte/SPRITES_UI_PLANO.md](../../docs/arte/SPRITES_UI_PLANO.md)
- Origens e licenças: [docs/arte/ASSETS_UI_ORIGENS.md](../../docs/arte/ASSETS_UI_ORIGENS.md)
- Mapa item → sprite: [docs/arte/INVENTARIO_SPRITES.md](../../docs/arte/INVENTARIO_SPRITES.md)
- Relatório dos packs recebidos: [docs/arte/RELATORIO_ENTRADA_SPRITES.md](../../docs/arte/RELATORIO_ENTRADA_SPRITES.md)
