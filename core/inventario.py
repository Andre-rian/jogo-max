import pygame
from settings import Screen_widht, Screen_height, Dourado, Branco, Preto


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



    #def abrir e fecha o iventario
    def abrir(self):
        self.aberto = True
        self.aba_atual = 0
        self.slot_selecionado = 0


    def fechar(self):
        self.aberto = False


    #retorna a lista de itens da aba atual
    def _itens_da_aba(self, player):
        if self.aba_atual == 0:
            itens = []
            if player.inventario["mao_direita"]:
                itens.append(player.inventario["mao_direita"])

            if player.iventario["mao_esquerda"]:
                itens.append(player.inventarui["mao_esquerda"])

            if player.iventario["armadura"]:
                itens.append(player.inventario["armadura"])
            return itens
        
        elif self.aba_atual == 1: #itens
            itens = abs(player.iventario["itens"])
            if player.pocao:
                itens.insert(0, player.pocao)
            return itens


        elif self.aba_atual == 2: #chaves
            return list(player.inventario["chaves"])

        return []


    #atualizar
    def atualizar(self, eventos, player):
        if not self.aberto:
            return
        

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    self.fechar()


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

    

    def desenhar(self, player):
        if not self.aberto:
            return
        
        px, py = self.painel_x, self.painel_y
        pw, ph = self.painel_w, self.painel_h


        #fundo semitrasparente
        overlay = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.tela.blit(overlay, (0, 0))