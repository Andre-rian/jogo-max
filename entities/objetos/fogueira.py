import pygame

import logging

logger = logging.getLogger("fogueira")

from core.audio import audio

from settings import Tile_size, DEBUG



class Fogueira:



    def __init__(self, x, y, col, linha, callback_descanso=None):



        self.col = col

        self.linha = linha



        self.rect = pygame.Rect(x, y, Tile_size, Tile_size)



        #area de interaçao com folga de meio tile - aceita o player encostado

        self.interacao = self.rect.inflate(Tile_size // 2, Tile_size // 2)





        self._callback_descanso = callback_descanso



        self._callback_abrir_menu = None





        self.ativa = False

        self._frame = 0  #contador geral para a animação





        self._timer_descanso = 0

        self.tecla_prompt = "e"





    def disponivel_para_prompt(self, player):

        return (player.rect.colliderect(self.interacao)

                and getattr(player, "cooldown_interacao", 0) <= 0)



    def prompt_anchor_mundo(self):

        return self.rect.centerx, self.rect.top - 10



    def atualizar(self, player, teclas, hud, sala_atual, fogueiras_ativas, selecionado=True):



        self._frame += 1



        if self._timer_descanso > 0:

            self._timer_descanso -= 1

            hud.mostra_mensagem("Descansando...")

            return



        colide = player.rect.colliderect(self.interacao)

        pode_interagir = (selecionado and colide

                          and getattr(player, "cooldown_interacao", 0) <= 0)



        if selecionado and colide:

            if not self.ativa:

                hud.mostrar_prompt("pressione E para descansar")

                if pode_interagir and teclas[pygame.K_e]:

                    logger.debug(f"E pressionado na fogueira id={id(self)}, callback={self._callback_abrir_menu}")

                    self.ativa = True

                    audio.play_sfx("campfire_light")

                    fogueiras_ativas.add((sala_atual, self.col, self.linha))

                    player.defenir_checkpoint(sala_atual, x=player.rect.x, y=player.rect.y)

                    player.cooldown_interacao = 60

                    hud.limpar_prompt()

                    if self._callback_abrir_menu:

                        self._callback_abrir_menu()

            else:

                hud.mostrar_prompt("pressione E para interagir")

                if pode_interagir and teclas[pygame.K_e]:

                    player.defenir_checkpoint(sala_atual, x=player.rect.x, y=player.rect.y)

                    logger.debug(f"E pressionado na fogueira id={id(self)}, callback={self._callback_abrir_menu}")

                    player.cooldown_interacao = 60

                    hud.limpar_prompt()

                    if self._callback_abrir_menu:

                        self._callback_abrir_menu()

        elif selecionado:

            hud.limpar_prompt()

    def _ativar(self, player, hud):

        self.ativa = True



        #passa a posição da fogueira para o player, para que ele respwane na fogueira



        player.defenir_checkpoint(

            player.checkpoint_sala,

            x=self.rect.x,

            y=self.rect.y

        )

        hud.mostra_mensagem("Ponto de descanso ativo")





    @classmethod
    def _obter_luz(cls, largura, altura, alfa):
        """Textura pequena com queda suave de alpha; calculada uma vez por tamanho."""
        if not hasattr(cls, "_cache_luz_suave"):
            cls._cache_luz_suave = {}
        chave = (largura, altura, alfa)
        if chave not in cls._cache_luz_suave:
            luz = pygame.Surface((largura, altura), pygame.SRCALPHA)
            for y in range(altura):
                dy = (2 * y / (altura - 1)) - 1
                for x in range(largura):
                    dx = (2 * x / (largura - 1)) - 1
                    queda = max(0.0, 1.0 - dx * dx - dy * dy)
                    luz.set_at((x, y), (95, 155, 250, round(alfa * queda ** 3)))
            cls._cache_luz_suave[chave] = luz
        return cls._cache_luz_suave[chave]

    def desenhar(self, tela, camera):
        import math

        sr = camera.aplicar(self.rect)
        # Ciclo de tres segundos a 60 Hz, sem alterar o ritmo de gameplay.
        pulso = math.sin(self._frame * math.tau / 180)
        base_y = sr.bottom - 12
        altura = (30 + round(2 * pulso)) if self.ativa else (12 + round(pulso))
        cx = sr.centerx
        topo = base_y - altura
        oscilacao = round(2 * math.sin(self._frame * math.tau / 120))

        luz = self._obter_luz(44, 60, 26) if self.ativa else self._obter_luz(26, 32, 14)
        luz.set_alpha(round(225 + 20 * pulso))
        # Blit alpha normal: a luz nunca soma RGB ignorando o alpha da textura.
        tela.blit(luz, luz.get_rect(center=(cx, base_y - altura // 2)))
        reflexo = self._obter_luz(40, 6, 34) if self.ativa else self._obter_luz(24, 4, 16)
        reflexo.set_alpha(round(215 + 20 * pulso))
        tela.blit(reflexo, reflexo.get_rect(center=(cx, sr.bottom + 1)))

        pygame.draw.rect(tela, (70, 72, 82), (sr.x + 4, sr.bottom - 10, sr.width - 8, 8), border_radius=2)
        pygame.draw.rect(tela, (95, 105, 135) if self.ativa else (80, 87, 106),
                         (sr.x + 6, sr.bottom - 9, sr.width - 12, 2), border_radius=1)

        largura = 8 if self.ativa else 5
        externa = (119, 91, 218) if self.ativa else (86, 74, 153)
        interna = (113, 174, 255) if self.ativa else (90, 132, 214)
        nucleo = (218, 244, 255) if self.ativa else (150, 191, 239)
        pygame.draw.polygon(tela, externa, [
            (cx + oscilacao, topo), (cx + largura - 2, topo + altura // 2),
            (cx + largura, base_y - 7), (cx + largura - 2, base_y),
            (cx - largura + 2, base_y), (cx - largura, base_y - 6),
            (cx - 3, topo + altura // 2),
        ])
        pygame.draw.polygon(tela, interna, [
            (cx + oscilacao, topo + altura // 5), (cx + largura - 3, base_y - 5),
            (cx + 3, base_y), (cx - 3, base_y), (cx - largura + 3, base_y - 5),
        ])
        pygame.draw.polygon(tela, nucleo, [
            (cx, topo + altura // 2), (cx + 2, base_y - 2),
            (cx, base_y), (cx - 2, base_y - 2),
        ])

        if not hasattr(self, "_sprite_particula"):
            self._sprite_particula = pygame.Surface((2, 2), pygame.SRCALPHA)
        # Trajetorias deterministicas: desenhar duas vezes nao avanca particulas.
        for i in range(7 if self.ativa else 2):
            fase = ((self._frame + i * 17) % 110) / 110
            px = cx + round(math.sin(fase * math.tau + i) * (4 if self.ativa else 2))
            py = base_y - 3 - round(fase * (45 if self.ativa else 20))
            alfa = round((140 if self.ativa else 70) * math.sin(math.pi * fase))
            cor = (160, 204, 255) if i % 2 == 0 else (180, 142, 250)
            self._sprite_particula.fill((*cor, alfa))
            tela.blit(self._sprite_particula, (px, py))

        if DEBUG:
            pygame.draw.rect(tela, (120, 100, 220), sr, 1)
