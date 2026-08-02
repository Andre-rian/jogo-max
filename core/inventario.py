import pygame
import logging
log = logging.getLogger("inventario")

from settings import Screen_widht, Screen_height, Dourado, Branco, Preto
from entities.objetos.item import get_item
from core.menu_navegavel import hover_index 


class Inventario:

    def __init__(self, tela):
        self.tela = tela
        self.aberto = False

        pygame.font.init()
        self.fonte_titulo = pygame.font.SysFont("Georgia", 20, bold=True)
        self.fonte_normal = pygame.font.SysFont("Georgia", 15)
        self.fonte_pequena = pygame.font.SysFont("Georgia", 13)


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
                #so mudar a aba no houve/ clique para confirma a mudança'
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
        
        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h


        #fundo semitrasparente
        overlay = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.tela.blit(overlay, (0, 0))


        #painel principal
        pygame.draw.rect(self.tela, (20, 15, 10),
                         (px, py, pw, ph), border_radius=6)
        
        pygame.draw.rect(self.tela, (100, 80, 50),
                         (px, py, pw, ph), 2, border_radius=6)
        

        #abas
        aba_w = pw // len(self.abas)
        for i, aba in enumerate(self.abas):
            aba_x = px + i * aba_w
            aba_y = py - 36
            selecionada = i == self.aba_atual
            cor_fundo = (50, 40, 25) if selecionada else (25, 20, 12)
            cor_borda = Dourado if selecionada else (80, 60, 35)

            pygame.draw.rect(self.tela, cor_fundo,
                             (aba_x, aba_y, aba_w - 2, 36), border_radius=4)
            
            pygame.draw.rect(self.tela, cor_borda, 
                             (aba_x, aba_y, aba_w - 1, 36), 1, border_radius=4)
            
            txt = self.fonte_normal.render(aba, True,
                                           Dourado if selecionada else (160, 130, 80))
            self.tela.blit(txt, (aba_x + aba_w // 2 - txt.get_width() // 2,
                                 aba_y + 10))
            
        #divisorias internas
        #colunas esquerda - slots equipados / centro - grid / direita - descriçao
        col1_x = px + 180
        col2_x = px + 480
        pygame.draw.line(self.tela, (80, 60, 35), 
                         (col1_x, py + 10), (col1_x, py + ph - 10))
        
        #coluna esquerda
        self._desenhar_slots_equipados(player, px + 10, py + 10, 160)
        #coluna central
        self._desenhar_grid(player, col1_x + 10, py + 10, 
                            col2_x - col1_x - 20)
        
        #coluna direita
        self._desenhar_detalhes(player, col2_x + 10, py + 10,
                                pw - (col2_x - px) - 20)
        
        #instruçoes na base 
        inst = self.fonte_pequena.render(
            "← → ↑ ↓  navegar    TAB  trocar aba    ESC  fechar MOUSE hover/clique",
            True, (100, 80, 50))
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


        #fundo do menu
        pygame.draw.rect(self.tela, (25, 20, 12),
                         (mx, my, menu_w, menu_h), border_radius=4)
        

        pygame.draw.rect(self.tela, Dourado,
                         (mx, my, menu_w, menu_h), 1, border_radius=4)

        pos_mouse = pygame.mouse.get_pos()

        for i, opcao in enumerate(opcoes):
            oy = my + 4 + i * opcao_h
            rect_opcao = pygame.Rect(mx, oy, menu_w, opcao_h)

            #hover

            if i == self.opcao_contexto_selecionada:
                pygame.draw.rect(self.tela, (50, 40, 25), rect_opcao, border_radius=3)

            txt = self.fonte_normal.render(opcao, True, Branco)
            self.tela.blit(txt, (mx + 10, oy + 6))   
    
    
    
    
    
    
    
    
    
    
    
    
    #slots equipados
    def _desenhar_slots_equipados(self, player, x, y, largura):
        titulo = self.fonte_normal.render("Equipado", True, Dourado)
        self.tela.blit(titulo, (x, y))

       

        slots = [
            ("Mão Dir", "mao_direita"),
            ("Mão Esq", "mao_esquerda"),
            ("Armadura", "armadura"),
        ]



        for i, (label, chave) in enumerate(slots):
            sy = y + 30 + i * 70


            item_id = player.inventario.get(chave)

            item = get_item(item_id) if item_id is not None else None

            
            #fundo do slot
            pygame.draw.rect(self.tela, (35, 28, 18),
                             (x, sy, largura, 58), border_radius=4)
            pygame.draw.rect(self.tela, (80, 60, 35),
                             (x, sy, largura, 58), 1, border_radius=4)
            
            #label
            lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
            self.tela.blit(lbl, (x + 6, sy + 4))


            #item ou vazio
            if item:

                nome = self.fonte_normal.render(item.nome, True, Branco)
                self.tela.blit(nome, (x + 6, sy + 22))
                
                if hasattr(item, "dano"):
                    dano = self.fonte_pequena.render(f"Dano: {item.dano}",
                                                     True, (180, 160, 100))
                    self.tela.blit(dano, (x + 6, sy + 40))

            else:
                vazio = self.fonte_pequena.render("- Vazio -", True, Branco)
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
            cor_borda = Dourado if selecionado else (80, 60, 35)
            cor_fundo = (50, 40, 25) if selecionado else (30, 24, 15)

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

            self._desenhar_icone(item, cx, cy, sx, sy, slot_size)\

            if esta_equipado:
                pygame.draw.circle(self.tela, Dourado,
                                   (sx + slot_size - 8, sy + 8), 5)
                pygame.draw.circle(self.tela, (20, 15, 10),
                                   (sx + slot_size - 8, sy + 8), 3)

            #aviso de requisitos de status nao cumprido
            from entities.objetos.item import Arma
            if isinstance(item, Arma) and not item.pode_equipar(player):
                txt = self.fonte_pequena.render("❗", True, (255, 60, 60))
                self.tela.blit(txt, (sx + 4, sy + 4))

            if hasattr(item, "id") and item.id in player.itens_novos:
                txt = self.fonte_pequena.render("!", True, (255, 80, 80))
                self.tela.blit(txt, (sx + slot_size - 10, sy + 4))


        if not itens:
            msg = self.fonte_normal.render("Nenhum item", True, (80, 65, 40))
            self.tela.blit(msg, (x + largura // 2 - msg.get_width() // 2, 
                                 y + 80))
            
    

    def _desenhar_icone(self, item, cx, cy, sx, sy, slot_size):
        if item.icone == "espada":
            # lamina longa apontando para baixo
            pygame.draw.polygon(self.tela, (200, 190, 150), [
                (cx,      cy + 22),  # ponta
                (cx - 3,  cy - 4),   # base esquerda
                (cx + 3,  cy - 4),   # base direita
            ])
            # detalhe central da lamina
            pygame.draw.line(self.tela, (160, 150, 110),
                             (cx, cy + 22), (cx, cy - 4), 1)
            # guarda longa
            pygame.draw.line(self.tela, (180, 150, 60),
                             (cx - 12, cy - 5), (cx + 12, cy - 5), 3)
            # ponta da guarda esquerda
            pygame.draw.circle(self.tela, (160, 130, 50),
                               (cx - 12, cy - 5), 2)
            # ponta da guarda direita
            pygame.draw.circle(self.tela, (160, 130, 50),
                               (cx + 12, cy - 5), 2)
            # cabo
            pygame.draw.line(self.tela, (120, 80, 40),
                             (cx, cy - 5), (cx, cy - 16), 4)
            # punho redondo
            pygame.draw.circle(self.tela, (150, 110, 60),
                               (cx, cy - 18), 4)
            pygame.draw.circle(self.tela, (180, 140, 80),
                               (cx, cy - 18), 4, 1)
            
        elif item.icone == "machado":
            # cabo
            pygame.draw.line(self.tela, (160, 120, 60),
                             (cx + 8, cy + 14), (cx - 6, cy - 10), 3)
            # lamina
            pygame.draw.polygon(self.tela, (200, 180, 100), [
                (cx - 6, cy - 10),
                (cx - 16, cy - 4),
                (cx - 8, cy + 6),
            ])

        elif item.icone == "pocao":
            pygame.draw.ellipse(self.tela, (160, 10, 20),
                                (cx - 10, cy - 5, 20, 18))
            pygame.draw.rect(self.tela, (190, 180, 190),
                             (cx - 4, cy - 14, 8, 10), border_radius=2)
            cargas_txt = self.fonte_pequena.render(
                str(item.cargas if item.cargas is not None else item.quantidade),
                True, Branco)
            self.tela.blit(cargas_txt, (sx + slot_size - 16, sy + slot_size - 18))

        elif item.icone == "raiz":
            # haste
            pygame.draw.line(self.tela, (100, 160, 80),
                             (cx, cy + 12), (cx, cy - 4), 2)
            # folhas
            pygame.draw.ellipse(self.tela, (80, 180, 60),
                                (cx - 10, cy - 12, 12, 8))
            pygame.draw.ellipse(self.tela, (80, 180, 60),
                                (cx - 2, cy - 16, 12, 8))
            cargas_txt = self.fonte_pequena.render(
                str(item.quantidade), True, Branco)
            self.tela.blit(cargas_txt, (sx + slot_size - 16, sy + slot_size - 18))

        else:  # generico
            pygame.draw.circle(self.tela, Dourado, (cx, cy), 12, 2)
            pygame.draw.line(self.tela, Dourado,
                             (cx, cy - 8), (cx, cy + 8), 2)



    #desenhar a DESCRRIÇAO e o status do player
    def _desenhar_detalhes(self, player, x, y, largura):
        itens = self._itens_da_aba(player)

        #detalhes dos itens selecionados
        if itens and self.slot_selecionado is not None and self.slot_selecionado< len(itens):
            item = itens[self.slot_selecionado]

            nome = self.fonte_titulo.render(item.nome, True, Dourado)
            self.tela.blit(nome, (x, y))

            #descriçao com a quebra de linha
            palavras = item.descricao.split(" ")
            linhas_txt = ""
            linha_y = y + 30
            
            for palavra in palavras:
                teste = linhas_txt + palavra + " "
                surf = self.fonte_pequena.render(teste, True, Branco)
                if surf.get_width() > largura - 10:
                    rendered = self.fonte_pequena.render(linhas_txt,
                                                         True, (180, 160, 120))
                    self.tela.blit(rendered, (x, linha_y))
                    linha_y += 18
                    linhas_txt = palavra + " "
                else:
                    linhas_txt = teste
            if linhas_txt:
                rendered = self.fonte_pequena.render(linhas_txt,
                                                     True, (180, 160, 120))
                self.tela.blit(rendered, (x, linha_y))
                linha_y += 18
                linhas_txt = palavra + " "



            #stats do item
            linha_y += 8
            pygame.draw.line(self.tela, (80, 60, 35),
                             (x, linha_y), (x + largura - 10, linha_y))
            linha_y += 8 

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
                    lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
                    val = self.fonte_pequena.render(valor, True, Branco)
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10,
                                         linha_y))
                    linha_y += 18

            elif hasattr(item, "cargas_max") and item.cargas_max is not None:
                
                stats = [
                    ("Cargas",  f"{item.cargas} / {item.cargas_max}"),
                ]
                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
                    val = self.fonte_pequena.render(valor, True, Branco)
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10,
                                         linha_y))
                    linha_y += 18
            
            elif hasattr(item, "quantidade") and item.quantidade is not None:
                stats = [
                    ("Quantidade", str(item.quantidade)),

                ]
                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
                    val = self.fonte_pequena.render(valor, True, Branco)
                    
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10, linha_y))
                    linha_y += 18

        #stats do player
        #linha separadora
        status_y = y + 260
        pygame.draw.line(self.tela, (80, 60, 35),
                         (x, status_y), (x + largura - 10, status_y))
        status_y += 10

        titulo_status = self.fonte_normal.render("Status", True, Dourado)
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
            lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
            val = self.fonte_pequena.render(valor, True, Branco)
            self.tela.blit(lbl, (x, status_y))
            self.tela.blit(val, (x + largura - val.get_width() - 10, status_y))
            status_y += 18
