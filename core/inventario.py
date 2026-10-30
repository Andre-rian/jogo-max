import pygame
import logging
log = logging.getLogger("inventario")

from settings import Screen_widht, Screen_height
from entities.objetos.item import get_item
from core.navegacao import hover_index 
from ui.icones import desenhar_icone_item
from ui.estilo import (
    Fonte_titulo, Fonte_texto,
    Roxo_espectral, Roxo_profundo, Azul_espectral, Azul_claro,
    Branco_texto, Cinza_texto, Cinza_texto_escuro, Vermelho_ritual,
    Cinza_carvao, Cinza_azulado,
    desenhar_overlay, desenhar_painel, desenhar_botao,
    desenhar_eco_profano, desenhar_linha_ornamental,
    adicionar_brilho, escurecer, misturar
)


class Inventario:

    def __init__(self, tela):
        self.tela = tela
        self.aberto = False

        pygame.font.init()
        self.fonte_titulo = Fonte_titulo(21, negrito=True)
        self.fonte_normal = Fonte_texto(16)
        self.fonte_pequena = Fonte_texto(14)

        self._frame = 0

        #abas de navegaçao
        self.abas = ["Equipamentos", "Itens", "Chaves", "materias"]
        self.aba_atual = 0


        #menu ações
        self.menu_contexto = None # NOne - fechado, senao iria guarda o item e a posição 
        self.callback_descartar = None 
        self.opcao_contexto_selecionada = 0

        #grid de itens
        self.slot_selecionado = None
        self._ignorar_frame_abertura = False
        self.slots_por_linha = 4


        #dimensao do painel
        self.painel_x = Screen_widht // 2 - 420
        self.painel_y = Screen_height // 2 - 260
        self.painel_w = 840
        self.painel_h = 520



    #def abrir e fecha o inventario
    def abrir(self):
        self.aberto = True
        self.aba_atual = 0
        self.slot_selecionado = None
        self._ignorar_frame_abertura = True #trava até o proximo atualizar
        self.menu_contexto = None
        self.opcao_contexto_selecionada = 0


    def fechar(self):
        self.aberto = False
        self.menu_contexto = None
        self.opcao_contexto_selecionada = 0


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


        elif self.aba_atual == 2: #chaves
            return [get_item(id_) for id_ in player.inventario["chaves"]]

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

        
        if self._ignorar_frame_abertura:
            self._ignorar_frame_abertura = False
            return #ignora qualquer evento que sobra do abrir inventario

        escs_no_frame = [e for e in eventos if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE]
        if escs_no_frame:
            log.debug(f"[FRAME] {len(escs_no_frame)} evento(s) ESC neste frame")



        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h
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
        col1_x = px + 180
        itens = self._itens_da_aba(player)
        slot_size = 60
        gap = 8

        itens_com_rect = []
        
        for i in range(len(itens)):
            col = i % self.slots_por_linha

            lin = i // self.slots_por_linha

            sx = col1_x + 10 + col * (slot_size + gap)
            sy = py + 10 + lin * (slot_size + gap)
            itens_com_rect.append((i, pygame.Rect(sx, sy, slot_size, slot_size)))                    

        indice_houver = hover_index(eventos, pos_mouse, itens_com_rect)
        if indice_houver is not None:
            self.slot_selecionado = indice_houver
            item = itens[indice_houver]
            if hasattr(item, "id"):
                player.itens_novos.discard(item.id)

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    log.debug(f"[esc] menu_contexto={'ABERTO' if self.menu_contexto else 'FECHADO'}")

                    if self.menu_contexto: #verificar se o menu de contexto esta aberto
                        self.menu_contexto = None
                        return
                    self.fechar()
                    log.debug("[esc] -> fechando o inventario inteiro")
                    return

                if self.menu_contexto:
                    opcoes = self.menu_contexto["opcoes"]
                    if evento.key == pygame.K_UP:
                        self.opcao_contexto_selecionada = (self.opcao_contexto_selecionada - 1) % len(opcoes)
                    elif evento.key == pygame.K_DOWN:
                        self.opcao_contexto_selecionada = (self.opcao_contexto_selecionada + 1) % len(opcoes)
                    elif evento.key == pygame.K_RETURN:
                        opcao = opcoes[self.opcao_contexto_selecionada]
                        self._executar_opcao(opcao, self.menu_contexto["item"], player)
                        self.menu_contexto = None
                    return   # não deixa cair nas teclas de navegação do grid abaixo


                elif evento.key == pygame.K_TAB:
                    self.aba_atual = (self.aba_atual + 1) % len(self.abas)
                    self.slot_selecionado = 0
                
                elif evento.key == pygame.K_RIGHT:
                    itens = self._itens_da_aba(player)
                    if itens:
                        atual = self.slot_selecionado if self.slot_selecionado is not None else -1
                        self.slot_selecionado = min(len(itens) - 1, atual+ 1)
                        
                elif evento.key == pygame.K_LEFT:
                    atual = self.slot_selecionado if self.slot_selecionado is not None else  1
                    self.slot_selecionado = max(0, atual - 1)


                elif evento.key == pygame.K_DOWN:
                    itens = self._itens_da_aba(player)
                    atual = self.slot_selecionado if self.slot_selecionado is not None else -self.slots_por_linha
                    novo = atual + self.slots_por_linha
                    if novo < len(itens):
                        self.slot_selecionado = novo

                elif evento.key == pygame.K_UP:
                    if self.slot_selecionado is not None:
                        novo = self.slot_selecionado - self.slots_por_linha
                        if novo >= 0:
                            self.slot_selecionado = novo

                elif evento.key == pygame.K_RETURN:          
                        itens = self._itens_da_aba(player)
                        if self.slot_selecionado is not None and self.slot_selecionado < len(itens):
                            item = itens[self.slot_selecionado]
                            col = self.slot_selecionado % self.slots_por_linha
                            lin = self.slot_selecionado // self.slots_por_linha
                            col1_x = px + 180
                            slot_size = 60
                            gap = 8
                            sx = col1_x + 10 + col * (slot_size + gap)
                            sy = py + 10 + lin * (slot_size + gap)
    
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
                                opcoes = ["Usar", "Descartar"]
    
                            else:
                                opcoes = ["Descartar"]
    
                            self.menu_contexto = {
                                "item": item,
                                "x": sx + slot_size + 4,
                                "y": sy,
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
                        self.aba_atual = i
                        self.slot_selecionado = 0
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
                            self._executar_opcao(opcao, self.menu_contexto["item"], player)
                            self.menu_contexto = None
                            break

                    if not clicou_opcao:
                        self.menu_contexto = None #clicou fora do menu - fecha ele
                    return
                
                
            
                #clique nos slots do grids
                itens = self._itens_da_aba(player)
                col1_x = px + 180
                slot_size = 60
                gap = 8
                for i, item in enumerate(itens):
                    col = i % self.slots_por_linha
                    lin = i // self.slots_por_linha
                    sx = col1_x + 10 + col * (slot_size + gap)
                    sy = py + 10 + lin * (slot_size + gap)
                    rect_slot = pygame.Rect(sx, sy, slot_size, slot_size)
                    if rect_slot.collidepoint(pos_mouse):
                        self.slot_selecionado = i

                        #define as opçoes seguindo o tipo dos itens
                        from entities.objetos.item import Arma, Consumivel

                        if isinstance(item, Arma):
                            #checa se o item esta equipado 
                                slots_equipados = [
                                        player.inventario["mao_direita"],
                                        player.inventario["mao_esquerda"],
                                        player.inventario["armadura"]]
                                
                                if hasattr(item, "id") and item.id in [s for s in slots_equipados if s is not None]:    
                                
                                    opcoes = ["Desequipar"]
                                else:
                                    opcoes = ["Equipar", "Descartar"]

                        elif isinstance(item, Consumivel) or hasattr(item, "cargas"):
                            opcoes = ["Usar", "Descartar"]
                        
                        else:
                            opcoes = ["Descartar"]

                        self.menu_contexto = {
                            "item": item,
                            "x": sx + slot_size + 4, #fica aparecendo ao lado direito do slot
                            "y": sy,
                            "opcoes" : opcoes
                        }
                        self.opcao_contexto_selecionada = 0

                        break

                    #houver do menu dos itens
                    if self.menu_contexto:
                        mx = self.menu_contexto["x"]
                        my = self.menu_contexto["y"]
                        opcoes = self.menu_contexto["opcoes"]
                        opcao_h = 28
                        menu_w = 110
                        for i, opcao in enumerate(opcoes):
                            oy = my + 4 + i * opcao_h
                            rect_opcao = pygame.Rect(mx, oy, menu_w, opcao_h)
                            if rect_opcao.collidepoint(pos_mouse):
                                self.opcao_contexto_selecionada = i 


                    
    def _tentar_equipar(self, item, player):
        from entities.objetos.item import Arma
        if isinstance(item, Arma):
            
            #se tem algo equipado na mao, subistutuio e retorna ele para o inventario
            id_atual = player.inventario["mao_direita"]
            if id_atual is not None:
                player.inventario["equipamentos"].append(id_atual)
            
            
            #remove da lista de itens e coloca na mao direita
            if item.id in player.inventario["equipamentos"]:
                player.inventario["equipamentos"].remove(item.id)
            player.inventario["mao_direita"] = item.id
            player.itens_novos.discard(item.id)


    def _executar_opcao(self, opcao, item , player):
        from entities.objetos.item import Arma, Consumivel

        if opcao == "Equipar":
            self._tentar_equipar(item, player)

        
        elif opcao == "Usar":
            
            if isinstance(item, Consumivel):
                item.usar(player, player.inventario)

        elif opcao == "Descartar" and self.callback_descartar:
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
                
                if item.id in player.inventario["itens"]:
                    player.inventario["itens"].pop(item.id)

                if item.id in player.inventario["materiais"]:
                    player.inventario["materiais"].pop(item.id)


            self.callback_descartar(item.id)

        elif opcao == "Desequipar":
            if isinstance(item, Arma):
                if player.inventario["mao_direita"] == item.id:
                    player.inventario["mao_direita"] = None
                    player.inventario["equipamentos"].append(item.id)

    def desenhar(self, player):
        if not self.aberto:
            return
        
        self._frame += 1
        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h


        #fundo semitrasparente
        desenhar_overlay(self.tela, 150)


        #painel principal
        desenhar_painel(self.tela, pygame.Rect(px, py, pw, ph),
                        self._frame, cor_borda=Azul_espectral)


        #abas
        aba_w = pw // len(self.abas)
        for i, aba in enumerate(self.abas):
            aba_x = px + i * aba_w
            aba_y = py - 36
            selecionada = i == self.aba_atual
            rect_aba = pygame.Rect(aba_x, aba_y, aba_w - 2, 36)
            desenhar_botao(self.tela, rect_aba, aba, selecionada, self._frame,
                           fonte_btn=self.fonte_normal, marcador=False)

        #divisorias internas
        col1_x = px + 180
        col2_x = px + 480
        pygame.draw.line(self.tela, escurecer(Azul_espectral, 0.6),
                         (col1_x, py + 10), (col1_x, py + ph - 10))
        
        #coluna esquerda
        self._desenhar_slots_equipados(player, px + 10, py + 20, 160)
        #coluna central
        self._desenhar_grid(player, col1_x + 10, py + 10, 
                            col2_x - col1_x - 20)
        
        #coluna direita
        self._desenhar_detalhes(player, col2_x + 10, py + 10,
                                pw - (col2_x - px) - 20)
        
        #instruçoes na base 
        inst = self.fonte_pequena.render(
            "← → ↑ ↓  navegar    TAB  trocar aba    ESC  fechar",
            True, Cinza_texto_escuro)
        self.tela.blit(inst, (px + pw // 2 - inst.get_width() // 2,
                              py + ph - 20))
           
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
            ("Mão Dir", "mao_direita"),
            ("Mão Esq", "mao_esquerda"),
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
            lbl = self.fonte_pequena.render(label, True, Cinza_texto)
            self.tela.blit(lbl, (x + 6, sy + 4))


            #item ou vazio
            if item:

                nome = self.fonte_normal.render(item.nome, True, Branco_texto)
                self.tela.blit(nome, (x + 6, sy + 22))
                
                if hasattr(item, "dano"):
                    dano = self.fonte_pequena.render(f"Dano: {item.dano}",
                                                     True, Azul_claro)
                    self.tela.blit(dano, (x + 6, sy + 40))

            else:
                vazio = self.fonte_pequena.render("- Vazio -", True, Cinza_texto_escuro)
                self.tela.blit(vazio, (x + 6, sy + 28))

 
    #grid de itens
    def _desenhar_grid(self, player, x, y, largura):
        itens = self._itens_da_aba(player)
        slot_size = 60
        gap = 8


        for i, item in enumerate(itens):
            col = i % self.slots_por_linha
            lin = i // self.slots_por_linha
            sx = x + col * (slot_size + gap)
            sy = y + lin * (slot_size + gap)


            selecionado =  self.slot_selecionado is not None and i == self.slot_selecionado
            cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.5)
            cor_fundo = Cinza_azulado if selecionado else escurecer(Cinza_carvao, 0.15)

            if selecionado:
                adicionar_brilho(self.tela, sx + slot_size // 2, sy + slot_size // 2,
                                 slot_size // 2 + 6, Roxo_profundo, self._frame,
                                 intensidade=0.22)

            #checar se o item esta equipado
            slots_equipados = [
                player.inventario["mao_direita"],
                player.inventario["mao_esquerda"],
                player.inventario["armadura"]
            ]

            esta_equipado = hasattr(item, "id") and item.id in [s for s in slots_equipados if s is not None]


            pygame.draw.rect(self.tela, cor_fundo,
                             (sx, sy, slot_size, slot_size), border_radius=4)
            
            pygame.draw.rect(self.tela, cor_borda,
                             (sx, sy, slot_size, slot_size), 2, border_radius=4)
            
            #icone simples por enquanto, baseado no tipo do item
            cx = sx + slot_size // 2
            cy = sy + slot_size // 2

            desenhar_icone_item(self.tela, item, cx, cy, sx, sy, slot_size,
                                self.fonte_pequena)

            if esta_equipado:
                desenhar_eco_profano(self.tela, sx + slot_size - 10,
                                     sy + 10, 6, self._frame)

            #aviso de requisitos de status nao cumprido
            from entities.objetos.item import Arma
            if isinstance(item, Arma) and not item.pode_equipar(player):
                pontos = [(sx + 8, sy + 4), (sx + 13, sy + 9),
                          (sx + 8, sy + 14), (sx + 3, sy + 9)]
                pygame.draw.polygon(self.tela, Vermelho_ritual, pontos)

            if hasattr(item, "id") and item.id in player.itens_novos:
                pontos = [(sx + slot_size - 10, sy + 7), (sx + slot_size - 5, sy + 12),
                          (sx + slot_size - 10, sy + 17), (sx + slot_size - 15, sy + 12)]
                pygame.draw.polygon(self.tela, Roxo_espectral, pontos)


        if not itens:
            msg = self.fonte_normal.render("Nenhum item", True, Cinza_texto_escuro)
            self.tela.blit(msg, (x + largura // 2 - msg.get_width() // 2, 
                                 y + 80))
            
    

