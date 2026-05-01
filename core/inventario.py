import pygame
from settings import Screen_widht, Screen_height, Dourado, Branco, Preto
from entities.objetos.item import get_item


class Inventario:

    def __init__(self, tela):
        self.tela = tela
        self.aberto = False

        pygame.font.init()
        self.fonte_titulo = pygame.font.SysFont("Georgia", 20, bold=True)
        self.fonte_normal = pygame.font.SysFont("Georgia", 15)
        self.fonte_pequena = pygame.font.SysFont("Georgia", 13)


        #abas de navegaçao
        self.abas = ["Equipamentos", "Itens", "Chaves"]
        self.aba_atual = 0

        #grid de itens
        self.slot_selecionado = 0
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
        self.slot_selecionado = 0


    def fechar(self):
        self.aberto = False


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

            return itens
        
        elif self.aba_atual == 1: #itens
            itens = [get_item(id_) for id_ in player.inventario["itens"]]
            if player.pocao:
                itens.insert(0, player.pocao)
            return itens


        elif self.aba_atual == 2: #chaves
            return [get_item(id_) for id_ in player.inventario["chaves"]]

        return []


    #atualizar
    def atualizar(self, eventos, player):
        if not self.aberto:
            return
        
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
        for i in range(len(itens)):
            col = i % self.slots_por_linha

            lin = i // self.slots_por_linha

            sx = col1_x + 10 + col * (slot_size + gap)
            sy = py + 10 + lin * (slot_size + gap)
            rect_slot = pygame.Rect(sx, sy, slot_size, slot_size)
            if rect_slot.collidepoint(pos_mouse):
                self.slot_selecionado = i

        


        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    self.fechar()
                    return


                elif evento.key == pygame.K_TAB:
                    self.aba_atual = (self.aba_atual + 1) % len(self.abas)
                    self.slot_selecionado = 0
                
                elif evento.key == pygame.K_RIGHT:
                    itens = self._itens_da_aba(player)
                    if itens:
                        self.slot_selecionado = min(len(itens) - 1,
                                                    self.slot_selecionado + 1)
                        
                elif evento.key == pygame.K_LEFT:
                    self.slot_selecionado = max(0, self.slot_selecionado - 1)


                elif evento.key == pygame.K_DOWN:
                    itens = self._itens_da_aba(player)
                    novo = self.slot_selecionado + self.slots_por_linha
                    if novo < len(itens):
                        self.slot_selecionado = novo

                elif evento.key == pygame.K_UP:
                    novo = self.slot_selecionado - self.slots_por_linha
                    if novo >= 0:
                        self.slot_selecionado = novo

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


            selecionado = i == self.slot_selecionado
            cor_borda = Dourado if selecionado else (80, 60, 35)
            cor_fundo = (50, 40, 25) if selecionado else (30, 24, 15)


            pygame.draw.rect(self.tela, cor_fundo,
                             (sx, sy, slot_size, slot_size), border_radius=4)
            
            pygame.draw.rect(self.tela, cor_borda,
                             (sx, sy, slot_size, slot_size), 2, border_radius=4)
            
            #icone simples por enquanto, baseado no tipo do item
            cx = sx + slot_size // 2
            cy = sy + slot_size // 2

            if hasattr(item, "dano"): #arma
                pygame.draw.line(self.tela, (200, 180, 100),
                                 (cx - 14, cy + 14), (cx + 14, cy - 14), 3)
                
                pygame.draw.line(self.tela, (160, 140, 80),
                                 (cx - 8, cy - 14), (cx + 8, cy - 14), 2)
                
            elif hasattr(item, "cargas"): #poçoes/ consumiveis
                pygame.draw.ellipse(self.tela, (220, 160, 30),
                                    (cx - 10, cy - 5, 20, 18))
                
                pygame.draw.rect(self.tela, (180, 140, 60),
                                 (cx - 4 , cy - 14, 8, 10), border_radius=2)
                
                #cargas
                cargas_txt = self.fonte_pequena.render(
                    str(item.cargas), True, Branco)
                self.tela.blit(cargas_txt,
                               (sx + slot_size - 16, sy + slot_size - 18))
                
            
            else:
                #chave/ outras coisas
                pygame.draw.circle(self.tela, Dourado, (cx, cy), 12, 2)
                pygame.draw.line(self.tela, Dourado,
                                 (cx, cy - 8), (cx, cy + 8), 2)
                


        if not itens:
            msg = self.fonte_normal.render("Nenhum item", True, (80, 65, 40))
            self.tela.blit(msg, (x + largura // 2 - msg.get_width() // 2, 
                                 y + 80))
            
    

    #desenhar a DESCRRIÇAO e o status do player
    def _desenhar_detalhes(self, player, x, y, largura):
        itens = self._itens_da_aba(player)

        #detalhes dos itens selecionados
        if itens and self.slot_selecionado < len(itens):
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
                stats = [
                    ("Dano",          str(item.dano)),
                    ("Escalonamento", item.escalonamento.capitalize()),
                    ("Req. Força",    str(item.requisitos["força"])),
                    ("Req. Destreza", str(item.requisitos["destreza"])),
                ]

                for label, valor in stats:
                    lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
                    val = self.fonte_pequena.render(valor, True, Branco)
                    self.tela.blit(lbl, (x, linha_y))
                    self.tela.blit(val, (x + largura - val.get_width() - 10,
                                         linha_y))
                    linha_y += 18

            elif hasattr(item, "cargas"):
                
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
            ("HP",      f"{player.hp} / {player.hp_max}"),
            ("Stamina", f"{int(player.stamina)} / {player.stamina_max}"),
            ("Nível",   "1"),        # futuro
            ("Força",   "10"),       # futuro
            ("Destreza","10"),       # futuro
        ]
        for label, valor in stats_player:
            lbl = self.fonte_pequena.render(label, True, (120, 100, 60))
            val = self.fonte_pequena.render(valor, True, Branco)
            self.tela.blit(lbl, (x, status_y))
            self.tela.blit(val, (x + largura - val.get_width() - 10, status_y))
            status_y += 18
