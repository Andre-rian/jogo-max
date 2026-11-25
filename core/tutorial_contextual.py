"""Dicas de sessao: observam o jogador, nunca comandam a fisica ou a progressao."""
import pygame

from ui.prompts_teclas import PromptTeclaMundo, obter_tecla_mundo


TECLAS = {"a": pygame.K_a, "d": pygame.K_d, "w": pygame.K_w,
          "s": pygame.K_s, "espaco": pygame.K_SPACE, "k": pygame.K_k}


class TutorialContextual:
    def __init__(self, mapa, player, concluidas=()):
        self.concluidas = set(concluidas)
        self.prompts = {nome: PromptTeclaMundo(nome) for nome in TECLAS}
        # Recursos e geometria preparados uma vez por entrada de sala.
        self.larguras = {}
        for nome in TECLAS:
            self.larguras[nome] = obter_tecla_mundo(nome).get_width()
            obter_tecla_mundo(nome, "pressionado")
        self.escadas = self._agrupar_escadas(mapa.rects_escada)
        ocupados = {(r.x, r.y) for r in mapa.rects_solidos}
        self.degraus = tuple(r.copy() for r in mapa.rects_solidos
                            if (r.x, r.y - r.height) not in ocupados)
        self._anterior = player.rect.copy()
        self._no_chao = player.no_chao
        self._andou = 0
        self._escalou = 0
        self._salto = None
        self._solicitada = None
        self.ativa = None
        self.teclas_ativas = ()
        self.opacidade = 0

    @staticmethod
    def _agrupar_escadas(celulas):
        corredores = []
        for rect in sorted(celulas, key=lambda r: (r.x, r.y)):
            if corredores and corredores[-1].x == rect.x and corredores[-1].bottom == rect.top:
                corredores[-1].height += rect.height
            else:
                corredores.append(rect.copy())
        return tuple(corredores)

    def ocultar(self, player):
        """Supressao imediata, sem perder conclusoes nem acumular deslocamento oculto."""
        self.ativa = None
        self.teclas_ativas = ()
        self.opacidade = 0
        self._anterior = player.rect.copy()
        self._no_chao = player.no_chao
        self._salto = None
        self._escalou = 0

    def solicitar(self, identificador, teclas):
        """Ponto de extensao: o Arsenal podera solicitar ('ataque', ('k',)).

        O chamador decide o contexto e chama concluir() ao observar a acao real.
        Nenhuma dica de ataque e solicitada automaticamente aqui.
        """
        teclas = tuple(teclas)
        if not teclas or any(t not in TECLAS for t in teclas):
            raise ValueError("Grupo de teclas desconhecido")
        self._solicitada = (identificador, teclas)

    def cancelar_solicitacao(self):
        self._solicitada = None

    def concluir(self, identificador):
        self.concluidas.add(identificador)
        if self._solicitada and self._solicitada[0] == identificador:
            self._solicitada = None

    def _escada_proxima(self, rect):
        candidatas = [e for e in self.escadas if e.inflate(96, 0).colliderect(rect)]
        return min(candidatas, key=lambda e: abs(e.centerx - rect.centerx), default=None)

    def _degrau_adiante(self, rect, direcao):
        candidatos = []
        for d in self.degraus:
            distancia = d.left - rect.right if direcao > 0 else rect.left - d.right
            if 0 <= distancia <= 80 and 8 <= rect.bottom - d.top <= 64:
                candidatos.append((distancia, d))
        return min(candidatos, key=lambda item: item[0])[1] if candidatos else None

    def atualizar(self, player, teclas, *, suprimido=False, interacao=False):
        if suprimido or interacao or not player.vivo:
            self.ocultar(player)
            return
        anterior = self._anterior
        dx, dy = player.rect.x - anterior.x, player.rect.y - anterior.y
        direcao = 1 if teclas[pygame.K_d] else -1 if teclas[pygame.K_a] else (1 if player.olhando_dir else -1)
        if (teclas[pygame.K_a] or teclas[pygame.K_d]) and dx * direcao > 0 and self._no_chao:
            if not player.em_dahs and not player.recebendo_knockback:
                self._andou += abs(dx)
        if self._andou >= 64:
            self.concluir("movimento")

        escada = self._escada_proxima(player.rect)
        if escada and player._escalando and (teclas[pygame.K_w] or teclas[pygame.K_s]):
            self._escalou += abs(dy)
            if self._escalou >= 24:
                self.concluir("escada")
        elif not escada:
            self._escalou = 0

        # O frame anterior ainda estava apoiado: distingue salto de queda/drop.
        obstaculo = self._degrau_adiante(anterior, direcao)
        if ("pulo" not in self.concluidas and self._no_chao and obstaculo is not None
                and teclas[pygame.K_SPACE] and not player.no_chao and player.vel.y < 0):
            self._salto = (obstaculo, direcao)
        if self._salto and player.no_chao:
            alvo, sentido = self._salto
            passou = player.rect.centerx > alvo.left + 8 if sentido > 0 else player.rect.centerx < alvo.right - 8
            if passou and player.rect.bottom <= alvo.top + 2:
                self.concluir("pulo")
            self._salto = None

        desejada = None
        if self._solicitada and self._solicitada[0] not in self.concluidas:
            desejada = self._solicitada
        elif escada and "escada" not in self.concluidas:
            if player.rect.centery <= escada.top + player.rect.height:
                grupo = ("s",)
            elif player.rect.bottom >= escada.bottom - 32:
                grupo = ("w",)
            else:
                grupo = ("w", "s")
            desejada = ("escada", grupo)
        elif "pulo" not in self.concluidas and (self._salto or (player.no_chao and self._degrau_adiante(player.rect, direcao))):
            desejada = ("pulo", ("espaco",))
        elif "movimento" not in self.concluidas:
            desejada = ("movimento", ("a", "d"))

        if desejada:
            if desejada != (self.ativa, self.teclas_ativas):
                self.ativa, self.teclas_ativas = desejada
                self.opacidade = 0
            self.opacidade = min(255, self.opacidade + 32)
        else:
            self.opacidade = max(0, self.opacidade - 22)
            if not self.opacidade:
                self.ativa, self.teclas_ativas = None, ()
        for nome in self.teclas_ativas:
            self.prompts[nome].atualizar(bool(teclas[TECLAS[nome]]), entrada_real=True)
        self._anterior = player.rect.copy()
        self._no_chao = player.no_chao

    def desenhar(self, vista, camera, player):
        if not self.teclas_ativas or not self.opacidade:
            return False
        largura = sum(self.larguras[t] for t in self.teclas_ativas) + 3 * (len(self.teclas_ativas) - 1)
        x = player.rect.centerx - largura / 2
        desenhou = False
        for nome in self.teclas_ativas:
            w = self.larguras[nome]
            desenhou |= self.prompts[nome].desenhar(vista, camera, x + w / 2,
                                                  player.rect.top - 4, opacidade=self.opacidade)
            x += w + 3
        return desenhou
