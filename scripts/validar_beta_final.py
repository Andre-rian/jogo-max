"""Percurso de integração com teclado simulado, física/IA/combate reais e SQLite temporário.

python scripts/validar_beta_final.py --capturas
Não importa main, não abre jogo.log e não acessa saves pessoais.
"""
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import argparse
import json
import os
import random
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from core.game_scene import Gamescene
from scripts.validar_bloco_celas import Percurso
from save_manager import Savemaneger
from world.niveis import SALAS_BETA
from world.validacao_tiled import validar_mapa_tmx, validar_conexoes

SAIDA = RAIZ / "docs/beta/polimento/percurso"


class PartidaBeta:
    def __init__(self, tela, capturas=False):
        random.seed(25)
        self.scene = Gamescene(tela)
        self.capturas = capturas
        self.frames = 0
        self.marcos = []
        self.inimigos_derrotados = []
        self.combates = []

    def passo(self, *keys, eventos=()):
        with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {k: True for k in keys})):
            self.scene.atualizar(list(eventos))
        self.frames += 1
        # A notificação legada avança no desenho, não no update.
        self.scene.hud.notificacao_item.desenhar(self.scene.tela)
        p = self.scene.player
        assert p.vivo, ("Morte durante percurso", self.scene.sala_atual, p.rect, self.frames)
        assert p.rect.collidelist(self.scene.mapa.rects_solidos) == -1, ("Colisão", p.rect)

    def repousar(self, n=60):
        for _ in range(n):
            self.passo()

    def marco(self, nome):
        self.marcos.append({"nome": nome, "sala": self.scene.sala_atual,
                            "frame": self.frames, "hp": self.scene.player.hp,
                            "frascos": [self.scene.player.pocao.cargas, self.scene.player.pocao.cargas_max],
                            "posicao": list(self.scene.player.rect.topleft)})
        if self.capturas:
            SAIDA.mkdir(parents=True, exist_ok=True)
            self.scene.desenhar()
            pygame.image.save(self.scene.tela, str(SAIDA / f"{nome}.png"))

    def lutar(self, inimigo):
        hp_inicial = inimigo.hp
        inicio = self.frames
        impactos = dano_recebido = curas = 0
        recuperando = False
        for frame in range(4800):
            if not inimigo.vivo:
                self.inimigos_derrotados.append(type(inimigo).__name__)
                self.combates.append({"inimigo": type(inimigo).__name__, "hp": hp_inicial,
                                      "frames": self.frames - inicio, "impactos": impactos,
                                      "dano_recebido": dano_recebido, "frascos_usados": curas})
                if self.scene._conclusao_beta_timer is None:
                    self.repousar(100)
                return
            p = self.scene.player
            delta = inimigo.rect.centerx - p.rect.centerx
            keys = []
            contornar_escudo = (getattr(inimigo, "_escudo_ativo", False)
                               and (delta < 0) == inimigo.olhando_dir)
            if abs(delta) > 58 or contornar_escudo:
                keys.append(pygame.K_d if delta > 0 else pygame.K_a)
            elif p.olhando_dir != (delta > 0):
                keys.append(pygame.K_d if delta > 0 else pygame.K_a)
            if p.stamina < 22:
                recuperando = True
            elif p.stamina > 75:
                recuperando = False
            golpe = frame % 32 < 19
            if not recuperando and not contornar_escudo and golpe:
                keys.append(pygame.K_k)
            if p.hp < 110 and p.pocao.cargas:
                keys.append(pygame.K_f)
            hp_antes, vida_antes, cargas_antes = inimigo.hp, p.hp, p.pocao.cargas
            self.passo(*keys)
            impactos += int(inimigo.hp < hp_antes)
            dano_recebido += max(0, vida_antes - p.hp)
            curas += max(0, cargas_antes - p.pocao.cargas)
        raise AssertionError(("Combate não terminou", type(inimigo).__name__, hp_inicial,
                              inimigo.hp, inimigo.rect, p.rect, p.hp))

    def andar(self, x, combate=True):
        sala = self.scene.sala_atual
        for _ in range(1800):
            if self.scene.sala_atual != sala:
                return
            p = self.scene.player
            perto = [i for i in self.scene.inimigos if i.vivo and
                     abs(i.rect.centerx - p.rect.centerx) < 240]
            if combate and perto:
                self.lutar(min(perto, key=lambda i: abs(i.rect.centerx - p.rect.centerx)))
            delta = x - p.rect.centerx
            if abs(delta) <= 3:
                return
            direita = delta > 0
            keys = [pygame.K_d if direita else pygame.K_a]
            probe = pygame.Rect(p.rect.right if direita else p.rect.left - 28,
                                p.rect.bottom - 24, 28, 23)
            if p.no_chao and probe.collidelist(self.scene.mapa.rects_solidos) != -1:
                keys.append(pygame.K_SPACE)
            self.passo(*keys)
        raise AssertionError(("Caminho bloqueado", sala, x, p.rect))

    def executar(self):
        s = self.scene
        assert s.sala_atual == SALAS_BETA[0] and not s.player.tem_arma_equipada
        assert s.player.pocao.cargas == s.player.pocao.cargas_max == 0
        self.repousar(15)
        self.marco("01_celas")
        celas = Percurso(s)
        celas.andar(21 * 32 + 16)
        celas.escalar(24 * 32)
        celas.andar(54 * 32 + 16)
        celas.escalar(9 * 32)
        celas.andar(79 * 32 + 16)
        self.frames += celas.frames
        celas.frames = 0
        self.passo(pygame.K_e)
        self.repousar(45)
        assert 9 in s.player.inventario["chaves"]
        self.marco("01b_insignia")
        celas.andar(54 * 32 + 16)
        celas.escalar(24 * 32)
        celas.andar(119 * 32 + 16)
        self.frames += celas.frames
        self.andar(126 * 32)
        assert s.sala_atual == SALAS_BETA[1]
        # Retorno real pelo arco e spawn nomeado das celas.
        self.repousar(65)
        self.andar(-30)
        assert s.sala_atual == SALAS_BETA[0] and s.player.rect.x == 3808
        self.repousar(65)
        self.andar(126 * 32)
        assert s.sala_atual == SALAS_BETA[1]
        self.andar(10 * 32 + 16)
        self.passo(pygame.K_e)
        self.repousar(45)
        assert s.player.inventario["mao_direita"] == 1
        assert 1 not in s.player.inventario["equipamentos"]
        assert s.tutorial_contextual.teclas_ativas == ("k",)
        self.marco("02_arsenal")
        self.andar(36 * 32)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.pocao.cargas == s.player.pocao.cargas_max == 1
        assert "2" not in s.player.inventario["itens"]
        self.marco("02a_primeiro_frasco")
        self.andar(40 * 32)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.inventario["itens"].get("4", 0) >= 1
        self.andar(38 * 32 + 16)
        for _ in range(75):
            self.passo(pygame.K_w)
        self.andar(43 * 32 + 16, combate=False)
        self.passo(pygame.K_e)
        self.repousar(45)
        assert s.player.inventario["itens"].get("6", 0) == 1
        self.passo(pygame.K_s, pygame.K_SPACE)
        self.repousar(60)
        self.passo(eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)])
        assert s.inventario.aberto
        self.marco("02b_inventario")
        self.passo(eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)])
        self.andar(s.largura_mapa + 20)
        assert s.sala_atual == SALAS_BETA[2]
        self.andar(23 * 32 + 16)
        for _ in range(75):
            self.passo(pygame.K_w)
        self.andar(27 * 32 + 16, combate=False)
        assert s.player._sobre_plataforma
        self.passo(pygame.K_e)
        self.repousar(45)
        assert 10 in s.player.inventario["chaves"]
        self.marco("03a_galeria")
        self.passo(pygame.K_s, pygame.K_SPACE)
        self.repousar(60)
        assert s.player.rect.bottom == 640
        self.andar(31 * 32)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.inventario["itens"].get("7", 0) == 1
        self.andar(62 * 32 + 16)
        for _ in range(90):
            self.passo(pygame.K_w)
        self.andar(65 * 32, combate=False)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.pocao.cargas_max == 2
        self.marco("03c_segundo_frasco")
        self.andar(69 * 32, combate=False)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.inventario["materiais"].get("8", 0) == 1
        self.passo(pygame.K_s, pygame.K_SPACE)
        self.repousar(60)
        self.andar(102 * 32)
        self.passo(pygame.K_e)
        self.repousar(50)
        assert s.player.pocao.cargas == s.player.pocao.cargas_max == 3
        self.marco("03d_terceiro_frasco")
        self.andar(105 * 32 + 16)
        self.passo(pygame.K_e)
        assert s.menu_fogueira.aberto
        assert s.player.checkpoint_sala == SALAS_BETA[2]
        self.marco("03b_ecofoco_menu")
        self.passo(eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        assert not s.menu_fogueira.aberto
        assert s.player.hp == s.player.hp_max and s.player.pocao.cargas == 3
        assert len(s.inimigos) == 4
        self.marco("03_corredores")
        checkpoint = (s.player.checkpoint_sala, tuple(s.player.checkpoint_pos))
        self.andar(s.largura_mapa + 20)
        assert s.sala_atual == SALAS_BETA[3]
        assert not s.boss_batalha_ativa
        # Save/load em DB descartável: posição atual e Ecofoco são distintos.
        with TemporaryDirectory(prefix="profane_beta_save_") as tmp:
            with patch("save_manager.CAMINHO_DB", str(Path(tmp) / "saves.db")):
                db = Savemaneger()
            try:
                assert s.salvar(db, 1)
                nova = Gamescene(s.tela)
                nova.carregar_save(db.carregar(1))
                assert nova.sala_atual == SALAS_BETA[3]
                assert (nova.player.checkpoint_sala, tuple(nova.player.checkpoint_pos)) == checkpoint
                assert nova.player.inventario == s.player.inventario
                assert nova.player.pocao.cargas == nova.player.pocao.cargas_max == 3
                # Morte induzida exclusivamente para testar o retorno ao Ecofoco.
                nova.player.receber_dano(nova.player.hp)
                for _ in range(182):
                    nova.atualizar([])
                assert nova.player.vivo and nova.sala_atual == SALAS_BETA[2]
                assert nova.player.rect.collidelist(nova.mapa.rects_solidos) == -1
                assert tuple(nova.player.checkpoint_pos) == checkpoint[1]
                assert nova.player.pocao.cargas_max == 3
                assert not any(d.ativo and d.frasco for d in nova.drops)
                self.marcos.append({"nome": "save_load_morte_respawn", "resultado": "ok"})
                self.andar(22 * 32, combate=False)
                s.hud.limpar_mensagem()
                self.marco("04_arena")
                self.lutar(s.boss_atual)
                assert SALAS_BETA[3] in s.bosses_derrotados
                self.repousar(125)
                assert s.fim_beta is not None
                self.marco("05_fim_beta")
                assert s.salvar(db, 1)
                concluida = Gamescene(s.tela)
                concluida.carregar_save(db.carregar(1))
                assert concluida.fim_beta is not None and concluida.boss_atual is None
            finally:
                db.fechar()
        retornou = []
        s._menu_callback = lambda: retornou.append(True)
        self.passo(eventos=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        assert retornou == [True]
        return {"frames": self.frames, "marcos": self.marcos,
                "inimigos_derrotados": self.inimigos_derrotados,
                "combates": self.combates,
                "metodo": "Teclado simulado, física/IA/combate reais; morte induzida em cena separada; SQLite temporário."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capturas", action="store_true")
    args = parser.parse_args()
    os.chdir(RAIZ)
    pygame.init()
    tela = pygame.display.set_mode((1280, 720))
    problemas = validar_conexoes()
    for sala in SALAS_BETA:
        problemas += validar_mapa_tmx(f"assets/maps/{sala}.tmx")
    assert not problemas, problemas
    resultado = PartidaBeta(tela, args.capturas).executar()
    saida = RAIZ / "docs/beta/polimento"
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "percurso.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    pygame.quit()


if __name__ == "__main__":
    main()