#desenhar a DESCRRIÇao e o status do player
    def _desenhar_detalhes(self, player, x, y, largura):
        itens = self._itens_da_aba(player)

        #detalhes dos itens selecionados
        if itens and self.slot_selecionado is not None and self.slot_selecionado< len(itens):
            item = itens[self.slot_selecionado]

            nome = self.fonte_titulo.render(item.nome, True, Azul_claro)
            self.tela.blit(nome, (x, y))

            #descriçao com a quebra de linha
            palavras = item.descricao.split(" ")
            linhas_txt = ""
            linha_y = y + 30
            
            for palavra in palavras:
                teste = linhas_txt + palavra + " "
                surf = self.fonte_pequena.render(teste, True, Branco_texto)
                if surf.get_width() > largura - 10:
                    rendered = self.fonte_pequena.render(linhas_txt,
                                                         True, Cinza_texto)
                    self.tela.blit(rendered, (x, linha_y))
                    linha_y += 18
                    linhas_txt = palavra + " "
                else:
                    linhas_txt = teste
            if linhas_txt:
                rendered = self.fonte_pequena.render(linhas_txt,
                                                     True, Cinza_texto)
                self.tela.blit(rendered, (x, linha_y))
                linha_y += 18
                linhas_txt = palavra + " "



            #stats do item
            linha_y += 8
            desenhar_linha_ornamental(self.tela, x + largura // 2, linha_y,
                                      largura // 2 - 10, Azul_espectral)
            linha_y += 12 

            if hasattr(item, "dano"):
                #mostra o string do escalonamento
                escalonamento_txt = " / ".join(
                    f"{atr.capitalize()} {grau}"
                    for atr, grau in item.escalonamento.items()
                )
                

                
                
                stats = [
                    ("Dano",          str(item.dano)),
                    ("Escalonamento", escalonamento_txt,),
                    ("Req. Força",    str(item.requisitos["forca"])),
                    ("Req. Destreza", str(item.requisitos["destreza"])),
                ]

                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, Cinza_texto)
                    val = self.fonte_pequena.render(valor, True, Branco_texto)
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10,
                                         linha_y))
                    linha_y += 18

            elif hasattr(item, "cargas_max") and item.cargas_max is not None:
                
                stats = [
                    ("Cargas",  f"{item.cargas} / {item.cargas_max}"),
                ]
                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, Cinza_texto)
                    val = self.fonte_pequena.render(valor, True, Branco_texto)
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10,
                                         linha_y))
                    linha_y += 18
            
            elif hasattr(item, "quantidade") and item.quantidade is not None:
                stats = [
                    ("Quantidade", str(item.quantidade)),

                ]
                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, Cinza_texto)
                    val = self.fonte_pequena.render(valor, True, Branco_texto)
                    
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10, linha_y))
                    linha_y += 18

        #stats do player
        #linha separadora
        status_y = y + 260
        desenhar_linha_ornamental(self.tela, x + largura // 2, status_y,
                                  largura // 2 - 10, Azul_espectral)
        status_y += 14

        titulo_status = self.fonte_normal.render("Status", True, Roxo_espectral)
        self.tela.blit(titulo_status, (x, status_y))
        status_y += 22

        #parte dos status que só vem no futuro
        stats_player = [
            ("Nível",   str(player.nivel)),
            ("Vigor",      str(player.vigor)),
            ("Resistencia", str(player.resistencia)),        
            ("Força",   str(player.forca)),       
            ("Destreza",str(player.destreza)),       
        ]
        for label, valor in stats_player:
            lbl = self.fonte_pequena.render(label, True, Cinza_texto)
            val = self.fonte_pequena.render(valor, True, Branco_texto)
            self.tela.blit(lbl, (x, status_y))
            self.tela.blit(val, (x + largura - val.get_width() - 10, status_y))
            status_y += 18