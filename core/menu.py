import pygame
import sys
from core.audio import audio
from core import preferencias as prefs
from settings import Screen_widht, Screen_height
from core.navegacao import hover_index, mouse_mouveu
from ui.estilo import (
    Fonte_titulo, Fonte_texto,
    Roxo_profundo, Roxo_espectral, Azul_espectral, Azul_claro,
    Branco_texto, Cinza_texto, Cinza_texto_escuro, Vermelho_ritual,
    desenhar_fundo, desenhar_overlay, desenhar_painel, desenhar_botao,
    desenhar_titulo, desenhar_linha_ornamental, desenhar_eco_profano,
    adicionar_brilho, clarear, escurecer, definir_escala_texto, obter_escala_texto,
)
from ui.moldura_menu_lygame import (
    desenhar_moldura_slot, disponivel as moldura_lygame_disponivel
)
from ui.prompts_teclas import criar_prompt, desenhar_prompts

USAR_MOLDURA_LYGAME = True

ESCALA_PROMPT_DISCRETO = 1.25
ESCALA_PROMPT_MODAL = 1.50
FONTE_PROMPT_DISCRETO = 18
FONTE_PROMPT_MODAL = 20
PADDING_PROMPT_DISCRETO = (5, 3)
PADDING_PROMPT_MODAL = (8, 5)
FUNDO_PROMPT_DISCRETO = (10, 10, 14, 80)
FUNDO_PROMPT_MODAL = (18, 16, 22, 140)
ESPACO_TECLAS_PROMPT = 4
ESPACO_TEXTO_PROMPT = 9
ESPACO_TECLAS_MODAL = 5
ESPACO_TEXTO_MODAL = 11

SLIDERS_AUDIO = [
    ("geral", "Geral"),
    ("musica", "Música"),
    ("efeitos", "Efeitos"),
    ("interface", "Interface"),
    ("ambiencia", "Ambiência"),
]


