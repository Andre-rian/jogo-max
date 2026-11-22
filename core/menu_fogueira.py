import pygame

import math

import logging

from settings import Screen_widht, Screen_height

from core.audio import audio

from ui.estilo import (

    Fonte_titulo, Fonte_texto,

    Roxo_espectral, Azul_espectral, Azul_claro,

    Branco_texto, Cinza_texto, Cinza_texto_escuro, Vermelho_ritual, Verde_cura,

    desenhar_overlay, desenhar_painel, desenhar_botao,

    desenhar_titulo, desenhar_linha_ornamental, desenhar_eco_profano,

    escurecer, misturar, versao_escala_texto

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



        #menu principal da fogueira

        self.opcoes = ["Descansar", "Subir de nível", "Sair"]

        self.opcao_selecionada = 0



        #sistema do level up - pontos pendentes por atributo

        self.pendente = {

            "vigor": 0,

            "resistencia": 0,

            "forca": 0,

            "destreza": 0,

        }



        self.atributo_selecionado = 0

        self._atributos = ["vigor", "resistencia", "forca", "destreza"]

        self._labes = {

            "vigor": "Vigor",

            "resistencia": "Resistência",

            "forca": "Força",

            "destreza": "Destreza",

        }



        pygame.font.init()

        self._configurar_fontes()



    def _configurar_fontes(self):

        self.fonte_titulo = Fonte_titulo(22, negrito=True)

        self.fonte_normal = Fonte_texto(20)

        self.fonte_pequena = Fonte_texto(15)

        self.fonte_titulo_menu = Fonte_titulo(34, negrito=True)

        self._versao_escala = versao_escala_texto()



    def _garantir_escala(self):

        if getattr(self, "_versao_escala", None) != versao_escala_texto():

            self._configurar_fontes()



    def _layout(self):

        from ui.estilo import obter_escala_texto

        e = obter_escala_texto()

        pw = min(Screen_widht - 60, int(520 + 120 * (e - 1.0)))

        ph = min(Screen_height - 100, int(360 + 120 * (e - 1.0)))

        return pw, ph



        self.atributo_selecionado = 0

        self._atributos = ["vigor", "resistencia", "forca", "destreza"]

        self._labes = {

            "vigor"         : "Vigor",

            "resistencia": "Resistência",

            "forca": "Força",

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

        

        if custo > self.player.ecos or sum(self.pendente.values()) == 0:

            audio.play_sfx("ui_error")

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



        audio.play_sfx("level_up")

        self._resetar_pendente()





    def atualizar(self, eventos):

        if not self.aberto:

            return

        self._garantir_escala()



        pos_mouse = pygame.mouse.get_pos()



        # hover por movimento do mouse (1x por mudanca de selecao)

        if any(e.type == pygame.MOUSEMOTION for e in eventos):

            if self.estado == self.MENU_PRINCIPAL:

                pw, ph = self._layout()

                x = Screen_widht // 2 - pw // 2

                y = Screen_height // 2 - ph // 2

                bw = min(300, pw - 60)

                bh = max(40, self.fonte_normal.get_height() + 16)

                bx = Screen_widht // 2 - bw // 2

                y_base = y + 120

                for i in range(len(self.opcoes)):

                    oy = y_base + i * (bh + 10)

                    rect = pygame.Rect(bx, oy, bw, bh)

                    if rect.collidepoint(pos_mouse) and i != self.opcao_selecionada:

                        self.opcao_selecionada = i

                        audio.play_sfx("ui_move")

                        break

            elif self.estado == self.LEVEL_UP:
                for i, r in self._rects_levelup_atributos():
                    if r.collidepoint(pos_mouse) and i != self.atributo_selecionado:
                        self.atributo_selecionado = i
                        audio.play_sfx("ui_move")
                        break

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

            audio.play_sfx("ui_move")

        

        elif evento.key == pygame.K_DOWN:

            self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)

            audio.play_sfx("ui_move")



        elif evento.key == pygame.K_RETURN:

            self._confirmar_opcao()

        

        elif evento.key == pygame.K_ESCAPE:

            audio.play_sfx("ui_back")

            self.fechar()



    

    def _input_level_up(self, evento):

        if evento.key == pygame.K_ESCAPE:

            audio.play_sfx("ui_back")

            self._resetar_pendente()

            self.estado = self.MENU_PRINCIPAL

        

        elif evento.key == pygame.K_UP:

            self.atributo_selecionado = (self.atributo_selecionado - 1) % len(self._atributos)

            audio.play_sfx("ui_move")



        elif evento.key == pygame.K_DOWN:

            self.atributo_selecionado = (self.atributo_selecionado + 1) % len(self._atributos)

            audio.play_sfx("ui_move")

            

        elif evento.key == pygame.K_RIGHT:

            if self._adicionar_ponto():

                audio.play_sfx("ui_move")



        elif evento.key == pygame.K_LEFT:

            if self._remover_ponto():

                audio.play_sfx("ui_move")



        elif evento.key == pygame.K_RETURN:

            self._confirmar_level_up()





    

    def _adicionar_ponto(self):

        atr = self._atributos[self.atributo_selecionado]

        nivel_atual = self.player.nivel + sum(self.pendente.values())

        if nivel_atual >= 99:

            return False

        

        custo_proximo = custo_nivel(nivel_atual)

        custo_atual = self._calcular_custo_total()

        if custo_atual + custo_proximo <= self.player.ecos:

            self.pendente[atr] += 1

            return True

        return False



    def _remover_ponto(self):

        atr = self._atributos[self.atributo_selecionado]

        if self.pendente[atr] > 0:

            self.pendente[atr] -= 1

            return True

        return False



    def _confirmar_opcao(self):

        opcao = self.opcoes[self.opcao_selecionada]

        if opcao == "Descansar":

            # callback executa o som/acao de descanso; evita duplicacao com ui_confirm

            if self.callback_descansar:

                self.callback_descansar()

            self.fechar()

            return



        audio.play_sfx("ui_confirm")

        if self.opcao_selecionada == 2 or opcao == "Sair":

            self.fechar()

            return



        # Subir Nivel

        self.estado = self.LEVEL_UP

        self.atributo_selecionado = 0



    def _clique_menu(self, pos_mouse):

        pw, ph = self._layout()

        x = Screen_widht // 2 - pw // 2

        y = Screen_height // 2 - ph // 2

        bw = min(300, pw - 60)

        bh = max(40, self.fonte_normal.get_height() + 16)

        bx = Screen_widht // 2 - bw // 2

        y_base = y + 120

        for i, _ in enumerate(self.opcoes):

            oy = y_base + i * (bh + 10)

            rect = pygame.Rect(bx, oy, bw, bh)

            if rect.collidepoint(pos_mouse):

                self.opcao_selecionada = i

                self._confirmar_opcao()



    def _clique_level_up(self, pos_mouse):
        for i, menos, mais in self._rects_levelup_botoes():
            if mais.collidepoint(pos_mouse):
                self.atributo_selecionado = i
                if self._adicionar_ponto(): audio.play_sfx("ui_move")
                return
            if menos.collidepoint(pos_mouse):
                self.atributo_selecionado = i
                if self._remover_ponto(): audio.play_sfx("ui_move")
                return
        btn = self._rect_levelup_confirmar()
        if btn.collidepoint(pos_mouse):
            self._confirmar_level_up()

    def desenhar(self):

        if not self.aberto:

            return

        self._garantir_escala()

        self._frame += 1



        #overlay 

        desenhar_overlay(self.tela, 165)



        if self.estado == self.MENU_PRINCIPAL:

            self._desenhar_menu_principal()

        elif self.estado == self.LEVEL_UP:

            self._desenhar_level_up()



    def _desenhar_menu_principal(self):
        pw, ph = self._layout()
        x = Screen_widht // 2 - pw // 2
        y = Screen_height // 2 - ph // 2
        painel = pygame.Rect(x, y, pw, ph)
        import math
        cx, cy = painel.centerx, painel.top + 88
        # sem halos grandes; partículas discretas
        for i in range(8):
            pxp = cx - 48 + (i * 12 % 96)
            fase = (self._frame * 0.30 + i * 31) % 72
            pyp = painel.top + 120 - fase
            a = max(0, min(70, int(70 - fase)))
            s = pygame.Surface((2, 2), pygame.SRCALPHA)
            s.fill((150, 190, 255, a) if i % 2 == 0 else (175, 120, 255, a))
            self.tela.blit(s, (int(pxp), int(pyp)))

        desenhar_painel(self.tela, painel, self._frame, titulo="FOGUEIRA", titulo_fonte=self.fonte_titulo_menu)
        sub = self.fonte_normal.render("chama antiga entre as ru?nas", True, Cinza_texto_escuro)
        self.tela.blit(sub, (Screen_widht // 2 - sub.get_width() // 2, y + 56))
        desenhar_linha_ornamental(self.tela, Screen_widht // 2, y + 82, min(220, pw - 80), Roxo_espectral)
        desenhar_eco_profano(self.tela, Screen_widht // 2, y + 82, 6, self._frame, alpha_real=True, intensidade_halo=0.0, raio_halo=0)
        bw = min(320, pw - 60)
        bh = max(44, self.fonte_normal.get_height() + 18)
        bx = Screen_widht // 2 - bw // 2
        y_base = y + 124
        for i, opcao in enumerate(self.opcoes):
            oy = y_base + i * (bh + 12)
            if oy + bh > y + ph - 20: break
            selecionada = i == self.opcao_selecionada
            rect = pygame.Rect(bx, oy, bw, bh)
            desenhar_botao(self.tela, rect, opcao, selecionada, self._frame, fonte_btn=self.fonte_normal, brilho=False)


    def _desenhar_level_up(self):

        p = self.player

        custo_total = self._calcular_custo_total()

        hp_novo, stamina_nova = self._preview_stats()

        total_pontos = sum(self.pendente.values())

        from ui.estilo import obter_escala_texto

        e = obter_escala_texto()



        # layout responsivo: empilha em escala alta / telas pequenas

        margem = 24

        if e >= 1.25 or Screen_widht < 1100:
            pw = min(Screen_widht - 40, 860)
            ph = min(Screen_height - 40, 620)
            painel = pygame.Rect(Screen_widht//2 - pw//2, Screen_height//2 - ph//2, pw, ph)
            desenhar_painel(self.tela, painel, self._frame, titulo="Subir de n?vel", titulo_fonte=self.fonte_titulo)
            x = painel.x + 16
            y = painel.y + 52
            info = [f"N?vel {p.nivel} -> {p.nivel + total_pontos}", f"Ecos {p.ecos}  Custo {custo_total}  Restam {p.ecos-custo_total}"]
            for i, t in enumerate(info):
                cor = Vermelho_ritual if i==1 and custo_total > p.ecos else Branco_texto
                srf = self.fonte_pequena.render(t, True, cor)
                self.tela.blit(srf, (x, y)); y += srf.get_height()+4
            y += 6
            row_h = max(34, self.fonte_normal.get_height() + 14)
            for i, atr in enumerate(self._atributos):
                ay = y + i * row_h
                if ay + row_h > painel.bottom - 100: break
                selecionado = i == self.atributo_selecionado
                cor = Azul_claro if selecionado else Cinza_texto
                label = self._labes[atr]
                valor_atual = getattr(p, atr)
                pendente = self.pendente[atr]
                self.tela.blit(self.fonte_normal.render(label, True, cor), (x, ay))
                val = f"{valor_atual}" + (f" +{pendente}" if pendente else "")
                val_x = painel.right - 210
                self.tela.blit(self.fonte_normal.render(val, True, Branco_texto), (val_x, ay))
                menos = pygame.Rect(painel.right - 110, ay-2, 38, row_h - 4)
                mais = pygame.Rect(painel.right - 64, ay-2, 38, row_h - 4)
                desenhar_botao(self.tela, menos, "-", False, self._frame, fonte_btn=self.fonte_normal)
                desenhar_botao(self.tela, mais, "+", selecionado, self._frame, fonte_btn=self.fonte_normal)
            y_prev = painel.bottom - 92
            linhas = [f"HP {p.hp_max} -> {hp_novo}", f"Stamina {p.stamina_max} -> {stamina_nova}"]
            for i,t in enumerate(linhas):
                srf = self.fonte_pequena.render(t, True, Verde_cura)
                self.tela.blit(srf, (x, y_prev + i*(srf.get_height()+2)))
            btn_w = min(260, painel.width - 40)
            btn = pygame.Rect(painel.centerx - btn_w//2, painel.bottom - 48, btn_w, 36)
            ativo = not (custo_total > p.ecos or total_pontos == 0)
            desenhar_botao(self.tela, btn, "Confirmar", ativo, self._frame, fonte_btn=self.fonte_normal)
            return



        # layout amplo original, com fontes escaladas

        px, py = 80, Screen_height // 2 - 160

        painel_esq = pygame.Rect(px, py, 230, 220)

        desenhar_painel(self.tela, painel_esq, self._frame, titulo="Subir de n?vel", titulo_fonte=self.fonte_titulo)

        desenhar_eco_profano(self.tela, px + 22, py + 34, 6, self._frame, alpha_real=True, intensidade_halo=0.0, raio_halo=0)

        infos = [("Nivel", f"{p.nivel} -> {p.nivel + total_pontos}"), ("Ecos", str(p.ecos)), ("Custo", str(custo_total)), ("Restam", str(p.ecos - custo_total))]

        for i, (label, valor) in enumerate(infos):

            cor_valor = Vermelho_ritual if label == "Custo" and custo_total > p.ecos else Branco_texto

            lbl = self.fonte_pequena.render(label, True, Cinza_texto)

            val = self.fonte_pequena.render(valor, True, cor_valor)

            yy = py + 74 + i * (self.fonte_pequena.get_height() + 10)

            self.tela.blit(lbl, (px + 12, yy))

            self.tela.blit(val, (px + painel_esq.w - 12 - val.get_width(), yy))



        cx = Screen_widht // 2 - 140

        painel_central = pygame.Rect(cx, py, 280, 300)

        desenhar_painel(self.tela, painel_central, self._frame, titulo="Atributos", titulo_fonte=self.fonte_titulo)

        for i, atr in enumerate(self._atributos):

            ay = py + 58 + i * (self.fonte_normal.get_height() + 30)

            selecionado = i == self.atributo_selecionado

            cor = Azul_claro if selecionado else Cinza_texto

            label = self._labes[atr]

            valor_atual = getattr(p, atr)

            pendente = self.pendente[atr]

            self.tela.blit(self.fonte_normal.render(label, True, cor), (cx + 14, ay))

            val_txt = self.fonte_normal.render(f"{valor_atual}" + (f" +{pendente}" if pendente else ""), True, Branco_texto)

            self.tela.blit(val_txt, (cx + 140, ay))

            menos = pygame.Rect(cx + 210, ay - 2, 28, 28)

            mais = pygame.Rect(cx + 244, ay - 2, 28, 28)

            desenhar_botao(self.tela, menos, "-", False, self._frame, fonte_btn=self.fonte_pequena)

            desenhar_botao(self.tela, mais, "+", selecionado, self._frame, fonte_btn=self.fonte_pequena)



        dx = Screen_widht - 80 - 220

        painel_dir = pygame.Rect(dx, py, 220, 180)

        desenhar_painel(self.tela, painel_dir, self._frame, titulo="Previa", titulo_fonte=self.fonte_titulo)

        prev = [("HP max", f"{p.hp_max} -> {hp_novo}"), ("Stamina", f"{p.stamina_max} -> {stamina_nova}")]

        for i, (label, valor) in enumerate(prev):

            yy = py + 74 + i * (self.fonte_pequena.get_height() + 14)

            self.tela.blit(self.fonte_pequena.render(label, True, Cinza_texto), (dx+12, yy))

            self.tela.blit(self.fonte_pequena.render(valor, True, Verde_cura), (dx+12, yy + self.fonte_pequena.get_height()+2))



        btn = pygame.Rect(cx, py + 320, 280, 40)

        ativo = not (custo_total > p.ecos or total_pontos == 0)

        desenhar_botao(self.tela, btn, "Confirmar", ativo, self._frame, fonte_btn=self.fonte_normal)
