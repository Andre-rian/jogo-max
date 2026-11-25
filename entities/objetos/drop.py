import pygame

import logging

from settings import Tile_size

from core.audio import audio

from entities.objetos.item import get_item
from ui.sprites_itens import obter_sprite_item, obter_fallback



logger = logging.getLogger(__name__)



class Drop:



    Raio = 12

    Alcance_coleta = 50





    def __init__(self, x, y, id_item):

        self.id_item = id_item

        self.item = get_item(id_item)

        self.ativo = True



        logger.debug(f"Drop criado: id_item={id_item}, item={self.item}")



        #rect para centralizar o ponto do drop

        self.rect = pygame.Rect(0, 0, self.Raio * 2, self.Raio * 2)

        self.rect.centerx = x

        self.rect.centery = y



        #area de interaçao com folga - pega quando o player passa por cima/encostado

        self.interacao = self.rect.inflate(Tile_size // 2, Tile_size // 2)



        self._timer = 0



        self.chave_fixa = None

        self.callback_coletado = None

        self.tecla_prompt = "e"
        self.frasco = False
        sprite = obter_sprite_item(id_item)
        if sprite is None:
            sprite = obter_fallback()
        self._sprite_mundo = pygame.transform.scale(sprite, (32, 32)) if sprite is not None else None
        if self._sprite_mundo is not None:
            # O apoio considera os pixels visíveis, sem a margem transparente do ícone.
            limites = self._sprite_mundo.get_bounding_rect()
            if limites.width and limites.height:
                self._sprite_mundo = self._sprite_mundo.subsurface(limites).copy()

    def apoiar(self, suportes):
        """Apoia o pickup na superfície abaixo da posição informada, sem física nova."""
        pisos = [r.top for r in suportes
                 if r.left <= self.rect.centerx < r.right and r.top >= self.rect.centery]
        if pisos:
            self.rect.bottom = min(pisos)
            self.interacao = self.rect.inflate(Tile_size // 2, Tile_size // 2)





    def disponivel_para_prompt(self, player):

        return (self.ativo and player.rect.colliderect(self.interacao)

                and getattr(player, "cooldown_interacao", 0) <= 0
                and (not self.frasco or player.pocao.cargas_max < 3))



    def prompt_anchor_mundo(self):

        return self.rect.centerx, self.rect.top - 8



    def atualizar(self, player, teclas, hud, selecionado=True):

        if not self.ativo:

            return



        self._timer += 1

        colide = player.rect.colliderect(self.interacao)

        quantidade = player.inventario["materiais"].get(str(self.item.id),

                                                        player.inventario["itens"].get(str(self.item.id), 1))

        if selecionado and colide:

            hud.mostrar_prompt(f"E -- Pegar {self.item.nome}")

            if teclas[pygame.K_e] and getattr(player, "cooldown_interacao", 0) <= 0:

                if self.frasco:
                    if not player.pocao.obter_frasco():
                        return
                else:
                    player.adicionar_ao_inventario(self.item)

                audio.play_sfx("item_pickup")

                player.iniciar_pegar_item()

                self.ativo = False

                player.cooldown_interacao = 30

                if self.callback_coletado:

                    self.callback_coletado(self.chave_fixa)

                hud.limpar_prompt()

                hud.mostrar_item_coletado(self.item, quantidade)

        elif selecionado:

            hud.limpar_prompt()

    def desenhar(self, tela, camera):

        if not self.ativo:

            return



        sr = camera.aplicar(self.rect)



        pygame.draw.ellipse(tela, (15, 17, 26), (sr.centerx - 10, sr.bottom - 2, 20, 3))
        if self._sprite_mundo is not None:
            destino = self._sprite_mundo.get_rect(midbottom=(sr.centerx, sr.bottom))
            tela.blit(self._sprite_mundo, destino)
