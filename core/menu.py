import pygame
import sys
from settings import Screen_widht, Screen_height
from core.navegacao import hover_index
from ui.estilo import (
    Fonte_titulo, Fonte_texto,
    Roxo_profundo, Roxo_espectral, Azul_espectral, Azul_claro,
    Branco_texto, Cinza_texto, Cinza_texto_escuro, Vermelho_ritual,
    desenhar_fundo, desenhar_overlay, desenhar_painel, desenhar_botao,
    desenhar_titulo, desenhar_linha_ornamental, desenhar_eco_profano,
    adicionar_brilho, escurecer
)

class MenuInicial:

    def __init__(self, tela, save_manager):
        
        self.tela = tela
        self.save_manager = save_manager

        self.fonte_titulo = Fonte_titulo(78, negrito=True)
        self.fonte_slot = Fonte_titulo(27, negrito=True)
        self.fonte_info = Fonte_texto(17)

        self._frame = 0

        self.slot_selecionado = 1 #1, 2 ou 3
        self.confirmando_delete = False
        self.estado = "selecionar" # selecione / confirme o delet

        #callback - serve para avisa o main que o player escolheu um slot 
        self.callback_iniciar = None #recebe o slot la do db


    def atualizar(self, eventos):
        slots = self.save_manager.listar_slots()
        pos_mouse = pygame.mouse.get_pos()


        itens_com_rect = []

        #houver com os mouses nos slots
        for i in  range(1, 4):
            slot_y = 240 + (i - 1) * 140
            rect_slot = pygame.Rect(Screen_widht // 2 - 250, slot_y, 500, 110)  
            itens_com_rect.append((i, rect_slot))

        indice_houver = hover_index(eventos, pos_mouse, itens_com_rect)
        if indice_houver is not None:
            self.slot_selecionado = indice_houver




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
        self._frame += 1
        slots = self.save_manager.listar_slots()

        desenhar_fundo(self.tela, self._frame)

        #titulo
        adicionar_brilho(self.tela, Screen_widht // 2, 84, 320, Roxo_profundo,
                         self._frame, intensidade=0.22)
        desenhar_titulo(self.tela, "PROFANE ECHO", self.fonte_titulo,
                        Roxo_espectral, Screen_widht // 2, 58, espacamento=6)

        sub = self.fonte_info.render("o eco profano desperta entre os escombros",
                                     True, Cinza_texto_escuro)
        self.tela.blit(sub, (Screen_widht // 2 - sub.get_width() // 2, 146))

        desenhar_linha_ornamental(self.tela, Screen_widht // 2, 176, 260, Roxo_espectral)
        desenhar_eco_profano(self.tela, Screen_widht // 2, 176, 12, self._frame)


        #slots
        for i in range(1, 4):
            dados = slots[i]
            selecionado = i == self.slot_selecionado

            #posiçao do slot na tela
            slot_y = 240 + (i - 1) * 140
            rect_slot = pygame.Rect(Screen_widht // 2 - 250, slot_y, 500, 110)

            cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.45)
            desenhar_painel(self.tela, rect_slot, self._frame, cor_borda=cor_borda)

            if selecionado:
                desenhar_eco_profano(self.tela, rect_slot.left + 24,
                                     rect_slot.centery, 11, self._frame)

            #conteudo do slot
            if dados is None:
                #slot vazio
                txt = self.fonte_slot.render(f"Slot {i} - Novo Jogo",
                                             True, Cinza_texto if not selecionado else Azul_claro)
                self.tela.blit(txt, (rect_slot.left + 52, rect_slot.top + 22))
                sub = self.fonte_info.render("Nenhum save encontrado",
                                             True, Cinza_texto_escuro)
                self.tela.blit(sub, (rect_slot.left + 52, rect_slot.top + 62))

            else:
                #slot com save
                txt = self.fonte_slot.render(f"Slot {i} - Continuar",
                                             True, Branco_texto)
                self.tela.blit(txt, (rect_slot.left + 52, rect_slot.top + 16))

                sala = self.fonte_info.render(
                    f"Sala: {dados['checkpoint_sala']}", True, Cinza_texto)
                self.tela.blit(sala, (rect_slot.left + 52, rect_slot.top + 56))

                data = self.fonte_info.render(
                    f"Salvo em: {dados['data_hora']}", True, Cinza_texto_escuro)
                self.tela.blit(data, (rect_slot.left + 52, rect_slot.top + 78))

                #DEL para deletar o save
                del_txt = self.fonte_info.render("DEL p/ apagar o save",
                                                 True, Vermelho_ritual)
                self.tela.blit(del_txt, (rect_slot.right - del_txt.get_width() - 20,
                                         rect_slot.top + 78))


        #confirmaçao de deletar o save
        if self.estado == "confirmar_delete":
            desenhar_overlay(self.tela, 190)

            painel = pygame.Rect(Screen_widht // 2 - 260, Screen_height // 2 - 70, 520, 140)
            desenhar_painel(self.tela, painel, self._frame,
                            cor_borda=escurecer(Vermelho_ritual, 0.25))

            msg1 = self.fonte_slot.render("Apagar este save?", True, Vermelho_ritual)
            msg2 = self.fonte_info.render("ENTER para confirmar   ESC para cancelar",
                                          True, Cinza_texto)
            self.tela.blit(msg1, (Screen_widht // 2 - msg1.get_width() // 2,
                                  painel.top + 26))
            self.tela.blit(msg2, (Screen_widht // 2 - msg2.get_width() // 2,
                                  painel.top + 84))

        #instruçao de teclas na base
        inst = self.fonte_info.render("↑↓ para navegar  ENTER para selecionar",
                                      True, Cinza_texto_escuro)
        self.tela.blit(inst, (Screen_widht // 2 - inst.get_width() // 2,
                              Screen_height - 40))
        desenhar_eco_profano(self.tela, Screen_widht - 60, Screen_height - 40,
                             9, self._frame)