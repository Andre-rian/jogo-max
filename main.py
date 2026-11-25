import os
import sys
from pathlib import Path


def _usar_venv_do_projeto():
    if os.environ.get("PROFANE_VENV_ATIVO") == "1":
        return
    raiz = Path(__file__).resolve().parent
    pasta_venv = raiz / ".venv"
    pasta_bin = Path("Scripts") if os.name == "nt" else Path("bin")
    executavel = "python.exe" if os.name == "nt" else "python"
    python_venv = pasta_venv / pasta_bin / executavel
    if not python_venv.exists():
        return
    if Path(sys.prefix).resolve() == pasta_venv.resolve():
        return
    os.environ["PROFANE_VENV_ATIVO"] = "1"
    os.execv(str(python_venv), [str(python_venv), str(Path(__file__).resolve()), *sys.argv[1:]])


_usar_venv_do_projeto()

if sys.version_info < (3, 11):
    sys.exit("Profane Echo requer Python 3.11 ou superior (recomendado 3.14).")

import pygame
import atexit
import logging
import argparse

from logging_config import configurar_logging

configurar_logging()

log = logging.getLogger("main")
log.debug("Logging inicializado")


from settings import *
from core.audio import audio
from core.menu import MenuInicial
from core.game_scene import Gamescene
from save_manager import Savemaneger
from core import preferencias as prefs
from ui.estilo import definir_escala_texto



class Jogo:
    def __init__(self, modo_teste_combate=False, teste_celas=False):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.preferencias = prefs.carregar()
        audio.inicializar()
        audio.aplicar_preferencias_audio(prefs.volumes_normalizados(self.preferencias))
        definir_escala_texto(prefs.escala_texto(self.preferencias))
        self.Criar_janela()
        self.clock = pygame.time.Clock()
        self.save_manager = Savemaneger()
        atexit.register(self.save_manager.fechar)
        self.estado = "menu" #menu do jogo
        self.slot_atual = None
        self.scene = None
        self.modo_teste_combate = modo_teste_combate
        self.teste_celas = teste_celas

        self.menu = MenuInicial(self.tela, self.save_manager, preferencias=self.preferencias)
        self.menu.callback_iniciar = self._iniciar_jogo
        self.menu.callback_sair = self._sair
        try:
            audio.play_music("menu", origem="main", fade_ms=2500, fade_out_ms=0, motivo="menu_inicial")
        except TypeError:
            audio.play_music("menu")

        if self.modo_teste_combate or self.teste_celas:
            self._iniciar_jogo(None, None)
        

    def _atualizar_visibilidade_mouse(self):
        if self.estado == "menu":
            pygame.mouse.set_visible(True)
            return

        if self.estado == "jogo" and self.scene:
            menu_aberto = (
                self.scene.pausado or self.scene.inventario.aberto or self.scene.menu_fogueira.aberto
                or self.scene.fim_beta is not None
            )
            pygame.mouse.set_visible(menu_aberto)
        else:
            pygame.mouse.set_visible(True)

    def _iniciar_jogo(self, slot, dados_save):
        self.slot_atual = slot
        if self.teste_celas:
            self.slot_atual = None
            dados_save = None
            self.scene = Gamescene(self.tela, sala_teste="bloco_celas_esquecidas")
        else:
            self.scene = Gamescene(self.tela, modo_teste_combate=self.modo_teste_combate)
        self.scene._menu_callback = self._voltar_menu

        if self.slot_atual is not None:
            def _fazer_save():
                if self.scene:
                    self.scene.salvar(self.save_manager, self.slot_atual)
            self.scene._save_callback = _fazer_save


        if dados_save is not None:
            #carrega o save no gameScene
            self.scene.carregar_save(dados_save)

        self.estado = "jogo"


    def _voltar_menu(self):
        self.teste_celas = False
        self.modo_teste_combate = False
        audio.stop_all_sfx()
        try:
            audio.play_music("menu", origem="main", fade_ms=2000, fade_out_ms=800, motivo="voltar_menu")
        except TypeError:
            audio.play_music("menu")
        self.estado = "menu"
        self.scene = None
        self.slot_atual = None
        self.menu.tela_menu = "principal"
        self.menu.estado = "selecionar"
        self.menu.slot_selecionado = 1



    def Criar_janela(self):
        flags = pygame.SCALED
        if Telacheia_normal:
            flags |= pygame.FULLSCREEN
        self.tela = pygame.display.set_mode(
            (Screen_widht, Screen_height), flags
        )
        pygame.display.set_caption(Titulo)

    def _Mudar_telacheia(self):
        pygame.display.toggle_fullscreen()

    def _salvar_emergencia(self):
        #tenta preservar o progresso antes de fechar por causa de erro
        if self.scene and self.slot_atual is not None:
            try:
                self.scene.salvar(self.save_manager, self.slot_atual)
                log.info("Save de emergǦncia gravado antes do tǸrmino anormal")
            except Exception as e:
                log.warning(f"Nǜo foi poss��vel salvar antes do tǸrmino (slot {self.slot_atual}): {e}")

    def _sair(self):
        try:
            prefs.salvar(getattr(self.menu, "preferencias", self.preferencias))
        except Exception:
            pass
        self.save_manager.fechar()
        audio.stop_all_sfx()
        audio.stop_music()
        pygame.quit()
        sys.exit()

    def rodar(self):
        while True:
            try:
                eventos = pygame.event.get()
            except Exception:
                log.exception("Falha ao ler eventos do pygame")
                self._sair()
            atualizar_audio = getattr(audio, "atualizar", None)
            if atualizar_audio is not None:
                atualizar_audio()

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self._sair()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_F11:
                        self._Mudar_telacheia()
                    if evento.key == pygame.K_ESCAPE and self.estado == "jogo" and self.scene:
                        if not (self.scene.inventario.aberto or self.scene.menu_fogueira.aberto):
                            self.scene.alternar_pausa()

            try:
                self._atualizar_visibilidade_mouse()

                self.tela.fill(Preto)

                if self.estado == "menu":
                    self.menu.atualizar(eventos)
                    self.menu.desenhar()

                elif self.estado == "jogo" and self.scene:

                    self.scene.atualizar(eventos)
                    if self.scene:
                        self.scene.desenhar()

                pygame.display.flip()
                self.clock.tick(FPS)

            except Exception:
                log.exception("Exce��ǜo nǜo tratada no loop principal")
                self._salvar_emergencia()
                self._sair()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profane Echo")
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--teste-combate", action="store_true",
                        help="inicia direto na arena de teste de combate")
    modos.add_argument("--teste-celas", action="store_true",
                       help="abre o Bloco das Celas em sessão temporária, sem saves")
    args = parser.parse_args()
    Jogo(modo_teste_combate=args.teste_combate, teste_celas=args.teste_celas).rodar()
