import pygame
import math
import logging
from settings import Screen_widht, Screen_height
from ui.estilo import (
    Fonte_titulo, Fonte_texto,
    Roxo_espectral, Azul_espectral, Azul_claro,
    Branco_texto, Cinza_texto, Cinza_texto_escuro, Vermelho_ritual, Verde_cura,
    desenhar_overlay, desenhar_painel, desenhar_botao,
    desenhar_titulo, desenhar_linha_ornamental, desenhar_eco_profano,
    escurecer, misturar
)

logger = logging.getLogger(__name__)

def custo_nivel(nivel):
    return int(50 * (1.25 ** nivel))


class MenuFogueira:

    MENU_PRINCIPAL = "menu"
    LEVEL_UP = "level_up"


    def __init__(self, tela, player, callback_descansar, callback_fechar):

        self.tela = tela
        self.player = player
        self.callback_descansar = callback_descansar
        self.callback_fechar = callback_fechar

        self.estado = self.MENU_PRINCIPAL
        self.aberto = False
        self._frame = 0

        pygame.font.init()
        self.fonte_titulo = Fonte_titulo(22, negrito=True)
        self.fonte_normal = Fonte_texto(20)
        self.fonte_pequena = Fonte_texto(15)

        #menu principal da fogueira
        self.opcoes = ["Descansar", "Subir Nível", "Sair"]
        self.opcao_selecionada = 0
            

        
        #sistema do level up - pontos pendentes por atributo
        self.pendente = {
            "vigor" :       0,
            "resistencia":  0,
            "forca":        0,
            "destreza":     0

        }

        self.atributo_selecionado = 0
        self._atributos = ["vigor", "resistencia", "forca", "destreza"]
        self._labes = {
            "vigor"         : "Vigor",
            "resistencia"   : "Resistência",
            "forca"         : "Força",
            "destreza"      : "Destreza"

        }

    def abrir(self):
        logger.debug("MenuFogueira.abrir() chamado")
        self.aberto = True
        self.estado = self.MENU_PRINCIPAL
        self.opcao_selecionada = 0
        self._resetar_pendente()

    def fechar(self):
        self.aberto = False
        self._resetar_pendente()
        if self.callback_fechar:
            self.callback_fechar()


    def _resetar_pendente(self):
        for k in self.pendente:
            self.pendente[k] = 0

    def _calcular_custo_total(self):
        nivel_atual = self.player.nivel
        total_pontos = sum(self.pendente.values())
        custo = 0
        for i in range(total_pontos):
            custo += custo_nivel(nivel_atual + i)
        return custo
    

    def _preview_stats(self):
        p = self.player
        
        vigor_novo = p.vigor + self.pendente["vigor"]
        
        res_novo = p.resistencia + self.pendente["resistencia"]

        hp_novo = p.HP_BASE + (vigor_novo * p.HP_POR_VIGOR)

        stamina_nova = p.STAMINA_BASE + (res_novo * p.STAMINA_POR_RES)

        return hp_novo, stamina_nova
    
    def _confirmar_level_up(self):
        custo = self._calcular_custo_total()
        
        if custo > self.player.ecos:
            return
        
        if sum(self.pendente.values()) == 0:
            return
        

        self.player.ecos -= custo
        total_pontos = sum(self.pendente.values())
        self.player.nivel += total_pontos

        self.player.vigor          +=   self.pendente["vigor"]
        self.player.resistencia    +=   self.pendente["resistencia"]
        self.player.forca          +=   self.pendente["forca"]
        self.player.destreza       +=   self.pendente["destreza"]


        #reecalcular o hp e a stamina
        self.player.hp_max = self.player.HP_BASE + (self.player.vigor * self.player.HP_POR_VIGOR)
        self.player.hp = self.player.hp_max
        self.player.stamina_max = self.player.STAMINA_BASE + (self.player.resistencia * self.player.STAMINA_POR_RES)
        self.player.stamina = self.player.stamina_max

        self._resetar_pendente()


    def atualizar(self, eventos):
        if not self.aberto:
            return
        
        pos_mouse = pygame.mouse.get_pos()


        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if self.estado == self.MENU_PRINCIPAL:
                    self._input_menu(evento)
                elif self.estado == self.LEVEL_UP:
                    self._input_level_up(evento)

            
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.estado == self.MENU_PRINCIPAL:
                    self._clique_menu(pos_mouse)
                elif self.estado == self.LEVEL_UP:
                    self._clique_level_up(pos_mouse)

    def _input_menu(self, evento):
        if evento.key == pygame.K_UP:
            self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)
        
        elif evento.key == pygame.K_DOWN:
            self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)

        elif evento.key == pygame.K_RETURN:
            self._confirmar_opcao()
        
        elif evento.key == pygame.K_ESCAPE:
            self.fechar()

    
    def _input_level_up(self, evento):
        if evento.key == pygame.K_ESCAPE:
            self._resetar_pendente()
            self.estado = self.MENU_PRINCIPAL
        
        elif evento.key == pygame.K_UP:
            self.atributo_selecionado = (self.atributo_selecionado - 1) % len(self._atributos)

        elif evento.key == pygame.K_DOWN:
            self.atributo_selecionado = (self.atributo_selecionado + 1) % len(self._atributos)
            
        elif evento.key == pygame.K_RIGHT:
            self._adicionar_ponto()

        elif evento.key == pygame.K_LEFT:
            self._remover_ponto()

        elif evento.key == pygame.K_RETURN:
            self._confirmar_level_up()


    
    def _adicionar_ponto(self):
        atr = self._atributos[self.atributo_selecionado]
        nivel_atual = self.player.nivel + sum(self.pendente.values())
        if nivel_atual >= 99:
            return
        
        custo_proximo = custo_nivel(nivel_atual)
        custo_atual = self._calcular_custo_total()
        if custo_atual + custo_proximo <= self.player.ecos:
            self.pendente[atr] += 1

    def _remover_ponto(self):
        atr = self._atributos[self.atributo_selecionado]
        if self.pendente[atr] > 0:
            self.pendente[atr] -= 1

    def _confirmar_opcao(self):
        opcao = self.opcoes[self.opcao_selecionada]
        if opcao == "Descansar":
            if self.callback_descansar:
                self.callback_descansar()
            
            self.fechar() 
        
        elif opcao == "Subir Nível":
            self.estado = self.LEVEL_UP
            self.atributo_selecionado = 0

        elif opcao == "Sair":
            self.fechar()

    def _clique_menu(self, pos_mouse):
        x = Screen_widht // 2 - 120
        for i, opcao in enumerate(self.opcoes):
            y = Screen_height // 2 - 60 + i * 50
            rect = pygame.Rect(x, y, 240, 40)
            
            if rect.collidepoint(pos_mouse):
                self.opcao_selecionada = i
                self._confirmar_opcao()

    def _clique_level_up(self, pos_mouse):
        #os botoes + e - de cada atributo
        cx = Screen_widht // 2 - 120
        py = Screen_height // 2 - 160



        for i, atr in enumerate(self._atributos):
            ay = py +  20 + i * 60
            
            
            rect_menos = pygame.Rect(cx - 40, ay, 30, 30)
            rect_mais = pygame.Rect(cx + 250, ay, 30, 30)

            if rect_mais.collidepoint(pos_mouse):
                self.atributo_selecionado = i
                self._adicionar_ponto()

            elif rect_menos.collidepoint(pos_mouse):
                self.atributo_selecionado = i
                self._remover_ponto()
        
        #botao de confirma
        rect_confirma = pygame.Rect(cx, py + 250, 240, 40)
        if rect_confirma.collidepoint(pos_mouse):
            self._confirmar_level_up()

    def desenhar(self):
        if not self.aberto:
            return
        
        self._frame += 1

        #overlay 
        desenhar_overlay(self.tela, 165)

        if self.estado == self.MENU_PRINCIPAL:
            self._desenhar_menu_principal()
        elif self.estado == self.LEVEL_UP:
            self._desenhar_level_up()

    def _desenhar_menu_principal(self):
        x = Screen_widht // 2 - 120
        y_base = Screen_height // 2 - 80


        #titulo 
        cx_titulo = Screen_widht // 2
        desenhar_titulo(self.tela, "FOGUEIRA",
                        Fonte_titulo(34, negrito=True), Roxo_espectral,
                        cx_titulo, y_base - 80, espacamento=3)
        sub = self.fonte_normal.render("chama antiga entre as ruinas",
                                       True, Cinza_texto_escuro)
        self.tela.blit(sub, (cx_titulo - sub.get_width() // 2, y_base - 52))
        desenhar_linha_ornamental(self.tela, cx_titulo, y_base - 34, 180, Roxo_espectral)
        desenhar_eco_profano(self.tela, cx_titulo, y_base - 34, 10, self._frame)


        for i, opcao in enumerate(self.opcoes):
            y = y_base + 20 + i * 50
            selecionada = i == self.opcao_selecionada
            desenhar_botao(self.tela, pygame.Rect(x, y, 240, 40), opcao,
                           selecionada, self._frame, fonte_btn=self.fonte_normal)


    def _desenhar_level_up(self):
        p = self.player
        custo_total = self._calcular_custo_total()
        hp_novo, stamina_nova = self._preview_stats()
        total_pontos = sum(self.pendente.values())


        #painel esquerdo = informaçoes do player
        px, py = 80, Screen_height // 2 - 160
        painel_esq = pygame.Rect(px, py, 220, 200)
        desenhar_painel(self.tela, painel_esq, self._frame,
                        titulo="Subir Nível", titulo_fonte=self.fonte_titulo)

        desenhar_eco_profano(self.tela, px + 22, py + 34, 9, self._frame)

        infos = [
            ("Nível", f"{p.nivel} → {p.nivel + total_pontos}"),
            ("Ecos", str(p.ecos)),
            ("Custo", str(custo_total)),
            ("Ecos restantes", str(p.ecos - custo_total))
        ]

        for i, (label, valor) in enumerate(infos):
            cor_valor = Vermelho_ritual if label == "Custo" and custo_total > p.ecos else Branco_texto
            lbl = self.fonte_pequena.render(label, True, Cinza_texto)
            val = self.fonte_pequena.render(valor, True, cor_valor)
            self.tela.blit(lbl, (px + 12, py + 74 + i * 28))
            self.tela.blit(val, (px + 208 - val.get_width(), py + 74 + i * 28))


        #painel central - atributops
        cx = Screen_widht // 2 - 120
        painel_central = pygame.Rect(cx, py, 240, 280)
        desenhar_painel(self.tela, painel_central, self._frame,
                        titulo="Atributos", titulo_fonte=self.fonte_titulo)

        for i, atr in enumerate(self._atributos):
            ay = py + 20 + i * 60
            selecionado = i == self.atributo_selecionado
            cor = Azul_claro if selecionado else Cinza_texto

            label = self._labes[atr]
            valor_atual = getattr(p, atr)
            pendente = self.pendente[atr]

            lbl = self.fonte_normal.render(label, True, cor)
            self.tela.blit(lbl, (cx + 14, ay))


            #valor atual → novo
            if pendente > 0:
                val_txt = f"{valor_atual}  →  {valor_atual + pendente}"
                cor_val = Verde_cura
            
            else:
                val_txt = str(valor_atual)
                cor_val = Branco_texto

            val = self.fonte_normal.render(val_txt, True, cor_val)
            self.tela.blit(val, (cx + 236 - val.get_width(), ay))


            #botao -
            rect_menos = pygame.Rect(cx - 40, ay, 30, 30)
            desenhar_botao(self.tela, rect_menos, "-", selecionado, self._frame,
                           fonte_btn=self.fonte_normal, marcador=False)

            #botao +
            rect_mais = pygame.Rect(cx + 250, ay, 30, 30)
            desenhar_botao(self.tela, rect_mais, "+", selecionado, self._frame,
                           fonte_btn=self.fonte_normal, marcador=False)

        #botao confirmar
        pode_confirmar = custo_total <= p.ecos and total_pontos > 0
        rect_confirma = pygame.Rect(cx, py + 250, 240, 40)
        desenhar_botao(self.tela, rect_confirma, "Confirmar", pode_confirmar,
                       self._frame, fonte_btn=self.fonte_normal)


        #painel direito - mostra como vai ficar os status
        dx = Screen_widht - 300
        painel_dir = pygame.Rect(dx, py, 220, 200)
        desenhar_painel(self.tela, painel_dir, self._frame,
                        titulo="Preview", titulo_fonte=self.fonte_titulo)

        previews = [
            ("HP",        f"{p.hp_max} → {hp_novo}"),
            ("Stamina",   f"{p.stamina_max} → {stamina_nova}")
        ]

        for i, (label, valor) in enumerate(previews):
            lbl = self.fonte_pequena.render(label, True, Cinza_texto)
            val = self.fonte_pequena.render(valor, True, Verde_cura)
            self.tela.blit(lbl, (dx + 12, py + 74 + i * 28))
            self.tela.blit(val, (dx + 208 - val.get_width(), py + 74 + i * 28))

        #apoio visual do custo disponivel
        desenhar_eco_profano(self.tela, dx + 26, py + 150, 13, self._frame)
        eco_txt = self.fonte_normal.render(str(p.ecos), True, Branco_texto)
        self.tela.blit(eco_txt, (dx + 44, py + 146))


        #instruções
        inst = self.fonte_pequena.render(
            "← → ajustar   ENTER confirmar   ESC voltar",
            True, Cinza_texto_escuro)
        self.tela.blit(inst, (Screen_widht // 2 - inst.get_width() // 2,
                               Screen_height - 40))