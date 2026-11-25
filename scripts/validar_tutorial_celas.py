"""Percursos reais e capturas da I.3; nao inicia main, logging ou saves."""
from pathlib import Path
import json
import os
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from core.game_scene import Gamescene
from scripts.validar_bloco_celas import Percurso
from settings import Screen_widht, Screen_height

SAIDA = RAIZ / "docs/mapas/previews/i3"


class PercursoTutorial(Percurso):
    def __init__(self, scene):
        super().__init__(scene)
        self.capturados = {}

    def capturar(self, nome):
        if nome in self.capturados:
            return
        t = self.scene.tutorial_contextual
        self.scene.desenhar()
        pygame.image.save(self.scene.tela, str(SAIDA / (nome + ".png")))
        self.capturados[nome] = {"player": list(self.scene.player.rect),
                                "camera": list(self.scene.camera.offset), "zoom": self.scene.camera.zoom,
                                "dica": t.ativa, "teclas": list(t.teclas_ativas), "alpha": t.opacidade,
                                "estados": {k: t.prompts[k].estado for k in t.teclas_ativas},
                                "concluidas": sorted(t.concluidas)}

    def passo(self, *keys):
        super().passo(*keys)
        t = self.scene.tutorial_contextual
        if t.opacidade < 224:
            return
        if t.ativa == "movimento" and "movimento" not in t.concluidas:
            if not keys:
                self.capturar("01_ad_spawn")
            elif pygame.K_d in keys:
                self.capturar("02_d_pressionado")
            elif pygame.K_a in keys:
                self.capturar("03_a_pressionado")
        if t.ativa == "escada" and "escada" not in t.concluidas:
            if t.teclas_ativas == ("s",):
                self.capturar("04_s_topo_escada")
            if t.teclas_ativas == ("w",):
                self.capturar("06_w_base_escada")
            if pygame.K_s in keys:
                self.capturar("05_s_descendo")
            if pygame.K_w in keys:
                self.capturar("07_w_subindo")
        if t.ativa == "pulo" and "pulo" not in t.concluidas:
            self.capturar("09_espaco_pressionado" if pygame.K_SPACE in keys else "08_espaco_degrau")


def main():
    os.chdir(RAIZ)
    SAIDA.mkdir(parents=True, exist_ok=True)
    pygame.init()
    tela = pygame.display.set_mode((Screen_widht, Screen_height))
    cena = Gamescene(tela, sala_teste="bloco_celas_esquecidas")
    p = PercursoTutorial(cena)
    p.repousar(12)
    p.passo(pygame.K_d)
    p.passo(pygame.K_a)
    resultado = p.executar()
    p.capturar("10_retorno_sem_dicas")
    assert cena.tutorial_contextual.concluidas == {"movimento", "escada", "pulo"}
    # Segunda sessao: deixa cair sem S, aprende subida na base da mesma escada.
    outra = Gamescene(tela, sala_teste="bloco_celas_esquecidas")
    q = PercursoTutorial(outra)
    q.capturados = p.capturados
    q.repousar(12)
    q.andar(21 * 32 + 16)
    q.repousar(100)
    q.escalar(9 * 32)
    obrigatorias = ("01_ad_spawn", "02_d_pressionado", "03_a_pressionado", "04_s_topo_escada",
                   "05_s_descendo", "06_w_base_escada", "07_w_subindo", "08_espaco_degrau", "09_espaco_pressionado")
    assert all(n in q.capturados for n in obrigatorias), q.capturados.keys()
    (SAIDA / "capturas.json").write_text(json.dumps(q.capturados, indent=2), encoding="utf-8")
    (SAIDA / "percurso.json").write_text(json.dumps(resultado, indent=2), encoding="utf-8")
    pygame.quit()
    print(json.dumps({"capturas": len(q.capturados), "concluidas": sorted(cena.tutorial_contextual.concluidas),
                      "frames": resultado["frames"]}))


if __name__ == "__main__":
    main()
