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

                    fogueiras_ativas.add((self.col, self.linha))

                    player.defenir_checkpoint(sala_atual, x=self.rect.centerx, y=self.rect.centery)

                    player.cooldown_interacao = 60

                    hud.limpar_prompt()

                    if self._callback_abrir_menu:

                        self._callback_abrir_menu()

            else:

                hud.mostrar_prompt("pressione E para interagir")

                if pode_interagir and teclas[pygame.K_e]:

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





    def _garantir_particulas(self):
        if not hasattr(self, '_particulas'):
            self._particulas = []
        if not self._particulas:
            base_x = self.rect.centerx
            base_y = self.rect.bottom - 12
            for i in range(8):
                self._particulas.append({
                    'x': base_x + (i % 4 - 1.5) * 2,
                    'y': base_y - i * 3,
                    'vx': 0.0,
                    'vy': -0.25 - (i % 3) * 0.05,
                    'vida': 30 + i * 7,
                    'vida_max': 40 + i * 5,
                    'cor': (150, 200, 255) if i % 2 == 0 else (175, 120, 255),
                })

    def _atualizar_particulas(self):
        self._garantir_particulas()
        import random, math
        rnd = random.Random((self.col * 131 + self.linha * 17 + self._frame // 6) & 0xFFFFFFFF)
        for p in self._particulas:
            p['x'] += p['vx'] + math.sin((self._frame + p['vida']) * 0.08) * 0.08
            p['y'] += p['vy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                p['x'] = self.rect.centerx + rnd.uniform(-4, 4)
                p['y'] = self.rect.bottom - 14 + rnd.uniform(-2, 2)
                p['vy'] = rnd.uniform(-0.45, -0.20)
                p['vida_max'] = rnd.randint(28, 52)
                p['vida'] = p['vida_max']
                p['cor'] = (150, 210, 255) if rnd.random() < 0.5 else (180, 130, 255)

    @classmethod
    def _obter_mascara_luz(cls, raio):
        cache = getattr(cls, '_cache_luz', None)
        if cache is None:
            cache = {}
            cls._cache_luz = cache
        surf = cache.get(raio)
        if surf is not None:
            return surf
        surf = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        cx = cy = raio
        max_d2 = raio * raio
        # Máscara radial suave (sem anéis/círculo sólido). Pequena e delicada.
        for y in range(raio * 2):
            dy = y - cy
            for x in range(raio * 2):
                dx = x - cx
                d2 = dx * dx + dy * dy
                if d2 > max_d2:
                    continue
                t = 1.0 - (d2 / max_d2)
                # curva suave: centro leve, borda some naturalmente
                a = int(70 * (t * t))
                if a <= 0:
                    continue
                b = 255
                g = 170
                r = 120
                # leve nuance violeta nas bordas
                if t < 0.45:
                    r = 150
                    b = 235
                surf.set_at((x, y), (r, g, b, a))
        cache[raio] = surf
        return surf

    def _desenhar_luz_ambiente(self, tela, camera, sr, pulso):
        # Iluminação 2D gradual localizada, sem contorno perceptível.
        if not self.ativa:
            return
        import math
        raio = 26  # pequena, sensação de solidão
        intensidade = 0.22 + 0.05 * (0.5 + 0.5 * math.sin(self._frame * 0.07))
        base = self._obter_mascara_luz(raio)
        luz = base.copy()
        luz.fill((255, 255, 255, max(0, min(255, int(255 * intensidade)))), special_flags=pygame.BLEND_RGBA_MULT)
        # leve deslocamento vertical acompanha chama; sem forma geométrica visível
        tela.blit(luz, (sr.centerx - raio, sr.bottom - raio - 10 + pulso), special_flags=pygame.BLEND_RGBA_ADD)

    def desenhar(self, tela, camera):
        sr = camera.aplicar(self.rect)
        import math

        pygame.draw.rect(tela, (70, 72, 82), (sr.x + 4, sr.bottom - 10, sr.width - 8, 8), border_radius=2)
        pygame.draw.rect(tela, (95, 96, 110), (sr.x + 6, sr.bottom - 9, sr.width - 12, 2), border_radius=1)

        if not self.ativa:
            pygame.draw.ellipse(tela, (60, 55, 75), (sr.centerx - 6, sr.bottom - 16, 12, 8))
            pygame.draw.ellipse(tela, (95, 85, 130), (sr.centerx - 3, sr.bottom - 14, 6, 4))
            if DEBUG:
                pygame.draw.rect(tela, (200, 100, 30), sr, 1)
            return

        pulso = int(math.sin(self._frame * 0.12) * 2)
        altura_extra = int(math.sin(self._frame * 0.07) * 1)
        self._atualizar_particulas()
        self._desenhar_luz_ambiente(tela, camera, sr, pulso)
        # brilho discreto local na chama (gradiente suave, sem círculo visível)
        glow_r = 8
        glow = self._obter_mascara_luz(glow_r).copy()
        glow.fill((255, 255, 255, 46), special_flags=pygame.BLEND_RGBA_MULT)
        tela.blit(glow, (sr.centerx - glow_r, sr.centery - glow_r + 2 + pulso), special_flags=pygame.BLEND_RGBA_ADD)

        topo = sr.top + 7 + pulso - altura_extra
        base_y = sr.bottom - 12
        pygame.draw.polygon(tela, (120, 80, 210), [(sr.centerx, topo), (sr.centerx - 9, base_y), (sr.centerx + 9, base_y)])
        pygame.draw.polygon(tela, (90, 140, 255), [(sr.centerx, topo + 3), (sr.centerx - 6, base_y), (sr.centerx + 6, base_y)])
        pygame.draw.polygon(tela, (170, 225, 255), [(sr.centerx, topo + 7), (sr.centerx - 3, base_y), (sr.centerx + 3, base_y)])
        pygame.draw.ellipse(tela, (235, 245, 255), (sr.centerx - 2, sr.centery + 2 + pulso, 4, 4))

        for p in self._particulas:
            vida_t = max(0.0, min(1.0, p['vida'] / max(1, p['vida_max'])))
            a = int(140 * vida_t)
            px = int(p['x'])
            py = int(p['y'] + pulso * 0.2)
            pr = camera.aplicar(pygame.Rect(px, py, 2, 2))
            ps = pygame.Surface((2, 2), pygame.SRCALPHA)
            ps.fill((*p['cor'], a))
            tela.blit(ps, (pr.x, pr.y))

        if DEBUG:
            pygame.draw.rect(tela, (120, 100, 220), sr, 1)