class MenuInicial:

    def __init__(self, tela, save_manager, preferencias=None, caminho_preferencias=None):
        self.tela = tela
        self.save_manager = save_manager
        self.caminho_preferencias = caminho_preferencias
        self.preferencias = prefs.normalizar(preferencias)

        self._frame = 0

        # fluxo principal: principal -> slots | opcoes
        self.tela_menu = "principal"
        self.estado = "selecionar"  # selecionar / confirmar_delete (na tela de slots)

        self.opcao_principal = 0  # Jogar, Opções, Sair
        self.slot_selecionado = 1  # 1, 2 ou 3
        self.item_opcao_selecionado = 0
        self.aba_opcoes = "acessibilidade"  # acessibilidade | audio
        self.arrastando_slider = None

        self.callback_iniciar = None
        self.callback_sair = None

        self._reconstruir_fontes()
        self._aplicar_audio_preferencias()

    def _reconstruir_fontes(self):
        self.fonte_titulo = Fonte_titulo(78, negrito=True)
        self.fonte_menu = Fonte_titulo(34, negrito=True)
        self.fonte_slot = Fonte_titulo(27, negrito=True)
        self.fonte_info = Fonte_texto(17)
        self.fonte_opcao = Fonte_texto(22)
        self.fonte_opcao_pequena = Fonte_texto(16)
        self.fonte_prompt = Fonte_texto(FONTE_PROMPT_DISCRETO)
        self.fonte_prompt_modal = Fonte_texto(FONTE_PROMPT_MODAL)

    # ---------- preferencias ----------
    def _salvar_preferencias(self):
        return prefs.salvar(self.preferencias, self.caminho_preferencias)

    def _aplicar_audio_preferencias(self):
        aplicar = getattr(audio, "aplicar_preferencias_audio", None)
        if callable(aplicar):
            aplicar(prefs.volumes_normalizados(self.preferencias))

    def _aplicar_texto_preferencias(self, salvar=True):
        definir_escala_texto(prefs.escala_texto(self.preferencias))
        self._reconstruir_fontes()
        if salvar:
            self._salvar_preferencias()

    def _ajustar_slider(self, chave, valor, salvar=True):
        valor = max(0, min(100, int(valor)))
        atual = int(self.preferencias["audio"].get(chave, 100))
        if valor == atual:
            return False
        self.preferencias["audio"][chave] = valor
        self._aplicar_audio_preferencias()
        if salvar:
            self._salvar_preferencias()
        return True

    def _set_tamanho_texto(self, tamanho, salvar=True):
        if tamanho not in prefs.TAMANHOS_TEXTO:
            return False
        atual = self.preferencias["acessibilidade"].get("tamanho_texto", "padrao")
        if tamanho == atual:
            return False
        self.preferencias["acessibilidade"]["tamanho_texto"] = tamanho
        self._aplicar_texto_preferencias(salvar=salvar)
        return True

    def _restaurar_padroes_opcoes(self):
        self.preferencias = prefs.normalizar(None)
        self._aplicar_texto_preferencias(salvar=False)
        self._aplicar_audio_preferencias()
        self._salvar_preferencias()

    # ---------- layout ----------
    def _rects_principal(self):
        opcoes = ["Jogar", "Opções", "Sair"]
        base_y = 310
        rects = []
        for i, _ in enumerate(opcoes):
            rects.append(pygame.Rect(Screen_widht // 2 - 160, base_y + i * 70, 320, 52))
        return rects, opcoes

    def _rects_slots(self):
        rects = []
        for i in range(1, 4):
            slot_y = 240 + (i - 1) * 140
            rects.append((i, pygame.Rect(Screen_widht // 2 - 250, slot_y, 500, 110)))
        rect_voltar = pygame.Rect(Screen_widht // 2 - 90, Screen_height - 86, 180, 40)
        return rects, rect_voltar

    def _layout_opcoes(self):
        escala = obter_escala_texto()
        pw = min(Screen_widht - 48, int(860 + max(0.0, escala - 1.0) * 220))
        ph = min(Screen_height - 120, int(430 + max(0.0, escala - 1.0) * 170))
        painel = pygame.Rect(Screen_widht // 2 - pw // 2, 175, pw, ph)
        inner = painel.inflate(-48, -48)
        aba_w = max(170, (inner.width - 10) // 2)
        aba_h = max(34, self.fonte_opcao_pequena.get_height() + 14)
        abas = {
            "acessibilidade": pygame.Rect(inner.left, painel.top + 18, aba_w, aba_h),
            "audio": pygame.Rect(inner.left + aba_w + 10, painel.top + 18, min(aba_w, inner.right - (inner.left + aba_w + 10)), aba_h),
        }
        conteudo_top = abas["acessibilidade"].bottom + 14
        conteudo = pygame.Rect(inner.left, conteudo_top, inner.width, painel.bottom - conteudo_top - 24)
        preview_h = max(84, self.fonte_opcao.get_height() + self.fonte_info.get_height() + 44)
        preview = pygame.Rect(conteudo.left, conteudo.top + max(120, self.fonte_opcao.get_height() + 90), conteudo.width, preview_h)
        if preview.bottom > conteudo.bottom - 52:
            preview.height = max(64, conteudo.bottom - 52 - preview.top)
        if self.aba_opcoes == "acessibilidade":
            botoes = []
            gap = 10
            btn_w = max(120, (conteudo.width - gap * 2) // 3)
            btn_h = max(36, self.fonte_opcao_pequena.get_height() + 16)
            y = conteudo.top + self.fonte_opcao.get_height() + 24
            for idx, chave in enumerate(prefs.TAMANHOS_TEXTO):
                botoes.append((idx, chave, pygame.Rect(conteudo.left + idx * (btn_w + gap), y, btn_w, btn_h)))
            btn_rw = min(260, max(180, int(conteudo.width * 0.35)))
            btn_rh = max(34, self.fonte_opcao_pequena.get_height() + 14)
            btn_restaurar = pygame.Rect(conteudo.right - btn_rw, conteudo.bottom - btn_rh - 2, btn_rw, btn_rh)
            return painel, abas, conteudo, preview, botoes, [], btn_restaurar
        # audio - layout responsivo para escalas grandes
        sliders = []
        label_w = max(120, int(conteudo.width * 0.28))
        valor_w = 64
        gap = 14
        slider_x = conteudo.left + label_w + gap
        slider_w = max(120, conteudo.width - label_w - valor_w - gap * 3)
        slider_h = 10
        row_h = max(42, self.fonte_opcao_pequena.get_height() + 24)
        y = conteudo.top + 8
        for idx, (chave, rotulo) in enumerate(SLIDERS_AUDIO):
            track = pygame.Rect(slider_x, y + idx * row_h + (row_h - slider_h) // 2, slider_w, slider_h)
            sliders.append((idx, chave, rotulo, track))
        btn_w = min(260, max(180, int(conteudo.width * 0.35)))
        btn_h = max(34, self.fonte_opcao_pequena.get_height() + 14)
        btn_restaurar = pygame.Rect(conteudo.right - btn_w, conteudo.bottom - btn_h - 2, btn_w, btn_h)
        return painel, abas, conteudo, preview, [], sliders, btn_restaurar

    # ---------- update helpers ----------
    def _ir_para_slots(self):
        self.tela_menu = "slots"
        self.estado = "selecionar"
        self.slot_selecionado = 1

    def _ir_para_opcoes(self):
        self.tela_menu = "opcoes"
        self.aba_opcoes = "acessibilidade"
        self.item_opcao_selecionado = 0
        self.arrastando_slider = None

    def _voltar_principal(self):
        self.tela_menu = "principal"
        self.estado = "selecionar"
        self.arrastando_slider = None

    # ---------- eventos ----------
    def atualizar(self, eventos):
        if self.tela_menu == "principal":
            self._atualizar_principal(eventos)
        elif self.tela_menu == "slots":
            self._atualizar_slots(eventos)
        elif self.tela_menu == "opcoes":
            self._atualizar_opcoes(eventos)

    def _atualizar_principal(self, eventos):
        rects, opcoes = self._rects_principal()
        pos_mouse = pygame.mouse.get_pos()
        itens = [(i, r) for i, r in enumerate(rects)]
        hover = hover_index(eventos, pos_mouse, itens)
        if hover is not None and hover != self.opcao_principal:
            self.opcao_principal = hover
            audio.play_sfx("ui_move")

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(pos_mouse):
                        self.opcao_principal = i
                        self._ativar_principal(opcoes[i])
                        return
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    novo = (self.opcao_principal - 1) % len(opcoes)
                    if novo != self.opcao_principal:
                        self.opcao_principal = novo
                        audio.play_sfx("ui_move")
                elif evento.key == pygame.K_DOWN:
                    novo = (self.opcao_principal + 1) % len(opcoes)
                    if novo != self.opcao_principal:
                        self.opcao_principal = novo
                        audio.play_sfx("ui_move")
                elif evento.key == pygame.K_RETURN:
                    self._ativar_principal(opcoes[self.opcao_principal])
                elif evento.key == pygame.K_ESCAPE:
                    # no menu principal, ESC sai (acao explicita existente: sair)
                    audio.play_sfx("ui_back")
                    self._ativar_principal("Sair")

    def _ativar_principal(self, nome):
        audio.play_sfx("ui_confirm")
        if nome == "Jogar":
            self._ir_para_slots()
        elif nome == "Opções":
            self._ir_para_opcoes()
        elif nome == "Sair":
            if self.callback_sair:
                self.callback_sair()

    def _atualizar_slots(self, eventos):
        slots = self.save_manager.listar_slots()
        pos_mouse = pygame.mouse.get_pos()
        itens_slot, rect_voltar = self._rects_slots()

        # hover slots/voltar (apenas com movimento real)
        if mouse_mouveu(eventos):
            for i, rect_slot in itens_slot:
                if rect_slot.collidepoint(pos_mouse):
                    if i != self.slot_selecionado or self.estado != "selecionar":
                        self.slot_selecionado = i
                        if self.estado == "selecionar":
                            audio.play_sfx("ui_move")
                    break
            # voltar nao tem indice sonoro separado para evitar ruido; selecao visual implicita no clique/teclado

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.estado == "selecionar":
                    for indice, rect_slot in itens_slot:
                        if rect_slot.collidepoint(pos_mouse):
                            self.slot_selecionado = indice
                            dados = slots[self.slot_selecionado]
                            audio.play_sfx("ui_confirm")
                            if self.callback_iniciar:
                                self.callback_iniciar(self.slot_selecionado, dados)
                            return
                    if rect_voltar.collidepoint(pos_mouse):
                        audio.play_sfx("ui_back")
                        self._voltar_principal()
                        return
                    continue
                elif self.estado == "confirmar_delete":
                    continue

            if evento.type == pygame.KEYDOWN:
                if self.estado == "selecionar":
                    if evento.key == pygame.K_UP:
                        anterior = self.slot_selecionado
                        self.slot_selecionado = max(1, self.slot_selecionado - 1)
                        if self.slot_selecionado != anterior:
                            audio.play_sfx("ui_move")
                    elif evento.key == pygame.K_DOWN:
                        anterior = self.slot_selecionado
                        self.slot_selecionado = min(3, self.slot_selecionado + 1)
                        if self.slot_selecionado != anterior:
                            audio.play_sfx("ui_move")
                    elif evento.key == pygame.K_RETURN:
                        dados = slots[self.slot_selecionado]
                        audio.play_sfx("ui_confirm")
                        if self.callback_iniciar:
                            self.callback_iniciar(self.slot_selecionado, dados)
                    elif evento.key == pygame.K_DELETE:
                        if slots[self.slot_selecionado] is not None:
                            audio.play_sfx("ui_confirm")
                            self.estado = "confirmar_delete"
                        else:
                            audio.play_sfx("ui_error")
                    elif evento.key == pygame.K_ESCAPE:
                        audio.play_sfx("ui_back")
                        self._voltar_principal()
                elif self.estado == "confirmar_delete":
                    if evento.key == pygame.K_RETURN:
                        audio.play_sfx("ui_confirm")
                        self.save_manager.deletar(self.slot_selecionado)
                        self.estado = "selecionar"
                    elif evento.key == pygame.K_ESCAPE:
                        audio.play_sfx("ui_back")
                        self.estado = "selecionar"

    def _slider_valor_do_x(self, track, x):
        if track.width <= 0:
            return 0
        proporcao = (x - track.left) / float(track.width)
        return int(round(max(0.0, min(1.0, proporcao)) * 100))

    def _atualizar_opcoes(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        painel, abas, conteudo, preview, botoes_tam, sliders, btn_restaurar = self._layout_opcoes()

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                self.arrastando_slider = None

            elif evento.type == pygame.MOUSEMOTION and self.arrastando_slider is not None:
                # arraste atualiza sem som repetitivo
                for _idx, chave, _rotulo, track in sliders:
                    if chave == self.arrastando_slider:
                        valor = self._slider_valor_do_x(track, evento.pos[0])
                        self._ajustar_slider(chave, valor, salvar=True)
                        break

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if abas["acessibilidade"].collidepoint(pos_mouse):
                    if self.aba_opcoes != "acessibilidade":
                        self.aba_opcoes = "acessibilidade"
                        self.item_opcao_selecionado = 0
                        audio.play_sfx("ui_move")
                    continue
                if abas["audio"].collidepoint(pos_mouse):
                    if self.aba_opcoes != "audio":
                        self.aba_opcoes = "audio"
                        self.item_opcao_selecionado = 0
                        audio.play_sfx("ui_move")
                    continue

                if self.aba_opcoes == "acessibilidade":
                    for idx, chave, rect in botoes_tam:
                        if rect.collidepoint(pos_mouse):
                            self.item_opcao_selecionado = idx
                            audio.play_sfx("ui_confirm")
                            self._set_tamanho_texto(chave, salvar=True)
                            break
                else:
                    for idx, chave, _rotulo, track in sliders:
                        hit = track.inflate(18, 18)
                        if hit.collidepoint(pos_mouse):
                            self.item_opcao_selecionado = idx
                            valor = self._slider_valor_do_x(track, pos_mouse[0])
                            mudou = self._ajustar_slider(chave, valor, salvar=True)
                            if not mudou:
                                audio.play_sfx("ui_move")
                            self.arrastando_slider = chave
                            break

                if btn_restaurar.collidepoint(pos_mouse):
                    audio.play_sfx("ui_confirm")
                    self._restaurar_padroes_opcoes()

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    audio.play_sfx("ui_back")
                    self._voltar_principal()
                elif evento.key == pygame.K_TAB:
                    self.aba_opcoes = "audio" if self.aba_opcoes == "acessibilidade" else "acessibilidade"
                    self.item_opcao_selecionado = 0
                    audio.play_sfx("ui_move")
                elif evento.key == pygame.K_UP:
                    if self.aba_opcoes == "acessibilidade":
                        # botoes de tamanho em linha + restaurar (ultimo)
                        total = len(prefs.TAMANHOS_TEXTO) + 1
                    else:
                        total = len(SLIDERS_AUDIO) + 1
                    novo = (self.item_opcao_selecionado - 1) % total
                    if novo != self.item_opcao_selecionado:
                        self.item_opcao_selecionado = novo
                        audio.play_sfx("ui_move")
                elif evento.key == pygame.K_DOWN:
                    if self.aba_opcoes == "acessibilidade":
                        total = len(prefs.TAMANHOS_TEXTO) + 1
                    else:
                        total = len(SLIDERS_AUDIO) + 1
                    novo = (self.item_opcao_selecionado + 1) % total
                    if novo != self.item_opcao_selecionado:
                        self.item_opcao_selecionado = novo
                        audio.play_sfx("ui_move")
                elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    delta = -5 if evento.key == pygame.K_LEFT else 5
                    if self.aba_opcoes == "acessibilidade":
                        if self.item_opcao_selecionado < len(prefs.TAMANHOS_TEXTO):
                            idx = self.item_opcao_selecionado
                            idx = max(0, min(len(prefs.TAMANHOS_TEXTO) - 1, idx + (1 if delta > 0 else -1)))
                            if idx != self.item_opcao_selecionado:
                                self.item_opcao_selecionado = idx
                                audio.play_sfx("ui_move")
                                self._set_tamanho_texto(prefs.TAMANHOS_TEXTO[idx], salvar=True)
                    else:
                        if self.item_opcao_selecionado < len(SLIDERS_AUDIO):
                            chave, _ = SLIDERS_AUDIO[self.item_opcao_selecionado]
                            atual = int(self.preferencias["audio"][chave])
                            self._ajustar_slider(chave, atual + delta, salvar=True)
                elif evento.key == pygame.K_RETURN:
                    if self.aba_opcoes == "acessibilidade":
                        if self.item_opcao_selecionado < len(prefs.TAMANHOS_TEXTO):
                            audio.play_sfx("ui_confirm")
                            self._set_tamanho_texto(
                                prefs.TAMANHOS_TEXTO[self.item_opcao_selecionado], salvar=True
                            )
                        else:
                            audio.play_sfx("ui_confirm")
                            self._restaurar_padroes_opcoes()
                    else:
                        if self.item_opcao_selecionado < len(SLIDERS_AUDIO):
                            audio.play_sfx("ui_confirm")  # foco/confirmacao sem acao destrutiva
                        else:
                            audio.play_sfx("ui_confirm")
                            self._restaurar_padroes_opcoes()

    # ---------- desenho ----------
    def desenhar(self):
        self._frame += 1
        desenhar_fundo(self.tela, self._frame)
        self._desenhar_titulo()
        if self.tela_menu == "principal":
            self._desenhar_principal()
        elif self.tela_menu == "slots":
            self._desenhar_slots()
        elif self.tela_menu == "opcoes":
            self._desenhar_opcoes()
        self._desenhar_rodape()
        desenhar_eco_profano(self.tela, Screen_widht - 60, Screen_height - 40,
                             8, self._frame, alpha_real=True, intensidade_halo=0.0, raio_halo=0)

    def _desenhar_titulo(self):
        # sem halo grande no título do menu
        desenhar_titulo(self.tela, "PROFANE ECHO", self.fonte_titulo,
                        clarear(Roxo_espectral, 0.08), Screen_widht // 2, 58,
                        espacamento=6)
        sub = self.fonte_info.render("o eco profano desperta entre os escombros",
                                     True, clarear(Cinza_texto_escuro, 0.12))
        self.tela.blit(sub, (Screen_widht // 2 - sub.get_width() // 2, 146))
        desenhar_linha_ornamental(self.tela, Screen_widht // 2, 176, 260, Roxo_espectral)
        desenhar_eco_profano(self.tela, Screen_widht // 2, 176, 10,
                             self._frame, alpha_real=True, intensidade_halo=0.0, raio_halo=0)

    def _desenhar_principal(self):
        rects, opcoes = self._rects_principal()
        for i, (rect, nome) in enumerate(zip(rects, opcoes)):
            selecionado = i == self.opcao_principal
            cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.45)
            desenhar_painel(self.tela, rect, self._frame, cor_borda=cor_borda)
            txt = self.fonte_menu.render(nome, True, Branco_texto if selecionado else Cinza_texto)
            self.tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
            if selecionado:
                desenhar_eco_profano(self.tela, rect.left + 22, rect.centery, 10,
                                     self._frame, alpha_real=True)

    def _desenhar_slots(self):
        slots = self.save_manager.listar_slots()
        itens_slot, _rect_voltar = self._rects_slots()
        cor_alerta = clarear(Vermelho_ritual, 0.30)
        cor_prompt_delete = clarear(Vermelho_ritual, 0.40)
        usar_moldura_lygame = USAR_MOLDURA_LYGAME and moldura_lygame_disponivel()

        for i, rect_slot in itens_slot:
            dados = slots[i]
            selecionado = i == self.slot_selecionado and self.estado == "selecionar"

            moldura_ok = usar_moldura_lygame and desenhar_moldura_slot(
                self.tela, rect_slot, selecionado, dados is not None
            )
            if not moldura_ok:
                cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.45)
                desenhar_painel(self.tela, rect_slot, self._frame, cor_borda=cor_borda)

            if selecionado:
                desenhar_eco_profano(self.tela, rect_slot.left + 24,
                                     rect_slot.centery, 11, self._frame, alpha_real=True)

            if dados is None:
                txt = self.fonte_slot.render(f"Slot {i} - Novo Jogo",
                                             True, Cinza_texto if not selecionado else Azul_claro)
                self.tela.blit(txt, (rect_slot.left + 52, rect_slot.top + 22))
                sub = self.fonte_info.render("Nenhum save encontrado",
                                             True, Cinza_texto_escuro)
                self.tela.blit(sub, (rect_slot.left + 52, rect_slot.top + 62))
            else:
                txt = self.fonte_slot.render(f"Slot {i} - Continuar", True, Branco_texto)
                self.tela.blit(txt, (rect_slot.left + 52, rect_slot.top + 16))
                sala = self.fonte_info.render(f"Sala: {dados['checkpoint_sala']}", True, Cinza_texto)
                self.tela.blit(sala, (rect_slot.left + 52, rect_slot.top + 56))
                data = self.fonte_info.render(f"Salvo em: {dados['data_hora']}", True, Cinza_texto_escuro)
                self.tela.blit(data, (rect_slot.left + 52, rect_slot.top + 78))
                prompt_del = criar_prompt(
                    ["delete"], "apagar save", self.fonte_prompt, cor_prompt_delete,
                    espaco_teclas=ESPACO_TECLAS_PROMPT, espaco_texto=ESPACO_TEXTO_PROMPT,
                    escala=ESCALA_PROMPT_DISCRETO, padding=PADDING_PROMPT_DISCRETO,
                    cor_fundo=FUNDO_PROMPT_DISCRETO,
                )
                self.tela.blit(prompt_del, (rect_slot.right - prompt_del.get_width() - 18, rect_slot.top + 70))

        if self.estado == "confirmar_delete":
            desenhar_overlay(self.tela, 190)
            painel = pygame.Rect(Screen_widht // 2 - 260, Screen_height // 2 - 70, 520, 140)
            desenhar_painel(self.tela, painel, self._frame,
                            cor_borda=escurecer(Vermelho_ritual, 0.25))
            msg1 = self.fonte_slot.render("Apagar este save?", True, cor_alerta)
            self.tela.blit(msg1, (Screen_widht // 2 - msg1.get_width() // 2, painel.top + 26))
            desenhar_prompts(
                self.tela,
                [(["enter"], "confirmar"), (["esc"], "cancelar")],
                Screen_widht // 2, painel.top + 74,
                self.fonte_prompt_modal, Cinza_texto, espaco=34,
                escala=ESCALA_PROMPT_MODAL, padding=PADDING_PROMPT_MODAL,
                cor_fundo=FUNDO_PROMPT_MODAL,
                espaco_teclas=ESPACO_TECLAS_MODAL, espaco_texto=ESPACO_TEXTO_MODAL,
            )

    def _desenhar_opcoes(self):
        painel, abas, conteudo, preview, botoes_tam, sliders, btn_restaurar = self._layout_opcoes()
        desenhar_painel(self.tela, painel, self._frame, cor_borda=Azul_espectral)

        # abas
        for chave, rotulo in (("acessibilidade", "Acessibilidade"), ("audio", "Áudio")):
            rect = abas[chave]
            ativo = self.aba_opcoes == chave
            cor_borda = Azul_claro if ativo else escurecer(Azul_espectral, 0.45)
            desenhar_painel(self.tela, rect, self._frame, cor_borda=cor_borda)
            txt = self.fonte_opcao_pequena.render(rotulo, True, Branco_texto if ativo else Cinza_texto)
            self.tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        if self.aba_opcoes == "acessibilidade":
            titulo = self.fonte_opcao.render("Tamanho do texto", True, Branco_texto)
            self.tela.blit(titulo, (conteudo.left, conteudo.top + 8))
            atual = self.preferencias["acessibilidade"]["tamanho_texto"]
            for idx, chave, rect in botoes_tam:
                selecionado = atual == chave or self.item_opcao_selecionado == idx
                cor_borda = Azul_claro if selecionado else escurecer(Azul_espectral, 0.45)
                desenhar_painel(self.tela, rect, self._frame, cor_borda=cor_borda)
                rotulo = prefs.ROTULOS_TAMANHO_TEXTO[chave]
                cor = Branco_texto if atual == chave else Cinza_texto
                txt = self.fonte_opcao_pequena.render(rotulo, True, cor)
                self.tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

            # previa de texto ampliado
            desenhar_painel(self.tela, preview, self._frame, cor_borda=escurecer(Azul_espectral, 0.35))
            cab = self.fonte_opcao_pequena.render("Pr?via", True, Cinza_texto)
            self.tela.blit(cab, (preview.left + 12, preview.top + 8))
            exemplo1 = self.fonte_opcao.render("Exemplo de menu e HUD", True, Branco_texto)
            msg = "Mensagens, prompts e invent?rio usam este tamanho."
            palavras = msg.split()
            linhas, linha = [], ""
            max_w = preview.width - 24
            for palavra in palavras:
                teste = (linha + " " + palavra).strip()
                if self.fonte_info.size(teste)[0] <= max_w or not linha:
                    linha = teste
                else:
                    linhas.append(linha)
                    linha = palavra
            if linha:
                linhas.append(linha)
            y_txt = preview.top + 32
            old_clip = self.tela.get_clip()
            self.tela.set_clip(preview.inflate(-16, -16))
            self.tela.blit(exemplo1, (preview.left + 12, y_txt))
            y_txt += exemplo1.get_height() + 4
            for l in linhas[:3]:
                srf = self.fonte_info.render(l, True, Cinza_texto)
                if y_txt + srf.get_height() > preview.bottom - 8:
                    break
                self.tela.blit(srf, (preview.left + 12, y_txt))
                y_txt += srf.get_height() + 2
            self.tela.set_clip(old_clip)

        else:
            titulo = self.fonte_opcao.render("Volumes", True, Branco_texto)
            self.tela.blit(titulo, (conteudo.left, conteudo.top - 2))
            label_x = conteudo.left + 4
            label_w = max(120, int(conteudo.width * 0.28)) - 8
            valor_x = conteudo.right - 58
            for idx, chave, rotulo, track in sliders:
                valor = int(self.preferencias["audio"][chave])
                selecionado = idx == self.item_opcao_selecionado
                cor_txt = Branco_texto if selecionado else Cinza_texto
                row_h = max(42, self.fonte_opcao_pequena.get_height() + 24)
                row = pygame.Rect(conteudo.left, track.centery - row_h // 2, conteudo.width, row_h)
                if selecionado:
                    pygame.draw.rect(self.tela, escurecer(Azul_espectral, 0.35), row.inflate(-4, -6), 1, border_radius=4)
                txt = self.fonte_opcao_pequena.render(rotulo, True, cor_txt)
                label_y = track.centery - txt.get_height() // 2
                label_area = pygame.Rect(label_x, label_y, label_w, txt.get_height())
                old_clip = self.tela.get_clip()
                self.tela.set_clip(label_area)
                self.tela.blit(txt, (label_x, label_y))
                self.tela.set_clip(old_clip)
                pygame.draw.rect(self.tela, escurecer(Azul_espectral, 0.55), track, border_radius=4)
                preench = track.copy()
                preench.width = int(track.width * (valor / 100.0))
                if preench.width > 0:
                    pygame.draw.rect(self.tela, Azul_claro if selecionado else Azul_espectral, preench, border_radius=4)
                knob_x = track.left + preench.width
                pygame.draw.circle(self.tela, Branco_texto if selecionado else Cinza_texto, (knob_x, track.centery), 7)
                val_txt = self.fonte_opcao_pequena.render(f"{valor}%", True, cor_txt)
                self.tela.blit(val_txt, (valor_x, track.centery - val_txt.get_height() // 2))

        # botao restaurar padrões
        selecionado_rest = (self.item_opcao_selecionado == (len(prefs.TAMANHOS_TEXTO) if self.aba_opcoes == "acessibilidade" else len(SLIDERS_AUDIO)))
        cor_borda = Azul_claro if selecionado_rest else escurecer(Azul_espectral, 0.45)
        desenhar_painel(self.tela, btn_restaurar, self._frame, cor_borda=cor_borda)
        txt = self.fonte_opcao_pequena.render("Restaurar padrões", True, Branco_texto if selecionado_rest else Cinza_texto)
        self.tela.blit(txt, (btn_restaurar.centerx - txt.get_width() // 2, btn_restaurar.centery - txt.get_height() // 2))

    def _desenhar_rodape(self):
        if self.tela_menu == "principal":
            prompts = [(["seta_cima", "seta_baixo"], "navegar"), (["enter"], "selecionar"), (["esc"], "sair")]
        elif self.tela_menu == "slots":
            if self.estado == "confirmar_delete":
                prompts = [(["enter"], "confirmar"), (["esc"], "cancelar")]
            else:
                prompts = [(["seta_cima", "seta_baixo"], "navegar"), (["enter"], "selecionar"), (["esc"], "voltar")]
        else:
            if self.aba_opcoes == "audio":
                prompts = [(["seta_cima", "seta_baixo"], "item"), (["seta_esquerda", "seta_direita"], "ajustar"), (["tab"], "aba"), (["enter"], "aplicar"), (["esc"], "voltar")]
            else:
                prompts = [(["seta_cima", "seta_baixo"], "item"), (["seta_esquerda", "seta_direita"], "tamanho"), (["tab"], "aba"), (["enter"], "aplicar"), (["esc"], "voltar")]
        desenhar_prompts(
            self.tela, prompts, Screen_widht // 2, Screen_height - 50,
            self.fonte_prompt, Cinza_texto_escuro, espaco=22,
            escala=ESCALA_PROMPT_DISCRETO, padding=PADDING_PROMPT_DISCRETO,
            cor_fundo=FUNDO_PROMPT_DISCRETO,
            espaco_teclas=ESPACO_TECLAS_PROMPT, espaco_texto=ESPACO_TEXTO_PROMPT,
        )
