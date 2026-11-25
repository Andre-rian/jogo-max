import pygame
import logging
log = logging.getLogger("inventario")

from settings import Screen_widht, Screen_height
from core.audio import audio
from entities.objetos.item import get_item
from core.navegacao import hover_index, mouse_mouveu
from ui.icones import desenhar_icone_item
from ui.sprites_itens import precarregar as precarregar_sprites_itens
from ui.prompts_teclas import desenhar_prompts
from ui.painel_lygame import desenhar_painel_lygame, disponivel as lygame_disponivel
from ui.estilo import (
    Fonte_titulo, Fonte_texto, obter_escala_texto,
    Roxo_espectral, Azul_espectral, Azul_claro,
    Branco_texto, Cinza_texto, Vermelho_ritual,
    Cinza_carvao, Cinza_azulado,
    desenhar_overlay, desenhar_painel, desenhar_botao,
    desenhar_eco_profano, desenhar_linha_ornamental,
    escurecer, misturar, versao_escala_texto
)

USAR_PAINEL_LYGAME = True


class Inventario:

    def __init__(self, tela):
        self.tela = tela
        self.aberto = False

        pygame.font.init()
        self._frame = 0
        self._configurar_fontes()

        #abas de navegaçao
        self.abas = ["Equipamentos", "Itens", "Chaves", "Materiais"]
        self.aba_atual = 0


        #menu ações
        self.menu_contexto = None # NOne - fechado, senao iria guarda o item e a posição
        self.callback_descartar = None
        self.opcao_contexto_selecionada = 0

        #grid de itens
        self.slot_selecionado = None
        self._ignorar_frame_abertura = False
        self.slots_por_linha = 4


        self.usar_painel_lygame = USAR_PAINEL_LYGAME
        self._atualizar_layout()
        precarregar_sprites_itens()

    def _atualizar_layout(self):
        escala = versao_escala_texto() and None
        from ui.estilo import obter_escala_texto
        escala = obter_escala_texto()
        self.painel_w = min(Screen_widht - 40, int(840 * max(1.0, 0.92 + 0.12 * escala)))
        self.painel_h = min(Screen_height - 90, int(520 * max(1.0, 0.92 + 0.14 * escala)))
        self.painel_x = Screen_widht // 2 - self.painel_w // 2
        self.painel_y = Screen_height // 2 - self.painel_h // 2 + 10
        self.slots_por_linha = 4

    def _configurar_fontes(self):
        self.fonte_titulo = Fonte_titulo(21, negrito=True)
        self.fonte_normal = Fonte_texto(16)
        self.fonte_pequena = Fonte_texto(14)
        self.cor_texto_secundario = misturar(Cinza_texto, Branco_texto, 0.28)
        self._versao_escala = versao_escala_texto()
        if hasattr(self, 'painel_w'):
            self._atualizar_layout()

    def _garantir_escala(self):
        if self._versao_escala != versao_escala_texto():
            self._configurar_fontes()



    def _pad_conteudo(self):
        if self.usar_painel_lygame and lygame_disponivel():
            return 6
        return 0

    def _layout_colunas(self, px, py, pw, ph, pad):
        topo = py + 10 + pad
        base = py + ph - 34 - pad
        col_esq_w = max(150, min(210, int(pw * 0.24)))
        col_dir_w = max(190, min(300, int(pw * 0.30)))
        col1_x = px + col_esq_w
        col2_x = px + pw - col_dir_w
        if col2_x - col1_x < 180:
            col_dir_w = max(160, pw - col_esq_w - 180)
            col2_x = px + pw - col_dir_w
        return {
            "topo": topo, "base": base,
            "col1_x": col1_x, "col2_x": col2_x,
            "col_esq_w": col_esq_w - 20 - pad,
            "col_grid_w": max(120, col2_x - col1_x - 20),
            "col_dir_w": max(120, pw - (col2_x - px) - 20 - pad),
        }

    def _slot_geom(self, layout):
        gap = max(6, int(self.fonte_pequena.get_height() * 0.5))
        w = layout["col_grid_w"]
        slot = int((w - gap * (self.slots_por_linha - 1)) / self.slots_por_linha)
        slot = max(44, min(72, slot))
        return slot, gap

    def _rects_grid(self, itens, layout):
        slot, gap = self._slot_geom(layout)
        rects = []
        for i in range(len(itens)):
            col = i % self.slots_por_linha
            lin = i // self.slots_por_linha
            sx = layout["col1_x"] + 10 + col * (slot + gap)
            sy = layout["topo"] + lin * (slot + gap)
            rects.append(pygame.Rect(sx, sy, slot, slot))
        return rects


    #def abrir e fecha o inventario
    def abrir(self):
        self.aberto = True
        self.aba_atual = 0
        self.slot_selecionado = None
        self._ignorar_frame_abertura = True #trava até o proximo atualizar
        self.menu_contexto = None
        self.opcao_contexto_selecionada = 0
        audio.play_sfx("ui_inventory_open")


    def fechar(self):
        if not self.aberto:
            return
        self.aberto = False
        self.menu_contexto = None
        self.opcao_contexto_selecionada = 0
        audio.play_sfx("ui_inventory_close")


    #retorna a lista de itens da aba atual
    def _itens_da_aba(self, player):

        if self.aba_atual == 0:     #equipamentos
            itens = []
            for slots in ["mao_direita", "mao_esquerda", "armadura"]:
                id_ = player.inventario[slots]
                if id_:
                    item = get_item(id_)
                    #so adicionar na lista se for equipavel
                    if item and item.tipo in ["arma", "armadura"]:
                        itens.append(item)

            for id_ in player.inventario["equipamentos"]:
                item = get_item(id_)
                if item:
                    itens.append(item)
            return itens

        elif self.aba_atual == 1: #itens
            itens = []

            if player.pocao:
                itens.insert(0, player.pocao)

            for id_, quantidade in player.inventario["itens"].items():
                item = get_item(int(id_))

                if item:

                    item.quantidade = quantidade #atualiza a quantidade real de itens
                    itens.append(item)

            return itens


        elif self.aba_atual == 2: #chaves e relíquias (itens únicos, sem empilhamento)
            itens = []
            for id_ in player.inventario["chaves"]:
                item = get_item(id_)
                if item:
                    itens.append(item)
            return itens

        elif self.aba_atual == 3: #materias
            itens = []
            for id_, quantidade in player.inventario["materiais"].items():
                item  = get_item(int(id_))
                if item:
                    item.quantidade = quantidade
                    itens.append(item)
            return itens

        return []



    #atualizar
    def atualizar(self, eventos, player):
        if not self.aberto:
            return

        self._garantir_escala()
        if self._ignorar_frame_abertura:
            self._ignorar_frame_abertura = False
            return #ignora qualquer evento que sobra do abrir inventario

        escs_no_frame = [e for e in eventos if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE]
        if escs_no_frame:
            log.debug(f"[FRAME] {len(escs_no_frame)} evento(s) ESC neste frame")



        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h
        pad_conteudo = self._pad_conteudo()
        pos_mouse = pygame.mouse.get_pos()

        #hover na abas
        aba_w = pw // len(self.abas)
        for i in range(len(self.abas)):
            aba_x = px + i * aba_w
            aba_y = py - 36
            rect_aba = pygame.Rect(aba_x, aba_y, aba_w - 2, 36)
            if rect_aba.collidepoint(pos_mouse):
                pass


        #hover no slots do grid
        itens = self._itens_da_aba(player)
        layout = self._layout_colunas(px, py, pw, ph, pad_conteudo)
        itens_com_rect = []
        for i, rect in enumerate(self._rects_grid(itens, layout)):
            itens_com_rect.append((i, rect))

        # hover de opcoes do menu de contexto (1x por movimento)
        if self.menu_contexto and mouse_mouveu(eventos):
            mx = self.menu_contexto["x"]
            my = self.menu_contexto["y"]
            opcoes = self.menu_contexto["opcoes"]
            for i, opcao in enumerate(opcoes):
                oy = my + 4 + i * 28
                rect_opcao = pygame.Rect(mx, oy, 110, 28)
                if rect_opcao.collidepoint(pos_mouse):
                    if i != self.opcao_contexto_selecionada:
                        self.opcao_contexto_selecionada = i
                        audio.play_sfx("ui_move")
                    break

        indice_houver = hover_index(eventos, pos_mouse, itens_com_rect)
        if indice_houver is not None and indice_houver != self.slot_selecionado:
            self.slot_selecionado = indice_houver
            item = itens[indice_houver]
            if hasattr(item, "id"):
                player.itens_novos.discard(item.id)
            # evitar som de navegacao do grid enquanto contexto modal esta aberto
            if not self.menu_contexto:
                audio.play_sfx("ui_move")
        elif indice_houver is not None:
            item = itens[indice_houver]
            if hasattr(item, "id"):
                player.itens_novos.discard(item.id)

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    log.debug(f"[esc] menu_contexto={'ABERTO' if self.menu_contexto else 'FECHADO'}")

                    if self.menu_contexto: #verificar se o menu de contexto esta aberto
                        audio.play_sfx("ui_back")
                        self.menu_contexto = None
                        self.opcao_contexto_selecionada = 0
                        return
                    # fechar inventario = voltar (ui_back)
                    audio.play_sfx("ui_back")
                    self.aberto = False
                    self.menu_contexto = None
                    self.opcao_contexto_selecionada = 0
                    log.debug("[esc] -> fechando o inventario inteiro")
                    return

                if self.menu_contexto:
                    opcoes = self.menu_contexto["opcoes"]
                    if evento.key == pygame.K_UP:
                        novo = (self.opcao_contexto_selecionada - 1) % len(opcoes)
                        if novo != self.opcao_contexto_selecionada:
                            self.opcao_contexto_selecionada = novo
                            audio.play_sfx("ui_move")
                    elif evento.key == pygame.K_DOWN:
                        novo = (self.opcao_contexto_selecionada + 1) % len(opcoes)
                        if novo != self.opcao_contexto_selecionada:
                            self.opcao_contexto_selecionada = novo
                            audio.play_sfx("ui_move")
                    elif evento.key == pygame.K_RETURN:
                        opcao = opcoes[self.opcao_contexto_selecionada]
                        self._confirmar_opcao_contexto_ui(opcao, player)
                    return   # nao deixa cair nas teclas de navegacao do grid abaixo


                elif evento.key == pygame.K_TAB:
                    self.aba_atual = (self.aba_atual + 1) % len(self.abas)
                    self.slot_selecionado = 0
                    audio.play_sfx("ui_move")

                elif evento.key == pygame.K_RIGHT:
                    itens = self._itens_da_aba(player)
                    if itens:
                        anterior = self.slot_selecionado
                        atual = self.slot_selecionado if self.slot_selecionado is not None else -1
                        self.slot_selecionado = min(len(itens) - 1, atual+ 1)
                        if self.slot_selecionado != anterior:
                            audio.play_sfx("ui_move")

                elif evento.key == pygame.K_LEFT:
                    anterior = self.slot_selecionado
                    atual = self.slot_selecionado if self.slot_selecionado is not None else  1
                    self.slot_selecionado = max(0, atual - 1)
                    if self.slot_selecionado != anterior:
                        audio.play_sfx("ui_move")


                elif evento.key == pygame.K_DOWN:
                    itens = self._itens_da_aba(player)
                    anterior = self.slot_selecionado
                    atual = self.slot_selecionado if self.slot_selecionado is not None else -self.slots_por_linha
                    novo = atual + self.slots_por_linha
                    if novo < len(itens):
                        self.slot_selecionado = novo
                    if self.slot_selecionado != anterior:
                        audio.play_sfx("ui_move")

                elif evento.key == pygame.K_UP:
                    anterior = self.slot_selecionado
                    if self.slot_selecionado is not None:
                        novo = self.slot_selecionado - self.slots_por_linha
                        if novo >= 0:
                            self.slot_selecionado = novo
                    if self.slot_selecionado != anterior:
                        audio.play_sfx("ui_move")

                elif evento.key == pygame.K_RETURN:
                        itens = self._itens_da_aba(player)
                        if self.slot_selecionado is not None and self.slot_selecionado < len(itens):
                            item = itens[self.slot_selecionado]
                            audio.play_sfx("ui_confirm")
                            layout = self._layout_colunas(px, py, pw, ph, pad_conteudo)
                            rects = self._rects_grid(itens, layout)
                            r = rects[self.slot_selecionado]
                            from entities.objetos.item import Arma, Consumivel
                            if isinstance(item, Arma):
                                slots_equipados = [
                                    player.inventario["mao_direita"],
                                    player.inventario["mao_esquerda"],
                                    player.inventario["armadura"]]
                                if hasattr(item, "id") and item.id in [s for s in slots_equipados if s is not None]:
                                    opcoes = ["Desequipar"]
                                else:
                                    opcoes = ["Equipar", "Descartar"]
                            elif isinstance(item, Consumivel) or hasattr(item, "cargas"):
                                opcoes = ["Usar", "Descartar"] if hasattr(item, "id") else ["Usar"]
                            else:
                                opcoes = ["Descartar"]
                            mx = min(r.right + 4, px + pw - 120)
                            self.menu_contexto = {
                                "item": item,
                                "x": mx,
                                "y": r.y,
                                "opcoes": opcoes
                            }
                            self.opcao_contexto_selecionada = 0

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                #clique nas abas
                for i in range(len(self.abas)):
                    aba_x = px + i * aba_w
                    aba_y = py - 36
                    rect_aba = pygame.Rect(aba_x, aba_y, aba_w - 2, 36)
                    if rect_aba.collidepoint(pos_mouse):
                        if self.aba_atual != i:
                            self.aba_atual = i
                            self.slot_selecionado = 0
                        else:
                            self.slot_selecionado = 0
                        audio.play_sfx("ui_confirm")
                        break


                if self.menu_contexto:
                    mx = self.menu_contexto["x"]
                    my = self.menu_contexto["y"]
                    opcoes = self.menu_contexto["opcoes"]
                    opcao_h = 28
                    menu_w = 110

                    clicou_opcao = False
                    for i, opcao in enumerate(opcoes):
                        oy = my + 4 + i * opcao_h
                        rect_opcao = pygame.Rect(mx, oy, menu_w, opcao_h)
                        if rect_opcao.collidepoint(pos_mouse):
                            clicou_opcao = True
                            self.opcao_contexto_selecionada = i
                            self._confirmar_opcao_contexto_ui(opcao, player)
                            break

                    if not clicou_opcao:
                        audio.play_sfx("ui_back")
                        self.menu_contexto = None #clicou fora do menu - fecha ele
                    return




                #clique nos slots do grids
                itens = self._itens_da_aba(player)
                layout = self._layout_colunas(px, py, pw, ph, pad_conteudo)
                for i, rect_slot in enumerate(self._rects_grid(itens, layout)):
                    if rect_slot.collidepoint(pos_mouse):
                        self.slot_selecionado = i
                        audio.play_sfx("ui_confirm")
                        item = itens[i]
                        from entities.objetos.item import Arma, Consumivel
                        if isinstance(item, Arma):
                            slots_equipados = [
                                player.inventario["mao_direita"],
                                player.inventario["mao_esquerda"],
                                player.inventario["armadura"]]
                            if hasattr(item, "id") and item.id in [s for s in slots_equipados if s is not None]:
                                opcoes = ["Desequipar"]
                            else:
                                opcoes = ["Equipar", "Descartar"]
                        elif isinstance(item, Consumivel) or hasattr(item, "cargas"):
                            opcoes = ["Usar", "Descartar"] if hasattr(item, "id") else ["Usar"]
                        else:
                            opcoes = ["Descartar"]
                        mx = min(rect_slot.right + 4, px + pw - 120)
                        self.menu_contexto = {"item": item, "x": mx, "y": rect_slot.y, "opcoes": opcoes}
                        self.opcao_contexto_selecionada = 0
                        break

    def _opcao_contexto_valida(self, opcao, item, player):
        from entities.objetos.item import Arma, Consumivel
        if item is None:
            return False
        if opcao == "Equipar":
            return isinstance(item, Arma)
        if opcao == "Usar":
            return isinstance(item, Consumivel) or hasattr(item, "cargas")
        if opcao == "Descartar":
            return self.callback_descartar is not None and hasattr(item, "id")
        if opcao == "Desequipar":
            return isinstance(item, Arma)
        return False

    def _confirmar_opcao_contexto_ui(self, opcao, player):
        if not self.menu_contexto:
            return
        item = self.menu_contexto.get("item")
        if not self._opcao_contexto_valida(opcao, item, player):
            audio.play_sfx("ui_error")
            return
        audio.play_sfx("ui_confirm")
        self._executar_opcao(opcao, item, player, som_ui=True)
        self.menu_contexto = None
        self.opcao_contexto_selecionada = 0

    def _tentar_equipar(self, item, player, tocar_som=True):
        from entities.objetos.item import Arma
        if isinstance(item, Arma):

            #se tem algo equipado na mao, subistutuio e retorna ele para o inventario
            id_atual = player.inventario["mao_direita"]
            if id_atual == item.id:
                return
            if id_atual is not None:
                player.inventario["equipamentos"].append(id_atual)


            #remove da lista de itens e coloca na mao direita
            if item.id in player.inventario["equipamentos"]:
                player.inventario["equipamentos"].remove(item.id)
            player.inventario["mao_direita"] = item.id
            player.itens_novos.discard(item.id)
            if tocar_som:
                audio.play_sfx("equip_weapon")


    def _executar_opcao(self, opcao, item , player, som_ui=False):
        from entities.objetos.item import Arma, Consumivel

        if opcao == "Equipar":
            if not isinstance(item, Arma):
                if not som_ui:
                    audio.play_sfx("ui_error")
                return
            self._tentar_equipar(item, player, tocar_som=not som_ui)


        elif opcao == "Usar":

            if isinstance(item, Consumivel):
                item.usar(player, player.inventario)
            elif item is player.pocao:
                item.usar(player)
            else:
                if not som_ui:
                    audio.play_sfx("ui_error")

        elif opcao == "Descartar" and not self.callback_descartar:
            if not som_ui:
                audio.play_sfx("ui_error")

        elif opcao == "Descartar" and self.callback_descartar:
            if not hasattr(item, "id"):
                return
            #checar se esta equipado e desequipar primeiro
            if player.inventario["mao_direita"] == item.id:
                player.inventario["mao_direita"] = None

            elif player.inventario["mao_esquerda"] == item.id:
                player.inventario["mao_esquerda"] = None

            elif player.inventario["armadura"] == item.id:
                player.inventario["armadura"] = None



            #remove do inventario
            for lista in ["equipamentos", "chaves"]:
                if item.id in player.inventario[lista]:
                    player.inventario[lista].remove(item.id)
                    break

            for categoria in ("itens", "materiais"):
                chave = str(item.id)
                if chave in player.inventario[categoria]:
                    player.inventario[categoria][chave] -= 1
                    if player.inventario[categoria][chave] <= 0:
                        player.inventario[categoria].pop(chave)


            self.callback_descartar(item.id)

        elif opcao == "Desequipar":
            if isinstance(item, Arma):
                if player.inventario["mao_direita"] == item.id:
                    player.inventario["mao_direita"] = None
                    player.inventario["equipamentos"].append(item.id)
            else:
                if not som_ui:
                    audio.play_sfx("ui_error")

    def desenhar(self, player):
        if not self.aberto:
            return
        self._garantir_escala()
        self._frame += 1
        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h


        #fundo semitrasparente
        desenhar_overlay(self.tela, 150)


        #painel principal
        painel_rect = pygame.Rect(px, py, pw, ph)
        usou_lygame = False
        if self.usar_painel_lygame:
            usou_lygame = desenhar_painel_lygame(self.tela, painel_rect)
        if not usou_lygame:
            desenhar_painel(self.tela, painel_rect, self._frame,
                            cor_borda=Azul_espectral)

        pad_conteudo = 6 if usou_lygame else 0
        conteudo_topo = py + 10 + pad_conteudo
        conteudo_base = py + ph - 10 - pad_conteudo


        #abas
        aba_w = pw // len(self.abas)
        for i, aba in enumerate(self.abas):
            aba_x = px + i * aba_w
            aba_y = py - 36
            selecionada = i == self.aba_atual
            rect_aba = pygame.Rect(aba_x, aba_y, aba_w - 2, 36)
            desenhar_botao(self.tela, rect_aba, aba, selecionada, self._frame,
                           fonte_btn=self.fonte_normal,
                           cor_texto=self.cor_texto_secundario,
                           marcador=False, brilho=False)

        layout = self._layout_colunas(px, py, pw, ph, pad_conteudo)
        col1_x, col2_x = layout["col1_x"], layout["col2_x"]
        pygame.draw.line(self.tela, escurecer(Azul_espectral, 0.6),
                         (col1_x, conteudo_topo), (col1_x, conteudo_base))
        self._desenhar_slots_equipados(
            player, px + 10 + pad_conteudo, py + 20 + pad_conteudo, layout["col_esq_w"]
        )
        self._desenhar_grid(player, layout)
        self._desenhar_detalhes(player, col2_x + 10, conteudo_topo, layout["col_dir_w"])
        try:
            from ui.estilo import obter_escala_texto as _esc
            escala = _esc()
        except Exception:
            escala = 1.0
        if escala <= 1.25:
            prompts = [(["seta_esquerda","seta_direita","seta_cima","seta_baixo"], "navegar"), (["tab"], "aba"), (["esc"], "fechar")]
        else:
            prompts = [(["tab"], "aba"), (["esc"], "fechar")]
        desenhar_prompts(self.tela, prompts, px + pw // 2, py + ph - 26 - pad_conteudo,
                         self.fonte_pequena, self.cor_texto_secundario)

        #menu do contexto/ açoes para os itens
        if self.menu_contexto:
            self._desenhar_menu_contexto()


    def _desenhar_menu_contexto(self):
        if not self.menu_contexto:
            return

        mx = self.menu_contexto["x"]
        my = self.menu_contexto["y"]
        opcoes = self.menu_contexto["opcoes"]

        opcao_h = 28
        menu_w = 110
        menu_h = len(opcoes) * opcao_h + 8


        pygame.draw.rect(self.tela, Cinza_carvao,
                         (mx, my, menu_w, menu_h), border_radius=4)
        pygame.draw.rect(self.tela, escurecer(Azul_espectral, 0.35),
                         (mx, my, menu_w, menu_h), 1, border_radius=4)

        for i, opcao in enumerate(opcoes):
            oy = my + 4 + i * opcao_h
            rect_opcao = pygame.Rect(mx, oy, menu_w, opcao_h)

            if i == self.opcao_contexto_selecionada:
                pygame.draw.rect(self.tela, Cinza_azulado, rect_opcao, border_radius=3)
                pygame.draw.rect(self.tela, Azul_claro, rect_opcao, 1, border_radius=3)

            cor_txt = Azul_claro if i == self.opcao_contexto_selecionada else Branco_texto
            txt = self.fonte_normal.render(opcao, True, cor_txt)
            self.tela.blit(txt, (mx + 10, oy + 6))











    #slots equipados
    def _desenhar_slots_equipados(self, player, x, y, largura):
        titulo = self.fonte_normal.render("Equipado", True, Roxo_espectral)
        self.tela.blit(titulo, (x, y))



        slots = [
            ("Mão Direita", "mao_direita"),
            ("Mão Esquerda", "mao_esquerda"),
            ("Armadura", "armadura"),
        ]



        for i, (label, chave) in enumerate(slots):
            sy = y + 26 + i * 70


            item_id = player.inventario.get(chave)

            item = get_item(item_id) if item_id is not None else None


            #fundo do slot
            pygame.draw.rect(self.tela, escurecer(Cinza_carvao, 0.15),
                             (x, sy, largura, 58), border_radius=4)
            pygame.draw.rect(self.tela, escurecer(Azul_espectral, 0.5),
                             (x, sy, largura, 58), 1, border_radius=4)

            #label
            lbl = self.fonte_pequena.render(label, True, self.cor_texto_secundario)
            self.tela.blit(lbl, (x + 6, sy + 4))


            #item ou vazio
            if item:

                nome = self.fonte_pequena.render(item.nome, True, Branco_texto)
                self.tela.blit(nome, (x + 4, sy + 22))

                if hasattr(item, "dano"):
                    dano = self.fonte_pequena.render(f"Dano: {item.dano}",
                                                     True, Azul_claro)
                    self.tela.blit(dano, (x + 4, sy + 40))

                tamanho_icone = 26
                icone_x = x + largura - tamanho_icone - 4
                icone_y = sy + 16
                desenhar_icone_item(
                    self.tela, item, icone_x + tamanho_icone // 2,
                    icone_y + tamanho_icone // 2, icone_x, icone_y,
                    tamanho_icone, self.fonte_pequena
                )

            else:
                vazio = self.fonte_pequena.render("- Vazio -", True, self.cor_texto_secundario)
                self.tela.blit(vazio, (x + 4, sy + 28))


    #grid de itens
    def _desenhar_grid(self, player, layout):
        itens = self._itens_da_aba(player)
        slot, gap = self._slot_geom(layout)
        rects = self._rects_grid(itens, layout)
        clip = pygame.Rect(layout["col1_x"], layout["topo"], layout["col_grid_w"] + 20, layout["base"] - layout["topo"])
        antigo = self.tela.get_clip()
        self.tela.set_clip(clip.clip(antigo))
        for i, item in enumerate(itens):
            rect = rects[i]
            sx, sy = rect.x, rect.y
            selecionado = self.slot_selecionado is not None and i == self.slot_selecionado
            cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.5)
            cor_fundo = Cinza_azulado if selecionado else escurecer(Cinza_carvao, 0.15)
            slots_equipados = [
                player.inventario["mao_direita"],
                player.inventario["mao_esquerda"],
                player.inventario["armadura"],
            ]
            esta_equipado = hasattr(item, "id") and item.id in [s for s in slots_equipados if s is not None]
            pygame.draw.rect(self.tela, cor_fundo, rect, border_radius=4)
            pygame.draw.rect(self.tela, cor_borda, rect, 2, border_radius=4)
            cx, cy = rect.centerx, rect.centery
            desenhar_icone_item(self.tela, item, cx, cy, sx, sy, slot, self.fonte_pequena)
            if esta_equipado:
                desenhar_eco_profano(self.tela, sx + slot - 10, sy + 10, max(4, slot // 10), self._frame)
            from entities.objetos.item import Arma
            if isinstance(item, Arma) and not item.pode_equipar(player):
                pontos = [(sx + 8, sy + 4), (sx + 13, sy + 9), (sx + 8, sy + 14), (sx + 3, sy + 9)]
                pygame.draw.polygon(self.tela, Vermelho_ritual, pontos)
            if hasattr(item, "id") and item.id in player.itens_novos:
                pontos = [(sx + slot - 10, sy + 7), (sx + slot - 5, sy + 12), (sx + slot - 10, sy + 17), (sx + slot - 15, sy + 12)]
                pygame.draw.polygon(self.tela, Roxo_espectral, pontos)
        self.tela.set_clip(antigo)
        if not itens:
            msg = self.fonte_normal.render("Nenhum item", True, self.cor_texto_secundario)
            self.tela.blit(msg, msg.get_rect(center=(layout["col1_x"] + 10 + layout["col_grid_w"] // 2, layout["topo"] + 40)))


    def _desenhar_detalhes(self, player, x, y, largura):
        itens = self._itens_da_aba(player)
        rodape_h = self.fonte_pequena.get_height() * 2 + 8
        y_limite = self.painel_y + self.painel_h - 44 - self._pad_conteudo()
        y_cursor = y

        if itens and self.slot_selecionado is not None and self.slot_selecionado < len(itens):
            item = itens[self.slot_selecionado]
            for linha in self._quebrar_texto(getattr(item, "nome", ""), self.fonte_titulo, largura)[:2]:
                if y_cursor + self.fonte_titulo.get_height() > y_limite - rodape_h:
                    break
                self.tela.blit(self.fonte_titulo.render(linha, True, Azul_claro), (x, y_cursor))
                y_cursor += self.fonte_titulo.get_height() + 2
            y_cursor += 2

            fonte_desc = self.fonte_pequena
            for linha in self._quebrar_texto(getattr(item, "descricao", ""), fonte_desc, largura):
                if y_cursor + fonte_desc.get_height() > y_limite - rodape_h - 90:
                    break
                self.tela.blit(fonte_desc.render(linha, True, self.cor_texto_secundario), (x, y_cursor))
                y_cursor += fonte_desc.get_height() + 2

            y_cursor += 4
            stats = []
            if hasattr(item, "dano"):
                esc = " / ".join(f"{a.capitalize()} {g}" for a, g in getattr(item, "escalonamento", {}).items())
                stats.append(("Dano", str(item.dano)))
                if esc: stats.append(("Esc.", esc))
                req = getattr(item, "requisitos", {})
                if req:
                    stats.append(("Req. For", str(req.get("forca", 0))))
                    stats.append(("Req. Des", str(req.get("destreza", 0))))
            elif hasattr(item, "cargas_max") and item.cargas_max is not None:
                stats.append(("Cargas", f"{item.cargas} / {item.cargas_max}"))
            elif hasattr(item, "quantidade") and item.quantidade is not None:
                stats.append(("Qtd", str(item.quantidade)))

            for label, valor in stats:
                if y_cursor + self.fonte_pequena.get_height() > y_limite - rodape_h - 40:
                    break
                lbl = self.fonte_pequena.render(label, True, self.cor_texto_secundario)
                val = self.fonte_pequena.render(str(valor), True, Branco_texto)
                if lbl.get_width() + val.get_width() + 8 > largura:
                    val = self.fonte_pequena.render(str(valor)[:18], True, Branco_texto)
                self.tela.blit(lbl, (x, y_cursor))
                self.tela.blit(val, (x + largura - val.get_width(), y_cursor))
                y_cursor += self.fonte_pequena.get_height() + 2
        else:
            msg = self.fonte_normal.render("Selecione um item", True, self.cor_texto_secundario)
            self.tela.blit(msg, (x, y + 20))

        # status do player - compacto no rodape do detalhe
        status_y = max(y_cursor + 8, y_limite - rodape_h - self.fonte_pequena.get_height() * 6)
        status_y = min(status_y, y_limite - rodape_h - self.fonte_pequena.get_height() * 4)
        pygame.draw.line(self.tela, escurecer(Azul_espectral, 0.6), (x, status_y), (x + largura, status_y))
        status_y += 6
        self.tela.blit(self.fonte_normal.render("Status", True, Roxo_espectral), (x, status_y))
        status_y += self.fonte_normal.get_height() + 2
        stats_player = [("Nivel", str(player.nivel)), ("Vig", str(player.vigor)), ("Res", str(player.resistencia)), ("For", str(player.forca)), ("Des", str(player.destreza))]
        for label, valor in stats_player:
            if status_y + self.fonte_pequena.get_height() > y_limite:
                break
            lbl = self.fonte_pequena.render(label, True, self.cor_texto_secundario)
            val = self.fonte_pequena.render(valor, True, Branco_texto)
            self.tela.blit(lbl, (x, status_y))
            self.tela.blit(val, (x + largura - val.get_width(), status_y))
            status_y += self.fonte_pequena.get_height() + 1

    def _quebrar_texto(self, texto, fonte, largura_max):
        palavras = str(texto).split(" ")
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte.size(teste)[0] <= largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual.strip())
                # palavra maior que largura: quebra por caractere
                if fonte.size(palavra)[0] > largura_max:
                    pedaco = ""
                    for ch in palavra:
                        if fonte.size(pedaco + ch)[0] <= largura_max:
                            pedaco += ch
                        else:
                            if pedaco: linhas.append(pedaco)
                            pedaco = ch
                    linha_atual = pedaco + " "
                else:
                    linha_atual = palavra + " "
        if linha_atual:
            linhas.append(linha_atual.strip())
        return linhas
