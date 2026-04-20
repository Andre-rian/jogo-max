import pygame
import sys
from settings import Screen_widht, Screen_height, Preto, Dourado, Branco, Vermelho_sangue

class MenuInicial:

    def __init__(self, tela, save_manager):
        
        self.tela = tela
        self.save_manager = save_manager

        self.fonte_titulo = pygame.font.SysFont("Georgia", 64, bold=True)
        self.fonte_slot = pygame.font.SysFont("Georgia", 28, bold=True)
        self.fonte_info = pygame.font.SysFont("Georgia", 18)

        self.slot_selecionado = 1 #1, 2 ou 3
        self.confirmando_delete = False
        self.estado = "selecionar" # selecione / confirme o delet

        #callback - serve para avisa o main que o player escolheu um slot 
        self.callback_iniciar = None #recebe o slot la do db


    def atualizar(self, eventos):
        slots = self.save_manager.listar_slots()
        pos_mouse = pygame.mouse.get_pos()

        #houver com os mouses nos slots
        for i in  range(1, 4):
            slot_y = 240 + (i - 1) * 140
            rect_slot = pygame.Rect(Screen_widht // 2 - 250, slot_y, 500, 110)
            if rect_slot.collidepoint(pos_mouse):
                self.slot_selecionado = i





        for evento in eventos:
            if evento.type != pygame.KEYDOWN and evento.type != pygame.MOUSEBUTTONDOWN:
                continue

            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                dados = slots[self.slot_selecionado]
                if self.callback_iniciar:
                    self.callback_iniciar(self.slot_selecionado, dados)
                    return
                
                
            if evento.type == pygame.KEYDOWN:
                if self.estado == "selecionar":
                    if evento.key == pygame.K_UP:
                        self.slot_selecionado = max(1, self.slot_selecionado - 1)


                    elif evento.key == pygame.K_DOWN:
                        self.slot_selecionado = min(3, self.slot_selecionado + 1)


                    elif evento.key == pygame.K_RETURN:
                        dados = slots[self.slot_selecionado]
                        if self.callback_iniciar:
                            self.callback_iniciar(self.slot_selecionado, dados)


                    elif evento.key == pygame.K_DELETE:
                        #so deixa deleta se existir o save
                        if slots[self.slot_selecionado] is not None:
                            self.estado = "confirmar_delete"


                elif self.estado == "confirmar_delete":
                    if evento.key == pygame.K_RETURN:
                        self.save_manager.deletar(self.slot_selecionado)
                        self.estado = "selecionar"

                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "selecionar"

    def desenhar(self):

        self.tela.fill(Preto)
        slots = self.save_manager.listar_slots()


        #titulo
        titulo = self.fonte_titulo.render("KNIGHT TALES", True, Dourado)
        self.tela.blit(titulo, (Screen_widht // 2 - titulo.get_width() // 2, 80))


        #slots
        for i in range(1, 4):
            dados = slots[i]
            selecionado = i == self.slot_selecionado

            #posiçao do slot na tela
            slot_y = 240 + (i - 1) * 140

            #fundo do slot
            cor_fundo = (40, 30, 20) if selecionado else (20, 15, 10)
            cor_borda = Dourado if selecionado else (80, 60, 30)
            
            pygame.draw.rect(self.tela, cor_fundo,
                             (Screen_widht // 2 - 250, slot_y, 500, 110),
                             border_radius=8)
            
            pygame.draw.rect(self.tela, cor_borda,
                             (Screen_widht // 2 - 250, slot_y, 500, 110),
                             2, border_radius=8)
            

            #seta para mostra qual slot o jogador esta selecionando
            if selecionado:
                seta = self.fonte_slot.render("▶", True, Dourado)
                self.tela.blit(seta, (Screen_widht // 2 - 270, slot_y + 38))

            #conteudo do slot
            if dados is None:
                #slot vazio
                txt = self.fonte_slot.render(f"Slot {i} - Novo Jogo", True, (140, 120, 80))
                self.tela.blit(txt, (Screen_widht // 2 - 220, slot_y + 20))
                sub = self.fonte_info.render("Nenhum save encontrado", True, (80, 70, 50))
                self.tela.blit(sub, (Screen_widht // 2 - 220, slot_y + 60))

            else:
                #slot com save
                txt = self.fonte_slot.render(f"Slot {i} - Continuar", True, Branco)
                self.tela.blit(txt, (Screen_widht // 2 - 220, slot_y + 15))

                sala = self.fonte_info.render(
                    f"Sala: {dados['checkpoint_sala']}", True, (180, 160, 120))

                self.tela.blit(sala, (Screen_widht // 2 - 220, slot_y + 52))

                data = self.fonte_info.render(
                    f"Salvo em: {dados['data_hora']}", True, (120, 110, 80))
                self.tela.blit(data, (Screen_widht // 2 - 220, slot_y + 76))

                #DEL para deletar o save
                del_txt = self.fonte_info.render("clique DEL para apagar o save", True, (180, 60, 60))
                self.tela.blit(del_txt, (Screen_widht // 2 + 120, slot_y + 76))


        #confirmaçao de deletar o save
        if self.estado == "confirmar_delete":
            overlay = pygame.Surface((Screen_widht, Screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.tela.blit(overlay, (0, 0))

            msg1 = self.fonte_slot.render("Apagar este save?", True, Vermelho_sangue)
            msg2 = self.fonte_info.render("ENTER para confirmar ESC para cancelar", True, Branco)
            self.tela.blit(msg1, (Screen_widht // 2 - msg1.get_width() // 2, Screen_height // 2 - 40))
            self.tela.blit(msg2, (Screen_widht // 2 - msg2.get_width() // 2, Screen_height // 2 + 20))

        #instruçao de teclas na base
        inst = self.fonte_info.render("↑↓ para navegar  ENTER para selecionar", True, (80, 70, 50))
        self.tela.blit(inst, (Screen_widht // 2 - inst.get_width() // 2, Screen_height -40))